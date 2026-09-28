from collections import deque           # efficient FIFO queue for BFS
from src.indexer import tokenize        # reuse existing tokenizer for consistency


def build_graph(documents, window=5):
    """Build {word: set(neighbor_words)} where neighbors = words within `window` tokens."""
    graph = {}                          # adjacency map: word -> set of neighbors
    for doc in documents:               # process each document independently
        content = doc.get("content", "")  # safely fetch content field
        if not content:                 # skip empty docs per spec
            continue                    # nothing to add from this doc
        tokens = [t.lower() for t in tokenize(content)]  # normalize case for all tokens
        n = len(tokens)                 # total token count for bounds checking
        for i, word in enumerate(tokens):  # anchor word at position i
            if word == "or":            # skip 'or' as an anchor per spec
                continue                # don't build edges from this word
            if word not in graph:       # ensure entry exists before adding neighbors
                graph[word] = set()     # fresh neighbor set for new word
            lo = max(0, i - window)     # left bound of the window
            hi = min(n, i + window + 1) # right bound of the window (exclusive)
            for j in range(lo, hi):     # scan all tokens within window range
                if j == i:              # skip the anchor word itself
                    continue            # not its own neighbor
                neighbor = tokens[j]    # candidate neighbor word
                if neighbor == "or":    # skip 'or' as a neighbor per spec
                    continue            # excluded from co-occurrence graph
                graph[word].add(neighbor)  # record co-occurrence edge
    return graph                        # final co-occurrence graph


def bfs(graph, start, max_depth=2):
    """BFS from start node. Return dict {word: distance}. Include start at distance 0."""
    start = start.lower()               # normalize case to match graph keys
    if start not in graph:              # start word not present in graph
        return {}                       # nothing reachable, return empty
    distances = {start: 0}              # track shortest distance per word
    visited = {start}                   # prevents revisiting processed nodes
    queue = deque([start])              # BFS frontier, starts with the root word
    while queue:                        # process until frontier is exhausted
        current = queue.popleft()       # dequeue next word to expand
        current_dist = distances[current]  # distance of the word being expanded
        if current_dist >= max_depth:   # stop expanding beyond max depth
            continue                    # don't enqueue further neighbors
        for neighbor in graph.get(current, ()):  # iterate co-occurring words
            if neighbor not in visited: # only process unseen neighbors
                visited.add(neighbor)   # mark as seen to avoid duplicates
                distances[neighbor] = current_dist + 1  # one hop further than current
                queue.append(neighbor)  # enqueue for further expansion
    return distances                    # word -> distance mapping


def related(word, graph, max_results=10):
    """Return list of words reachable from `word` within max_depth, sorted by distance."""
    word = word.lower()                 # normalize case to match graph keys
    if word not in graph:               # word absent from graph entirely
        return []                       # nothing to return per spec
    distances = bfs(graph, word)        # get all reachable words with distances
    distances.pop(word, None)           # exclude the word itself from results
    ordered = sorted(distances.items(), key=lambda pair: (pair[1], pair[0]))  # sort by distance then alpha
    return [w for w, _ in ordered][:max_results]  # strip distances, cap results