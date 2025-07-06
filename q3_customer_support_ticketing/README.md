# 🎫 Intelligent Customer Support System

A comprehensive RAG-powered customer support system that automatically categorizes incoming tickets, generates smart responses, and provides intelligent escalation logic using Google Gemini 2.0 Flash.

## 🚀 Features

### Core Functionality
- **Automatic Ticket Categorization**: AI-powered classification into 8 categories (shipping, payment, returns, etc.)
- **Smart Response Generation**: Context-aware responses based on historical tickets and knowledge base
- **Priority Assignment**: Intelligent priority scoring based on content analysis and sentiment
- **Sentiment Analysis**: Real-time customer sentiment detection
- **Confidence Scoring**: AI confidence metrics for response quality assessment
- **Escalation Logic**: Automatic escalation triggers for complex cases

### Advanced Features
- **Multi-source RAG Pipeline**: Combines historical tickets, knowledge base, and company documentation
- **Vector Similarity Search**: Finds similar past tickets for context-aware responses
- **Customer History Integration**: Personalized responses based on customer history
- **Real-time Analytics**: Dashboard with ticket statistics and performance metrics
- **Knowledge Base Management**: Dynamic knowledge base for company policies and procedures

### Technical Implementation
- **FastAPI Backend**: RESTful API with automatic documentation
- **Streamlit Frontend**: Interactive web interface for agents and customers
- **ChromaDB Vector Store**: Efficient vector embeddings for similarity search
- **SQLite Database**: Persistent storage for tickets, customers, and knowledge base
- **Google Gemini 2.0 Flash**: State-of-the-art LLM for analysis and response generation

## 📋 Requirements

- Python 3.8+
- Google Gemini API key
- 4GB+ RAM (for vector operations)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   cd q3_customer_support_ticketing
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env and add your Google Gemini API key
   ```

4. **Initialize the database and sample data**
   ```bash
   # Start the API server
   python api.py
   
   # In another terminal, initialize sample data
   python init_sample_data.py
   ```

## 🚀 Quick Start

### 1. Start the API Server
```bash
python api.py
```
The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 2. Start the Streamlit Frontend
```bash
streamlit run streamlit_app.py
```
The web interface will be available at `http://localhost:8501`

### 3. Access the System
- **Customer Portal**: Submit tickets and view status
- **Agent Dashboard**: Manage tickets, view analytics, and handle escalations
- **Knowledge Base**: Manage company policies and procedures

## 📊 System Architecture

### RAG Pipeline
```
Customer Ticket → Analysis → Categorization → Similarity Search → Response Generation → Confidence Scoring
     ↓              ↓            ↓              ↓                ↓                    ↓
  Preprocessing  Sentiment   Priority      Vector Store    Knowledge Base      Escalation Logic
```

### Data Flow
1. **Ticket Ingestion**: Customer submits ticket via web interface or API
2. **AI Analysis**: Gemini analyzes content for category, priority, sentiment, and tags
3. **Similarity Search**: ChromaDB finds similar historical tickets
4. **Response Generation**: Multi-source RAG combines similar tickets and knowledge base
5. **Confidence Assessment**: AI evaluates response quality and suggests escalation if needed
6. **Storage**: Ticket and analysis stored in SQLite with vector embeddings

## 🎯 Use Cases

### E-commerce Support Scenarios

1. **"My order hasn't arrived"**
   - Auto-categorize: `shipping_issue`
   - Priority: `high`
   - Response: Shipping policy + tracking assistance
   - Similar tickets: Past delivery issues

2. **"I want to return this product"**
   - Auto-categorize: `product_return`
   - Priority: `medium`
   - Response: Return policy + process instructions
   - Knowledge base: Return policy reference

3. **"Payment failed but money deducted"**
   - Auto-categorize: `payment_problem`
   - Priority: `urgent`
   - Response: Investigation process + refund timeline
   - Escalation: High priority financial issue

4. **"Product damaged during delivery"**
   - Auto-categorize: `damaged_product`
   - Priority: `high`
   - Response: Replacement process + photo requirements
   - Similar tickets: Past damage claims

## 📁 Project Structure

```
q3_customer_support_ticketing/
├── api.py                 # FastAPI backend server
├── streamlit_app.py       # Streamlit frontend application
├── rag_engine.py          # Core RAG pipeline and AI logic
├── models.py              # Pydantic data models
├── database.py            # SQLAlchemy database configuration
├── init_sample_data.py    # Sample data initialization
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional (with defaults)
DATABASE_URL=sqlite:///./customer_support.db
CHROMA_PERSIST_DIRECTORY=./chroma_db
MAX_SIMILAR_TICKETS=5
CONFIDENCE_THRESHOLD=0.7
ESCALATION_THRESHOLD=0.3
```

