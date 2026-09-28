import time                             # for perf_counter timing measurements
from functools import lru_cache         # for memoizing tokenize results
from src.indexer import tokenize        # reuse existing tokenizer, don't duplicate logic
import sys                              # for sizeof estimation of index structure


@lru_cache(maxsize=1024)
def cached_tokenize(text):
    """Memoized tokenize. Same input string -> cached result."""
    return tokenize(text)               # delegate to real tokenizer, cache by text arg


def get_stats(documents, index):
    """Return dict with corpus stats."""
    total_docs = len(documents)         # count of documents in corpus
    if total_docs == 0:                 # guard against empty corpus
        return {                        # all stats are zero when no docs
            "total_docs": 0,
            "total_tokens": 0,
            "unique_words": 0,
            "avg_tokens_per_doc": 0.0,
            "index_size_bytes": 0,
        }
    total_tokens = 0                    # running sum of tokens across docs
    for doc in documents:               # iterate each document dict
        content = doc.get("content", "")  # safely fetch content field
        total_tokens += len(tokenize(content))  # count tokens for this doc
    unique_words = len(index)           # index keys are the unique vocabulary
    avg_tokens = total_tokens / total_docs  # mean tokens per document
    index_size_bytes = sys.getsizeof(index)  # shallow size estimate of index dict
    for word, doc_ids in index.items(): # add size of nested keys/values too
        index_size_bytes += sys.getsizeof(word)      # size of each word string
        index_size_bytes += sys.getsizeof(doc_ids)   # size of each posting list/set
    return {                            # assemble final stats dict
        "total_docs": total_docs,
        "total_tokens": total_tokens,
        "unique_words": unique_words,
        "avg_tokens_per_doc": round(avg_tokens, 4),  # rounded per spec
        "index_size_bytes": index_size_bytes,
    }


def measure_search_time(query, index, iterations=100):
    """Run search() N times, return average milliseconds."""
    from src.searcher import search     # ✅ FIX 1: search lives in src.searcher
    start = time.perf_counter()         # mark start of timing window
    for _ in range(iterations):         # repeat call to average out noise
        search(query, index)            # exercise the search function
    elapsed = time.perf_counter() - start  # total elapsed seconds for all runs
    avg_ms = (elapsed / iterations) * 1000  # convert to average milliseconds
    return round(avg_ms, 4)             # rounded per spec


def measure_rank_time(doc_ids, query, documents, iterations=100):
    """Run rank() N times, return average milliseconds."""
    from src.ranker import rank         # ✅ FIX 2: rank lives in src.ranker
    start = time.perf_counter()         # mark start of timing window
    for _ in range(iterations):         # repeat call to average out noise
        rank(doc_ids, query, documents)  # exercise the rank function
    elapsed = time.perf_counter() - start  # total elapsed seconds for all runs
    avg_ms = (elapsed / iterations) * 1000  # convert to average milliseconds
    return round(avg_ms, 4)             # rounded per spec


def comparison_report(documents, index):
    """Return dict comparing naive vs cached tokenization timing."""
    cached_tokenize.cache_clear()       # reset cache for a fair first-pass comparison
    if not documents:                   # guard against empty corpus
        return {                        # zeroed report when nothing to measure
            "naive_ms": 0.0,
            "cached_ms": 0.0,
            "speedup": 0.0,
        }
    texts = [doc.get("content", "") for doc in documents]  # pull content once for reuse

    start = time.perf_counter()         # begin naive timing window
    for text in texts:                  # naive path re-tokenizes every call
        tokenize(text)                  # no caching, always recomputes
    naive_elapsed = time.perf_counter() - start  # total naive elapsed seconds

    # ✅ FIX 3: warm cache OUTSIDE timer to avoid inflating cached_ms
    for text in texts:                  # warm-up pass (not measured)
        cached_tokenize(text)           # populates the lru_cache

    start = time.perf_counter()         # timer starts AFTER warm-up
    for text in texts:                  # measured pass — all cache hits
        cached_tokenize(text)           # should be much faster than naive
    cached_elapsed = time.perf_counter() - start  # total cached elapsed seconds

    naive_ms = naive_elapsed * 1000     # convert naive time to milliseconds
    cached_ms = cached_elapsed * 1000   # convert cached time to milliseconds
    speedup = (naive_ms / cached_ms) if cached_ms > 0 else 0.0  # ratio, guard div by zero
    return {                            # assemble comparison result
        "naive_ms": round(naive_ms, 4),
        "cached_ms": round(cached_ms, 4),
        "speedup": round(speedup, 4),
    }