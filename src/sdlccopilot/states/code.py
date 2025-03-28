from typing_extensions import Annotated, Literal
from langgraph.graph import add_messages
from typing import  Literal
from pydantic import BaseModel, Field

from langgraph.graph.message import add_messages

class CodeState(BaseModel):
    code_type : Literal["frontend", "backend"] = "frontend"
    frontend_status: Literal["pending", "in_progress", "pending_approval", "feedback", "completed"] = "pending"
    backend_status: Literal["pending", "in_progress", "pending_approval", "feedback", "completed"] = "pending"
    frontend_messages: Annotated[list, add_messages]
    backend_messages: Annotated[list, add_messages]
    revised_count : int = Field(default=0, description="The number of times the code has been revised")
    frontend_code : str = Field(description="The frontend code")
    backend_code : str = Field(description="The backend code")