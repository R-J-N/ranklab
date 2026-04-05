---
name: Ranklab README content - PageRank explanation
description: Key explanation to include in the README about how the PageRank iteration works
type: project
---

Include this explanation in the README under a "How It Works" section:

**PageRank iteration:**
- TF-IDF score is fixed — computed once before iterations start. It seeds the initial rank vector and acts as the 15% "pull back" force every iteration.
- Link score changes every iteration because it depends on the current scores of documents linking INTO you.
- Each iteration for a document: new score = 85% × (sum of scores of docs that link to it) + 15% × (TF-IDF relevance)
- Since neighbouring scores change each iteration, all scores keep updating until changes become smaller than the tolerance threshold — this is convergence.
- In one sentence: each document's score is continuously recalculated based on the current scores of its neighbours, until nobody's score is changing meaningfully anymore.

Also explain why hybrid PageRank (TF-IDF + link graph) is used instead of classic PageRank — because the submitted document set is small and most links point outside it, so pure link-graph authority is insufficient without query-relevance seeding.
