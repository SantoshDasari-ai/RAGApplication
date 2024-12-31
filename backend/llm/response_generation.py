import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Dict

# Load environment variables from the .env file
load_dotenv()

# Set Google API Key for Gemini
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')
os.environ['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY')

class LLMProcessor:
    def __init__(self):
        google_api_key = os.getenv('GOOGLE_API_KEY')
        pinecone_key = os.getenv('PINECONE_API_KEY')
        llm_model = os.getenv('LLM_MODEL')
        embedding_model = os.getenv('EMBEDDING_MODEL')
        index_name = os.getenv('INDEX_NAME')
        namespace = os.getenv('NAMESPACE')

        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(model=llm_model, temperature=0.3, streaming=True)
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=pinecone_key)
        self.index = self.pc.Index(index_name)
        
        # Load embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Namespace
        self.namespace = namespace
        
        # Initialize vector store and retriever
        self.embeddings = CustomEmbeddings(self.embedding_model)
        self.vectorstore = PineconeVectorStore(index=self.index, embedding=self.embeddings, namespace=self.namespace)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})

    def embed_text(self, text):
        try:
            return self.embedding_model.encode(text)
        except Exception as e:
            print(f"Error embedding text: {str(e)}")
            return None

    def get_answer_with_sources(self, question: str, chat_history: List[Dict] = []):
        try:
            # Convert chat history to LangChain message format
            messages = []
            for entry in chat_history[-5:]:  # Limit to last 5 messages for context
                messages.extend([
                    HumanMessage(content=entry['question']),
                    AIMessage(content=entry['answer'])
                ])
            
            # Add current question
            messages.append(HumanMessage(content=question))

            # Embed the query
            query_embedding = self.embeddings.embed_query(question)
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding, 
                top_k=10, 
                namespace=self.namespace, 
                include_metadata=True
            )
            
            # Process relevant documents as before
            import json
            relevant_docs_new = [
                {
                    'text': doc['metadata'].get('text'),
                    'source': json.loads(doc['metadata'].get('metadata')).get('source'),
                    'page_numbers': (
                    lambda pages: pages.split('-')[0] if len(pages.split('-')) == 2 
                    and pages.split('-')[0] == pages.split('-')[1] else pages
                    )(json.loads(doc['metadata'].get('metadata')).get('page_numbers'))
                }
                for doc in results['matches']
            ]

            # Build context without chat history
            context = "\nExtracted documents:\n"
            context += "".join([
                f'\n<a href="#" class="context-link" data-context-id="{i+1}">Context ID: {i+1}</a>'
                f'\nSource: {doc["source"]}\nPage(s): {doc["page_numbers"]}\n{doc["text"]}'
                for i, doc in enumerate(relevant_docs_new)
            ])

            if context.strip():
                # Create the prompt with context
                final_prompt = self.get_prompt_template().format(
                    context=context, 
                    question=question
                )
                
                # Add the final prompt as a human message
                messages.append(HumanMessage(content=final_prompt))
                
                # Stream the response using the message history
                response_stream = self.llm.stream(messages)
                
                partial_response = ""
                for chunk in response_stream:
                    if chunk.content:
                        partial_response += chunk.content
                        yield partial_response
            else:
                yield "No relevant context found to answer the question."
        except Exception as e:
            print(f"Error: {e}")
            yield None
    
    def get_prompt_template(self):
        template = """
        You are a GenAI application helping provide answers based on the given context.
        Do not answer the question if you can't answer from the given context. 
        Context: {context}
        
        Instructions:
        1. Read the provided question carefully
        2. Use only the information from the provided context to answer
        3. If the answer isn't in the context, say so
        4. Provide clear, concise answers
        5. Use markdown formatting when needed (e.g., for tables, lists)
        6. Include relevant examples from the context when applicable
        7. If a source has multiple page numbers, list them on the same line
        
        Sources should be listed at the end in this format:
        Sources:  
        - Source Name 1: Page Numbers (comma-separated)  
        - Source Name 2: Page Numbers (comma-separated)  
        
        Question: {question}
        Answer:

        Sources: 
        """
        return ChatPromptTemplate.from_template(template)

# Custom Embeddings Class
class CustomEmbeddings:
    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()

    def embed_query(self, text):
        return self.model.encode(text).tolist()

# Initialize LLMProcessor and process a query
llm_processor = LLMProcessor()
