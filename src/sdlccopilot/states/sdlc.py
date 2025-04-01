# from typing_extensions import TypedDict, Annotated, List, Literal
# from langchain_core.messages import AnyMessage, AIMessage, HumanMessage, SystemMessage
# from langgraph.graph import add_messages
# from typing import Dict, List, Optional, Union, Literal
# from pydantic import BaseModel, Field
# from IPython.display import Image, display 
# from langchain_core.messages import AnyMessage
# from langgraph.graph.message import add_messages


# class SDLCState(BaseModel):
#     project_requirements : ProjectRequirements
#     revised_count : int = Field(default=0, description="The number of times the revised")
#     # User story
#     user_stories : List[UserStory] = []
#     user_story_messages : Annotated[list, add_messages] = []
#     user_story_status : Literal["pending", "in_progress", "pending_approval", "feedback", "completed"] = "pending"
    
#     document_type: Literal["functional", "technical"] = "functional"
#     # functional documents
#     functional_documents : List[DocumentSection] = []
#     functional_messages : Annotated[list, add_messages] = []
#     functional_status: Literal["pending", "in_progress", "pending_approval", "feedback", "completed"] = "pending"
#     # technical documents
#     technical_documents : List[DocumentSection] = []
#     technical_messages : Annotated[list, add_messages] = []
#     technical_status: Literal["pending", "in_progress", "pending_approval", "feedback", "completed"] = "pending"
    
#     code_type : Literal["frontend", "backend"] = "frontend"
#     # frontend code
#     frontend_code : str = Field(default='', description="The frontend code")
#     frontend_messages: Annotated[list, add_messages] = []
#     frontend_status: Literal["pending", "in_progress", "pending_approval", "feedback", "completed"] = "pending"
#     # backend code
#     backend_code : str = Field(default= '', description="The backend code")
#     backend_messages: Annotated[list, add_messages] = []
#     backend_status: Literal["pending", "in_progress", "pending_approval", "feedback", "completed"] = "pending"

#     # security review
#     security_reviews : List[SecurityReview] = []
#     security_reviews_messages: Annotated[list, add_messages] = []
#     security_reviews_status : Literal["pending", "in_progress", "pending_approval", "feedback", "completed"] = "pending"

#     ## test cases
#     test_cases : List[TestCase] = []
#     test_cases_messages: Annotated[list, add_messages] = []
#     test_cases_status : Literal["pending", "in_progress", "pending_approval", "feedback", "completed"] = "pending"