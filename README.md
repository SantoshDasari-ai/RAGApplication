# RAG Knowledge Base Application

A modern knowledge management system built with RAG (Retrieval-Augmented Generation) technology that helps organizations efficiently organize, search, and retrieve information.

## Features

- 🔍 Semantic search powered by Pinecone vector database
- 🤖 Advanced question answering using Google's Gemini Pro
- 📚 Document ingestion and processing
- 💬 Interactive chat interface
- 🔄 Context-aware conversations
- 🎯 Precise information retrieval

## Prerequisites

- Python 3.8 or higher
- Pinecone API key (Sign up at [Pinecone](https://www.pinecone.io/))
- Google API key for Gemini Pro (Get from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/rag-knowledge-base.git
   cd rag-knowledge-base
   ```

2. Set up environment:

   ```bash
   # For Unix/MacOS
   chmod +x install.sh
   ./install.sh

   # For Windows
   # Run these commands manually:
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:

   - Copy `.env.example` to `.env`
   - Add your API keys and configurations:

````plaintext
    GOOGLE_API_KEY=your_google_api_key_here
    PINECONE_API_KEY=your_pinecone_api_key_here
    PINECONE_ENVIRONMENT=your_pinecone_environment
    ```

4. Run the application:

  ```bash
  python app.py
````

5.Open your browser and navigate to:

```plaintext
http://localhost:5000
```

## Adding Your Knowledge Base

1. Create a `data/raw_text` directory
2. Add your PDF or text documents to this directory
3. Run the indexing script:
   ```bash
   python backend/pinecone/extract_and_chunk.py
   ```

## Customizing the System

### Modifying the RAG Prompt

The system prompt defines how the AI processes and responds to questions. You can customize it in `backend/llm/response_generation.py`:

1. Locate the `get_prompt_template` method
2. Modify the template string to:
   - Change the AI's persona
   - Adjust response formatting
   - Add domain-specific instructions
   - Customize source citation format

### Adjusting Document Processing

Customize how documents are processed in `backend/pinecone/extract_and_chunk.py`:

1. Modify chunk size and overlap
2. Adjust text extraction rules
3. Customize metadata extraction
4. Change document type handling

## Development

### Project Structure

rag-knowledge-base/
├── backend/
│ ├── llm/ # LLM integration
│ └── pinecone/ # Vector database operations
├── data/
│ └── raw_text/ # Place your documents here
├── static/ # Frontend assets
├── templates/ # HTML templates
├── app.py # Main Flask application
└── requirements.txt # Python dependencies

### Key Components

- `app.py`: Main Flask application
- `backend/llm/response_generation.py`: RAG implementation
- `backend/pinecone/extract_and_chunk.py`: Document processing
- `templates/index.html`: Chat interface
- `static/js/chat.js`: Frontend logic

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Apache License Version 2.0 - See LICENSE file for details
