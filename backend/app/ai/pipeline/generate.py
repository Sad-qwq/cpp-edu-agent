from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, func, select

from app.ai.clients.factory import get_model_provider
from app.ai.retrieval.search import retrieve_relevant_chunks
from app.models.ai_question_generation import (
    DraftTeacherAction,
    DraftValidationStatus,
    QuestionDraft,
    QuestionGenerationJob,
    QuestionGenerationStatus,
    QuestionValidationRun,
    ValidationType,
)

ALLOWED_TYPES = {"choice", "short_answer", "coding"}
ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
REGENERATION_ANGLES = {
    "choice": [
        "概念辨析",
        "代码片段判断",
        "常见错误识别",
        "课堂场景应用",
    ],
    "short_answer": [
        "概念说明",
        "比较分析",
        "常见误区总结",
        "结合代码现象解释",
    ],
    "coding": [
        "基础统计实现",
        "查找与判断",
        "数组遍历处理",
        "函数封装实现",
    ],
}


def _normalize_distribution(raw_distribution: dict[str, int], total_count: int) -> list[str]:
    distribution = {key: int(value) for key, value in (raw_distribution or {}).items() if key in ALLOWED_TYPES and int(value) > 0}
    if not distribution:
        base = ["choice", "short_answer", "coding"]
        return [base[index % len(base)] for index in range(total_count)]

    ordered_types: list[str] = []
    for question_type, count in distribution.items():
        ordered_types.extend([question_type] * count)

    if len(ordered_types) < total_count:
        fallback_order = sorted(distribution.items(), key=lambda item: item[1], reverse=True)
        index = 0
        while len(ordered_types) < total_count:
            ordered_types.append(fallback_order[index % len(fallback_order)][0])
            index += 1

    return ordered_types[:total_count]


def _normalize_difficulties(raw_distribution: dict[str, int], total_count: int) -> list[str]:
    distribution = {key: int(value) for key, value in (raw_distribution or {}).items() if key in ALLOWED_DIFFICULTIES and int(value) > 0}
    if not distribution:
        return ["medium"] * total_count

    ordered: list[str] = []
    for difficulty, count in distribution.items():
        ordered.extend([difficulty] * count)
    if len(ordered) < total_count:
        ordered.extend(["medium"] * (total_count - len(ordered)))
    return ordered[:total_count]


def _build_context(chunks: list[Any]) -> str:
    if not chunks:
        return "暂无可用资料，请结合通用 C++ 基础教学目标出题。"

    parts: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk.metadata_json or {}
        doc_name = metadata.get("document_name") or f"文档 {chunk.document_id}"
        parts.append(
            f"[检索序号 {index}] chunk_id={chunk.id} document_id={chunk.document_id} 来源: {doc_name}\n"
            f"{chunk.content[:600]}"
        )
    return "\n\n".join(parts)


def _build_system_prompt() -> str:
    return """
你是 C++ 教学平台的智能出题助手，服务对象是中职/高校程序设计课程教师。

你的任务不是泛化闲聊，而是依据“主题、知识点、题型分布、难度分布、可用资料”生成可直接进入教师审核流程的题目草稿。

必须遵守以下规则：
1. 全部输出必须是合法 JSON，禁止输出 JSON 以外的任何说明文字。
2. 所有题目必须使用中文表述，题干简洁、明确、可作答。
3. 题目必须优先贴合本次请求中的主题与知识点，不得被无关资料带偏。
4. 如果检索资料中出现与主题无关的代码片段、类名、业务对象、框架内容，应主动忽略，不得机械抄入题干。
5. 优先使用教学性资料：概念定义、语法规则、样例、章节说明、课堂讲义。不要把偶然检索到的项目代码直接改写成题目。
6. 选择题用于概念辨析，至少 4 个选项，且正确答案必须与某个选项完全一致。
7. 简答题用于考查原理理解、概念说明、步骤总结，不要把简答题写成开放闲聊题。
8. 编程题必须包含：明确题意、可运行的 code_template、至少 2 个 test_cases、参考解 reference_solution。
9. easy 难度只考单一核心点；medium 可以组合 2 个相关知识点；hard 允许综合应用，但不能超出当前主题范围。
10. 若资料不足，可基于通用 C++ 教学目标补足细节，但仍必须紧扣主题与知识点，不能凭空切换到别的章节。
11. explanation 字段应简短说明本题考查什么、为什么符合当前知识点。
12. target_knowledge_points 必须只填与本题直接相关的知识点。
13. source_chunk_ids 必须填写真正支撑本题的 chunk_id；如果某题主要依据通用教学常识补足且没有直接引用资料，可返回空数组。
14. 估计分值应与题型和难度匹配：选择题通常 5-10 分，简答题通常 10-15 分，编程题通常 15-25 分。

质量标准：
1. 题干和知识点一致。
2. 不出现明显跑题、串章节、乱引用代码片段的问题。
3. 不照抄资料原文，尽量转化为教学语境下的问题。
4. 编程题输入输出和测试用例要自洽。

如果资料中出现“数组”主题却混入“继承、多态、车辆类”等无关内容，必须忽略这些无关内容，继续围绕数组、函数、循环等目标知识点出题。
""".strip()


