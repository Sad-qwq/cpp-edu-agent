from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, select

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
        parts.append(f"[{index}] 来源: {doc_name}\n{chunk.content[:600]}")
    return "\n\n".join(parts)


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
) -> dict[str, Any]:
    knowledge_point = job.knowledge_points[draft_index % len(job.knowledge_points)] if job.knowledge_points else job.topic
    excerpt = context_excerpt.strip()[:180] or f"围绕 {knowledge_point} 的课堂资料"

    if question_type == "choice":
        return {
            "type": "choice",
            "content": f"根据课堂资料，关于“{knowledge_point}”的说法，哪一项最准确？\n参考材料：{excerpt}",
            "options": [
                f"{knowledge_point} 的核心目标是提升程序正确性与可读性",
                f"{knowledge_point} 只适用于图形界面程序开发",
                f"{knowledge_point} 与 C++ 语法、算法设计完全无关",
                f"{knowledge_point} 只能在不使用标准库时发挥作用",
            ],
            "correct_answer": f"{knowledge_point} 的核心目标是提升程序正确性与可读性",
            "code_template": None,
            "test_cases": [],
            "reference_solution": None,
            "explanation": f"题目基于资料摘要生成，考查学生是否理解 {knowledge_point} 的基本作用。",
            "target_knowledge_points": [knowledge_point],
            "difficulty": difficulty,
            "estimated_score": 10,
            "source_chunk_ids": source_chunk_ids,
        }

    if question_type == "short_answer":
        return {
            "type": "short_answer",
            "content": f"请结合课堂资料，简述“{knowledge_point}”的核心概念，并说明它在 C++ 学习中的实际意义。\n可参考材料：{excerpt}",
            "options": [],
            "correct_answer": f"回答应覆盖 {knowledge_point} 的定义、典型使用场景，以及它对代码结构或程序行为的影响。",
            "code_template": None,
            "test_cases": [],
            "reference_solution": None,
            "explanation": f"该题要求学生复述并组织资料中的关键概念，验证是否真正理解 {knowledge_point}。",
            "target_knowledge_points": [knowledge_point],
            "difficulty": difficulty,
            "estimated_score": 15,
            "source_chunk_ids": source_chunk_ids,
        }

    return {
        "type": "coding",
        "content": (
            f"编写一个 C++ 程序，读取一个整数 n 和随后输入的 n 个整数，输出其中大于平均值的元素个数。"
            f"请在实现过程中体现“{knowledge_point}”相关的编程规范或思路，并参考资料中的表达方式。"
        ),
        "options": [],
        "correct_answer": None,
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
        "explanation": f"该编程题使用基础数组统计任务承载 {knowledge_point} 相关训练，适合课堂练习和自动判题。",
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
    system_prompt = (
        "你是 C++ 教学平台的智能出题助手。"
        "请严格基于提供的资料生成题目草稿，输出中文，禁止输出 JSON 以外的任何文本。"
        "题目需适合课堂教学，编程题必须带测试用例和参考解。"
    )

    response = await provider.generate_json(system_prompt=system_prompt, user_prompt=user_prompt, schema=schema)
    drafts = response.get("drafts") if isinstance(response, dict) else None
    return drafts if isinstance(drafts, list) else []


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
    chunk = chunks[draft.draft_index % len(chunks)] if chunks else None
    regenerated = _fallback_draft(
        job=job,
        draft_index=draft.draft_index,
        question_type=ordered_types[draft.draft_index % len(ordered_types)],
        difficulty=ordered_difficulties[draft.draft_index % len(ordered_difficulties)],
        context_excerpt=chunk.content if chunk else "",
        source_chunk_ids=[chunk.id] if chunk else [],
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