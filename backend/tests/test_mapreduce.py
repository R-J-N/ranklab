import pytest
from app.core.mapreduce import tokenize, map_phase, reduce_phase, compute_tfidf


def test_tokenize_basic():
    """Lowercases, removes stopwords and short words."""
    result = tokenize("The quick brown fox is a great jumper")
    assert result == ["quick", "brown", "fox", "great", "jumper"]


def test_tokenize_punctuation():
    """Punctuation is stripped, only alphabetic characters survive."""
    result = tokenize("hello, world!")
    assert result == ["hello", "world"]


def test_tokenize_numbers():
    """Numeric characters are stripped, only alphabetic parts survive."""
    result = tokenize("test123 abc")
    assert result == ["test", "abc"]


def test_tokenize_empty():
    """Empty string returns empty list."""
    result = tokenize("")
    assert result == []


def test_map_phase_basic():
    """Each token is paired with the correct doc_id."""
    result = map_phase("doc_A", "machine learning is great")
    assert result == [("machine", "doc_A"), ("learning", "doc_A"), ("great", "doc_A")]


def test_map_phase_empty():
    """Empty text produces no pairs."""
    result = map_phase("doc_A", "")
    assert result == []


def test_map_phase_all_stopwords():
    """All stopword tokens produces no pairs."""
    result = map_phase("doc_A", "the is a and")
    assert result == []


def test_reduce_phase_basic():
    """Counts are correctly aggregated per word per document."""
    pairs = [("learning", "doc_A"), ("learning", "doc_B"), ("machine", "doc_A")]
    result = reduce_phase(pairs)
    assert result["learning"]["doc_A"] == 1
    assert result["learning"]["doc_B"] == 1
    assert result["machine"]["doc_A"] == 1


def test_reduce_phase_duplicate_words():
    """Same word appearing multiple times in a document is counted correctly."""
    pairs = [("learning", "doc_A"), ("learning", "doc_A")]
    result = reduce_phase(pairs)
    assert result["learning"]["doc_A"] == 2


def test_reduce_phase_empty():
    """Empty pairs produce empty dict."""
    result = reduce_phase([])
    assert result == {}


def test_compute_tfidf_basic():
    """Distinctive words score higher than common words across all docs."""
    docs = {"doc_A": "machine learning", "doc_B": "deep learning"}
    result = compute_tfidf(docs)
    # "learning" appears in both docs → IDF = log(1) = 0.0
    assert result["doc_A"]["learning"] == 0.0
    assert result["doc_B"]["learning"] == 0.0
    # "machine" appears in only doc_A → score > 0
    assert result["doc_A"]["machine"] > 0.0


def test_compute_tfidf_empty():
    """Empty input returns empty dict."""
    result = compute_tfidf({})
    assert result == {}


def test_compute_tfidf_single_doc():
    """With only one document, all TF-IDF scores are 0.0."""
    result = compute_tfidf({"doc_A": "machine learning"})
    assert result["doc_A"]["machine"] == 0.0
    assert result["doc_A"]["learning"] == 0.0
