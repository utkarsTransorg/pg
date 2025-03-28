from typing_extensions import TypedDict, Annotated, List, Literal
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage, SystemMessage
from langgraph.graph import add_messages
from typing import Dict, List, Optional, Union, Literal

class ProjectRequirements(TypedDict):
    title: str
    description: str
    requirements : List[str]

class UserStory(TypedDict):
    story_id : str
    title : str
    description : str 
    acceptance_criteria : List[str]

class UserStoryState(TypedDict):
    project_requirements : ProjectRequirements
    user_stories : List[UserStory]
    user_stories_messages: Annotated[list, add_messages]
    status: Literal["in_progress", "pending_approval", "completed", "feedback"] = "in_progress"
    revised_count : int = 0