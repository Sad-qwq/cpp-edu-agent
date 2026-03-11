from __future__ import annotations

from datetime import datetime
import json
import re
from typing import Any, Iterable

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.ai.clients.factory import get_model_provider
from app.ai.retrieval.search import retrieve_relevant_chunks
from app.models.ai_question_generation import KnowledgeChunk
from app.models.ai_tutor import TutorMessage, TutorMessageRole, TutorMode, TutorSession
from app.models.assignment import Assignment, Problem, Submission
from app.models.classroom import ClassMembership, Classroom
from app.models.user import User, UserRole
from app.schemas.ai_tutor import PracticeRecommendationRead, TutorReplyPayload


def _extract_keywords(*texts: str, limit: int = 8) -> list[str]:
    tokens: list[str] = []
    for text in texts:
        for token in re.split(r"[\s,，。；;：:\n\t\-_/()（）【】\[\]]+", text or ""):
            normalized = token.strip()
            if len(normalized) < 2:
                continue
            if normalized.lower() in {"请问", "这个", "那个", "代码", "题目", "作业", "学习", "帮助", "一下"}:
                continue
            tokens.append(normalized[:30])

    deduplicated: list[str] = []
    for token in tokens:
        if token not in deduplicated:
            deduplicated.append(token)
    return deduplicated[:limit]


async def ensure_class_access(session: AsyncSession, class_id: int, current_user: User) -> Classroom:
    classroom = await session.get(Classroom, class_id)
    if not classroom or not classroom.is_active:
        raise HTTPException(status_code=404, detail="Classroom not found or inactive")

    if current_user.role == UserRole.ADMIN or classroom.teacher_id == current_user.id:
        return classroom

    membership_result = await session.execute(
        select(ClassMembership).where(
            ClassMembership.class_id == class_id,
            ClassMembership.student_id == current_user.id,
            ClassMembership.is_active == True,
        )
    )
    membership = membership_result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return classroom


async def ensure_session_access(session: AsyncSession, tutor_session: TutorSession, current_user: User) -> TutorSession:
    await ensure_class_access(session, tutor_session.class_id, current_user)
    if current_user.role == UserRole.STUDENT and tutor_session.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Students can only access their own tutor sessions")
    return tutor_session


async def _load_assignment_context(session: AsyncSession, assignment_id: int | None, problem_id: int | None) -> tuple[Assignment | None, Problem | None]:
    assignment = await session.get(Assignment, assignment_id) if assignment_id else None
    problem = await session.get(Problem, problem_id) if problem_id else None
    return assignment, problem


def _format_chunk_context(chunks: list[KnowledgeChunk]) -> str:
    if not chunks:
        return "暂无命中的班级资料或公共知识库内容。"

    parts: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk.metadata_json or {}
        document_name = metadata.get("document_name") or f"文档 {chunk.document_id}"
        parts.append(f"[资料 {index}] chunk_id={chunk.id} 来源={document_name}\n{chunk.content[:500]}")
    return "\n\n".join(parts)


def _build_system_prompt(mode: TutorMode) -> str:
    mode_guidance = {
        TutorMode.CONCEPT: "你要扮演概念讲解型助教，重点是解释知识点、澄清误区、给出下一步学习动作。",
        TutorMode.HINT: "你要扮演解题提示型助教，只给分层提示，不直接给最终完整答案。",
        TutorMode.CODE_REVIEW: "你要扮演代码纠错型助教，重点解释编译错误、运行错误、逻辑问题和最小修改方向。",
        TutorMode.PRACTICE: "你要扮演练习推荐型助教，输出最值得继续练习的方向和理由。",
    }[mode]
    return (
        "你是 C++ 教学平台中的 AI 智能助学助手，面向学生提供课程内答疑、提示和学习建议。\n"
        f"{mode_guidance}\n"
        "必须遵守以下规则：\n"
        "1. 只输出合法 JSON。\n"
        "2. 回答必须使用中文。\n"
        "3. 优先引用资料中的定义、规则、样例和课堂语境。\n"
        "4. 如果是提示模式，禁止直接给完整标准答案或整段可直接提交的最终代码。\n"
        "5. 如果资料不足，可以给保守解释，但要避免编造具体教材内容。\n"
        "6. follow_up_questions 必须给出学生接下来可以继续追问的问题。\n"
        "7. recommended_action 必须是一个明确动作，例如“先画变量变化表”“先验证循环边界”。\n"
        "8. risk_flags 用来标记潜在风险，例如“资料不足”“可能涉及直接答案”“缺少报错信息”。"
    )


