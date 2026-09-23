import os

def load_documents(folder_path):
    """
    Reads every .txt file in folder_path.
    Returns a list of dicts with keys: id (int), name (str), content (str).
    """
    # Create an empty list to store document dictionaries
    documents = []
    # Scan the folder and sort all text file names alphabetically
    files = sorted(f for f in os.listdir(folder_path) if f.endswith(".txt"))
    # Loop through the sorted files using an incremental index counter
    for doc_id, filename in enumerate(files):
        # Join the folder path and filename into an absolute path
        full_path = os.path.join(folder_path, filename)
        # Open each text file safely using explicit UTF-8 character encoding
        with open(full_path, "r", encoding="utf-8") as f:
            # Read the entire text file payload into runtime memory
            content = f.read()
        # Append the structured document map to the collection list
        documents.append({
            "id": doc_id,
            "name": filename,
            "content": content
        })
    # Hand back the finalized list of document dictionaries
    return documents