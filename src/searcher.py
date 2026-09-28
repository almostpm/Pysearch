from src.indexer import tokenize  # Import the tokenizer function from the indexer module

def _parse_query(query):  # Define function to extract tokens and mode from the query
    """Extract keyword tokens from a query string. Strips 'OR'. Returns (tokens, mode)."""  # Docstring for _parse_query
    raw_tokens = tokenize(query)  # Tokenize the input query into raw lowercase tokens
    mode = "OR" if "or" in raw_tokens else "AND"  # Detect if the literal word 'or' is in the query
    tokens = [t for t in raw_tokens if t != "or"]  # Filter out the literal word 'or' from the token list
    return tokens, mode  # Return the cleaned tokens and the detected mode

def search(query, index, mode="AND"):  # Define search function with a default AND mode
    """Search the inverted index for documents matching the query."""  # Docstring for search function
    if mode not in ("AND", "OR"):  # Validate that the provided mode parameter is acceptable
        raise ValueError(f"Invalid mode: {mode}. Must be 'AND' or 'OR'.")  # Raise ValueError for invalid modes (Bug 2 fix)
        
    tokens, parsed_mode = _parse_query(query)  # Parse the query to extract tokens and check for 'or' keyword
    
    if not tokens:  # Check if the query resulted in an empty token list
        return []  # Return an empty list if there is nothing to search for
        
    effective_mode = "OR" if parsed_mode == "OR" else mode  # Explicitly use OR if 'or' was in query, else use param (Bug 1 & 3 fix)
    
    doc_lists = [set(index.get(word, [])) for word in tokens]  # Retrieve the set of document IDs for each token
    
    if effective_mode == "OR":  # Execute search logic for OR mode
        result = set()  # Initialize an empty set for accumulating documents
        for doc_list in doc_lists:  # Loop through each token's document list
            result |= doc_list  # Union the current list with the accumulated results
    else:  # Execute search logic for AND mode
        result = doc_lists[0] if doc_lists else set()  # Initialize results with the first document list
        for doc_list in doc_lists[1:]:  # Loop through all subsequent document lists
            result &= doc_list  # Intersect the current list with the accumulated results
            
    return sorted(result)  # Return the final deduplicated document IDs in sorted order