def _build_blueprint_payload(job: QuestionGenerationJob, ordered_types: list[str], ordered_difficulties: list[str]) -> dict[str, Any]:
    return {
        "topic": job.topic,
        "knowledge_points": job.knowledge_points,
        "question_count": len(ordered_types),
        "type_distribution": dict(Counter(ordered_types)),
        "difficulty_distribution": dict(Counter(ordered_difficulties)),
    }


def _fallback_draft(
    *,
    job: QuestionGenerationJob,
    draft_index: int,
    question_type: str,
    difficulty: str,
    context_excerpt: str,
    source_chunk_ids: list[int],
    variation_index: int = 0,
) -> dict[str, Any]:
    knowledge_point = job.knowledge_points[draft_index % len(job.knowledge_points)] if job.knowledge_points else job.topic
    excerpt = context_excerpt.strip()[:180] or f"围绕 {knowledge_point} 的课堂资料"
    angle_index = variation_index % 4

    if question_type == "choice":
        choice_variants = [
            {
                "content": f"根据课堂资料，关于“{knowledge_point}”的说法，哪一项最准确？\n参考材料：{excerpt}",
                "options": [
                    f"{knowledge_point} 的核心目标是提升程序正确性与可读性",
                    f"{knowledge_point} 只适用于图形界面程序开发",
                    f"{knowledge_point} 与 C++ 语法、算法设计完全无关",
                    f"{knowledge_point} 只能在不使用标准库时发挥作用",
                ],
                "correct_answer": f"{knowledge_point} 的核心目标是提升程序正确性与可读性",
                "explanation": f"该题从概念辨析角度考查学生是否理解 {knowledge_point} 的基本作用。",
            },
            {
                "content": f"阅读下面关于“{knowledge_point}”的描述，哪一项判断正确？\n参考材料：{excerpt}",
                "options": [
                    f"只要出现 {knowledge_point}，程序运行效率一定提升",
                    f"{knowledge_point} 的使用需要结合具体语境判断，不能脱离问题场景",
                    f"{knowledge_point} 与程序可读性无关",
                    f"{knowledge_point} 只能用于面向对象编程",
                ],
                "correct_answer": f"{knowledge_point} 的使用需要结合具体语境判断，不能脱离问题场景",
                "explanation": f"该题从课堂场景应用角度考查 {knowledge_point} 的合理使用条件。",
            },
            {
                "content": f"关于“{knowledge_point}”的下列说法中，哪一项最能体现常见错误的纠正？\n参考材料：{excerpt}",
                "options": [
                    f"学习 {knowledge_point} 时只需要记结论，不需要理解原因",
                    f"{knowledge_point} 的理解应结合定义、使用方式和易错点一起掌握",
                    f"{knowledge_point} 只在考试中有意义，实际编程中不重要",
                    f"{knowledge_point} 与其他 C++ 基础知识没有关联",
                ],
                "correct_answer": f"{knowledge_point} 的理解应结合定义、使用方式和易错点一起掌握",
                "explanation": f"该题从常见误区识别角度考查学生对 {knowledge_point} 的完整理解。",
            },
            {
                "content": f"若教师希望学生准确掌握“{knowledge_point}”，下列哪项课堂结论最合理？\n参考材料：{excerpt}",
                "options": [
                    f"{knowledge_point} 可以脱离具体代码单独记忆，不需要练习",
                    f"{knowledge_point} 应通过概念理解与基础代码练习共同掌握",
                    f"{knowledge_point} 只适合在复杂项目中学习",
                    f"{knowledge_point} 学完后不需要再与函数、数组、循环等内容联系",
                ],
                "correct_answer": f"{knowledge_point} 应通过概念理解与基础代码练习共同掌握",
                "explanation": f"该题从教学目标角度考查 {knowledge_point} 的正确学习方式。",
            },
        ]
        variant = choice_variants[angle_index]
        return {
            "type": "choice",
            "content": variant["content"],
            "options": variant["options"],
            "correct_answer": variant["correct_answer"],
            "code_template": None,
            "test_cases": [],
            "reference_solution": None,
            "explanation": variant["explanation"],
            "target_knowledge_points": [knowledge_point],
            "difficulty": difficulty,
            "estimated_score": 10,
            "source_chunk_ids": source_chunk_ids,
        }

    if question_type == "short_answer":
        short_answer_variants = [
            {
                "content": f"请结合课堂资料，简述“{knowledge_point}”的核心概念，并说明它在 C++ 学习中的实际意义。\n可参考材料：{excerpt}",
                "correct_answer": f"回答应覆盖 {knowledge_point} 的定义、典型使用场景，以及它对代码结构或程序行为的影响。",
                "explanation": f"该题要求学生复述并组织资料中的关键概念，验证是否真正理解 {knowledge_point}。",
            },
            {
                "content": f"请说明“{knowledge_point}”在课堂练习中通常解决什么问题，并举出一个适合它的简单使用场景。\n可参考材料：{excerpt}",
                "correct_answer": f"回答应说明 {knowledge_point} 的主要用途、适用场景，并给出一个贴合课堂内容的基础示例。",
                "explanation": f"该题从应用场景角度考查学生是否能把 {knowledge_point} 与实际问题联系起来。",
            },
            {
                "content": f"学习“{knowledge_point}”时，学生最容易出现哪些理解偏差？请结合课堂资料进行分析。\n可参考材料：{excerpt}",
                "correct_answer": f"回答应指出学习 {knowledge_point} 时的常见误区，并结合定义、规则或代码现象说明正确理解方式。",
                "explanation": f"该题从常见误区总结角度考查学生对 {knowledge_point} 的深入理解。",
            },
            {
                "content": f"请比较“{knowledge_point}”与相关基础知识在使用方式上的联系或区别，并说明为什么需要掌握这一点。\n可参考材料：{excerpt}",
                "correct_answer": f"回答应围绕 {knowledge_point} 与相关知识点的联系或区别展开，并说明其对代码编写或理解的意义。",
                "explanation": f"该题从比较分析角度考查学生是否能把 {knowledge_point} 放到更完整的知识结构中理解。",
            },
        ]
        variant = short_answer_variants[angle_index]
        return {
            "type": "short_answer",
            "content": variant["content"],
            "options": [],
            "correct_answer": variant["correct_answer"],
            "code_template": None,
            "test_cases": [],
            "reference_solution": None,
            "explanation": variant["explanation"],
            "target_knowledge_points": [knowledge_point],
            "difficulty": difficulty,
            "estimated_score": 15,
            "source_chunk_ids": source_chunk_ids,
        }

    coding_variants = [
        {
            "content": (
                f"编写一个 C++ 程序，读取一个整数 n 和随后输入的 n 个整数，输出其中大于平均值的元素个数。"
                f"请在实现过程中体现“{knowledge_point}”相关的编程规范或思路，并参考资料中的表达方式。"
            ),
            "code_template": (
                "#include <iostream>\n"
                "#include <vector>\n"
                "using namespace std;\n\n"
                "int main() {\n"
                "    int n;\n"
                "    cin >> n;\n"
                "    vector<int> nums(n);\n"
                "    // TODO: 读取数据并输出结果\n"
                "    return 0;\n"
                "}\n"
            ),
            "test_cases": [
                {"input": "5\n1 2 3 4 5\n", "output": "2\n"},
                {"input": "4\n2 2 2 2\n", "output": "0\n"},
            ],
            "reference_solution": (
                "#include <iostream>\n"
                "#include <vector>\n"
                "using namespace std;\n\n"
                "int main() {\n"
                "    int n;\n"
                "    cin >> n;\n"
                "    vector<int> nums(n);\n"
                "    long long sum = 0;\n"
                "    for (int i = 0; i < n; ++i) {\n"
                "        cin >> nums[i];\n"
                "        sum += nums[i];\n"
                "    }\n"
                "    double avg = static_cast<double>(sum) / n;\n"
                "    int count = 0;\n"
                "    for (int value : nums) {\n"
                "        if (value > avg) {\n"
                "            ++count;\n"
                "        }\n"
                "    }\n"
                "    cout << count << endl;\n"
                "    return 0;\n"
                "}\n"
            ),
            "explanation": f"该编程题使用数组统计任务承载 {knowledge_point} 相关训练，适合课堂练习和自动判题。",
        },
        {
            "content": (
                f"编写一个 C++ 程序，读取一个整数 n 和随后输入的 n 个整数，输出其中的最大值与最小值。"
                f"要求使用基础循环完成，并体现“{knowledge_point}”相关的实现要点。"
            ),
            "code_template": (
                "#include <iostream>\n"
                "#include <vector>\n"
                "using namespace std;\n\n"
                "int main() {\n"
                "    int n;\n"
                "    cin >> n;\n"
                "    vector<int> nums(n);\n"
                "    // TODO: 输出最大值和最小值\n"
                "    return 0;\n"
                "}\n"
            ),
            "test_cases": [
                {"input": "5\n1 3 2 5 4\n", "output": "5 1\n"},
                {"input": "3\n-1 -5 -3\n", "output": "-1 -5\n"},
            ],
            "reference_solution": (
                "#include <iostream>\n"
                "#include <vector>\n"
                "using namespace std;\n\n"
                "int main() {\n"
                "    int n;\n"
                "    cin >> n;\n"
                "    vector<int> nums(n);\n"
                "    for (int i = 0; i < n; ++i) {\n"
                "        cin >> nums[i];\n"
                "    }\n"
                "    int maxValue = nums[0];\n"
                "    int minValue = nums[0];\n"
                "    for (int i = 1; i < n; ++i) {\n"
                "        if (nums[i] > maxValue) maxValue = nums[i];\n"
                "        if (nums[i] < minValue) minValue = nums[i];\n"
                "    }\n"
                "    cout << maxValue << ' ' << minValue << endl;\n"
                "    return 0;\n"
                "}\n"
            ),
            "explanation": f"该题改为查找与判断任务，考查学生是否能用循环和数组完成基础分析。",
        },
        {
            "content": (
                f"编写一个 C++ 程序，读取一个整数 n 和随后输入的 n 个整数，输出所有偶数元素的个数。"
                f"要求代码结构清晰，并体现“{knowledge_point}”相关的基础实现能力。"
            ),
            "code_template": (
                "#include <iostream>\n"
                "#include <vector>\n"
                "using namespace std;\n\n"
                "int main() {\n"
                "    int n;\n"
                "    cin >> n;\n"
                "    vector<int> nums(n);\n"
                "    // TODO: 统计偶数个数\n"
                "    return 0;\n"
                "}\n"
            ),
            "test_cases": [
                {"input": "6\n1 2 3 4 5 6\n", "output": "3\n"},
                {"input": "4\n1 3 5 7\n", "output": "0\n"},
            ],
            "reference_solution": (
                "#include <iostream>\n"
                "#include <vector>\n"
                "using namespace std;\n\n"
                "int main() {\n"
                "    int n;\n"
                "    cin >> n;\n"
                "    vector<int> nums(n);\n"
                "    int count = 0;\n"
                "    for (int i = 0; i < n; ++i) {\n"
                "        cin >> nums[i];\n"
                "        if (nums[i] % 2 == 0) {\n"
                "            ++count;\n"
                "        }\n"
                "    }\n"
                "    cout << count << endl;\n"
                "    return 0;\n"
                "}\n"
            ),
            "explanation": f"该题从遍历与条件统计角度训练学生对 {knowledge_point} 的基础应用。",
        },
        {
            "content": (
                f"定义一个函数，用于计算长度为 n 的整型数组中正数元素的和，并在主函数中调用它。"
                f"请结合“{knowledge_point}”完成程序。"
            ),
            "code_template": (
                "#include <iostream>\n"
                "#include <vector>\n"
                "using namespace std;\n\n"
                "int sumPositive(const vector<int>& nums) {\n"
                "    // TODO: 返回正数元素之和\n"
                "    return 0;\n"
                "}\n\n"
                "int main() {\n"
                "    int n;\n"
                "    cin >> n;\n"
                "    vector<int> nums(n);\n"
                "    // TODO: 读取数据并调用函数\n"
                "    return 0;\n"
                "}\n"
            ),
            "test_cases": [
                {"input": "5\n1 -2 3 4 -5\n", "output": "8\n"},
                {"input": "4\n-1 -2 -3 -4\n", "output": "0\n"},
            ],
            "reference_solution": (
                "#include <iostream>\n"
                "#include <vector>\n"
                "using namespace std;\n\n"
                "int sumPositive(const vector<int>& nums) {\n"
                "    int sum = 0;\n"
                "    for (int value : nums) {\n"
                "        if (value > 0) {\n"
                "            sum += value;\n"
                "        }\n"
                "    }\n"
                "    return sum;\n"
                "}\n\n"
                "int main() {\n"
                "    int n;\n"
                "    cin >> n;\n"
                "    vector<int> nums(n);\n"
                "    for (int i = 0; i < n; ++i) {\n"
                "        cin >> nums[i];\n"
                "    }\n"
                "    cout << sumPositive(nums) << endl;\n"
                "    return 0;\n"
                "}\n"
            ),
            "explanation": f"该题从函数封装角度考查学生是否能把 {knowledge_point} 与数组处理结合起来。",
        },
    ]
    variant = coding_variants[angle_index]
    return {
        "type": "coding",
        "content": variant["content"],
        "options": [],
        "correct_answer": None,
        "code_template": variant["code_template"],
        "test_cases": variant["test_cases"],
        "reference_solution": variant["reference_solution"],
        "explanation": variant["explanation"],
        "target_knowledge_points": [knowledge_point],
        "difficulty": difficulty,
        "estimated_score": 20,
        "source_chunk_ids": source_chunk_ids,
    }


