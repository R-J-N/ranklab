import numpy as np
import pytest
from app.core.pagerank import build_link_matrix, compute_pagerank, get_word_contributions


def test_build_link_matrix_basic():
    """A links to B and B links to A — authority flows between them."""
    doc_ids = ["doc_A", "doc_B"]
    outbound_links = {"doc_A": ["doc_B"], "doc_B": ["doc_A"]}
    matrix = build_link_matrix(doc_ids, outbound_links)
    expected = np.array([[0.0, 1.0], [1.0, 0.0]])
    np.testing.assert_array_almost_equal(matrix, expected)


def test_build_link_matrix_dangling():
    """Docs with no outbound links spread authority equally to all docs."""
    doc_ids = ["doc_A", "doc_B"]
    outbound_links = {}
    matrix = build_link_matrix(doc_ids, outbound_links)
    expected = np.array([[0.5, 0.5], [0.5, 0.5]])
    np.testing.assert_array_almost_equal(matrix, expected)


def test_build_link_matrix_external_links_ignored():
    """Links to URLs outside the submitted set are treated as dangling."""
    doc_ids = ["doc_A", "doc_B"]
    outbound_links = {"doc_A": ["https://external.com"]}
    matrix = build_link_matrix(doc_ids, outbound_links)
    # doc_A has no internal links → dangling → column is 1/N
    np.testing.assert_array_almost_equal(matrix[:, 0], [0.5, 0.5])


def test_build_link_matrix_columns_sum_to_one():
    """Every column must sum to 1.0 regardless of link structure."""
    doc_ids = ["doc_A", "doc_B", "doc_C"]
    outbound_links = {"doc_A": ["doc_B", "doc_C"], "doc_B": ["doc_A"]}
    matrix = build_link_matrix(doc_ids, outbound_links)
    for j in range(len(doc_ids)):
        assert abs(matrix[:, j].sum() - 1.0) < 1e-9


def test_build_link_matrix_split_links():
    """A doc linking to two others splits its authority equally."""
    doc_ids = ["doc_A", "doc_B", "doc_C"]
    outbound_links = {"doc_A": ["doc_B", "doc_C"]}
    matrix = build_link_matrix(doc_ids, outbound_links)
    # Column 0 (doc_A): 0 to itself, 0.5 to B, 0.5 to C
    np.testing.assert_array_almost_equal(matrix[:, 0], [0.0, 0.5, 0.5])


def test_compute_pagerank_higher_seed_wins():
    """With no link structure, the doc with higher TF-IDF seed ranks higher."""
    doc_ids = ["doc_A", "doc_B"]
    link_matrix = build_link_matrix(doc_ids, {})  # both dangling
    seed_scores = {"doc_A": 0.8, "doc_B": 0.2}
    result = compute_pagerank(doc_ids, link_matrix, seed_scores)
    assert result["doc_A"] > result["doc_B"]


def test_compute_pagerank_link_boosts_score():
    """A low-seed doc linked to by a high-seed doc scores higher than an unlinked doc."""
    doc_ids = ["doc_A", "doc_B", "doc_C"]
    # doc_A (high seed) links to doc_B (low seed), doc_C is isolated
    outbound_links = {"doc_A": ["doc_B"]}
    link_matrix = build_link_matrix(doc_ids, outbound_links)
    seed_scores = {"doc_A": 0.9, "doc_B": 0.05, "doc_C": 0.05}
    result = compute_pagerank(doc_ids, link_matrix, seed_scores)
    assert result["doc_B"] > result["doc_C"]


def test_compute_pagerank_scores_sum_to_one():
    """All PageRank scores should sum to approximately 1.0."""
    doc_ids = ["doc_A", "doc_B", "doc_C"]
    link_matrix = build_link_matrix(doc_ids, {"doc_A": ["doc_B"], "doc_B": ["doc_C"]})
    seed_scores = {"doc_A": 0.6, "doc_B": 0.3, "doc_C": 0.1}
    result = compute_pagerank(doc_ids, link_matrix, seed_scores)
    assert abs(sum(result.values()) - 1.0) < 1e-6


def test_compute_pagerank_all_zero_seeds():
    """When all seeds are 0, scores should be equal (uniform fallback)."""
    doc_ids = ["doc_A", "doc_B"]
    link_matrix = build_link_matrix(doc_ids, {})
    seed_scores = {"doc_A": 0.0, "doc_B": 0.0}
    result = compute_pagerank(doc_ids, link_matrix, seed_scores)
    assert abs(result["doc_A"] - result["doc_B"]) < 1e-6


def test_get_word_contributions_basic():
    """Query words are returned sorted by TF-IDF score descending."""
    tfidf_scores = {"doc_A": {"machine": 0.4, "learning": 0.0}}
    result = get_word_contributions("doc_A", ["machine", "learning"], tfidf_scores)
    assert result == [("machine", 0.4), ("learning", 0.0)]


def test_get_word_contributions_missing_word():
    """Query words not in the document still appear with score 0.0."""
    tfidf_scores = {"doc_A": {"machine": 0.4}}
    result = get_word_contributions("doc_A", ["machine", "learning"], tfidf_scores)
    assert ("learning", 0.0) in result


def test_get_word_contributions_unknown_doc():
    """Unknown doc_id returns all query words with score 0.0."""
    tfidf_scores = {}
    result = get_word_contributions("doc_X", ["machine", "learning"], tfidf_scores)
    assert result == [("machine", 0.0), ("learning", 0.0)]
