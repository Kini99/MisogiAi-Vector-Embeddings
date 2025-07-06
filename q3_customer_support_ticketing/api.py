from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from database import get_db, create_tables, DBTicket, DBCustomer, DBKnowledgeBase, DBTicketHistory
from models import (
    TicketCreate, TicketResponse, TicketUpdate, CustomerCreate, CustomerResponse,
    KnowledgeBaseEntry, TicketAnalysis, AutoResponse
)
from rag_engine import RAGEngine

# Initialize FastAPI app
app = FastAPI(
    title="Intelligent Customer Support System",
    description="RAG-powered customer support system with automatic categorization and response generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG engine
rag_engine = RAGEngine()

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Helper functions
def db_ticket_to_response(db_ticket: DBTicket) -> TicketResponse:
    """Convert database ticket to response model"""
    return TicketResponse(
        id=db_ticket.id,
        subject=db_ticket.subject,
        description=db_ticket.description,
        customer_email=db_ticket.customer_email,
        customer_name=db_ticket.customer_name,
        priority=db_ticket.priority,
        category=db_ticket.category,
        status=db_ticket.status,
        tags=json.loads(db_ticket.tags) if db_ticket.tags else [],
        sentiment=db_ticket.sentiment,
        confidence_score=db_ticket.confidence_score,
        auto_response=db_ticket.auto_response,
        similar_tickets=json.loads(db_ticket.similar_tickets) if db_ticket.similar_tickets else None,
        created_at=db_ticket.created_at,
        updated_at=db_ticket.updated_at
    )

# Ticket endpoints
@app.post("/tickets/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    """Create a new support ticket with automatic analysis"""
    
    # Analyze ticket using RAG engine
    analysis = rag_engine.analyze_ticket(ticket.subject, ticket.description)
    
    # Find similar tickets
    similar_tickets = rag_engine.find_similar_tickets(ticket.subject, ticket.description)
    
    # Generate auto-response
    auto_response = rag_engine.generate_response(
        ticket.subject, 
        ticket.description, 
        analysis.category, 
        similar_tickets
    )
    
    # Create database ticket
    db_ticket = DBTicket(
        subject=ticket.subject,
        description=ticket.description,
        customer_email=ticket.customer_email,
        customer_name=ticket.customer_name,
        priority=analysis.priority,
        category=analysis.category,
        tags=json.dumps(analysis.tags),
        sentiment=analysis.sentiment,
        confidence_score=auto_response.confidence_score,
        auto_response=auto_response.response_text,
        similar_tickets=json.dumps([t.dict() for t in auto_response.similar_tickets])
    )
    
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    # Add to vector store for future similarity searches
    rag_engine.add_ticket_to_vector_store(
        db_ticket.id, 
        ticket.subject, 
        ticket.description, 
        analysis.category.value
    )
    
    # Add to ticket history
    history_entry = DBTicketHistory(
        ticket_id=db_ticket.id,
        action="ticket_created",
        description="Ticket created with automatic analysis and response generation"
    )
    db.add(history_entry)
    db.commit()
    
    return db_ticket_to_response(db_ticket)

@app.get("/tickets/", response_model=List[TicketResponse])
async def get_tickets(
    skip: int = 0, 
    limit: int = 100, 
    status_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all tickets with optional filtering"""
    
    query = db.query(DBTicket)
    
    if status_filter:
        query = query.filter(DBTicket.status == status_filter)
    if category_filter:
        query = query.filter(DBTicket.category == category_filter)
    if priority_filter:
        query = query.filter(DBTicket.priority == priority_filter)
    
    tickets = query.offset(skip).limit(limit).all()
    return [db_ticket_to_response(ticket) for ticket in tickets]

@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Get a specific ticket by ID"""
    
    ticket = db.query(DBTicket).filter(DBTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return db_ticket_to_response(ticket)

@app.put("/tickets/{ticket_id}", response_model=TicketResponse)
async def update_ticket(ticket_id: int, ticket_update: TicketUpdate, db: Session = Depends(get_db)):
    """Update a ticket"""
    
    db_ticket = db.query(DBTicket).filter(DBTicket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update fields
    update_data = ticket_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ticket, field, value)
    
    db_ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_ticket)
    
    # Add to history
    history_entry = DBTicketHistory(
        ticket_id=ticket_id,
        action="ticket_updated",
        description=f"Ticket updated: {', '.join(update_data.keys())}"
    )
    db.add(history_entry)
    db.commit()
    
    return db_ticket_to_response(db_ticket)

@app.post("/tickets/{ticket_id}/resolve", response_model=TicketResponse)
async def resolve_ticket(ticket_id: int, resolution: str, db: Session = Depends(get_db)):
    """Mark a ticket as resolved with resolution details"""
    
    db_ticket = db.query(DBTicket).filter(DBTicket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db_ticket.status = "resolved"
    db_ticket.resolution = resolution
    db_ticket.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_ticket)
    
    # Add to history
    history_entry = DBTicketHistory(
        ticket_id=ticket_id,
        action="ticket_resolved",
        description=f"Ticket resolved: {resolution[:100]}..."
    )
    db.add(history_entry)
    db.commit()
    
    return db_ticket_to_response(db_ticket)

@app.post("/tickets/{ticket_id}/escalate", response_model=TicketResponse)
async def escalate_ticket(ticket_id: int, escalation_reason: str, db: Session = Depends(get_db)):
    """Escalate a ticket to human agent"""
    
    db_ticket = db.query(DBTicket).filter(DBTicket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db_ticket.status = "escalated"
    db_ticket.agent_notes = escalation_reason
    db_ticket.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_ticket)
    
    # Add to history
    history_entry = DBTicketHistory(
        ticket_id=ticket_id,
        action="ticket_escalated",
        description=f"Ticket escalated: {escalation_reason}"
    )
    db.add(history_entry)
    db.commit()
    
    return db_ticket_to_response(db_ticket)

# Customer endpoints
@app.post("/customers/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer"""
    
    # Check if customer already exists
    existing_customer = db.query(DBCustomer).filter(DBCustomer.email == customer.email).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer with this email already exists")
    
    db_customer = DBCustomer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    return CustomerResponse(
        id=db_customer.id,
        email=db_customer.email,
        name=db_customer.name,
        phone=db_customer.phone,
        address=db_customer.address,
        total_tickets=0,
        created_at=db_customer.created_at,
        updated_at=db_customer.updated_at
    )

@app.get("/customers/", response_model=List[CustomerResponse])
async def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all customers"""
    
    customers = db.query(DBCustomer).offset(skip).limit(limit).all()
    
    # Add ticket count for each customer
    customer_responses = []
    for customer in customers:
        ticket_count = db.query(DBTicket).filter(DBTicket.customer_email == customer.email).count()
        customer_responses.append(CustomerResponse(
            id=customer.id,
            email=customer.email,
            name=customer.name,
            phone=customer.phone,
            address=customer.address,
            total_tickets=ticket_count,
            created_at=customer.created_at,
            updated_at=customer.updated_at
        ))
    
    return customer_responses

@app.get("/customers/{customer_email}/tickets", response_model=List[TicketResponse])
async def get_customer_tickets(customer_email: str, db: Session = Depends(get_db)):
    """Get all tickets for a specific customer"""
    
    tickets = db.query(DBTicket).filter(DBTicket.customer_email == customer_email).all()
    return [db_ticket_to_response(ticket) for ticket in tickets]

# Knowledge base endpoints
@app.post("/knowledge-base/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_knowledge_entry(entry: KnowledgeBaseEntry, db: Session = Depends(get_db)):
    """Add a new knowledge base entry"""
    
    db_entry = DBKnowledgeBase(
        title=entry.title,
        content=entry.content,
        category=entry.category,
        tags=json.dumps(entry.tags)
    )
    
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    # Add to vector store
    rag_engine.knowledge_collection.add(
        documents=[entry.content],
        metadatas=[{"title": entry.title, "category": entry.category}],
        ids=[f"kb_{db_entry.id}"]
    )
    
    return {"message": "Knowledge base entry added successfully", "id": db_entry.id}

@app.get("/knowledge-base/", response_model=List[dict])
async def get_knowledge_entries(db: Session = Depends(get_db)):
    """Get all knowledge base entries"""
    
    entries = db.query(DBKnowledgeBase).all()
    return [
        {
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "category": entry.category,
            "tags": json.loads(entry.tags) if entry.tags else [],
            "created_at": entry.created_at
        }
        for entry in entries
    ]

# Analysis and RAG endpoints
@app.post("/analyze-ticket/", response_model=TicketAnalysis)
async def analyze_ticket_content(subject: str, description: str):
    """Analyze ticket content without creating a ticket"""
    
    return rag_engine.analyze_ticket(subject, description)

@app.post("/generate-response/", response_model=AutoResponse)
async def generate_response(subject: str, description: str, category: str):
    """Generate response for a ticket"""
    
    # Find similar tickets
    similar_tickets = rag_engine.find_similar_tickets(subject, description)
    
    # Generate response
    return rag_engine.generate_response(subject, description, TicketCategory(category), similar_tickets)

@app.get("/similar-tickets/")
async def find_similar_tickets(subject: str, description: str, limit: int = 5):
    """Find similar historical tickets"""
    
    similar_tickets = rag_engine.find_similar_tickets(subject, description, limit)
    return [ticket.dict() for ticket in similar_tickets]

# Statistics and dashboard endpoints
@app.get("/statistics/")
async def get_statistics():
    """Get system statistics"""
    
    return rag_engine.get_ticket_statistics()

@app.get("/dashboard/")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Get dashboard data for the support system"""
    
    # Get basic statistics
    stats = rag_engine.get_ticket_statistics()
    
    # Get recent tickets
    recent_tickets = db.query(DBTicket).order_by(DBTicket.created_at.desc()).limit(10).all()
    
    # Get tickets by status
    status_counts = {}
    for status in ["open", "in_progress", "resolved", "closed", "escalated"]:
        count = db.query(DBTicket).filter(DBTicket.status == status).count()
        status_counts[status] = count
    
    # Get average response time (simplified)
    resolved_tickets = db.query(DBTicket).filter(DBTicket.status == "resolved").all()
    avg_response_time = 0
    if resolved_tickets:
        total_time = 0
        for ticket in resolved_tickets:
            if ticket.updated_at and ticket.created_at:
                time_diff = (ticket.updated_at - ticket.created_at).total_seconds() / 3600  # hours
                total_time += time_diff
        avg_response_time = total_time / len(resolved_tickets)
    
    return {
        "statistics": stats,
        "recent_tickets": [db_ticket_to_response(ticket).dict() for ticket in recent_tickets],
        "status_distribution": status_counts,
        "average_response_time_hours": round(avg_response_time, 2)
    }

# Health check endpoint
@app.get("/health/")
async def health_check():
    """Health check endpoint"""
    
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 