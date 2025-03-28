from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from uuid import uuid4
from src.sdlccopilot.graph.user_story_graph import UserStoryGraphBuilder
from src.sdlccopilot.graph.design_document_graph import DesignDocumentGraphBuilder
from src.sdlccopilot.graph.code_development_graph import CodeDevelopmentGraphBuilder
from src.sdlccopilot.requests import ProjectRequirementsRequest, OwnerFeedbackRequest
from src.sdlccopilot.responses import UserStoriesResponse, DesignDocumentsResponse, CodeResponse
from src.sdlccopilot.prompts.functional_document import functional_document
from src.sdlccopilot.prompts.technical_document import technical_document


# Initialize FastAPI
app = FastAPI(title="User Stories Generator API")

# Initialize the user story workflow
user_story_graph_builder = UserStoryGraphBuilder()
user_story_workflow = user_story_graph_builder.build()

# Initialize the design document workflow
design_document_graph_builder = DesignDocumentGraphBuilder()
design_document_workflow = design_document_graph_builder.build()

## Initialize the code development workflow
code_development_graph_builder = CodeDevelopmentGraphBuilder()
code_development_workflow = code_development_graph_builder.build()

active_sessions = {}

# Status response model
class ServerStatusResponse(BaseModel):
    status: str
    message: str

@app.get("/status", response_model=ServerStatusResponse)
async def get_server_status():
    return ServerStatusResponse(
        status="OK",
        message="Server is up and running 🚀"
    )


