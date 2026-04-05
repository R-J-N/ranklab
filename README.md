# Ranklab

Rank documents and web pages by relevance to a query using **MapReduce** + **PageRank**.

## Features

- Submit URLs, paste raw text, or upload `.txt` / `.pdf` files
- MapReduce pipeline computes TF-IDF scores across all documents
- PageRank algorithm ranks documents using both query relevance and link relationships
- Expandable score boxes show word-by-word contribution to each document's score

## How It Works

### 1. Ingestion

Each input is converted to plain text:
- **URLs** — fetched with `httpx`, parsed with `BeautifulSoup`. Outbound links are extracted to build the link graph.
- **Files** — `.txt` decoded directly, `.pdf` extracted with `pypdf`
- **Pasted text** — used as-is

### 2. MapReduce → TF-IDF

Documents are processed through a MapReduce pipeline:

- **Map phase:** tokenize each document → emit `(word, doc_id)` pairs
- **Reduce phase:** count occurrences per word per document
- **TF-IDF:** compute how distinctive each word is to each document

```
TF  = word_count / total_words_in_doc
IDF = log(total_docs / docs_containing_word)
TF-IDF = TF × IDF
```

IDF measures how *rare* a word is across the document set — a word that appears in every document gets a low IDF (it tells us nothing distinctive), while a word unique to one document gets a high IDF. Words that appear in every document score `0.0` — they carry no discriminating power.

### 3. PageRank (Query-Biased)

Classic PageRank ranks pages purely by link structure — pages with many inbound links from authoritative pages rank highest. However, Ranklab uses a **hybrid approach** for two reasons:

1. The submitted document set is small (typically 2–10 pages)
2. Most outbound links point *outside* the submitted set — the internal link graph is sparse

Pure link-graph authority is therefore insufficient. Instead, Ranklab seeds each document's initial PageRank score with its **TF-IDF query relevance**, then lets the link graph redistribute authority.

**Each iteration:**
```
new_score = 0.85 × (authority flowing in from linking docs)
          + 0.15 × (TF-IDF relevance to query)
```

The 0.85/0.15 damping split was chosen by Larry Page and Sergey Brin in the original PageRank paper (1998) and has become the industry standard. The 15% "teleportation" probability models a user who, instead of following a link, randomly jumps to another page — in Ranklab this jump is biased toward query-relevant documents rather than a random page.

- The TF-IDF score is fixed — computed once and used as the 15% "pull back" force every iteration
- The link score changes every iteration because it depends on the current scores of documents linking into this one
- Scores keep updating until the change drops below a tolerance threshold — this is **convergence**

In one sentence: *each document's score is continuously recalculated based on the current scores of its neighbours, until nobody's score is changing meaningfully anymore.*

### 4. Word Contributions

Each result shows a breakdown of which query words drove its score, sorted by TF-IDF contribution (highest first). Click the score box to expand.

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python, FastAPI |
| Algorithms | NumPy (PageRank matrix math) |
| Scraping | httpx, BeautifulSoup |
| Frontend | React, TypeScript, Vite |

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

## Running Tests

```bash
cd backend
pytest tests/ -v
```
