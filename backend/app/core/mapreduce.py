import re
import math
from collections import defaultdict

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "not", "no", "nor",
    "so", "yet", "both", "either", "neither", "this", "that", "these",
    "those", "it", "its", "as", "if", "then", "than", "such", "into",
    "about", "also", "just", "more", "other", "some", "there", "their",
    "they", "what", "which", "who", "how", "when", "where", "why",
}


def tokenize(text: str) -> list[str]:
    """
    Convert raw text into a list of clean tokens.

    Steps:
    1. Lowercase the text
    2. Extract only alphabetic words using re.findall(r"[a-z]+", text)
    3. Filter out tokens that are in STOPWORDS or shorter than 3 characters
    4. Return the filtered list
    """
    text = text.lower()
    tokens = re.findall(r"[a-z]+", text)
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]


def map_phase(doc_id: str, text: str) -> list[tuple[str, str]]:
    """
    Map step: emit (word, doc_id) pairs for every token in the document.

    Steps:
    1. Call tokenize(text) to get the list of tokens
    2. Return a list of (token, doc_id) tuples — one per token
    """
    return [(token, doc_id) for token in tokenize(text)]


def reduce_phase(pairs: list[tuple[str, str]]) -> dict[str, dict[str, int]]:
    """
    Reduce step: count how many times each word appears in each document.

    Steps:
    1. Create a nested defaultdict to hold counts: { word: { doc_id: count } }
    2. Loop over each (word, doc_id) pair and increment counts[word][doc_id]
    3. Return the counts dictionary
    """
    """
        counts["learning"]["doc_A"] += 1
        # No KeyError even though neither key existed yet
        # → {"learning": {"doc_A": 1}}
    """
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for word, doc_id in pairs:
        counts[word][doc_id] += 1
    return counts


def compute_tfidf(doc_texts: dict[str, str]) -> dict[str, dict[str, float]]:
    """
    Full MapReduce pipeline + TF-IDF computation.

    Input:  { doc_id: raw_text }
    Output: { doc_id: { word: tfidf_score } }

    Steps:
    1. For each document, run map_phase() and collect:
       - all (word, doc_id) pairs into a single list
       - total token count per document into a dict { doc_id: count }
    2. Run reduce_phase() on all collected pairs → { word: { doc_id: raw_count } }
    3. For each word and its doc counts:
       a. IDF = log(total_num_docs / number_of_docs_containing_this_word)
       b. For each doc: TF = word_count / total_tokens_in_that_doc
       c. Store TF * IDF as the score in doc_tfidf[doc_id][word]
    4. Return doc_tfidf
    """
    num_docs = len(doc_texts)
    if num_docs == 0:
        return {}

    # Step 1: Map phase across all documents
    all_pairs: list[tuple[str, str]] = []
    doc_token_counts: dict[str, int] = {}

    for doc_id, text in doc_texts.items():
        pairs = map_phase(doc_id, text)
        all_pairs.extend(pairs)
        doc_token_counts[doc_id] = len(pairs)

    # Step 2: Reduce phase
    word_doc_counts = reduce_phase(all_pairs)

    # Step 3: Compute TF-IDF
    doc_tfidf: dict[str, dict[str, float]] = defaultdict(dict)

    for word, doc_counts in word_doc_counts.items():
        idf = math.log(num_docs / len(doc_counts))
        for doc_id, count in doc_counts.items():
            tf = count / doc_token_counts[doc_id]
            doc_tfidf[doc_id][word] = tf * idf

    return dict(doc_tfidf)
