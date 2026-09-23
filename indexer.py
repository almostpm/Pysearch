import collections
import json

# Create a global translation table to strip out common punctuation marks
_PUNCT_TABLE = str.maketrans("", "", ".,!?;:\"'()[]{}")


def tokenize(text):
    """
    Splits text into a list of clean lowercase words.
    """
    # Initialize an empty list to store the cleaned word tokens
    tokens = []
    # Force the text to lowercase and split it on whitespace chunks
    for word in text.lower().split():
        # Strip out specific punctuation marks and trailing hyphens from words
        word = word.translate(_PUNCT_TABLE).strip("-")
        # Ensure the token is not empty before keeping it
        if word:
            # Append the cleaned word to our running token collection
            tokens.append(word)
    # Return the completed list of lowercase word tokens
    return tokens


def build_index(documents):
    """
    Build inverted index from list of documents.
    Each document is a dict with keys: id, name, content.
    Returns dict: {word: [doc_ids]}
    """
    # Create a default dictionary that automatically builds sets for new keys
    index = collections.defaultdict(set)
    # Loop through each document dictionary in the collection one by one
    for doc in documents:
        # Safely extract the content string from the current document record
        content = doc.get("content")
        # Skip the document completely if the content field is empty
        if not content:
            # Continue directly to the next document in the collection
            continue
        # Convert text to tokens and filter duplicates out using a set
        for word in set(tokenize(content)):
            # Add the unique document ID to this specific word's posting set
            index[word].add(doc["id"])
    # Return a sorted list of integer document IDs for every unique word
    return {word: sorted(doc_ids) for word, doc_ids in index.items()}


def save_index(index, filepath):
    """
    Save inverted index to a JSON file.
    """
    # Open the target file path with explicit write permissions and UTF-8 encoding
    with open(filepath, "w", encoding="utf-8") as f:
        # Serialize the index dictionary to disk with pretty printing format
        json.dump(index, f, indent=2, ensure_ascii=False)


def load_index(filepath):
    """
    Load inverted index from a JSON file.
    Returns dict: {word: [doc_ids]}
    """
    # Open the saved index JSON file with explicit read permissions
    with open(filepath, "r", encoding="utf-8") as f:
        # Parse the JSON string back into a standard Python lookup dictionary
        return json.load(f)