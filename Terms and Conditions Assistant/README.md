# Terms and Conditions Assistant

An AI-powered assistant that provides intelligent answers to questions about Terms and Conditions documents using LLMs and semantic search.

## Overview

The Terms and Conditions Assistant is a FastAPI-based application that helps users quickly find answers to their questions about T&C documents. It leverages:

- **Semantic Search**: FAISS vector embeddings for intelligent document retrieval
- **AI Language Models**: Groq's Mixtral model for generating natural language answers
- **Async Processing**: Celery task queue for non-blocking document processing
- **Web Scraping**: Automatic extraction of T&C text from URLs

## Features

- 🔗 **URL-based Document Upload**: Fetch T&C documents directly from URLs
- 🤖 **AI-Powered Q&A**: Ask natural language questions and get relevant answers
- ⚡ **Async Processing**: Background task processing with Celery and Redis
- 📚 **Vector Embedding**: Semantic search using FAISS and HuggingFace embeddings
- 🐳 **Docker Support**: Full containerization for easy deployment
- ☁️ **Cloud Ready**: Pre-configured for Fly.io deployment
- 🧪 **Test Coverage**: pytest-based testing framework

## Architecture

```
FastAPI Application (main.py)
    ├── POST /upload_tos - Upload and process T&C documents
    └── POST /ask - Ask questions about T&C

Document Processing (tasks.py)
    └── Celery tasks for async vectorization

Language Model Pipeline (langchain_qna.py)
    ├── LLM: Groq Mixtral 8x7b
    ├── Embeddings: HuggingFace sentence-transformers
    └── Vector Store: FAISS

Data Storage
    ├── PostgreSQL - Document metadata
    ├── FAISS - Vector embeddings
    └── Redis - Task queue
```

## Prerequisites

- Python 3.10+
- PostgreSQL (or compatible database)
- Redis (for Celery task queue)
- Groq API key

## Installation

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Term and Conditions Assistant"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Required environment variables:
   ```
   GROQ_API_KEY=your_groq_api_key
   BROKER_URL=redis://localhost:6379/0
   DATABASE_URL=postgresql://user:password@localhost/tandc
   ```

5. **Start Redis** (for Celery)
   ```bash
   redis-cli
   ```

6. **Start the application**
   ```bash
   # Start the FastAPI server
   uvicorn app.main:app --reload --port 8000
   
   # In another terminal, start the Celery worker
   celery -A app.tasks worker --loglevel=info
   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **For Fly.io deployment**
   ```bash
   flyctl deploy
   ```

## API Endpoints

### 1. Upload Terms & Conditions

**Endpoint**: `POST /upload_tos`

**Request**:
```json
{
  "url": "https://example.com/terms-and-conditions"
}
```

**Response**:
```json
{
  "message": "TOS updated and queued for processing."
}
```

The application automatically:
- Extracts the domain from the URL
- Fetches the T&C document
- Detects if content has changed
- Queues it for vector embedding processing

### 2. Ask Questions

**Endpoint**: `POST /ask`

**Request**:
```json
{
  "domain": "example.com",
  "question": "What is the refund policy?"
}
```

**Response**:
```json
{
  "answer": "Based on the terms and conditions, the refund policy states..."
}
```

## Project Structure

```
├── app/
│   ├── main.py              # FastAPI application and endpoints
│   ├── langchain_qna.py     # LLM and embedding pipeline
│   ├── tasks.py             # Celery task definitions
│   ├── utils.py             # Utility functions
│   ├── celery_worker.py     # Celery worker configuration
│   └── tests/
│       └── test_main.py     # Unit tests
├── Docker-compose.yml       # Docker services orchestration
├── Dockerfile               # Application container configuration
├── fly.toml                 # Fly.io deployment configuration
├── pytest.ini               # pytest configuration
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Key Dependencies

- **FastAPI**: Modern web framework for building APIs
- **LangChain**: LLM orchestration and document processing
- **Groq**: LLM API provider (Mixtral 8x7b model)
- **FAISS**: Vector similarity search and clustering
- **HuggingFace**: Pre-trained embedding models
- **Celery**: Distributed task queue
- **Redis**: Message broker for Celery
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Data persistence
- **BeautifulSoup4**: HTML parsing
- **PyMuPDF**: PDF text extraction
- **pytest**: Testing framework

## Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```

Run specific test file:
```bash
pytest app/tests/test_main.py -v
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Groq Configuration
GROQ_API_KEY=your_api_key_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/tandc

# Redis/Celery Configuration
BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Application
DEBUG=False
LOG_LEVEL=INFO
```

## Development

### Adding New Features

1. Update dependencies in `requirements.txt` if needed
2. Implement features in the `app/` directory
3. Add tests in `app/tests/`
4. Update this README with new endpoints/features

### Code Quality

- Follow PEP 8 style guidelines
- Write unit tests for new functionality
- Use type hints in function signatures
- Keep functions focused and small

## Deployment

### Fly.io

The project is pre-configured for Fly.io deployment:

```bash
# Login to Fly.io
flyctl auth login

# Deploy
flyctl deploy

# View logs
flyctl logs

# Scale resources
flyctl scale vm memory 2048
```

### Docker

Build and run locally:
```bash
docker build -t tandc .
docker run -p 8000:8000 tandc
```

Or use Docker Compose for full stack:
```bash
docker-compose up
```

## Performance Optimization

- **Vector Embeddings**: Pre-computed FAISS indexes are cached on disk
- **Async Processing**: Long-running document processing happens in background Celery tasks
- **Change Detection**: Documents are only re-processed if content has changed
- **GPU Support**: FAISS and embeddings support GPU acceleration (modify `device` parameter in `langchain_qna.py`)

## Troubleshooting

**Redis Connection Error**: Ensure Redis is running
```bash
redis-cli ping  # Should return PONG
```

**Database Connection Error**: Check PostgreSQL is running and `DATABASE_URL` is correct

**Groq API Error**: Verify `GROQ_API_KEY` is set correctly

**FAISS Index Not Found**: Ensure documents are uploaded via `/upload_tos` endpoint before asking questions

## License

[Specify your license here]

## Contributing

[Contributing guidelines here]

## Support

For issues, questions, or feature requests, please open an issue in the repository.
