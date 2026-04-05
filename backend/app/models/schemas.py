from pydantic import BaseModel
from typing import Optional


class WordContribution(BaseModel):
    word: str
    score: float


class RankedDocument(BaseModel):
    id: str
    label: str          # filename, URL, or "Text snippet"
    content_preview: str
    pagerank_score: float
    word_contributions: list[WordContribution]


class RankResponse(BaseModel):
    query: str
    results: list[RankedDocument]


# Internal model — not exposed in API responses
class IngestedDocument(BaseModel):
    id: str
    label: str
    text: str
    outbound_links: list[str] = []