### API Endpoints

#### Ticket Management
- `POST /tickets/` - Create new ticket with AI analysis
- `GET /tickets/` - List tickets with filtering
- `GET /tickets/{id}` - Get specific ticket
- `PUT /tickets/{id}` - Update ticket
- `POST /tickets/{id}/resolve` - Resolve ticket
- `POST /tickets/{id}/escalate` - Escalate ticket

#### Customer Management
- `POST /customers/` - Create customer
- `GET /customers/` - List customers
- `GET /customers/{email}/tickets` - Get customer tickets

#### AI Analysis
- `POST /analyze-ticket/` - Analyze ticket content
- `POST /generate-response/` - Generate AI response
- `GET /similar-tickets/` - Find similar tickets

#### Analytics
- `GET /statistics/` - System statistics
- `GET /dashboard/` - Dashboard data

## 🎨 Frontend Features

### Customer Portal
- **Ticket Submission**: User-friendly form with real-time AI analysis preview
- **Ticket Tracking**: View ticket status and responses
- **Customer History**: Access to past tickets and resolutions

### Agent Dashboard
- **Ticket Management**: Filter, sort, and manage tickets
- **Real-time Analytics**: Charts and metrics for performance monitoring
- **Response Generation**: AI-assisted response creation
- **Escalation Handling**: Tools for managing complex cases

### Analytics Dashboard
- **Performance Metrics**: Response times, resolution rates, satisfaction scores
- **Category Analysis**: Distribution and trends by ticket type
- **Priority Management**: High-priority ticket tracking
- **Knowledge Base Insights**: Usage analytics and effectiveness

## 🔍 Technical Details

### AI Models Used
- **Google Gemini 2.0 Flash**: Primary LLM for analysis and response generation
- **TextBlob**: Sentiment analysis
- **ChromaDB**: Vector similarity search

### Database Schema
- **Tickets**: Main ticket data with AI analysis results
- **Customers**: Customer information and history
- **Knowledge Base**: Company policies and procedures
- **Ticket History**: Audit trail of ticket changes

### Vector Embeddings
- **Ticket Embeddings**: Combined subject + description for similarity search
- **Knowledge Base Embeddings**: Policy and procedure content
- **Similarity Metrics**: Cosine similarity for finding related content

## 🧪 Testing

### Sample Data
The system includes comprehensive sample data:
- 5 sample customers
- 10 historical tickets with resolutions
- 5 knowledge base entries
- Various ticket categories and priorities

### Test Scenarios
1. **New Ticket Submission**: Test automatic categorization and response generation
2. **Similar Ticket Search**: Verify similarity matching with historical data
3. **Escalation Logic**: Test confidence scoring and escalation triggers
4. **Knowledge Base Integration**: Verify policy reference in responses

## 📈 Performance Metrics

### Response Quality
- **Confidence Scoring**: AI confidence in generated responses
- **Similarity Matching**: Accuracy of finding relevant historical tickets
- **Categorization Accuracy**: Precision of automatic ticket classification

### System Performance
- **Response Time**: Average time for ticket analysis and response generation
- **Throughput**: Number of tickets processed per hour
- **Escalation Rate**: Percentage of tickets requiring human intervention

## 🔒 Security Considerations

- **API Key Management**: Secure storage of Gemini API key
- **Data Privacy**: Customer information protection
- **Input Validation**: Sanitization of user inputs
- **Rate Limiting**: Protection against API abuse

## 🚀 Deployment

### Local Development
```bash
# Start API server
python api.py

# Start Streamlit app
streamlit run streamlit_app.py

# Initialize sample data
python init_sample_data.py
```

### Production Deployment
1. **Environment Setup**: Configure production environment variables
2. **Database Migration**: Set up production database
3. **API Deployment**: Deploy FastAPI with Gunicorn/Uvicorn
4. **Frontend Deployment**: Deploy Streamlit app
5. **Monitoring**: Set up logging and monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `http://localhost:8000/docs`
2. Review the sample data and test scenarios
3. Check the logs for error messages
4. Verify your Google Gemini API key is valid

## 🎯 Future Enhancements

- **Multi-language Support**: Internationalization for global support
- **Voice Integration**: Speech-to-text for phone support
- **Advanced Analytics**: Machine learning for trend prediction
- **Integration APIs**: Connect with CRM and e-commerce platforms
- **Mobile App**: Native mobile application for agents
- **Advanced NLP**: More sophisticated text analysis and understanding 