def _build_reply_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "required": [
            "answer",
            "hint_level",
            "cited_chunk_ids",
            "related_knowledge_points",
            "follow_up_questions",
            "recommended_action",
            "risk_flags",
        ],
        "properties": {
            "answer": {"type": "string"},
            "hint_level": {"type": ["integer", "null"]},
            "cited_chunk_ids": {"type": "array", "items": {"type": "integer"}},
            "related_knowledge_points": {"type": "array", "items": {"type": "string"}},
            "follow_up_questions": {"type": "array", "items": {"type": "string"}},
            "recommended_action": {"type": "string"},
            "risk_flags": {"type": "array", "items": {"type": "string"}},
        },
    }


def _build_user_prompt(
    *,
    mode: TutorMode,
    question: str,
    hint_level: int | None,
    assignment: Assignment | None,
    problem: Problem | None,
    recent_messages: Iterable[TutorMessage],
    chunks: list[KnowledgeChunk],
    student_code: str | None = None,
    compiler_output: str | None = None,
    student_answer: str | None = None,
    expected_output: str | None = None,
) -> str:
    recent_dialogue = "\n".join(f"- {message.role.value}: {message.content[:200]}" for message in recent_messages)
    problem_block = ""
    if problem:
        problem_block = (
            f"\n当前题目：{problem.content}\n"
            f"题型：{problem.type}\n"
            f"参考答案字段：{problem.correct_answer or '无'}\n"
            f"代码模板：{problem.code_template or '无'}\n"
            f"测试用例：{json.dumps(problem.test_cases, ensure_ascii=False)}\n"
        )
    assignment_block = ""
    if assignment:
        assignment_block = f"\n当前作业：{assignment.title}\n作业说明：{assignment.description or '无'}\n"

    extra = []
    if student_answer:
        extra.append(f"学生当前答案：{student_answer}")
    if student_code:
        extra.append(f"学生代码：\n{student_code}")
    if compiler_output:
        extra.append(f"编译或运行输出：\n{compiler_output}")
    if expected_output:
        extra.append(f"期望输出：\n{expected_output}")

    return (
        f"模式：{mode.value}\n"
        f"学生问题：{question}\n"
        f"提示层级：{hint_level if hint_level is not None else '无'}\n"
        f"最近对话：\n{recent_dialogue or '无'}\n"
        f"{assignment_block}"
        f"{problem_block}"
        f"附加信息：\n{'\n'.join(extra) if extra else '无'}\n\n"
        f"可参考资料：\n{_format_chunk_context(chunks)}"
    )


def _normalize_reply(raw: dict[str, Any], hint_level: int | None, chunks: list[KnowledgeChunk], fallback_keywords: list[str]) -> TutorReplyPayload:
    cited_chunk_ids = [int(item) for item in raw.get("cited_chunk_ids", []) if isinstance(item, (int, float))]
    valid_chunk_ids = {chunk.id for chunk in chunks if chunk.id is not None}
    cited_chunk_ids = [item for item in cited_chunk_ids if item in valid_chunk_ids]
    related_knowledge_points = [str(item) for item in raw.get("related_knowledge_points", []) if str(item).strip()]
    if not related_knowledge_points:
        related_knowledge_points = fallback_keywords[:3]
    follow_up_questions = [str(item) for item in raw.get("follow_up_questions", []) if str(item).strip()][:3]
    risk_flags = [str(item) for item in raw.get("risk_flags", []) if str(item).strip()]
    answer = str(raw.get("answer") or "")
    if not answer:
        answer = "我先帮你聚焦问题。你可以先确认题目要求、关键变量变化和边界条件，再告诉我你卡住的具体一步。"
    recommended_action = str(raw.get("recommended_action") or "先把题目中的输入、处理过程和输出逐行写清楚。")

    return TutorReplyPayload(
        answer=answer,
        hint_level=hint_level if hint_level is not None else raw.get("hint_level"),
        cited_chunk_ids=cited_chunk_ids,
        related_knowledge_points=related_knowledge_points,
        follow_up_questions=follow_up_questions or ["这一步你最不确定的是变量、循环还是条件判断？"],
        recommended_action=recommended_action,
        risk_flags=risk_flags,
    )


