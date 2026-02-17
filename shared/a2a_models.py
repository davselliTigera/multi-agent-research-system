"""
a2a_models.py (FIXED)
Agent-to-Agent (A2A) Protocol Implementation
Based on Google's A2A specification
"""

from typing import Optional, Dict, Any, List, Literal, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """A2A Message Types"""
    ACTION_REQUEST = "ActionRequest"
    ACTION_RESPONSE = "ActionResponse"
    CAPABILITY_REQUEST = "CapabilityRequest"
    CAPABILITY_RESPONSE = "CapabilityResponse"
    ERROR = "Error"
    STATUS_UPDATE = "StatusUpdate"


class MessageStatus(str, Enum):
    """Message processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class A2ACapability(BaseModel):
    """Agent capability description"""
    name: str = Field(description="Action name")
    description: str = Field(description="What this action does")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Expected parameters")
    returns: Dict[str, Any] = Field(default_factory=dict, description="Return value description")


class A2AAgent(BaseModel):
    """Agent identity and metadata"""
    id: str = Field(description="Unique agent identifier (e.g., agent://topic-refiner)")
    name: str = Field(description="Human-readable agent name")
    version: str = Field(default="1.0.0")
    capabilities: List[A2ACapability] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class A2AContent(BaseModel):
    """Base content structure"""
    type: str = Field(alias="@type")
    
    class Config:
        populate_by_name = True


class A2AActionRequest(A2AContent):
    """Request to perform an action"""
    type: Literal["ActionRequest"] = Field(default="ActionRequest", alias="@type")
    action: str = Field(description="Action name to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class A2AActionResponse(A2AContent):
    """Response from action execution"""
    type: Literal["ActionResponse"] = Field(default="ActionResponse", alias="@type")
    action: str = Field(description="Action that was executed")
    result: Dict[str, Any] = Field(description="Action result")
    status: MessageStatus = Field(description="Execution status")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class A2ACapabilityRequest(A2AContent):
    """Request agent capabilities"""
    type: Literal["CapabilityRequest"] = Field(default="CapabilityRequest", alias="@type")


class A2ACapabilityResponse(A2AContent):
    """Response with agent capabilities"""
    type: Literal["CapabilityResponse"] = Field(default="CapabilityResponse", alias="@type")
    capabilities: List[A2ACapability]
    agent: A2AAgent


class A2AError(A2AContent):
    """Error message"""
    type: Literal["Error"] = Field(default="Error", alias="@type")
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class A2AStatusUpdate(A2AContent):
    """Status update during long-running operations"""
    type: Literal["StatusUpdate"] = Field(default="StatusUpdate", alias="@type")
    status: MessageStatus
    progress: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    message: Optional[str] = None


# Union type for content with discriminator
A2AContentUnion = Union[
    A2AActionRequest,
    A2AActionResponse,
    A2ACapabilityRequest,
    A2ACapabilityResponse,
    A2AError,
    A2AStatusUpdate
]


class A2AMessage(BaseModel):
    """
    A2A Protocol Message
    Standard message format for agent-to-agent communication
    """
    type: Literal["Message"] = Field(default="Message", alias="@type")
    id: str = Field(description="Unique message ID")
    to: str = Field(description="Recipient agent ID (e.g., agent://topic-refiner)")
    from_agent: str = Field(alias="from", description="Sender agent ID")
    content: A2AContentUnion = Field(description="Message content")
    reply_to: Optional[str] = Field(default=None, description="ID of message being replied to")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('content', mode='before')
    @classmethod
    def parse_content(cls, v):
        """Parse content based on @type discriminator"""
        if isinstance(v, dict):
            content_type = v.get('@type') or v.get('type')
            
            if content_type == 'ActionRequest':
                return A2AActionRequest(**v)
            elif content_type == 'ActionResponse':
                return A2AActionResponse(**v)
            elif content_type == 'CapabilityRequest':
                return A2ACapabilityRequest(**v)
            elif content_type == 'CapabilityResponse':
                return A2ACapabilityResponse(**v)
            elif content_type == 'Error':
                return A2AError(**v)
            elif content_type == 'StatusUpdate':
                return A2AStatusUpdate(**v)
            else:
                raise ValueError(f"Unknown content type: {content_type}")
        
        return v
    
    def model_dump(self, **kwargs):
        """Override model_dump to properly serialize Union content types"""
        # Get the base serialization
        data = super().model_dump(**kwargs)
        
        # Manually serialize the content field to ensure all fields are included
        if hasattr(self.content, 'model_dump'):
            # Use the same kwargs (by_alias, exclude_none, etc.)
            data['content'] = self.content.model_dump(**kwargs)
        
        return data
    
    class Config:
        populate_by_name = True


# Helper functions
def create_action_request(
    message_id: str,
    to: str,
    from_agent: str,
    action: str,
    parameters: Dict[str, Any] = None,
    context: Dict[str, Any] = None,
    reply_to: Optional[str] = None
) -> A2AMessage:
    """Create an action request message"""
    return A2AMessage(
        id=message_id,
        to=to,
        from_agent=from_agent,
        content=A2AActionRequest(
            action=action,
            parameters=parameters or {},
            context=context or {}
        ),
        reply_to=reply_to
    )


def create_action_response(
    message_id: str,
    to: str,
    from_agent: str,
    action: str,
    result: Dict[str, Any],
    status: MessageStatus = MessageStatus.COMPLETED,
    error: Optional[str] = None,
    reply_to: Optional[str] = None
) -> A2AMessage:
    """Create an action response message"""
    return A2AMessage(
        id=message_id,
        to=to,
        from_agent=from_agent,
        content=A2AActionResponse(
            action=action,
            result=result,
            status=status,
            error=error
        ),
        reply_to=reply_to
    )


def create_capability_request(
    message_id: str,
    to: str,
    from_agent: str
) -> A2AMessage:
    """Create a capability request message"""
    return A2AMessage(
        id=message_id,
        to=to,
        from_agent=from_agent,
        content=A2ACapabilityRequest()
    )


def create_error_message(
    message_id: str,
    to: str,
    from_agent: str,
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    reply_to: Optional[str] = None
) -> A2AMessage:
    """Create an error message"""
    return A2AMessage(
        id=message_id,
        to=to,
        from_agent=from_agent,
        content=A2AError(
            code=code,
            message=message,
            details=details
        ),
        reply_to=reply_to
    )


# Agent URIs
AGENT_URIS = {
    "coordinator": "agent://coordinator",
    "topic_refiner": "agent://topic-refiner",
    "question_architect": "agent://question-architect",
    "search_strategist": "agent://search-strategist",
    "data_analyst": "agent://data-analyst",
    "report_writer": "agent://report-writer"
}

# Agent service URLs (for HTTP communication)
# Auto-detect local vs Kubernetes environment
import os

def _get_agent_services():
    """Get agent service URLs based on environment"""
    # Allow override via environment variable
    env_override = os.getenv("AGENT_ENVIRONMENT", "").lower()
    
    # Auto-detect if not explicitly set
    if env_override == "local" or (env_override == "" and (
        os.path.exists("venv") or 
        os.path.exists(".env.local") or
        os.getenv("REDIS_HOST") == "localhost"
    )):
        # Local development URLs
        return {
            "agent://coordinator": "http://localhost:8006",
            "agent://topic-refiner": "http://localhost:8001",
            "agent://question-architect": "http://localhost:8002",
            "agent://search-strategist": "http://localhost:8003",
            "agent://data-analyst": "http://localhost:8004",
            "agent://report-writer": "http://localhost:8005"
        }
    else:
        # Kubernetes service URLs
        return {
            "agent://coordinator": "http://coordinator-service:8006",
            "agent://topic-refiner": "http://topic-refiner-service:8001",
            "agent://question-architect": "http://question-architect-service:8002",
            "agent://search-strategist": "http://search-strategist-service:8003",
            "agent://data-analyst": "http://data-analyst-service:8004",
            "agent://report-writer": "http://report-writer-service:8005"
        }

AGENT_SERVICES = _get_agent_services()