def _validate_draft_payload(draft: dict[str, Any]) -> tuple[DraftValidationStatus, dict[str, Any]]:
    issues: list[str] = []
    question_type = draft.get("type")

    if question_type not in ALLOWED_TYPES:
        issues.append("Unsupported question type")
    if not str(draft.get("content") or "").strip():
        issues.append("Question content is empty")

    if question_type == "choice":
        options = [option for option in draft.get("options", []) if str(option).strip()]
        if len(options) < 2:
            issues.append("Choice question must have at least two options")
        if draft.get("correct_answer") and draft.get("correct_answer") not in options:
            issues.append("Choice correct answer must match one option")

    if question_type == "coding" and not draft.get("test_cases"):
        issues.append("Coding question must include test cases")

    status = DraftValidationStatus.PASSED if not issues else DraftValidationStatus.WARNING
    return status, {"issues": issues}


async def _generate_with_provider(
    session: AsyncSession,
    *,
    job: QuestionGenerationJob,
    context: str,
    ordered_types: list[str],
    ordered_difficulties: list[str],
) -> list[dict[str, Any]]:
    provider = await get_model_provider(session)
    if provider is None:
        return []

    schema = {
        "type": "object",
        "properties": {
            "drafts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "content": {"type": "string"},
                        "options": {"type": "array"},
                        "correct_answer": {"type": ["string", "null"]},
                        "code_template": {"type": ["string", "null"]},
                        "test_cases": {"type": "array"},
                        "reference_solution": {"type": ["string", "null"]},
                        "explanation": {"type": ["string", "null"]},
                        "target_knowledge_points": {"type": "array"},
                        "difficulty": {"type": ["string", "null"]},
                        "estimated_score": {"type": ["integer", "null"]},
                        "source_chunk_ids": {"type": "array"},
                    },
                    "required": ["type", "content", "options", "test_cases", "target_knowledge_points", "source_chunk_ids"],
                },
            },
        },
        "required": ["drafts"],
    }

    user_prompt = (
        f"主题：{job.topic}\n"
        f"知识点：{', '.join(job.knowledge_points) if job.knowledge_points else '无'}\n"
        f"题型顺序：{ordered_types}\n"
        f"难度顺序：{ordered_difficulties}\n"
        f"额外约束：{job.request_payload.get('extra_constraints') or '无'}\n\n"
        f"可用资料：\n{context}"
    )
    system_prompt = _build_system_prompt()

    response = await provider.generate_json(system_prompt=system_prompt, user_prompt=user_prompt, schema=schema)
    drafts = response.get("drafts") if isinstance(response, dict) else None
    return drafts if isinstance(drafts, list) else []