def _fallback_reply(
    *,
    mode: TutorMode,
    question: str,
    hint_level: int | None,
    chunks: list[KnowledgeChunk],
    keywords: list[str],
    compiler_output: str | None = None,
    problem: Problem | None = None,
) -> TutorReplyPayload:
    excerpt = chunks[0].content[:120] if chunks else "当前没有命中课程资料"
    if mode == TutorMode.HINT:
        hints = {
            1: "先不要急着写完整答案，先把输入、输出和中间需要维护的变量列出来。",
            2: "把题目拆成“读取数据”“处理逻辑”“输出结果”三步，再检查每一步是否和题意一一对应。",
            3: "重点检查循环边界、条件判断以及变量初始化，很多错误都出在这三类位置。",
        }
        answer = f"提示 {hint_level or 1}：{hints.get(hint_level or 1, hints[1])} 结合当前资料看，相关内容可能与“{keywords[0] if keywords else '当前题目'}”有关。资料片段：{excerpt}"
        return TutorReplyPayload(
            answer=answer,
            hint_level=hint_level,
            cited_chunk_ids=[chunk.id for chunk in chunks[:1] if chunk.id is not None],
            related_knowledge_points=keywords[:3],
            follow_up_questions=["你现在最难的是读题、写循环还是验证输出？"],
            recommended_action="先手写一组最小样例，推演每一步变量变化。",
            risk_flags=[] if chunks else ["资料不足"],
        )

    if mode == TutorMode.CODE_REVIEW:
        answer = "我先从报错和代码结构帮你定位。"
        if compiler_output:
            answer += f" 目前最直接的线索是：{compiler_output[:180]}。"
        answer += " 优先检查变量是否先声明后使用、循环条件是否越界、输出格式是否与题目一致。"
        return TutorReplyPayload(
            answer=answer,
            hint_level=hint_level,
            cited_chunk_ids=[chunk.id for chunk in chunks[:1] if chunk.id is not None],
            related_knowledge_points=keywords[:3],
            follow_up_questions=["你希望我先解释报错含义，还是先检查核心逻辑？"],
            recommended_action="先根据报错定位到第一处出错行，再检查该行前后的变量状态。",
            risk_flags=[] if compiler_output else ["缺少报错信息"],
        )

    if mode == TutorMode.PRACTICE:
        title = problem.content[:40] if problem else (keywords[0] if keywords else "当前知识点")
        return TutorReplyPayload(
            answer=f"建议你先围绕“{title}”做一轮小步练习：先做概念辨析，再做一题基础实现，最后回到综合题复盘。",
            hint_level=hint_level,
            cited_chunk_ids=[chunk.id for chunk in chunks[:1] if chunk.id is not None],
            related_knowledge_points=keywords[:3],
            follow_up_questions=["你更想补基础概念，还是补代码实现？"],
            recommended_action="今天先完成 2 道小题，并记录自己最容易出错的一步。",
            risk_flags=[] if chunks else ["资料不足"],
        )

    return TutorReplyPayload(
        answer=f"我先按课程语境帮你解释。你这次问题主要围绕“{keywords[0] if keywords else question[:20]}”。建议先确认它的定义、典型用法和常见误区。资料片段：{excerpt}",
        hint_level=hint_level,
        cited_chunk_ids=[chunk.id for chunk in chunks[:1] if chunk.id is not None],
        related_knowledge_points=keywords[:3],
        follow_up_questions=["你是卡在概念理解，还是卡在把它写进代码？"],
        recommended_action="先用自己的话复述这个知识点，再找一个最小代码样例验证。",
        risk_flags=[] if chunks else ["资料不足"],
    )


async def generate_tutor_reply(
    session: AsyncSession,
    *,
    class_id: int,
    mode: TutorMode,
    question: str,
    hint_level: int | None = None,
    assignment_id: int | None = None,
    problem_id: int | None = None,
    student_answer: str | None = None,
    student_code: str | None = None,
    compiler_output: str | None = None,
    expected_output: str | None = None,
    recent_messages: list[TutorMessage] | None = None,
) -> TutorReplyPayload:
    assignment, problem = await _load_assignment_context(session, assignment_id, problem_id)
    keywords = _extract_keywords(
        question,
        assignment.title if assignment else "",
        assignment.description if assignment and assignment.description else "",
        problem.content if problem else "",
        compiler_output or "",
    )
    topic = keywords[0] if keywords else (question[:50] or "C++ 课程问题")
    chunks = await retrieve_relevant_chunks(
        session,
        class_id=class_id,
        topic=topic,
        knowledge_points=keywords[1:],
        use_class_materials=True,
        use_admin_knowledge_base=True,
        limit=5,
    )

    provider = await get_model_provider(session)
    if provider and provider.is_available:
        try:
            raw = await provider.generate_json(
                system_prompt=_build_system_prompt(mode),
                user_prompt=_build_user_prompt(
                    mode=mode,
                    question=question,
                    hint_level=hint_level,
                    assignment=assignment,
                    problem=problem,
                    recent_messages=recent_messages or [],
                    chunks=chunks,
                    student_code=student_code,
                    compiler_output=compiler_output,
                    student_answer=student_answer,
                    expected_output=expected_output,
                ),
                schema=_build_reply_schema(),
            )
            return _normalize_reply(raw, hint_level, chunks, keywords)
        except Exception:
            pass

    return _fallback_reply(
        mode=mode,
        question=question,
        hint_level=hint_level,
        chunks=chunks,
        keywords=keywords,
        compiler_output=compiler_output,
        problem=problem,
    )


