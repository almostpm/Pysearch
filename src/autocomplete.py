class TrieNode:
    """One node in the trie. children maps char->TrieNode. is_end marks word end."""

    def __init__(self):
        self.children = {}              # maps char -> TrieNode
        self.is_end = False             # marks if a word ends here


def build_trie(words):
    """Build trie from list of words. Returns root TrieNode."""
    root = TrieNode()                   # root has no character, just links
    for word in words:                  # insert each word one at a time
        if not isinstance(word, str):   # guard against bad input types
            raise TypeError("words must be strings")
        node = root                     # start insertion at root each time
        for ch in word.lower():         # normalize case before inserting
            if ch not in node.children: # create branch if char not seen
                node.children[ch] = TrieNode()  # new node for this char
            node = node.children[ch]    # descend into the child node
        node.is_end = True              # mark final node as word end
    return root                         # caller stores this for lookups


def _collect_words(node, prefix, max_results, results):
    """Depth-first collect words from node, stopping once cap is reached."""
    if len(results) >= max_results:     # stop early once cap hit
        return
    if node.is_end:                     # this path forms a complete word
        results.append(prefix)          # record the completed word
    for ch in sorted(node.children):    # visit children in sorted order
        if len(results) >= max_results: # re-check cap before recursing
            return
        _collect_words(node.children[ch], prefix + ch, max_results, results)  # recurse deeper


def autocomplete(prefix, trie, max_results=10):
    """Return list of words starting with prefix, capped at max_results, sorted alphabetically."""
    if not isinstance(prefix, str):     # enforce string-only prefixes
        raise TypeError("prefix must be a string")
    node = trie                         # start traversal at trie root
    prefix_lower = prefix.lower()       # normalize case for lookup
    for ch in prefix_lower:             # walk down trie following prefix chars
        if ch not in node.children:     # prefix path doesn't exist
            return []                   # no matches possible
        node = node.children[ch]        # move to next matching node
    results = []                        # accumulator for matched words
    _collect_words(node, prefix_lower, max_results, results)  # gather completions
    return sorted(results)              # ensure alphabetical order in output