async def _regenerate_single_with_provider(
    session: AsyncSession,
    *,
    job: QuestionGenerationJob,
    draft: QuestionDraft,
    context: str,
    question_type: str,
    difficulty: str,
    variation_index: int,
) -> dict[str, Any] | None:
    provider = await get_model_provider(session)
    if provider is None:
        return None

    schema = {
        "type": "object",
        "properties": {
            "draft": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "content": {"type": "string"},
                    "options": {"type": "array"},
                    "correct_answer": {"type": ["string", "null"]},
                    "code_template": {"type": ["string", "null"]},
                    "test_cases": {"type": "array"},
                    "reference_solution": {"type": ["string", "null"]},
                    "explanation": {"type": ["string", "null"]},
                    "target_knowledge_points": {"type": "array"},
                    "difficulty": {"type": ["string", "null"]},
                    "estimated_score": {"type": ["integer", "null"]},
                    "source_chunk_ids": {"type": "array"},
                },
                "required": ["type", "content", "options", "test_cases", "target_knowledge_points", "source_chunk_ids"],
            },
        },
        "required": ["draft"],
    }

    angle = REGENERATION_ANGLES.get(question_type, ["不同角度重写"])[variation_index % len(REGENERATION_ANGLES.get(question_type, ["不同角度重写"]))]
    user_prompt = (
        f"当前任务：对单道题进行重生成，必须生成与旧题明显不同的新版本。\n"
        f"主题：{job.topic}\n"
        f"知识点：{', '.join(job.knowledge_points) if job.knowledge_points else '无'}\n"
        f"题型：{question_type}\n"
        f"难度：{difficulty}\n"
        f"本次要求采用的重生成角度：{angle}\n"
        f"额外约束：{job.request_payload.get('extra_constraints') or '无'}\n\n"
        f"旧题内容：\n{draft.content}\n\n"
        f"重生成要求：\n"
        f"1. 新题必须仍然贴合原主题和知识点。\n"
        f"2. 新题与旧题在题干表述、考查角度、任务场景或代码任务上至少有一项明显不同。\n"
        f"3. 不得只做同义改写。\n"
        f"4. 若为编程题，应尽量更换任务目标或输入输出要求，但保持难度层级一致。\n\n"
        f"可用资料：\n{context}"
    )

    response = await provider.generate_json(system_prompt=_build_system_prompt(), user_prompt=user_prompt, schema=schema)
    regenerated = response.get("draft") if isinstance(response, dict) else None
    return regenerated if isinstance(regenerated, dict) else None


