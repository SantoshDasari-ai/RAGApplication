# utils.py
from langchain.docstore.document import Document as LangchainDocument
import pickle

def create_no_chunks(documents):
    """
    Creates chunks from a list of documents without any additional processing.
    Each document becomes a chunk with its original content and metadata.

    Args:
        documents (list): List of LangchainDocument objects.

    Returns:
        list: List of LangchainDocument objects representing the chunks.

    Raises:
        ValueError: If the documents list is empty.
    """
    if not documents:
        raise ValueError("Documents list must not be empty.")

    # Simply return the original documents as chunks
    return [
        LangchainDocument(
            page_content=doc.page_content.strip(),
            metadata={
                'source': doc.metadata.get('source'),
                'page_numbers': doc.metadata.get('page_numbers')
            }
        ) for doc in documents
    ]

def save_to_file(obj, filename):
    """
    Save an object to a file using pickle.

    Args:
        obj: The object to be saved.
        filename (str): The path to the file where the object will be saved.
    """
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)

def load_from_file(filename):
    """
    Load an object from a file using pickle.

    Args:
        filename (str): The path to the file from which to load the object.

    Returns:
        The loaded object.
    """
    with open(filename, 'rb') as f:
        return pickle.load(f)
