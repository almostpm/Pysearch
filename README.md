# Pysearch - Mini Search Engine

A lightweight search engine built from scratch in Python. No frameworks, no external libraries — just standard library and clear code.

**Reference:** *Grokking Algorithms* by Aditya Bhargava

**Status:** Phases 0–2 complete. Phases 3+ planned.

---

## What This Project Is

This project reads `.txt` files from a folder, breaks them into clean words, and builds an **inverted index** — a map from every word to the documents that contain it.

The result: you can look up any word and instantly know which documents have it, without scanning every file.

It's a learning project that walks through the data structures real search engines use: **binary search**, **arrays**, and **hash tables**.

---

## Rules

The engine follows these rules everywhere.

| Rule | What It Means |
|:---|:---|
| **Sorted input for binary search** | Binary search only works on sorted lists. Unsorted input gives wrong answers silently. |
| **Case-insensitive matching** | `"Python"` and `"python"` are treated as the same word. |
| **Punctuation ignored** | `"hello!"` and `"hello"` are the same word. |
| **One entry per word per document** | If `"python"` appears 100 times in one doc, the doc ID is stored once. |
| **0-indexed document IDs** | First document is ID 0, second is ID 1. Matches Python's list indexing. |
| **Index is persistent** | Saved to JSON. Reload instantly. No rebuild on every run. |
| **Only `.txt` files** | Other file types are skipped. Predictable input only. |
| **Deterministic output** | Same input always gives the same output. No randomness. |

---

## Architecture

Three layers. Each does one job.

┌─────────────────────────────────────┐
│ INPUT LAYER │
│ docs/*.txt → load_documents() │
│ Output: list[dict] │
└──────────────┬──────────────────────┘
↓
┌─────────────────────────────────────┐
│ INDEX LAYER │
│ tokenize() + build_index() │
│ Output: {word: [doc_ids]} │
└──────────────┬──────────────────────┘
↓
┌─────────────────────────────────────┐
│ PERSISTENCE LAYER │
│ save_index() + load_index() │
│ Output: output/index.json │
└─────────────────────────────────────┘



### Phase → Layer Mapping

| Phase | Name | Layer |
|:---|:---|:---|
| Phase 0 | Binary search | Not a layer — practice exercise |
| Phase 1 | Document ingestion | Input layer |
| Phase 2 | Inverted index | Index layer + Persistence layer |

**Note:** Phase 0 doesn't run in the final engine. It teaches Big O intuition and sets up the project structure. The actual engine starts at Phase 1.

---

## Design

| Principle | What It Means |
|:---|:---|
| **Separation of concerns** | One function, one job. `tokenize` splits. `build_index` maps. `save_index` writes. |
| **Stateless functions** | No global state. Every function takes input, returns output. |
| **Deterministic** | Sorted lists, fixed order. Same input = same output. |
| **Defensive** | Type checks, empty checks, missing-key checks. No silent failures. |
| **Persistent** | Index saved to disk. Reload instant. |
| **Standard library only** | No `pip install`. Uses `os`, `json`, `collections`. |

### Data Structures

| Structure | Where | Why |
|:---|:---|:---|
| **list** | `documents`, `tokens` | O(1) index access, fast iteration |
| **dict** (hash table) | `index` word → doc IDs | O(1) lookup — core of search |
| **set** | Temporary dedupe during `build_index` | Removes duplicate doc IDs |
| **JSON** | Persistence file | Human-readable, cross-language |

### Complexity

| Operation | Complexity |
|:---|:---|
| Load all documents | O(n × m) — n docs, m avg chars |
| Tokenize one doc | O(m) — m chars |
| Build index | O(total words) |
| **Lookup one word** | **O(1)** |
| Save index | O(unique words) |
| Load index | O(unique words) |

---

## Measures Taken

Steps to keep the code correct and predictable.

| Measure | Purpose |
|:---|:---|
| Type check in `tokenize` | Rejects non-string input early, prevents garbage |
| Skip empty content | Empty documents don't pollute the index |
| Filter only `.txt` files | Non-text files like `.pdf` are ignored |
| Sort filenames alphabetically | Stable document order across runs |
| UTF-8 encoding on read/write | Handles accents, emojis, any character |
| `os.path.join` for paths | Cross-platform — works on Windows, Mac, Linux |
| `with open(...) as f` | Files always closed, even on error |
| Dedupe via set | Same doc ID never stored twice per word |
| Sort doc IDs before output | Deterministic index structure |
| JSON `indent=2` | Human-readable output file |
| 10 test cells per phase | Structure + edge cases + round-trip verified |

---

## Files

mini-search-engine/
├── docs/ # Raw .txt files to search
├── src/
│ ├── init.py # Marks src/ as a package
│ ├── binary_search.py # Phase 0 — binary search
│ ├── documents.py # Phase 1 — load .txt files
│ └── indexer.py # Phase 2 — build inverted index
├── notebooks/ # Test notebooks per phase
│ ├── phase0_binary_search.ipynb
│ ├── phase1_final.ipynb
│ └── phase2_final.ipynb
├── output/
│ └── index.json # Generated by Phase 2
└── README.md


### Functions

| Function | Input | Output |
|:---|:---|:---|
| `binary_search(list, target)` | Sorted list, target | Index or `None` |
| `load_documents(folder)` | Folder path | List of `{id, name, content}` |
| `tokenize(text)` | Raw string | List of clean lowercase words |
| `build_index(documents)` | List of doc dicts | `{word: [doc_ids]}` |
| `save_index(index, path)` | Index dict, path | Writes JSON file |
| `load_index(path)` | File path | Index dict |

---

## User Expectations

### What Users Can Expect

| Expectation | Delivered |
|:---|:---|
| "Type a word, get the docs" | ✅ `index.get(word, [])` |
| "Case doesn't matter" | ✅ `tokenize` lowercases |
| "Punctuation doesn't matter" | ✅ Punctuation stripped |
| "Fast lookup" | ✅ O(1) via dict |
| "No rebuild every time" | ✅ JSON persistence |
| "Same input = same output" | ✅ Sorted, deterministic |
| "Never crashes silently" | ✅ Edge cases handled |

### What Users Should NOT Expect (Yet)

| Expectation | Why Not |
|:---|:---|
| "How many times word appeared" | Phase 2 stores only *which docs*, not counts |
| "Best results first" | Ranking comes in Phase 4 (TF-IDF) |
| "Multi-word search" | Phase 3 — `"python AND search"` |
| "Handles PDFs, Word docs" | Only `.txt` files |
| "Handles typos" | No fuzzy matching |
| "Filters common words" | Stop words come in Phase 6 |

---

## Current Status

**Completed:** Phases 0–2

| Phase | Deliverable | Tests |
|:---|:---|:---|
| Phase 0 | `src/binary_search.py` | 6 test cases ✅ |
| Phase 1 | `src/documents.py` | 5 test cases ✅ |
| Phase 2 | `src/indexer.py` | 10 test cases ✅ |

**Sample output from Phase 2:**

Loaded 3 documents
0: doc1.txt (167 chars)
1: doc2.txt (162 chars)
2: doc3.txt (164 chars)

Unique words in index: 60

'python' → [0, 2] → ['doc1.txt', 'doc3.txt']
'search' → [1] → ['doc2.txt']
'hash' → [2] → ['doc3.txt']
'nonexistent' → NOT FOUND

✅ Saved index to output/index.json (1733 bytes)
✅ Round-trip save/load matches original


**Index structure (`output/index.json`):**

```json
{
  "python":   [0, 2],
  "search":   [1],
  "hash":     [2],
  "language": [0]
}
