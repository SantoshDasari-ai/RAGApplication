import os
from dataset_loader import load_or_generate_dataset_from_textfiles
import llm_provider as LLMProvider
import pinecone
from sentence_transformers import SentenceTransformer
import time
import utils as RagUtility
from dotenv import load_dotenv
import json 

# Folder containing our source text files
TXT_PATH = 'data/raw_text'
# Where we save our processed dataset
DATASET_DIR = "data/datasets/CXDataset"
DATASET_CSV_TEXT_PATH = "data/datasets/CXDataset.csv"

# Load environment variables from .env file
load_dotenv()

def load_embeddings(knowledge_base, embedding_model_name, index_name):
    """
    Loads embeddings for the documents and stores them in a Pinecone index.

    Args:
        knowledge_base: List of documents to be embedded.
        chunk_size: The maximum size of each chunk.
        embedding_model_name: The name of the embedding model to use.
        index_name: The name of the Pinecone index.
        chunking_method: The method of chunking ('recursive' or 'per_page').

    Returns:
        The Pinecone index.
    """
    # Initialize Pinecone
    pc = pinecone.Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    spec = pinecone.ServerlessSpec(
        cloud=os.getenv('PINECONE_CLOUD', 'aws'),
        region=os.getenv('PINECONE_REGION', 'us-east-1')
    )
    
    
    embedding_model = SentenceTransformer(embedding_model_name)
    embedding_dim = embedding_model.get_sentence_embedding_dimension()
        
    if index_name in pc.list_indexes().names():
        return pc.Index(index_name)
    else:
        pc.create_index(index_name, dimension=embedding_dim, metric='dotproduct', spec=spec)
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)

    index = pc.Index(index_name)

    # Prepare and upsert embeddings into Pinecone
    docs_processed = RagUtility.create_no_chunks(knowledge_base)
    
    for i, doc in enumerate(docs_processed):
        embedding = embedding_model.encode(doc.page_content)
        try:
            index.upsert([(f"doc-{i}", embedding, {"text": doc.page_content, "metadata":json.dumps(doc.metadata)})])
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

    return index

def chunk_and_index():
    """
    This function chunks our text data and indexes it in Pinecone.
    """
    
    # Load or create our dataset from text files
    contextDataset = load_or_generate_dataset_from_textfiles(TXT_PATH, DATASET_DIR, DATASET_CSV_TEXT_PATH, True)

    # Define our embedding settings
    embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Create a name to identify these specific settings
    settings_name = f"embeddings:{embedding_model.replace('/', '~')}"

    # Chunk the text, create embeddings, and load them into Pinecone
    knowledge_index = load_embeddings(contextDataset, embedding_model, "knowledge-index")

    print(f"Finished chunking text and indexing in Pinecone with settings: {settings_name}")

if __name__ == "__main__":
    chunk_and_index()
