import math  # import math module for natural log in IDF
from src.indexer import tokenize  # import tokenizer for query normalization

def compute_tf(term, doc_content):  # calculate term frequency for a given term and document
    """Term frequency: (count of term in doc) / (total tokens in doc)."""  # docstring for compute_tf
    tokens = tokenize(doc_content)  # tokenize the document content into lowercase words
    total = len(tokens)  # count total number of tokens in the document
    if total == 0:  # guard against empty documents to prevent division by zero
        return 0.0  # return 0.0 score if document has no tokens
    count = tokens.count(term)  # count how many times the term appears in the document tokens
    if count == 0:  # check if the term is absent from the document
        return 0.0  # return 0.0 since term doesn't appear
    return count / total  # return the normalized term frequency

def compute_idf(term, documents):  # calculate inverse document frequency for a term
    """Inverse document frequency: log(total_docs / docs_containing_term)."""  # docstring for compute_idf
    total_docs = len(documents)  # count the total number of documents in the corpus
    if total_docs == 0:  # check if the corpus is entirely empty
        return 0.0  # return 0.0 if no documents exist to avoid math errors
    doc_count = 0  # initialize counter for documents that contain the target term
    for doc in documents:  # iterate over each document in the corpus
        if term in tokenize(doc["content"]):  # check if term exists in the tokenized document content
            doc_count += 1  # increment the match counter if term is found
    if doc_count == 0:  # check if the term was not found in any document
        return 0.0  # return 0.0 to prevent division by zero in log calculation
    return math.log(total_docs / doc_count)  # calculate and return natural log of the inverse doc frequency

def rank(doc_ids, query, documents):  # rank documents based on TF-IDF relevance to query
    """Rank doc_ids by TF-IDF relevance to query."""  # docstring for rank function
    doc_ids = list(dict.fromkeys(doc_ids))  # deduplicate doc_ids while preserving order (Bug 2 fix)
    query_terms = tokenize(query)  # tokenize the raw query string into normalized terms
    query_terms = [t for t in query_terms if t != "or"]  # filter out the literal keyword 'or' (Bug 3 fix)
    
    if not doc_ids or not query_terms:  # verify we have both documents to rank and terms to search
        return []  # return empty list if nothing to rank
        
    doc_lookup = {doc["id"]: doc for doc in documents}  # build a lookup dictionary mapping doc id to document object
    
    idf_cache = {}  # initialize a cache dictionary to store computed IDF values
    for term in query_terms:  # iterate over each cleaned term in the query
        if term not in idf_cache:  # check if the term's IDF has not been computed yet
            idf_cache[term] = compute_idf(term, documents)  # compute and cache the IDF value for the term
            
    scored = []  # initialize an empty list to accumulate document scores
    for doc_id in doc_ids:  # iterate over each candidate document ID
        doc = doc_lookup.get(doc_id)  # retrieve the document object using its ID
        if doc is None:  # check if the requested document ID is missing from the corpus
            raise ValueError(f"Unknown doc_id: {doc_id}")  # raise exception for unknown doc_id (Bug 1 fix)
            
        score = 0.0  # initialize the running TF-IDF sum for the current document
        for term in query_terms:  # iterate over each term in the query
            tf = compute_tf(term, doc["content"])  # calculate the term frequency for the current document
            idf = idf_cache[term]  # retrieve the cached inverse document frequency for the term
            score += tf * idf  # multiply TF by IDF and add to the running score
        scored.append((doc_id, score))  # append a tuple of the document ID and its final score
        
    scored.sort(key=lambda pair: (-pair[1], pair[0]))  # sort the results descending by score, then ascending by doc_id
    return scored  # return the final ranked list of document tuples