# PySearch

**A tiny search engine built from scratch.**

**Reference:** *Grokking Algorithms* by Aditya Bhargava

I read `.txt` files from a folder, build an **inverted index**, and answer multi-word queries with **TF-IDF** ranked results. I use only Python's standard library, except for my web UI, which uses **Streamlit**.

**Status:** 8 build phases (0-7, see Phase Reference below) complete. 65 tests passing.
**Repo:** https://github.com/almostpm/Pysearch
**Direct link:** [https://github.com/almostpm/Pysearch](https://pysearch-9jymfbaydqnfenisuahvqe.streamlit.app/)

---

## Why PySearch Exists

Most search tutorials hand you a library and hide the mechanics. I exist so you can read every line of a working search engine and see how an inverted index, a ranking formula, a trie, and a graph search each earn their place. I am small enough to read in an afternoon and complete enough to run.

---

## What PySearch Does

| Capability | How I do it |
|------------|-------------|
| Read documents | I load every `.txt` file from a folder |
| Tokenize | Lowercase, strip punctuation, keep internal hyphens |
| Index | I build an inverted index: `{word: [doc_ids]}` |
| Search | AND / OR logic on multi-word queries |
| Rank | TF-IDF relevance scoring |
| Autocomplete | Prefix suggestions from a trie |
| Related words | BFS on a co-occurrence graph |
| Optimize | Caching and corpus statistics |
| Persist | I save and load the index as JSON |
| Web UI | A Streamlit app in `app.py` |

---

## Requirements

| Dependency | Version | When needed |
|------------|---------|-------------|
| Python | 3.10+ | Always |
| streamlit | >=1.30.0 | Web UI only |
| notebook | >=7.0.0 | Running tests only |

---

## Quick Start

```bash
git clone https://github.com/almostpm/Pysearch.git
cd Pysearch
pip install -r requirements.txt
python -c "from src.documents import load_documents; from src.indexer import build_index; d=load_documents('docs'); i=build_index(d); print(len(d), 'docs,', len(i), 'unique words')"
```

Expected output:

```
3 docs, 60 unique words
```

For the full walkthrough, see Install and Run the Web App below.

---

## Install

```bash
git clone https://github.com/almostpm/Pysearch.git
cd Pysearch
pip install -r requirements.txt
```

`requirements.txt` contains `streamlit>=1.30.0` and nothing else. To run my tests, also install:

```bash
pip install "notebook>=7.0.0"
```

---

## Run the Web App

```bash
python -m streamlit run app.py
```

Open **http://localhost:8501**, the Streamlit default. If that port is taken, Streamlit prints the URL it chose.

I do not read a folder in the web app. You drag `.txt` files into Streamlit's file uploader, click **Build Index**, and I index them in memory. You see four tabs:

| Tab | What you do |
|-----|-------------|
| Upload & Index | Upload `.txt` files and build the index |
| Search | Enter a query, pick AND or OR, toggle TF-IDF ranking, cap the result count |
| Autocomplete | Enter a prefix and get word suggestions |
| Stats | See corpus statistics, the top 10 most common words, and a related-words lookup |

The web app does not write `output/index.json`.

---

## Real Output Example

Run this from the project root so `src` imports resolve. It uses the three sample files in `docs/`.

```python
from collections import Counter
from src.documents import load_documents
from src.indexer import build_index
from src.searcher import search
from src.ranker import rank
from src.related import build_graph, bfs, related
from src.optimizer import comparison_report

docs = load_documents("docs")
index = build_index(docs)
names = {d["id"]: d["name"] for d in docs}

query = "python hash"
matches = search(query, index, mode="AND")
print("matches:", matches)

ranked = rank(matches, query, docs)
print("ranked:", ranked)
for doc_id, score in ranked:
    print(f"doc {doc_id} ({names[doc_id]}): {score:.4f}")

print("OR:", rank(search(query, index, mode="OR"), query, docs))

graph = build_graph(docs)
print("bfs distance counts:", sorted(Counter(bfs(graph, "python").values()).items()))
print("related:", related("python", graph, max_results=5))
print("comparison_report:", comparison_report(docs, index))
```

Output:

```
matches: [2]
ranked: [(2, 0.09639591427571792)]
doc 2 (doc3.txt): 0.0964
OR: [(2, 0.09639591427571792), (0, 0.03118962370062803)]
bfs distance counts: [(0, 1), (1, 22), (2, 36)]
related: ['a', 'and', 'are', 'data', 'dictionaries']
comparison_report: {'naive_ms': 0.0441, 'cached_ms': 0.0005, 'speedup': 83.0151}
```

AND returns only doc 2. OR adds doc 0 with a lower score. `related` returns `a` and `and` first because I do no stop-word filtering. The `comparison_report` timings vary per machine.

| Function | Returns |
|----------|---------|
| `search(query, index, mode)` | `list[int]`: sorted doc IDs |
| `rank(doc_ids, query, documents)` | `list[tuple[int, float]]`: `(doc_id, score)`, best first |

---

## Architecture

```
INPUT -> INDEX -> SEARCH -> RANK -> AUTOCOMPLETE -> OPTIMIZE -> RELATED -> PERSIST
```

This chain shows my pipeline order. It is not a strict dependency graph. The table shows what each layer imports or needs.

| Layer | File | Depends On |
|-------|------|------------|
| INPUT | `documents.py` | Nothing |
| INDEX | `indexer.py` | Nothing |
| SEARCH | `searcher.py` | `indexer.tokenize` |
| RANK | `ranker.py` | `indexer.tokenize` |
| AUTOCOMPLETE | `autocomplete.py` | Nothing to import. You pass it a word list, such as `index.keys()` |
| OPTIMIZE | `optimizer.py` | `indexer`, `searcher`, `ranker` |
| RELATED | `related.py` | `indexer.tokenize`. You pass it documents |
| PERSIST | `indexer.py` | Nothing. `save_index` and `load_index` live beside `build_index` |

AUTOCOMPLETE and RELATED do not need SEARCH or RANK.

---

## File Structure

```
Pysearch/
├── app.py                        # Streamlit UI
├── requirements.txt
├── .gitignore
├── LICENSE
├── README.md
├── docs/                         # Sample .txt files (doc1, doc2, doc3)
├── src/                          # One file per phase (see table below)
├── notebooks/                    # 8 test notebooks, one per phase
└── output/                       # index.json appears here after save_index
```

`output/index.json` appears after you run `save_index(index, "output/index.json")`. See Phase 2.

---

## Phase Reference

You build me one phase at a time. Each phase has one file and one test notebook.

| Phase | File | Purpose |
|-------|------|---------|
| 0 | `src/binary_search.py` | Teaches Big O. Not used in the final engine. |
| 1 | `src/documents.py` | Reads all `.txt` files into `[{id, name, content}]` |
| 2 | `src/indexer.py` | Builds and persists the `{word: [doc_ids]}` index |
| 3 | `src/searcher.py` | AND / OR multi-word search |
| 4 | `src/ranker.py` | TF-IDF relevance scoring |
| 5 | `src/autocomplete.py` | Prefix suggestions via a trie |
| 6 | `src/optimizer.py` | Caching and performance stats |
| 7 | `src/related.py` | Related words via BFS on a co-occurrence graph |

### Signatures

| Function | Input | Output | Example |
|----------|-------|--------|---------|
| `binary_search(sorted_list, target)` | ascending list, target | `int` index, or `None` | `binary_search([1, 3, 5], 3)` |
| `load_documents(folder_path)` | `str` | `list[dict]` with `id`, `name`, `content` | `docs = load_documents("docs")` |
| `tokenize(text)` | `str` | `list[str]` | `tokenize("Hello, high-level world!")` |
| `build_index(documents)` | `list[dict]` | `dict[str, list[int]]` | `index = build_index(docs)` |
| `save_index(index, filepath)` | index, `str` path | `None`. Writes JSON | `save_index(index, "output/index.json")` |
| `load_index(filepath)` | `str` path | `dict[str, list[int]]` | `index = load_index("output/index.json")` |
| `search(query, index, mode="AND")` | `str`, index, `"AND"` or `"OR"` | `list[int]` | `search("python hash", index, mode="OR")` |
| `compute_tf(term, doc_content)` | `str`, `str` | `float` | `compute_tf("python", docs[0]["content"])` |
| `compute_idf(term, documents)` | `str`, `list[dict]` | `float` | `compute_idf("python", docs)` |
| `rank(doc_ids, query, documents)` | `list[int]`, `str`, `list[dict]` | `list[tuple[int, float]]` | `rank([0, 2], "python hash", docs)` |
| `build_trie(words)` | `Iterable[str]` | `TrieNode` root | `trie = build_trie(index.keys())` |
| `autocomplete(prefix, trie, max_results=10)` | `str`, `TrieNode`, `int` | `list[str]`, sorted | `autocomplete("pro", trie)` |
| `cached_tokenize(text)` | `str` | `list[str]`, cached (up to 1024 entries) | `cached_tokenize(docs[0]["content"])` |
| `get_stats(documents, index)` | `list[dict]`, index | `dict` | `get_stats(docs, index)` |
| `measure_search_time(query, index, iterations=100)` | `str`, index, `int` | `float`, average ms | `measure_search_time("python", index)` |
| `measure_rank_time(doc_ids, query, documents, iterations=100)` | `list[int]`, `str`, `list[dict]`, `int` | `float`, average ms | `measure_rank_time([0, 2], "python", docs)` |
| `comparison_report(documents, index)` | `list[dict]`, index | `dict` with `naive_ms`, `cached_ms`, `speedup` | `comparison_report(docs, index)` |
| `build_graph(documents, window=5)` | `list[dict]`, `int` | `dict[str, set[str]]` | `graph = build_graph(docs)` |
| `bfs(graph, start, max_depth=2)` | graph, `str`, `int` | `dict[str, int]`: word to distance | `bfs(graph, "python")` |
| `related(word, graph, max_results=10)` | `str`, graph, `int` | `list[str]` | `related("python", graph)` |

Notes:

- `get_stats` returns `total_docs`, `total_tokens`, `unique_words`, `avg_tokens_per_doc`, and `index_size_bytes`. `index_size_bytes` is `sys.getsizeof` of the index dict plus the sizes of all keys and posting lists. It is a shallow estimate, not exact memory usage.
- In `bfs`, the start word appears at distance 0. Words unreachable within `max_depth` are not in the result. The order of keys in the returned dict is not fixed, so sort it if you need a stable order. `related` sorts for you.
- `autocomplete("pro", build_trie(index.keys()))` returns `['programming', 'provide']` on the sample files.

---

## Formulas and Parameters

| Item | Definition |
|------|------------|
| TF(t, d) | count(t in d) / total_tokens(d). Returns 0.0 for an empty document. |
| IDF(t) | log(N / df(t)), natural log. If df(t) = 0, IDF = 0.0, which avoids log(0). |
| Document score | Sum of TF x IDF over every query term |
| Rank order | Score descending, then doc ID ascending |
| Co-occurrence window (Phase 7) | 5 tokens on each side of a word |
| Max BFS depth (Phase 7) | 2 |
| `related` ordering | Distance ascending, then alphabetical |

---

## Rules I Follow

| Rule | Testable statement |
|------|--------------------|
| Case-insensitive | `tokenize("Python")` returns `["python"]` |
| Punctuation | `. , ! ? ; : " ' ( ) [ ] { }` are removed from anywhere in a token, not only its edges. `tokenize("3.14")` returns `["314"]` and `tokenize("it's")` returns `["its"]`. |
| Hyphens | Internal hyphens stay, so `high-level` is one token. Leading and trailing hyphens are stripped. |
| No duplicate postings | Each doc ID appears once per word |
| Doc IDs | 0-indexed, assigned in alphabetical filename order |
| Sorted output | Posting lists and `search` results are sorted ascending by doc ID |
| Unknown words in AND mode | `search` returns `[]` |
| The word "or" | The word `or` in a query forces OR mode and is not searched as a term. If mode is passed explicitly and the query contains `or`, the query wins. Example: `search("python or hash", index, mode="AND")` runs in OR mode. |
| Invalid mode | `search` raises `ValueError` unless mode is `"AND"` or `"OR"` |
| Empty query | `search` and `rank` return `[]` |
| Unknown doc ID | `rank` raises `ValueError` |
| Empty corpus | `get_stats` returns zeros. `compute_idf` returns 0.0. |

---

## Testing

My tests are Jupyter notebooks, one per phase. To run them interactively:

```bash
python -m notebook
```

Open a `phaseN` notebook in `notebooks/` and choose **Run All**. To run every notebook headlessly from the project root:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
```

Notebooks for phases 1-7 use `assert` statements. If any assertion fails, the notebook stops at that cell and shows the failing assertion. The Phase 0 notebook prints its results and has no asserts.

| Notebook | Tests |
|----------|-------|
| `phase0_binary_search.ipynb` | 6 |
| `phase1_documents.ipynb` | 5 |
| `phase2_indexer.ipynb` | 10 |
| `phase3_searcher.ipynb` | 10 |
| `phase4_ranker.ipynb` | 10 |
| `phase5_autocomplete.ipynb` | 8 |
| `phase6_optimizer.ipynb` | 8 |
| `phase7_related.ipynb` | 8 |
| **Total** | **65** |

---

## Known Limitations

- I read `.txt` files only. I do not read PDF or DOCX.
- I do no stop-word filtering, so common words like "is" stay in the index.
- I do no fuzzy matching. A misspelled word matches nothing.
- I do no phrase search. Words match anywhere in a document, in any order.
- I do not scan subfolders. I read only the folder you point me at.
- When a term appears in every document, its IDF is 0, so that term contributes nothing to scores. On a 3-document corpus, this zeroes scores easily.
- I serve one local session. I have no multi-user features.

---

## Roadmap

Version 2 plans:

- PDF and DOCX input
- Stop-word filtering
- Phrase search
- Database persistence

---

## Reference

I follow ideas from **Grokking Algorithms** by Aditya Bhargava. Chapter numbers below follow the book's first edition.

| Phase | Idea | Book chapter |
|-------|------|--------------|
| 0 | Binary search, Big O | Ch 1, Introduction to Algorithms |
| 1 | Loading documents (arrays) | Ch 2, Selection Sort |
| 2 | Hash tables | Ch 5, Hash Tables |
| 2 | Inverted index | Ch 11, Where to Go Next (Inverted indexes section) |
| 3 | Hash table lookups | Ch 5, Hash Tables |
| 4 | TF-IDF scoring | Not covered in the book |
| 5 | Trie | Not covered in the book |
| 6 | Caching | Ch 5, Hash Tables |
| 7 | Breadth-first search | Ch 6, Breadth-First Search |

---

## License

Apache License 2.0. See the `LICENSE` file.

---

Built by a learner, for learners.
