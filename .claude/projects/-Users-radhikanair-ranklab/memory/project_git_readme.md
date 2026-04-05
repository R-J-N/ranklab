---
name: Ranklab git + README reminder
description: User wants to push to git with a README at the end, including explanation of hybrid PageRank approach
type: project
---

At the end of the project, the user wants to:
1. Push the full project to their git repository
2. Include a README

**Why:** They don't want to forget this task.

**How to apply:** When the project is complete (all steps done, frontend working), remind the user and offer to write the README + handle the git push. The README should include an explanation of why we use a hybrid PageRank (TF-IDF + link graph) instead of classic PageRank — because the submitted document set is small and most links point outside it, so pure link-graph authority is insufficient without query-relevance seeding.