async def _build_regenerated_draft(
    session: AsyncSession,
    *,
    job: QuestionGenerationJob,
    draft: QuestionDraft,
    ordered_types: list[str],
    ordered_difficulties: list[str],
    chunks: list[Any],
) -> dict[str, Any]:
    validation_count_stmt = select(func.count()).where(QuestionValidationRun.draft_id == draft.id)
    validation_count = int((await session.execute(validation_count_stmt)).scalar_one() or 0)
    variation_index = max(0, validation_count - 1)
    question_type = ordered_types[draft.draft_index % len(ordered_types)]
    difficulty = ordered_difficulties[draft.draft_index % len(ordered_difficulties)]

    selected_chunks: list[Any] = []
    if chunks:
        chunk_count = min(2, len(chunks))
        start = (draft.draft_index + variation_index) % len(chunks)
        selected_chunks = [chunks[(start + offset) % len(chunks)] for offset in range(chunk_count)]

    context = _build_context(selected_chunks)
    regenerated = await _regenerate_single_with_provider(
        session,
        job=job,
        draft=draft,
        context=context,
        question_type=question_type,
        difficulty=difficulty,
        variation_index=variation_index,
    )
    if regenerated:
        regenerated.setdefault("type", question_type)
        regenerated.setdefault("difficulty", difficulty)
        regenerated.setdefault("options", [])
        regenerated.setdefault("test_cases", [])
        regenerated.setdefault("target_knowledge_points", [job.knowledge_points[draft.draft_index % len(job.knowledge_points)]] if job.knowledge_points else [job.topic])
        regenerated.setdefault("source_chunk_ids", [chunk.id for chunk in selected_chunks])
        return regenerated

    primary_chunk = selected_chunks[0] if selected_chunks else None
    context_excerpt = "\n\n".join(chunk.content[:300] for chunk in selected_chunks) if selected_chunks else ""
    return _fallback_draft(
        job=job,
        draft_index=draft.draft_index,
        question_type=question_type,
        difficulty=difficulty,
        context_excerpt=context_excerpt or (primary_chunk.content if primary_chunk else ""),
        source_chunk_ids=[chunk.id for chunk in selected_chunks] if selected_chunks else ([primary_chunk.id] if primary_chunk else []),
        variation_index=variation_index,
    )


