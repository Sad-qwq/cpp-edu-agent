from collections import Counter
from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.ai_question_generation import KnowledgeChunk, KnowledgeDocument, KnowledgeParseStatus, KnowledgeSourceType


def _count_hits(text: str, keywords: Iterable[str]) -> int:
    normalized = (text or "").lower()
    counter = Counter()
    for keyword in keywords:
        term = keyword.strip().lower()
        if not term:
            continue
        counter[term] = normalized.count(term)
    return sum(counter.values())


async def retrieve_relevant_chunks(
    session: AsyncSession,
    *,
    class_id: int,
    topic: str,
    knowledge_points: list[str],
    use_class_materials: bool,
    use_admin_knowledge_base: bool,
    limit: int = 6,
) -> list[KnowledgeChunk]:
    keywords = [topic, *knowledge_points]

    source_filters = []
    if use_class_materials:
        source_filters.append(KnowledgeDocument.class_id == class_id)
    if use_admin_knowledge_base:
        source_filters.append(KnowledgeDocument.source_type == KnowledgeSourceType.ADMIN_MATERIAL)

    stmt = (
        select(KnowledgeChunk)
        .join(KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id)
        .where(KnowledgeDocument.parse_status == KnowledgeParseStatus.COMPLETED)
        .order_by(KnowledgeChunk.created_at.desc())
    )

    if source_filters:
        stmt = stmt.where(*source_filters)
    else:
        stmt = stmt.where(KnowledgeDocument.class_id == class_id)

    result = await session.execute(stmt.limit(200))
    chunks = result.scalars().all()
    ranked = sorted(
        chunks,
        key=lambda chunk: (
            _count_hits(chunk.content, keywords),
            _count_hits((chunk.metadata_json or {}).get("document_name", ""), keywords),
            -chunk.chunk_index,
        ),
        reverse=True,
    )
    matched = [chunk for chunk in ranked if _count_hits(chunk.content, keywords) > 0]
    return (matched or ranked)[:limit]