async def create_tutor_session(
    session: AsyncSession,
    *,
    class_id: int,
    student_id: int,
    mode: TutorMode,
    title: str | None,
    assignment_id: int | None = None,
    problem_id: int | None = None,
) -> TutorSession:
    tutor_session = TutorSession(
        class_id=class_id,
        student_id=student_id,
        assignment_id=assignment_id,
        problem_id=problem_id,
        mode=mode,
        title=title or "AI 助学会话",
        updated_at=datetime.utcnow(),
    )
    session.add(tutor_session)
    await session.flush()
    return tutor_session


async def append_conversation(
    session: AsyncSession,
    *,
    tutor_session: TutorSession,
    content: str,
    hint_level: int | None = None,
    student_answer: str | None = None,
    student_code: str | None = None,
    compiler_output: str | None = None,
    expected_output: str | None = None,
) -> TutorReplyPayload:
    recent_result = await session.execute(
        select(TutorMessage)
        .where(TutorMessage.session_id == tutor_session.id)
        .order_by(TutorMessage.created_at.desc())
        .limit(6)
    )
    recent_messages = list(reversed(recent_result.scalars().all()))

    user_message = TutorMessage(
        session_id=tutor_session.id,
        role=TutorMessageRole.USER,
        content=content,
        hint_level=hint_level,
    )
    session.add(user_message)
    await session.flush()

    reply = await generate_tutor_reply(
        session,
        class_id=tutor_session.class_id,
        mode=tutor_session.mode,
        question=content,
        hint_level=hint_level,
        assignment_id=tutor_session.assignment_id,
        problem_id=tutor_session.problem_id,
        student_answer=student_answer,
        student_code=student_code,
        compiler_output=compiler_output,
        expected_output=expected_output,
        recent_messages=recent_messages,
    )

    assistant_message = TutorMessage(
        session_id=tutor_session.id,
        role=TutorMessageRole.ASSISTANT,
        content=reply.answer,
        hint_level=reply.hint_level,
        cited_chunk_ids=reply.cited_chunk_ids,
        related_knowledge_points=reply.related_knowledge_points,
        reply_json=reply.model_dump(),
    )
    session.add(assistant_message)

    tutor_session.latest_summary = reply.answer[:300]
    if tutor_session.title == "AI 助学会话":
        tutor_session.title = content[:40]
    tutor_session.updated_at = datetime.utcnow()
    session.add(tutor_session)
    await session.commit()
    return reply


async def get_session_detail(session: AsyncSession, tutor_session: TutorSession) -> tuple[TutorSession, list[TutorMessage]]:
    messages_result = await session.execute(
        select(TutorMessage)
        .where(TutorMessage.session_id == tutor_session.id)
        .order_by(TutorMessage.created_at)
    )
    return tutor_session, messages_result.scalars().all()


async def build_practice_recommendations(
    session: AsyncSession,
    *,
    class_id: int,
    student_id: int,
) -> list[PracticeRecommendationRead]:
    submissions_result = await session.execute(
        select(Submission)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .where(Assignment.classroom_id == class_id, Submission.student_id == student_id)
        .order_by(Submission.submitted_at.desc())
        .limit(3)
    )
    submissions = submissions_result.scalars().all()

    problems_result = await session.execute(
        select(Problem)
        .join(Assignment, Problem.assignment_id == Assignment.id)
        .where(Assignment.classroom_id == class_id)
        .order_by(Problem.id.desc())
        .limit(6)
    )
    problems = problems_result.scalars().all()

    recommendations: list[PracticeRecommendationRead] = []
    if submissions:
        latest_submission = submissions[0]
        recommendations.append(
            PracticeRecommendationRead(
                title="复盘最近一次提交",
                reason="先回看最近一次作业提交，整理自己最容易出错的 1 到 2 个步骤，再带着问题来问 AI。",
                target_knowledge_points=["调试思路", "边界检查"],
                action_type="review_submission",
                assignment_id=latest_submission.assignment_id,
            )
        )

    for problem in problems[:3]:
        topic = _extract_keywords(problem.content)
        recommendations.append(
            PracticeRecommendationRead(
                title=f"针对题目 #{problem.id} 的补练",
                reason="这类题目适合拆成输入处理、核心逻辑和输出验证三步反复练习。",
                target_knowledge_points=topic[:3] or ["C++ 基础"],
                action_type="practice_problem",
                assignment_id=problem.assignment_id,
                problem_id=problem.id,
            )
        )

    if not recommendations:
        recommendations.append(
            PracticeRecommendationRead(
                title="先做一轮基础知识回顾",
                reason="当前还没有足够的提交记录，建议先从本班最近资料中的核心概念和基础样例开始。",
                target_knowledge_points=["输入输出", "循环", "数组"],
                action_type="review_material",
            )
        )

    return recommendations[:4]