async def run_generation_job(session: AsyncSession, job_id: int) -> QuestionGenerationJob:
    job = await session.get(QuestionGenerationJob, job_id)
    if not job:
        raise ValueError("Question generation job not found")

    request_payload = job.request_payload or {}
    total_count = int(request_payload.get("total_count") or 5)
    ordered_types = _normalize_distribution(request_payload.get("question_type_distribution", {}), total_count)
    ordered_difficulties = _normalize_difficulties(request_payload.get("difficulty_distribution", {}), total_count)

    job.status = QuestionGenerationStatus.RETRIEVING
    job.started_at = job.started_at or datetime.utcnow()
    job.error_message = None
    session.add(job)
    await session.commit()

    chunks = await retrieve_relevant_chunks(
        session,
        class_id=job.class_id,
        topic=job.topic,
        knowledge_points=job.knowledge_points,
        use_class_materials=bool(request_payload.get("use_class_materials", True)),
        use_admin_knowledge_base=bool(request_payload.get("use_admin_knowledge_base", True)),
        limit=max(4, min(total_count * 2, 10)),
    )
    context = _build_context(chunks)
    job.retrieval_summary = {
        "chunk_count": len(chunks),
        "chunk_ids": [chunk.id for chunk in chunks],
        "documents": [
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "document_name": (chunk.metadata_json or {}).get("document_name"),
            }
            for chunk in chunks
        ],
    }
    job.blueprint_json = _build_blueprint_payload(job, ordered_types, ordered_difficulties)
    job.status = QuestionGenerationStatus.GENERATING
    session.add(job)
    await session.commit()

    generated_drafts = await _generate_with_provider(
        session,
        job=job,
        context=context,
        ordered_types=ordered_types,
        ordered_difficulties=ordered_difficulties,
    )

    if not generated_drafts:
        generated_drafts = []
        for index, question_type in enumerate(ordered_types):
            chunk = chunks[index % len(chunks)] if chunks else None
            generated_drafts.append(
                _fallback_draft(
                    job=job,
                    draft_index=index,
                    question_type=question_type,
                    difficulty=ordered_difficulties[index],
                    context_excerpt=chunk.content if chunk else "",
                    source_chunk_ids=[chunk.id] if chunk else [],
                )
            )

    await session.execute(delete(QuestionValidationRun).where(QuestionValidationRun.draft_id.in_(select(QuestionDraft.id).where(QuestionDraft.job_id == job.id))))
    await session.execute(delete(QuestionDraft).where(QuestionDraft.job_id == job.id))

    job.status = QuestionGenerationStatus.VALIDATING
    session.add(job)
    await session.commit()

    for index, draft_payload in enumerate(generated_drafts[:total_count]):
        draft_payload.setdefault("type", ordered_types[index])
        draft_payload.setdefault("difficulty", ordered_difficulties[index])
        draft_payload.setdefault("options", [])
        draft_payload.setdefault("test_cases", [])
        draft_payload.setdefault("target_knowledge_points", job.knowledge_points[:1] if job.knowledge_points else [job.topic])
        draft_payload.setdefault("source_chunk_ids", [chunk.id for chunk in chunks[:1]])

        validation_status, validation_report = _validate_draft_payload(draft_payload)
        draft = QuestionDraft(
            job_id=job.id,
            draft_index=index,
            type=draft_payload["type"],
            content=draft_payload["content"],
            options=draft_payload.get("options", []),
            correct_answer=draft_payload.get("correct_answer"),
            code_template=draft_payload.get("code_template"),
            test_cases=draft_payload.get("test_cases", []),
            reference_solution=draft_payload.get("reference_solution"),
            explanation=draft_payload.get("explanation"),
            target_knowledge_points=draft_payload.get("target_knowledge_points", []),
            difficulty=draft_payload.get("difficulty"),
            estimated_score=draft_payload.get("estimated_score"),
            source_chunk_ids=draft_payload.get("source_chunk_ids", []),
            validation_status=validation_status,
            validation_report=validation_report,
            teacher_action=DraftTeacherAction.PENDING,
            updated_at=datetime.utcnow(),
        )
        session.add(draft)
        await session.flush()

        session.add(
            QuestionValidationRun(
                draft_id=draft.id,
                validation_type=ValidationType.SCHEMA,
                status=validation_status,
                report_json=validation_report,
            )
        )

    job.status = QuestionGenerationStatus.REVIEWING
    job.finished_at = datetime.utcnow()
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


