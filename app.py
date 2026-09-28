import streamlit as st                                          # core streamlit framework
import tempfile                                                 # for creating temp upload folders
import os                                                       # for file path joins

# wrap all src imports so app never crashes on missing modules
try:
    from src.documents import load_documents                     # loads docs from folder
    from src.indexer import build_index                          # builds inverted index
    from src.searcher import search                              # performs AND/OR search
    from src.ranker import rank                                  # ranks doc_ids by relevance
    from src.autocomplete import build_trie, autocomplete         # trie-based prefix search
    from src.optimizer import get_stats                           # corpus statistics
    from src.related import build_graph, related                  # co-occurrence related words
    IMPORT_ERROR = None                                          # marks imports as successful
except Exception as e:
    IMPORT_ERROR = str(e)                                        # capture exact import failure message

st.set_page_config(page_title="Mini Search Engine", layout="wide")  # wide layout, page title

if IMPORT_ERROR:                                                 # halt app if core modules missing
    st.error(IMPORT_ERROR)                                        # show exact import error
    st.stop()                                                     # prevent further execution

# initialize session state keys once per session
if "docs" not in st.session_state:
    st.session_state.docs = []                                    # holds loaded document dicts
if "index" not in st.session_state:
    st.session_state.index = {}                                   # holds inverted index
if "trie" not in st.session_state:
    st.session_state.trie = None                                  # lazily built autocomplete trie


@st.cache_data(show_spinner=False)                                # cache expensive load+index step
def _load_and_build(files_data):
    """files_data: tuple of (filename, bytes) pairs, hashable for caching."""
    temp_dir = tempfile.mkdtemp()                                 # isolated temp folder per call
    for filename, content in files_data:                          # write each uploaded file to disk
        filepath = os.path.join(temp_dir, filename)                # build full temp file path
        with open(filepath, "wb") as f:                            # write in binary mode
            f.write(content)                                       # persist uploaded bytes
    docs = load_documents(temp_dir)                                # parse temp folder into doc dicts
    index = build_index(docs)                                      # build inverted index from docs
    return docs, index                                             # cached return value


@st.cache_data(show_spinner=False)                                # cache trie build per index snapshot
def _build_trie_from_index(index):
    words = list(index.keys())                                    # vocabulary from index keys
    return build_trie(words)                                       # construct trie once per index


@st.cache_data(show_spinner=False)                                # cache graph build to prevent lag on rerun
def _build_graph_from_docs(docs):
    return build_graph(docs)                                      # construct related words graph


st.title("Mini Search Engine")                                    # app header
tab1, tab2, tab3, tab4 = st.tabs(["Upload & Index", "Search", "Autocomplete", "Stats"])  # top nav

# ---------------- TAB 1: Upload & Index ----------------
with tab1:
    st.caption("Upload .txt files and build the searchable index.")  # explains this section
    uploaded_files = st.file_uploader(                             # multi-file uploader widget
        "Upload text files", type=["txt"], accept_multiple_files=True
    )

    if not uploaded_files:                                         # nothing uploaded yet
        st.info("Upload one or more .txt files to get started.")    # guidance message

    build_clicked = st.button("Build Index")                        # trigger index construction

    if build_clicked:                                              # user requested a build
        if not uploaded_files:                                      # guard against empty upload
            st.warning("Please upload at least one .txt file first.")  # user-friendly warning
        else:
            try:
                files_data = tuple(                                  # hashable structure for caching
                    (f.name, f.getvalue()) for f in uploaded_files
                )
                docs, index = _load_and_build(files_data)             # cached load + index build
                st.session_state.docs = docs                          # persist docs in session
                st.session_state.index = index                        # persist index in session
                st.session_state.trie = None                           # invalidate stale trie
                stats = get_stats(docs, index)                         # quick stats for feedback
                st.success(                                            # confirm successful build
                    f"Indexed {stats['total_docs']} docs, "
                    f"{stats['unique_words']} unique words."
                )
            except Exception as e:
                st.error(f"Failed to build index: {e}")                # never crash, show message

    st.divider()                                                       # visual section break

    if st.session_state.docs:                                          # show indexed file list
        st.write("Indexed files:")                                     # section label
        for doc in st.session_state.docs:                              # iterate stored documents
            st.write(f"- {doc['name']} (id: {doc['id']})")              # display each doc entry
        st.caption(f"Total documents indexed: {len(st.session_state.docs)}")  # running count

    with st.expander("Debug info"):                                    # advanced/debug section
        st.write("Session doc count:", len(st.session_state.docs))     # raw debug value
        st.write("Session index size:", len(st.session_state.index))   # raw debug value

