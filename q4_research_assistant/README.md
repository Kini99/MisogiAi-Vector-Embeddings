# 🔬 Advanced Research Assistant

A comprehensive research assistant that combines document analysis, web search, and AI-powered synthesis to provide cutting-edge research insights. Built with FastAPI, Streamlit, and powered by Gemini 2.0 Flash.

## 🚀 Features

### Core Capabilities
- **📄 PDF Document Processing**: Upload and analyze PDF documents with advanced text extraction and chunking
- **🌐 Real-time Web Search**: Integrate with multiple search engines (Serper, Bing) for live information
- **🔍 Hybrid Search**: Combine dense and sparse retrieval methods for optimal results
- **🤖 AI-Powered Synthesis**: Generate comprehensive responses using Gemini 2.0 Flash
- **📊 Source Verification**: Automatic credibility scoring and source attribution
- **📈 Response Quality Monitoring**: Track and analyze response quality metrics

### Advanced Search Methods
- **Dense Retrieval**: Semantic search using sentence transformers
- **Sparse Retrieval**: Keyword-based TF-IDF matching
- **Hybrid Retrieval**: Weighted combination of dense and sparse scores
- **Re-ranking**: Cross-encoder optimization for precision

### Production Features
- **User Session Management**: Track user interactions and search history
- **Response Quality Assessment**: Multi-dimensional feedback system
- **Analytics Dashboard**: Comprehensive usage analytics and insights
- **Caching & Optimization**: Redis-based caching for improved performance

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI       │    │   Vector Store  │
│   Frontend      │◄──►│   Backend       │◄──►│   (ChromaDB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Gemini 2.0    │
                       │   Flash LLM     │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Web Search    │
                       │   APIs          │
                       └─────────────────┘
```

## 📋 Requirements

### System Requirements
- Python 3.8+
- 8GB+ RAM (for model loading)
- 10GB+ disk space

### API Keys Required
- **Google API Key**: For Gemini 2.0 Flash
- **Serper API Key**: For web search (optional)
- **Bing API Key**: For alternative web search (optional)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd q4_research_assistant
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp env.example .env
```

Edit `.env` file with your API keys:
```env
# Gemini API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Web Search API Configuration
SERPER_API_KEY=your_serper_api_key_here
BING_API_KEY=your_bing_api_key_here

# Other configurations...
```

### 5. Initialize Database
```bash
python -c "from database import init_db; init_db()"
```

## 🚀 Usage

### Starting the Backend API
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Starting the Frontend
```bash
streamlit run streamlit_app.py
```

### API Documentation
Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Core Endpoints
- `POST /sessions` - Create user session
- `POST /documents/upload` - Upload PDF document
- `GET /documents` - List uploaded documents
- `POST /search` - Perform hybrid search
- `POST /web-search` - Web-only search
- `GET /search-history` - Get search history
- `POST /feedback` - Submit response feedback
- `DELETE /documents/{id}` - Delete document

### Health & Monitoring
- `GET /health` - System health check

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Gemini API key | Required |
| `SERPER_API_KEY` | Serper search API key | Optional |
| `BING_API_KEY` | Bing search API key | Optional |
| `DATABASE_URL` | Database connection string | SQLite |
| `CHROMA_DB_PATH` | Vector database path | `./chroma_db` |
| `MAX_FILE_SIZE` | Maximum file upload size | 10MB |
| `HYBRID_SEARCH_WEIGHT_DENSE` | Dense retrieval weight | 0.7 |
| `HYBRID_SEARCH_WEIGHT_SPARSE` | Sparse retrieval weight | 0.3 |

### Model Configuration
- **Embedding Model**: `all-MiniLM-L6-v2`
- **Re-ranking Model**: `ms-marco-MiniLM-L-12-v2`
- **LLM**: Gemini 2.0 Flash

## 🔍 Search Methods Comparison

### Dense Retrieval
- **Pros**: Semantic understanding, handles synonyms
- **Cons**: Requires pre-computed embeddings
- **Use Case**: Semantic similarity search

### Sparse Retrieval
- **Pros**: Fast, handles exact keyword matches
- **Cons**: No semantic understanding
- **Use Case**: Keyword-based search

### Hybrid Retrieval
- **Pros**: Best of both worlds, improved recall
- **Cons**: More complex, requires tuning
- **Use Case**: Production search systems

### Re-ranking
- **Pros**: Improves precision, better ranking
- **Cons**: Slower, requires additional model
- **Use Case**: Final result optimization

## 📊 Performance Optimization

### Caching Strategies
- **Embedding Cache**: Pre-compute document embeddings
- **Search Cache**: Cache frequent queries
- **Response Cache**: Cache similar responses

### Indexing Techniques
- **Vector Indexes**: FAISS for similarity search
- **Text Indexes**: Elasticsearch for keyword search
- **Hybrid Indexes**: Combine both approaches

### Production Tips
- Use approximate nearest neighbor search
- Implement connection pooling
- Monitor response times and quality
- Scale horizontally with load balancing

## 🧪 Testing

### Run Tests
```bash
pytest tests/
```

### Test Coverage
```bash
pytest --cov=. tests/
```

## 📈 Monitoring & Analytics

### Response Quality Metrics
- **Relevance Score**: Query-response alignment
- **Accuracy Score**: Factual correctness
- **Completeness Score**: Information coverage
- **Coherence Score**: Logical flow and structure

### System Metrics
- Response time tracking
- Search result counts
- User interaction patterns
- Error rate monitoring

## 🔒 Security Considerations

- API key management
- Input validation and sanitization
- Rate limiting
- User session management
- Secure file upload handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini team for the LLM
- Sentence Transformers for embeddings
- ChromaDB for vector storage
- FastAPI and Streamlit communities

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API docs at `/docs`

---

**Built with ❤️ for advanced research and knowledge discovery** 