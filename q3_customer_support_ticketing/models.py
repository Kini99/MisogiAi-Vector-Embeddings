from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"

class TicketCategory(str, Enum):
    SHIPPING_ISSUE = "shipping_issue"
    PAYMENT_PROBLEM = "payment_problem"
    PRODUCT_RETURN = "product_return"
    TECHNICAL_SUPPORT = "technical_support"
    ACCOUNT_ISSUE = "account_issue"
    GENERAL_INQUIRY = "general_inquiry"
    REFUND_REQUEST = "refund_request"
    DAMAGED_PRODUCT = "damaged_product"

class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class TicketBase(BaseModel):
    subject: str = Field(..., description="Ticket subject line")
    description: str = Field(..., description="Detailed ticket description")
    customer_email: str = Field(..., description="Customer email address")
    customer_name: Optional[str] = Field(None, description="Customer name")
    priority: Optional[TicketPriority] = Field(TicketPriority.MEDIUM, description="Ticket priority")
    category: Optional[TicketCategory] = Field(None, description="Auto-categorized ticket type")
    tags: Optional[List[str]] = Field(default_factory=list, description="Auto-generated tags")
    sentiment: Optional[SentimentType] = Field(None, description="Customer sentiment analysis")

class TicketCreate(TicketBase):
    pass

class TicketResponse(BaseModel):
    id: int
    subject: str
    description: str
    customer_email: str
    customer_name: Optional[str]
    priority: TicketPriority
    category: Optional[TicketCategory]
    status: TicketStatus
    tags: List[str]
    sentiment: Optional[SentimentType]
    confidence_score: Optional[float] = Field(None, description="AI confidence in auto-response")
    auto_response: Optional[str] = Field(None, description="Generated auto-response")
    similar_tickets: Optional[List[Dict[str, Any]]] = Field(None, description="Similar historical tickets")
    created_at: datetime
    updated_at: datetime

class TicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    status: Optional[TicketStatus] = None
    tags: Optional[List[str]] = None
    agent_notes: Optional[str] = None
    resolution: Optional[str] = None

class CustomerBase(BaseModel):
    email: str = Field(..., description="Customer email")
    name: Optional[str] = Field(None, description="Customer name")
    phone: Optional[str] = Field(None, description="Customer phone number")
    address: Optional[str] = Field(None, description="Customer address")

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    total_tickets: int
    created_at: datetime
    updated_at: datetime

class KnowledgeBaseEntry(BaseModel):
    title: str = Field(..., description="Knowledge base entry title")
    content: str = Field(..., description="Knowledge base content")
    category: str = Field(..., description="Knowledge base category")
    tags: List[str] = Field(default_factory=list, description="Knowledge base tags")

class SimilarTicket(BaseModel):
    ticket_id: int
    subject: str
    description: str
    similarity_score: float
    resolution: Optional[str] = None
    category: Optional[str] = None

class AutoResponse(BaseModel):
    response_text: str
    confidence_score: float
    similar_tickets: List[SimilarTicket]
    knowledge_base_references: List[str]
    suggested_escalation: bool = False

class TicketAnalysis(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    sentiment: SentimentType
    tags: List[str]
    confidence_score: float
    escalation_needed: bool 