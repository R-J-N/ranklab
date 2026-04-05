import uuid
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from app.models.schemas import RankResponse, RankedDocument, WordContribution, IngestedDocument
from app.core.ingestion import fetch_url, read_file
from app.core.mapreduce import compute_tfidf, tokenize
from app.core.pagerank import build_link_matrix, compute_pagerank, get_word_contributions

router = APIRouter()


@router.post("/rank", response_model=RankResponse)
async def rank_documents(
    query: str = Form(...),
    urls: Optional[str] = Form(None),       # comma-separated URLs
    raw_text: Optional[str] = Form(None),   # pasted text
    files: Optional[list[UploadFile]] = File(default=None),
):
    # --- Step 1a: Ingest URLs ---
    docs: list[IngestedDocument] = []

    if urls:
        for url in [u.strip() for u in urls.split(",") if u.strip()]:
            text, links = await fetch_url(url)
            docs.append(IngestedDocument(
                id=url,
                label=url,
                text=text,
                outbound_links=links,
            ))

    # --- Step 1b: Ingest uploaded files ---
    for file in (files or []):
        content = await file.read()
        text = await read_file(content, file.filename or "upload")
        docs.append(IngestedDocument(
            id=str(uuid.uuid4()),
            label=file.filename or "Uploaded file",
            text=text,
        ))

    # --- Step 1c: Ingest pasted raw text ---
    if raw_text and raw_text.strip():
        docs.append(IngestedDocument(
            id=str(uuid.uuid4()),
            label="Pasted text",
            text=raw_text.strip(),
        ))

    if not docs:
        return RankResponse(query=query, results=[])

    # --- Step 2: TF-IDF via MapReduce ---
    doc_texts = {doc.id: doc.text for doc in docs}
    tfidf_scores = compute_tfidf(doc_texts)

    # --- Step 3: Compute seed scores from query ---
    query_tokens = tokenize(query)
    seed_scores = {
        doc.id: sum(tfidf_scores.get(doc.id, {}).get(word, 0.0) for word in query_tokens)
        for doc in docs
    }

    # --- Step 4: Build link matrix and run PageRank ---
    doc_ids = [doc.id for doc in docs]
    outbound_links = {doc.id: doc.outbound_links for doc in docs}
    link_matrix = build_link_matrix(doc_ids, outbound_links)
    pagerank_scores = compute_pagerank(doc_ids, link_matrix, seed_scores)

    # --- Step 5: Build response ---
    results = []
    for doc in docs:
        contributions = get_word_contributions(doc.id, query_tokens, tfidf_scores)
        results.append(RankedDocument(
            id=doc.id,
            label=doc.label,
            content_preview=doc.text[:200],
            pagerank_score=pagerank_scores[doc.id],
            word_contributions=[
                WordContribution(word=w, score=s) for w, s in contributions
            ],
        ))

    results.sort(key=lambda r: r.pagerank_score, reverse=True)
    return RankResponse(query=query, results=results)
