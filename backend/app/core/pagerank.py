import numpy as np


def build_link_matrix(doc_ids: list[str], outbound_links: dict[str, list[str]]) -> np.ndarray:
    """
    Build a column-stochastic adjacency matrix from the link graph.

    Input:
      - doc_ids: ordered list of document IDs e.g. ["doc_A", "doc_B", "doc_C"]
      - outbound_links: { doc_id: [list of URLs that doc links to] }
        Note: only links pointing to other docs in doc_ids count

    Output:
      - An (N x N) numpy matrix where matrix[i][j] = probability of
        moving from doc_j to doc_i (column = source, row = destination)

    Steps:
    1. Create an N x N matrix of zeros (N = number of docs)
    2. For each source doc (column j):
       a. Find which other docs in doc_ids it links to (by matching URLs)
       b. If it has outbound links to known docs: set matrix[i][j] = 1
          for each destination doc i, then normalize the column by dividing
          by the number of such links (so column sums to 1)
       c. If it has NO outbound links to known docs (dangling node):
          set the entire column to 1/N (spreads authority equally)
    3. Return the matrix
    """
    n = len(doc_ids)
    index = {doc_id: i for i, doc_id in enumerate(doc_ids)}
    matrix = np.zeros((n, n))

    for j, doc_id in enumerate(doc_ids):
        # Find which other docs in our set this doc links to
        targets = [
            index[url] for url in outbound_links.get(doc_id, [])
            if url in index
        ]
        if targets:
            for i in targets:
                matrix[i][j] = 1.0
            matrix[:, j] /= len(targets)  # normalize column to sum to 1
        else:
            matrix[:, j] = 1.0 / n  # dangling node: spread equally

    return matrix


def compute_pagerank(
    doc_ids: list[str],
    link_matrix: np.ndarray,
    seed_scores: dict[str, float],
    damping: float = 0.85,
    max_iterations: int = 100,
    tolerance: float = 1e-6,
) -> dict[str, float]:
    """
    Run the iterative PageRank algorithm with query-biased seed scores.

    Input:
      - doc_ids: ordered list of document IDs
      - link_matrix: column-stochastic matrix from build_link_matrix()
      - seed_scores: { doc_id: tfidf_relevance_score } — query relevance per doc
      - damping: probability of following a link (default 0.85)
      - max_iterations: stop after this many iterations
      - tolerance: stop early if scores change less than this

    Output:
      - { doc_id: pagerank_score }

    Steps:
    1. Normalize seed_scores into a probability vector (sums to 1)
       — if all seeds are 0, use uniform 1/N
    2. Initialise the rank vector r using the seed scores
    3. Iterate:
       a. new_r = damping * (link_matrix @ r) + (1 - damping) * seed_vector
       b. If the difference between new_r and r is below tolerance, stop early
       c. Otherwise set r = new_r
    4. Return { doc_id: score } mapping
    """
    n = len(doc_ids)

    # Step 1: Normalize seed scores into a probability vector
    seed_vector = np.array([seed_scores.get(doc_id, 0.0) for doc_id in doc_ids])
    total = seed_vector.sum()
    if total == 0:
        seed_vector = np.ones(n) / n  # uniform if all seeds are 0
    else:
        seed_vector = seed_vector / total

    # Step 2: Initialise rank vector from seed scores
    r = seed_vector.copy()

    # Step 3: Iterate until convergence
    # Each iteration: doc score = 85% * (authority from linking docs) + 15% * (TF-IDF relevance)
    # Neighbours' scores change each iteration, so all scores keep updating
    # until the total change drops below tolerance → convergence
    for _ in range(max_iterations):
        new_r = damping * (link_matrix @ r) + (1 - damping) * seed_vector
        if np.linalg.norm(new_r - r) < tolerance:
            break
        r = new_r

    # Step 4: Return { doc_id: score } mapping
    return {doc_id: float(r[i]) for i, doc_id in enumerate(doc_ids)}


def get_word_contributions(
    doc_id: str,
    query_tokens: list[str],
    tfidf_scores: dict[str, dict[str, float]],
) -> list[tuple[str, float]]:
    """
    Return per-word TF-IDF contributions for a document, sorted descending.

    Input:
      - doc_id: the document to explain
      - query_tokens: tokenized query words
      - tfidf_scores: full TF-IDF matrix from compute_tfidf()

    Output:
      - list of (word, score) tuples, sorted by score descending,
        only including words that appear in both the query and the document

    Steps:
    1. Get the tfidf scores for this doc_id
    2. For each token in query_tokens, look up its score in the doc (default 0.0)
    3. Sort by score descending
    4. Return the list
    """
    doc_scores = tfidf_scores.get(doc_id, {})
    contributions = [(word, doc_scores.get(word, 0.0)) for word in query_tokens]
    return sorted(contributions, key=lambda x: x[1], reverse=True)
