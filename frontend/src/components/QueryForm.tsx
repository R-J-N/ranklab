import { useState } from "react";
import type { RankResponse } from "../types";

interface Props {
  onResults: (data: RankResponse, hasUrls: boolean) => void;
  onLoading: (loading: boolean) => void;
}

export default function QueryForm({ onResults, onLoading }: Props) {
  const [query, setQuery] = useState("");
  const [urls, setUrls] = useState("");
  const [rawText, setRawText] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);

  const handleSubmit = async (e: React.SyntheticEvent) => {
    e.preventDefault();
    onLoading(true);

    const formData = new FormData();
    formData.append("query", query);
    formData.append("urls", urls.split("\n").filter(Boolean).join(","));
    formData.append("raw_text", rawText);
    if (files) {
      for (const file of Array.from(files)) {
        formData.append("files", file);
      }
    }

    try {
      const response = await fetch("http://localhost:8000/api/rank", {
        method: "POST",
        body: formData,
      });
      const data: RankResponse = await response.json();
      onResults(data, urls.trim().length > 0);
    } catch (err) {
      console.error("Request failed:", err);
    } finally {
      onLoading(false);
    }
  };

  return (
    <form className="query-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label>Query</label>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. machine learning"
          required
        />
      </div>

      <div className="form-group">
        <label>URLs <span className="hint">(one per line — enables link-based ranking)</span></label>
        <textarea
          value={urls}
          onChange={(e) => setUrls(e.target.value)}
          placeholder="https://example.com&#10;https://another.com"
          rows={4}
        />
      </div>

      <div className="form-group">
        <label>Paste text</label>
        <textarea
          value={rawText}
          onChange={(e) => setRawText(e.target.value)}
          placeholder="Paste any text here..."
          rows={4}
        />
      </div>

      <div className="form-group">
        <label>Upload files <span className="hint">(.txt or .pdf)</span></label>
        <input
          type="file"
          accept=".txt,.pdf"
          multiple
          onChange={(e) => setFiles(e.target.files)}
        />
      </div>

      <button type="submit" disabled={!query.trim()}>
        Rank
      </button>
    </form>
  );
}
