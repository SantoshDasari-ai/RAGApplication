import os
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file if present
load_dotenv()

def get_llm(model_name = 'gemini-1.5-flash', provider='google', temperature=0.1, top_k=30):
    """
    Factory function to initialize and return an LLM instance based on the provider and model name.

    Args:
        model_name (str): Name of the model to use.
        provider (str): Provider of the LLM ('openai' or 'google').
        temperature (float): Sampling temperature for the LLM.
        top_k (int): Top-k sampling parameter (for Google models).

    Returns:
        An instance of an LLM.

    Raises:
        ValueError: If the provider is unsupported or API keys are missing.
    """
    if provider == 'openai':
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        if model_name in ["gpt-3.5-turbo", "gpt-4"]:
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                openai_api_key=openai_api_key
            )
        else:
            return OpenAI(
                model_name=model_name,
                temperature=temperature,
                openai_api_key=openai_api_key
            )
    elif provider == 'google':
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=google_api_key,
            temperature=temperature,
            top_k=top_k
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def call_llm(llm_instance, prompt):
    """
    Calls the LLM instance with the given prompt and returns the response.

    Args:
        llm_instance: The language model instance (e.g., READER_LLM_GEMINI).
        prompt (str): The formatted prompt to pass to the LLM.

    Returns:
        str: The LLM-generated response.
    """

    # Use the ChatGoogleGenerativeAI instance to generate a response
    
    
    try:
        messages = [("human", prompt)]
        response = llm_instance.invoke(messages)
        return response
        #return response.content if hasattr(response, 'content') else response
    except Exception as e:
        print(f"Error calling the LLM: {e}")
        return None

def stream_llm(llm_instance, prompt):
    """
    Calls the LLM instance with the given prompt and returns the response.

    Args:
        llm_instance: The language model instance (e.g., READER_LLM_GEMINI).
        prompt (str): The formatted prompt to pass to the LLM.

    Returns:
        str: The LLM-generated response.
    """

    # Use the ChatGoogleGenerativeAI instance to generate a response
    
    
    try:
        messages = [("human", prompt)]
        response_stream = llm_instance.stream(messages)
        partial_response = ""
        for chunk in response_stream:
            if chunk.content:
                partial_response += chunk.content
                yield partial_response
    except Exception as e:
        print(f"Error calling the LLM: {e}")
        return None    


