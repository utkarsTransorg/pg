from pydantic import BaseModel
from typing import List


class ProjectRequirementsRequest(BaseModel):
    title : str
    description : str
    requirements : List[str]

class OwnerFeedbackRequest(BaseModel):
    feedback: str