@app.post("/stories/generate", response_model=UserStoriesResponse)
async def generate_user_stories(request: ProjectRequirementsRequest):
    session_id = str(uuid4())
    title = request.title
    description = request.description
    requirements = request.requirements


    try:    
        # initial_state = {
        #     "project_requirements" : project_requirements,
        #     "user_stories_messages": HumanMessage(content=f"{project_requirements}"),
        #     "user_stories": [],
        #     "status": "in_progress",
        #     "owner_feedback": "",
        #     "revised_count" : 0
        # }   

        project_requirements = {
            "title" : title,
            "description" : description,
            "requirements" : requirements
        }

        initial_story_state = {
            "project_requirements" : project_requirements,
            "user_stories": [],
            "user_stories_messages": HumanMessage(content=f"{project_requirements}"),
            "status": "in_progress",
            "owner_feedback": "",
            " b " : 0
        }

        state = None
        thread = {"configurable": {"thread_id": session_id}}
        for event in user_story_workflow.stream(initial_story_state, thread, stream_mode="values"):
            state = event

        active_sessions[session_id] = {
            "project_requirements": project_requirements,
            "user_stories": state["user_stories"],
            "story_status": state["status"],
            "story_messages": state["user_stories_messages"]
        }

        print("********* state : ", state)
        return UserStoriesResponse(
            session_id=session_id,
            project_requirements=project_requirements,
            status=state["status"],
            user_stories=state["user_stories"],
            message=state["user_stories_messages"]
        )    

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/stories/review/{session_id}", response_model=UserStoriesResponse)
async def review_user_stories(session_id: str, request: OwnerFeedbackRequest):
    feedback = request.feedback

    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:   
        thread = {"configurable": {"thread_id": session_id}}
        user_state = user_story_workflow.get_state(thread) 
        print("@@next node to call : ", user_state.next)
        print("@@user_state : ", user_state)

        user_story_workflow.update_state(thread, { "user_stories_messages" : HumanMessage(content=feedback)})

        state = None
        for event in user_story_workflow.stream(None, thread, stream_mode="values"):
            state = event

        print("********* state in feedback: ", state)

        active_sessions[session_id] = {
            "project_requirements": state["project_requirements"],
            "user_stories": state["user_stories"],
            "story_status": state["status"],
            "story_messages": state["user_stories_messages"]
        }

        return UserStoriesResponse(
            session_id=session_id,
            project_requirements=state["project_requirements"],
            status=state["status"],
            user_stories=state["user_stories"],
            message=state["user_stories_messages"]
        )    

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/functional/generate/{session_id}", response_model=DesignDocumentsResponse)
async def create_functional_design_documents(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    project_requirements = active_sessions[session_id]["project_requirements"]
    user_stories = active_sessions[session_id]["user_stories"]

    try:    
        initial_document_state = {
            "functional_documents" : [],
            "technical_documents" : [],
            "document_type" : "functional",
            "messages": [],
            "functional_status": "in_progress",
            "technical_status": "in_progress",
            "revised_count" : 0,
            "version" : 1.0
        }

        # Thread
        thread = {"configurable": {"thread_id": session_id}}
        document_state = None
        for event in design_document_workflow.stream(initial_document_state, thread, stream_mode="values"):
            document_state = event
        
        print("********* document_state : ", document_state)
        design_document_state = design_document_workflow.get_state(thread) 
        print("@@design_document_state next node : ", design_document_state.next)

        active_sessions[session_id] = {
            **active_sessions[session_id],
            "functional_documents": document_state["functional_documents"],
            "technical_documents": document_state["technical_documents"],
            "document_messages": document_state["messages"],
            "functional_status": document_state["functional_status"],
            "document_version": document_state["version"]
        }

        return DesignDocumentsResponse.model_construct(
            session_id=session_id,
            document_type=document_state["document_type"],
            status=document_state["functional_status"],
            document= functional_document,
            messages=document_state["messages"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/technical/generate/{session_id}", response_model=DesignDocumentsResponse)
async def create_technical_design_documents(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:    
        initial_document_state = {
            "technical_documents" : [],
            "document_type" : "technical",
            "technical_status" : "in_progress",
            "revised_count" : 0
        }

        # Thread
        thread = {"configurable": {"thread_id": session_id}}
        document_state = None
        for event in design_document_workflow.stream(initial_document_state, thread, stream_mode="values"):
            document_state = event
        
        print("********* technical document_state : ", document_state)
        design_document_state = design_document_workflow.get_state(thread) 
        print("@@technical next node : ", design_document_state.next)

        active_sessions[session_id] = {
            **active_sessions[session_id],
            "technical_documents": document_state["technical_documents"],
            "document_messages": document_state["messages"],
            "technical_status": document_state["technical_status"],
            "document_version": document_state["version"]
        }

        return DesignDocumentsResponse.model_construct(
            session_id=session_id,
            document_type=document_state["document_type"],
            status=document_state["technical_status"],
            document=technical_document,
            messages=document_state["messages"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/functional/review/{session_id}", response_model=DesignDocumentsResponse)
async def review_functional_design_documents(session_id: str, request: OwnerFeedbackRequest):
    feedback = request.feedback
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    if active_sessions[session_id]["functional_status"] != "pending_approval":
        raise HTTPException(status_code=400, detail="Functional design documents are not pending approval")

    try:   
        thread = {"configurable": {"thread_id": session_id}}
        document_state = design_document_workflow.get_state(thread) 
        print("@@next node to call : ", document_state.next)
        print("@@document_state : ", document_state)

        design_document_workflow.update_state(thread, { "messages" : HumanMessage(content=feedback)})

        document_state = None
        for event in design_document_workflow.stream(None, thread, stream_mode="values"):
            document_state = event
        
        print("********* functional document_state : ", document_state)
        active_sessions[session_id] = {
            **active_sessions[session_id],
            "functional_documents": document_state["functional_documents"],
            "technical_documents": document_state["technical_documents"],
            "document_messages": document_state["messages"],
            "functional_status": document_state["functional_status"],
            "technical_status": document_state["technical_status"],
            "document_version": document_state["version"]
        }
        return DesignDocumentsResponse.model_construct(
            session_id=session_id,
            document_type=document_state["document_type"],
            status=document_state["functional_status"],
            # Todo
            document = functional_document,
            messages=document_state["messages"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/documents/technical/review/{session_id}", response_model=DesignDocumentsResponse)
async def review_technical_design_documents(session_id: str, request: OwnerFeedbackRequest):
    feedback = request.feedback

    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    if active_sessions[session_id]["technical_status"] != "pending_approval":
        raise HTTPException(status_code=400, detail="Technical design documents are not pending approval")

    try:   
        thread = {"configurable": {"thread_id": session_id}}
        document_state = design_document_workflow.get_state(thread) 
        print("@@next node to call : ", document_state.next)
        print("@@document_state : ", document_state)

        design_document_workflow.update_state(thread, { "messages" : HumanMessage(content=feedback)})

        document_state = None
        for event in design_document_workflow.stream(None, thread, stream_mode="values"):
            document_state = event
        
        print("********* technical document_state : ", document_state)
        active_sessions[session_id] = {
            **active_sessions[session_id],
            "technical_documents": document_state["technical_documents"],
            "document_messages": document_state["messages"],
            "technical_status": document_state["technical_status"],
            "document_version": document_state["version"]
        }

        return DesignDocumentsResponse.model_construct(
            session_id=session_id,
            document_type=document_state["document_type"],
            status=document_state["technical_status"],
            document= technical_document,
            messages=document_state["messages"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Code Development
@app.post("/code/frontend/generate/{session_id}", response_model=CodeResponse)
async def generate_frontend_code(session_id: str):
    print("********* generate_frontend_code : ", session_id)
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        initial_code_state = {
            "code_type" : "frontend",
            "frontend_code" : "",
            "backend_code" : "",
            "frontend_status" : "in_progress",
            "backend_status" : "pending",
            "frontend_messages" : [],
            "backend_messages" : [],
            "revised_count" : 0
        }

        thread = {"configurable": {"thread_id": session_id}}
        code_state = None
        for event in code_development_workflow.stream(initial_code_state, thread, stream_mode="values"):
            code_state = event

        print("********* code_state : ", code_state)
        code_document_state = code_development_workflow.get_state(thread) 
        print("@@code next node : ", code_document_state.next)

        active_sessions[session_id] = {
            **active_sessions[session_id],
            "frontend_code": code_state["frontend_code"],
            "frontend_messages": code_state["frontend_messages"],
            "frontend_status": code_state["frontend_status"],
        }

        return CodeResponse.model_construct(
            session_id=session_id,
            code_type="frontend",
            status=code_state["frontend_status"],
            code=code_state["frontend_code"],
            messages=code_state["frontend_messages"],
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/code/backend/generate/{session_id}", response_model=CodeResponse)
async def generate_backend_code(session_id: str):
    print("********* generate_backend_code : ", session_id)
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        initial_code_state = {
            "code_type" : "backend",
            "backend_code" : "",
            "backend_status" : "in_progress",
            "backend_messages" : [],
            "revised_count" : 0
        }

        thread = {"configurable": {"thread_id": session_id}}
        code_state = None
        for event in code_development_workflow.stream(initial_code_state, thread, stream_mode="values"):
            code_state = event

        print("********* code_state : ", code_state)
        code_document_state = code_development_workflow.get_state(thread) 
        print("@@code next node : ", code_document_state.next)

        active_sessions[session_id] = {
            **active_sessions[session_id],
            "backend_code": code_state["backend_code"],
            "backend_messages": code_state["backend_messages"],
            "backend_status": code_state["backend_status"],
        }

        return CodeResponse.model_construct(
            session_id=session_id,
            code_type="backend",
            status=code_state["backend_status"],
            code=code_state["backend_code"],
            messages=code_state["backend_messages"],
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
