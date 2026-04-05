import { useState } from "react";
import type { RankResponse } from "./types";
import QueryForm from "./components/QueryForm";
import ResultsList from "./components/ResultsList";

export default function App() {
  const [results, setResults] = useState<RankResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [hasUrls, setHasUrls] = useState(false);

  const handleResults = (data: RankResponse, urls: boolean) => {
    setResults(data);
    setHasUrls(urls);
  };

  return (
    <div className="app">
      <header>
        <h1>Ranklab</h1>
        <p>Rank documents and links by relevance using MapReduce + PageRank</p>
      </header>

      <main>
        <QueryForm
          onResults={(data, urls) => handleResults(data, urls)}
          onLoading={setLoading}
        />

        {loading && <p className="loading">Ranking...</p>}

        {!loading && results && (
          <ResultsList data={results} hasUrls={hasUrls} />
        )}
      </main>
    </div>
  );
}
