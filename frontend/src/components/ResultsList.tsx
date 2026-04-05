import { useState } from "react";
import type { RankedDocument, RankResponse } from "../types";

interface Props {
  data: RankResponse;
  hasUrls: boolean;
}

function ResultItem({ doc }: { doc: RankedDocument }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="result-item">
      <div className="result-main">
        <div className="result-label">
          {doc.label.startsWith("http") ? (
            <a href={doc.label} target="_blank" rel="noreferrer">{doc.label}</a>
          ) : (
            <span>{doc.label}</span>
          )}
        </div>

        <div className="score-box" onClick={() => setExpanded(!expanded)}>
          <span className="score-value">{doc.pagerank_score.toFixed(4)}</span>
          <span className="score-toggle">{expanded ? "▲" : "▼"}</span>
        </div>
      </div>

      <p className="result-preview">{doc.content_preview}</p>

      {expanded && (
        <div className="word-contributions">
          <h4>Word contributions</h4>
          {doc.word_contributions.length === 0 ? (
            <p className="no-contributions">No query words found in this document.</p>
          ) : (
            <ul>
              {doc.word_contributions.map(({ word, score }) => (
                <li key={word}>
                  <span className="contrib-word">{word}</span>
                  <span className="contrib-score">{score.toFixed(4)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default function ResultsList({ data, hasUrls }: Props) {
  return (
    <div className="results-list">
      {!hasUrls && (
        <p className="info-note">
          No URLs submitted — ranking is based on TF-IDF only. Add URLs to enable link-based ranking.
        </p>
      )}
      {data.results.map((doc) => (
        <ResultItem key={doc.id} doc={doc} />
      ))}
    </div>
  );
}
