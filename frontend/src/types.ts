export interface WordContribution {
  word: string;
  score: number;
}

export interface RankedDocument {
  id: string;
  label: string;
  content_preview: string;
  pagerank_score: number;
  word_contributions: WordContribution[];
}

export interface RankResponse {
  query: string;
  results: RankedDocument[];
}