async def regenerate_single_draft(session: AsyncSession, *, job_id: int, draft_id: int) -> QuestionDraft:
    job = await session.get(QuestionGenerationJob, job_id)
    draft = await session.get(QuestionDraft, draft_id)
    if not job or not draft or draft.job_id != job_id:
        raise ValueError("Draft not found")

    request_payload = job.request_payload or {}
    ordered_types = _normalize_distribution(request_payload.get("question_type_distribution", {}), int(request_payload.get("total_count") or 5))
    ordered_difficulties = _normalize_difficulties(request_payload.get("difficulty_distribution", {}), int(request_payload.get("total_count") or 5))
    chunks = await retrieve_relevant_chunks(
        session,
        class_id=job.class_id,
        topic=job.topic,
        knowledge_points=job.knowledge_points,
        use_class_materials=bool(request_payload.get("use_class_materials", True)),
        use_admin_knowledge_base=bool(request_payload.get("use_admin_knowledge_base", True)),
        limit=6,
    )
    regenerated = await _build_regenerated_draft(
        session,
        job=job,
        draft=draft,
        ordered_types=ordered_types,
        ordered_difficulties=ordered_difficulties,
        chunks=chunks,
    )

    validation_status, validation_report = _validate_draft_payload(regenerated)
    draft.type = regenerated["type"]
    draft.content = regenerated["content"]
    draft.options = regenerated.get("options", [])
    draft.correct_answer = regenerated.get("correct_answer")
    draft.code_template = regenerated.get("code_template")
    draft.test_cases = regenerated.get("test_cases", [])
    draft.reference_solution = regenerated.get("reference_solution")
    draft.explanation = regenerated.get("explanation")
    draft.target_knowledge_points = regenerated.get("target_knowledge_points", [])
    draft.difficulty = regenerated.get("difficulty")
    draft.estimated_score = regenerated.get("estimated_score")
    draft.source_chunk_ids = regenerated.get("source_chunk_ids", [])
    draft.validation_status = validation_status
    draft.validation_report = validation_report
    draft.teacher_action = DraftTeacherAction.REGENERATED
    draft.updated_at = datetime.utcnow()
    session.add(draft)

    session.add(
        QuestionValidationRun(
            draft_id=draft.id,
            validation_type=ValidationType.SCHEMA,
            status=validation_status,
            report_json=validation_report,
        )
    )
    await session.commit()
    await session.refresh(draft)
    return draft