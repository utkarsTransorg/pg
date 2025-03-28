from typing_extensions import Annotated, List, Literal
from langgraph.graph import add_messages
from typing import List, Literal
from pydantic import BaseModel, Field

class DocumentSection(BaseModel):
    title: str = Field(description="The title of the section")
    content: str = Field(description="The content of the section")

class DocumentState(BaseModel):
    functional_documents: List[DocumentSection] = []
    technical_documents: List[DocumentSection] = []
    messages: Annotated[list, add_messages] = []
    document_type: Literal["functional", "technical"] = "functional"
    functional_status: Literal["in_progress", "pending_approval", "feedback", "completed"] = "in_progress"
    technical_status: Literal["in_progress", "pending_approval", "feedback", "completed"] = "in_progress"
    revised_count : int = 0
    version: float = 1.0