# ---------------- TAB 2: Search ----------------
with tab2:
    st.caption("Search indexed documents using AND/OR logic and optional ranking.")  # section intro

    if not st.session_state.index:                                     # index not yet built
        st.warning("Build an index first in the 'Upload & Index' tab.")  # blocking warning
    else:
        col1, col2 = st.columns(2)                                     # two-column layout for controls
        with col1:
            query = st.text_input("Search query")                      # free-text query input
            mode = st.radio("Match mode", ["AND", "OR"])                # AND/OR toggle
        with col2:
            max_results = st.slider("Max results", 1, 20, 10)          # cap on displayed results
            use_ranking = st.checkbox("Use TF-IDF ranking", value=True)  # toggle ranking on/off

        search_clicked = st.button("Search")                            # trigger search action

        if search_clicked:                                               # user requested search
            if not query.strip():                                        # empty query guard
                st.info("Enter a query above to search.")                 # hint for empty input
            else:
                try:
                    doc_ids = search(query, st.session_state.index, mode)  # run AND/OR search
                    total_matches = len(doc_ids)                           # count before truncation
                    st.write(f"Total matches: {total_matches}")            # show match count

                    if not doc_ids:                                        # no matches found
                        st.warning("No matching documents.")               # user-friendly notice
                    else:
                        if use_ranking:                                    # apply TF-IDF ranking
                            ranked = rank(doc_ids, query, st.session_state.docs)  # score+sort results
                        else:
                            ranked = [(doc_id, None) for doc_id in doc_ids]  # keep unranked order

                        ranked = ranked[:max_results]                       # apply display cap
                        doc_lookup = {                                      # id->doc map for content
                            d["id"]: d for d in st.session_state.docs
                        }
                        for doc_id, score in ranked:                        # render each result
                            doc = doc_lookup.get(doc_id)                    # fetch full doc dict
                            if doc is None:                                 # skip missing doc safely
                                continue
                            st.markdown(f"**{doc['name']}**")               # bold document name
                            if use_ranking and score is not None:           # show score if ranked
                                st.write(f"Score: {score:.4f}")             # display numeric score
                            snippet = doc["content"][:200]                  # first 200 chars preview
                            st.write(snippet)                               # show content snippet
                            st.divider()                                    # separate each result
                except Exception as e:
                    st.error(f"Search failed: {e}")                        # graceful error display

# ---------------- TAB 3: Autocomplete ----------------
with tab3:
    st.caption("Get word suggestions based on a prefix from the indexed vocabulary.")  # section intro

    if not st.session_state.index:                                     # need index for vocabulary
        st.warning("Build an index first in the 'Upload & Index' tab.")  # blocking warning
    else:
        prefix = st.text_input("Prefix")                                # user-entered prefix
        ac_max_results = st.slider("Max suggestions", 1, 20, 10)        # cap on suggestions shown
        suggest_clicked = st.button("Suggest")                          # trigger suggestion lookup

        if suggest_clicked:                                              # user requested suggestions
            if not prefix.strip():                                       # empty prefix guard
                st.info("Enter a prefix above to see suggestions.")      # hint for empty input
            else:
                try:
                    if st.session_state.trie is None:                    # lazy trie construction
                        st.session_state.trie = _build_trie_from_index(   # cached trie build
                            st.session_state.index
                        )
                    suggestions = autocomplete(                          # fetch matching words
                        prefix, st.session_state.trie, ac_max_results
                    )
                    if not suggestions:                                  # no matches for prefix
                        st.warning("No suggestions.")                    # user-friendly notice
                    else:
                        for word in suggestions:                         # render suggestion list
                            st.markdown(f"- {word}")                     # bullet-style entry
                except Exception as e:
                    st.error(f"Autocomplete failed: {e}")                # graceful error display

# ---------------- TAB 4: Stats ----------------
with tab4:
    st.caption("Corpus statistics and most frequent indexed words.")    # section intro

    if not st.session_state.index:                                      # need built index for stats
        st.warning("Build index first.")                                # blocking message per spec
    else:
        try:
            stats = get_stats(st.session_state.docs, st.session_state.index)  # compute stats dict
            m1, m2, m3, m4, m5 = st.columns(5)                            # five metric columns
            m1.metric("Total docs", stats["total_docs"])                  # doc count metric
            m2.metric("Total tokens", stats["total_tokens"])              # token count metric
            m3.metric("Unique words", stats["unique_words"])              # vocabulary size metric
            m4.metric("Avg tokens/doc", stats["avg_tokens_per_doc"])      # average tokens metric
            m5.metric("Index size (bytes)", stats["index_size_bytes"])    # memory estimate metric

            st.divider()                                                  # separate metrics from table
            st.write("Top 10 most common words:")                        # table section label
            word_counts = [                                               # doc-frequency per word
                (word, len(doc_ids))
                for word, doc_ids in st.session_state.index.items()
            ]
            top_words = sorted(                                          # sort descending by count
                word_counts, key=lambda pair: pair[1], reverse=True
            )[:10]                                                        # keep top 10 only
            st.table(                                                     # render as simple table
                {"Word": [w for w, _ in top_words], "Doc count": [c for _, c in top_words]}
            )
        except Exception as e:
            st.error(f"Failed to compute stats: {e}")                    # graceful error display

        with st.expander("Related words explorer"):                      # extra debug/advanced feature
            related_word = st.text_input("Word to explore", key="related_word")  # word input
            find_related = st.button("Find related")                     # manual trigger for lookup

            if find_related:                                             # execute lookup on button press
                if not related_word.strip():                             # guard against empty input
                    st.info("Enter a word first.")                       # hint for empty input
                else:
                    try:
                        graph = _build_graph_from_docs(st.session_state.docs) # fetch cached co-occurrence graph
                        neighbors = related(related_word.lower(), graph)      # fetch related words
                        if neighbors:                                          # show results if found
                            st.write(neighbors)                                # raw list display
                        else:
                            st.write("No related words found.")               # empty-result message
                    except Exception as e:
                        st.error(f"Related lookup failed: {e}")                # graceful error display