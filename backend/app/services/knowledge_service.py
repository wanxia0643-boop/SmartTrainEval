"""Document chunking and lightweight BM25 retrieval."""
import re
from pathlib import Path

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeChunk, KnowledgeDocument


def chunk_text(text: str, size: int = 1200, overlap: int = 150) -> list[str]:
    clean = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not clean:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(clean):
        end = min(len(clean), start + size)
        if end < len(clean):
            boundary = max(clean.rfind("\n", start, end), clean.rfind("。", start, end))
            if boundary > start + size // 2:
                end = boundary + 1
        chunks.append(clean[start:end].strip())
        if end >= len(clean):
            break
        start = max(start + 1, end - overlap)
    return [item for item in chunks if item]


def _tokens(text: str) -> list[str]:
    try:
        import jieba
        return [t.lower() for t in jieba.lcut(text) if len(t.strip()) > 1]
    except ImportError:
        return re.findall(r"[\w\u4e00-\u9fff]{2,}", text.lower())


def retrieve(
    db: Session, *, course_id: int, project_id: int | None, query: str, limit: int = 4
) -> list[dict]:
    stmt = (
        select(KnowledgeChunk, KnowledgeDocument)
        .join(KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id)
        .where(
            KnowledgeChunk.is_deleted == 0,
            KnowledgeDocument.is_deleted == 0,
            KnowledgeDocument.status == 1,
            KnowledgeDocument.course_id == course_id,
        )
    )
    if project_id is not None:
        stmt = stmt.where(or_(
            KnowledgeDocument.project_id.is_(None),
            KnowledgeDocument.project_id == project_id,
        ))
    rows = db.execute(stmt).all()
    if not rows:
        return []
    corpus = [_tokens(chunk.content) for chunk, _ in rows]
    query_tokens = _tokens(query)
    try:
        from rank_bm25 import BM25Okapi
        scores = BM25Okapi(corpus).get_scores(query_tokens)
    except ImportError:
        query_set = set(query_tokens)
        scores = [sum(1 for token in tokens if token in query_set) for tokens in corpus]
    ranked = sorted(zip(rows, scores), key=lambda item: item[1], reverse=True)
    result = []
    for ((chunk, document), score) in ranked[:limit]:
        if score <= 0 and query_tokens:
            continue
        result.append({
            "document_id": document.id,
            "title": document.title,
            "chunk_id": chunk.id,
            "source_label": chunk.source_label,
            "excerpt": chunk.content[:360],
            "content": chunk.content,
        })
    return result

