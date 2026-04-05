---
name: Ranklab UI note - link-based ranking
description: Show a note in the UI when no URLs are submitted, explaining that link-based ranking is disabled
type: project
---

In the frontend, show a small informational note to the user explaining that:
- If only text/files are submitted → ranking is pure TF-IDF (no link graph)
- If URLs are submitted → full PageRank with link relationships is enabled
- Suggested note: "Add URLs to enable link-based ranking"

**Why:** Without URLs, all documents are dangling nodes and the link matrix is uniform — PageRank has no structure to work with and degrades to TF-IDF only.

**How to apply:** When building the results UI in Step 6, add a subtle info banner or tooltip near the results that appears when no URLs were submitted in the query.
