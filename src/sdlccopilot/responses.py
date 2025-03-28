from pydantic import BaseModel, Field
from typing import List, Dict, Literal
from langchain_core.messages import AnyMessage

class UserStoriesResponse(BaseModel):
    session_id: str
    status: Literal["in_progress", "pending_approval", "feedback", "completed"]
    project_requirements : Dict
    user_stories: List[Dict]
    message: List[AnyMessage]


class DocumentSection(BaseModel):
    title: str = Field(description="The title of the section")
    content: str = Field(description="The content of the section")

class DesignDocumentsResponse(BaseModel):
    session_id: str
    version: float = 1.0
    document_type: Literal["functional", "technical"]
    status: Literal["in_progress", "pending_approval", "feedback", "completed"]
    document : List[DocumentSection]
    messages: List[AnyMessage]
   
class CodeResponse(BaseModel):
    session_id : str
    code_type : Literal["frontend", "backend"]
    status : Literal["in_progress", "pending_approval", "feedback", "completed"]
    code : str
    messages : List[AnyMessage]



#     ********* document_state :  {'functional_documents': [DocumentSection(title='INTRODUCTION', content='This document defines the functional requirements for the Password Reset 
# Feature of the User Management System.'), DocumentSection(title='BUSINESS CONTEXT', content='The business needs a secure mechanism for users to recover access to their accounts without compromising security, improving customer satisfaction and retention.')], 'technical_documents': [], 'messages': [AIMessage(content="Please review above functional design document and provide feedback or type 'Approved' if you're satisfied.", additional_kwargs={}, response_metadata={}, id='41a4334f-abcd-4e48-a1ce-f96f36454b07')], 'document_type': 'functional', 'status': 'pending_approval', 'revised_count': 0, 'version': 1.0}