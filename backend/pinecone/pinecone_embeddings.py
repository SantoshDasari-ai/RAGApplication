import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables from the .env file
load_dotenv()

# Load configuration from environment variables
PINECONE_KEY = os.getenv('PINECONE_KEY')
INDEX_NAME = os.getenv('INDEX_NAME')
NAMESPACE = os.getenv('NAMESPACE')  # Add this line
CHUNKED_TEXT_DIRECTORY = os.getenv('CHUNKED_TEXT_DIRECTORY')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')

class EmbeddingProcessor:
    def __init__(self, api_key, index_name, embedding_model, namespace):
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.model = SentenceTransformer(embedding_model)
        self.namespace = namespace  # Store namespace in the processor

    def embed_text(self, text):
        try:
            embedding = self.model.encode(text)
            if embedding is None:
                print(f"Embedding returned None for text: {text}")
            return embedding
        except Exception as e:
            print(f"Error embedding text: {str(e)}")
            return None

    def prepare_vector(self, text, text_file):
        embedding = self.embed_text(text)
        if embedding is None:
            return None
        vector_id = os.path.splitext(text_file)[0]
        metadata = {"text": text}
        print(f"Preparing vector for: {vector_id}")
        return {
            "id": vector_id,
            "values": embedding.tolist(),
            "metadata": metadata
        }

    def process_text_file(self, text_file, text_dir):
        try:
            text_path = os.path.join(text_dir, text_file)
            with open(text_path, 'r', encoding='utf-8') as file:
                text = file.read()
            vector = self.prepare_vector(text, text_file)
            if vector:
                upsert_response = self.index.upsert(vectors=[vector], namespace=self.namespace)  # Include namespace here
                print(f"Upsert response: {upsert_response}")
        except Exception as e:
            print(f"Error processing {text_file}: {str(e)}")
            return None

# Example usage
if __name__ == "__main__":
    processor = EmbeddingProcessor(PINECONE_KEY, INDEX_NAME, EMBEDDING_MODEL, NAMESPACE)  # Pass namespace here
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(processor.process_text_file, text_file, CHUNKED_TEXT_DIRECTORY)
                   for text_file in os.listdir(CHUNKED_TEXT_DIRECTORY) if text_file.endswith('.txt')]
        for future in as_completed(futures):
            future.result()
