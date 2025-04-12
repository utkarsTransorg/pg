from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from uuid import uuid4
from src.sdlccopilot.requests import ProjectRequirementsRequest, OwnerFeedbackRequest
from src.sdlccopilot.responses import UserStoriesResponse, DesignDocumentsResponse, CodeResponse, SecurityReviewResponse, SecurityReview, TestCasesResponse, TestCase
from src.sdlccopilot.llms.groq import GroqLLM
from src.sdlccopilot.graph.sdlc_graph import SDLCGraphBuilder

## Environment Variables
from dotenv import load_dotenv
load_dotenv()
import os 

# os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ['PROJECT_ENVIRONMENT'] = os.getenv("PROJECT_ENVIRONMENT")
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
os.environ['LANGSMITH_API_KEY'] = os.getenv("LANGSMITH_API_KEY")
os.environ['LANGSMITH_PROJECT'] = os.getenv("LANGSMITH_PROJECT")
os.environ['LANGSMITH_TRACING'] = os.getenv("LANGSMITH_TRACING")
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Initialize FastAPI
app = FastAPI(title="User Stories Generator API")

## Initialize the SDLC workflow
sdlc_graph_builder = SDLCGraphBuilder()
sdlc_workflow = sdlc_graph_builder.build()

active_sessions = {}

# Status response model
class ServerStatusResponse(BaseModel):
    status: str
    message: str
    

def serialize_message(msg):
    return {
        "content": msg.content,
        "type": msg.type,
        "id": msg.id
    }


@app.get("/status", response_model=ServerStatusResponse)
async def get_server_status():
    return ServerStatusResponse(
        status="OK",
        message="Server is up and running..."
    )

@app.post("/stories/generate", response_model=UserStoriesResponse)
async def generate_user_stories(request: ProjectRequirementsRequest):
    session_id = str(uuid4())
    title = request.title
    description = request.description
    requirements = request.requirements

    try:    
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
        for event in sdlc_workflow.stream(initial_story_state, thread, stream_mode="values"):
            state = event

        user_story_status = "completed" if state["user_story_status"] == 'approved' else state["user_story_status"]
        user_story = state["user_stories"]
        user_story_messages = [serialize_message(msg) for msg in state["user_story_messages"]]
        
        active_sessions[session_id] = {
            "project_requirements": project_requirements,
            "user_stories": user_story,
            "user_story_status": user_story_status,
            "user_story_messages": user_story_messages
        }

        print("*** User stories generated ****")
        print("==================================")

        return UserStoriesResponse(
            session_id=session_id,
            project_requirements=project_requirements,
            status=user_story_status,
            user_stories=user_story,
            message=user_story_messages
        )    

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/stories/review/{session_id}", response_model=UserStoriesResponse)
async def review_user_stories(session_id: str, request: OwnerFeedbackRequest):
    feedback = request.feedback
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if active_sessions[session_id]["user_story_status"] == "completed":
        raise HTTPException(status_code=400, detail="User stories are already completed")

    if active_sessions[session_id]["user_story_status"] != "pending_approval":
        raise HTTPException(status_code=400, detail="User stories are not pending approval")    

    try:   
        thread = {"configurable": {"thread_id": session_id}}
        user_state = sdlc_workflow.get_state(thread) 
        print("@@next node to call : ", user_state.next)

        sdlc_workflow.update_state(thread, { "user_story_messages" : HumanMessage(content=feedback)})

        state = None
        for event in sdlc_workflow.stream(None, thread, stream_mode="values"):
            state = event
            
        print("** updated_state : ", state)
        user_story_messages = state["user_story_messages"]
        user_story_status = "completed" if state["user_story_status"] == 'approved' else state["user_story_status"]
        user_story = state["user_stories"]
        
        print("** user_story_status : ", user_story_status)
        
        if user_story_status == "completed":
            functional_documents = state["functional_documents"]
            functional_status = state["functional_status"]
            functional_messages = state["functional_messages"]

        active_sessions[session_id] = {
            **active_sessions,
            "user_stories": user_story,
            "user_story_status": user_story_status,
            "user_story_messages": user_story_messages,
            "functional_documents" : functional_documents if user_story_status == "completed" else None,
            "functional_status": functional_status if user_story_status == "completed" else None,
            "functional_messages": functional_messages if user_story_status == "completed" else None
        }
                
        print("*** User stories reviewed ****")
        print("==================================")

        return UserStoriesResponse(
            session_id=session_id,
            project_requirements=active_sessions[session_id]["project_requirements"],
            status=user_story_status,
            user_stories=user_story,
            message=user_story_messages
        )    

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/functional/generate/{session_id}", response_model=DesignDocumentsResponse)
async def create_functional_design_documents(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if active_sessions[session_id]["functional_status"] != "pending_approval":
        raise HTTPException(status_code=400, detail="Functional design documents are not pending approval")

    try:    
        functional_status = active_sessions[session_id]["functional_status"]
        functional_documents = active_sessions[session_id]["functional_documents"]
        functional_messages = active_sessions[session_id]["functional_messages"]

        print("*** Functional documents generated ****")
        print("==================================")

        return DesignDocumentsResponse.model_construct(
            session_id=session_id,
            document_type="functional",
            status=functional_status,
            document= functional_documents,
            messages=functional_messages
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/functional/review/{session_id}", response_model=DesignDocumentsResponse)
async def review_functional_design_documents(session_id: str, request: OwnerFeedbackRequest):
    feedback = request.feedback
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if active_sessions[session_id]["user_story_status"] != "completed":
        raise HTTPException(status_code=400, detail="User stories are not completed")
    
    if active_sessions[session_id]["functional_status"] == "completed":
        raise HTTPException(status_code=400, detail="Functional design documents are already completed")

    if active_sessions[session_id]["functional_status"] != "pending_approval":
        raise HTTPException(status_code=400, detail="Functional design documents are not pending approval")

    try:   
        thread = {"configurable": {"thread_id": session_id}}
        document_state = sdlc_workflow.get_state(thread) 
        print("@@next node to call : ", document_state.next)
        print("@@document_state : ", document_state)
        sdlc_workflow.update_state(thread, { "functional_messages" : HumanMessage(content=feedback)})
        document_state = None
        for event in sdlc_workflow.stream(None, thread, stream_mode="values"):
            document_state = event
        
        print("********* functional document_state : ", document_state)
        functional_status = "completed" if document_state["functional_status"] == 'approved' else document_state["functional_status"]
        
        if functional_status == "completed":
            technical_documents = document_state["technical_documents"]
            technical_status = document_state["technical_status"]
            technical_messages = document_state["technical_messages"]
            
        active_sessions[session_id] = {
            **active_sessions[session_id],
            "functional_documents": document_state["functional_documents"],
            "functional_messages": document_state["functional_messages"],
            "functional_status": functional_status,
            "technical_documents": technical_documents if functional_status == "completed" else None,
            "technical_messages": technical_messages if functional_status == "completed" else None,
            "technical_status": technical_status if functional_status == "completed" else None,
        }
        print("**** Functional review completed ****")
        print("==================================")
        
        return DesignDocumentsResponse.model_construct(
            session_id=session_id,
            document_type="functional",
            status=functional_status,
            document = document_state["functional_documents"],
            messages=document_state["functional_messages"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.post("/documents/technical/generate/{session_id}", response_model=DesignDocumentsResponse)
async def create_technical_design_documents(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if active_sessions[session_id]["user_story_status"] != "completed":
        raise HTTPException(status_code=400, detail="User stories are not completed")
    
    if active_sessions[session_id]["functional_status"] != "completed":
        raise HTTPException(status_code=400, detail="Functional design documents are not completed")
    
    if active_sessions[session_id]["technical_status"] == "completed":
        raise HTTPException(status_code=400, detail="Technical design documents are already completed")
    
    if active_sessions[session_id]["technical_status"] != "pending_approval":
        raise HTTPException(status_code=400, detail="Technical design documents are not pending approval")
        
    try:    
        technical_status = active_sessions[session_id]["technical_status"]
        technical_documents = active_sessions[session_id]["technical_documents"]
        technical_messages = active_sessions[session_id]["technical_messages"]
        
        print("*** Technical documents generated ****")
        print("==================================")
        
        return DesignDocumentsResponse.model_construct(
            session_id=session_id,
            document_type="technical",
            status=technical_status,
            document= technical_documents,
            messages=technical_messages
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/documents/technical/review/{session_id}", response_model=DesignDocumentsResponse)
async def review_technical_design_documents(session_id: str, request: OwnerFeedbackRequest):
    feedback = request.feedback

    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    if active_sessions[session_id]["user_story_status"] != "completed":
        raise HTTPException(status_code=400, detail="User stories are not completed")
    
    if active_sessions[session_id]["functional_status"] != "completed":
        raise HTTPException(status_code=400, detail="Functional design documents are not completed")
    
    if active_sessions[session_id]["technical_status"] == "completed":
        raise HTTPException(status_code=400, detail="Technical design documents are already completed")
    
    if active_sessions[session_id]["technical_status"] != "pending_approval":
        raise HTTPException(status_code=400, detail="Technical design documents are not pending approval")

    try:   
        thread = {"configurable": {"thread_id": session_id}}
        document_state = sdlc_workflow.get_state(thread) 
        print("@@next node to call : ", document_state.next)
        print("@@document_state : ", document_state)

        sdlc_workflow.update_state(thread, { "technical_messages" : HumanMessage(content=feedback)})

        document_state = None
        for event in sdlc_workflow.stream(None, thread, stream_mode="values"):
            document_state = event
            
        technical_status = "completed" if document_state["technical_status"] == 'approved' else document_state["technical_status"]
        
        if technical_status == "completed":
            frontend_documents = document_state["frontend_code"]
            frontend_status = document_state["frontend_status"]
            frontend_messages = document_state["frontend_messages"]
        
        print("********* technical document_state : ", document_state)
        active_sessions[session_id] = {
            **active_sessions[session_id],
            "technical_documents": document_state["technical_documents"],
            "technical_messages": document_state["technical_messages"],
            "technical_status": technical_status,
            "frontend_code": frontend_documents if technical_status == "completed" else None,
            "frontend_messages": frontend_messages if technical_status == "completed" else None,
            "frontend_status": frontend_status if technical_status == "completed" else None,
        }
        print("**** Technical review completed ****")
        print("==================================")

        return DesignDocumentsResponse.model_construct(
            session_id=session_id,
            document_type="technical",
            status=technical_status,
            document= document_state["technical_documents"],
            messages=document_state["technical_messages"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

## Code Development
@app.post("/code/frontend/generate/{session_id}", response_model=CodeResponse)
async def generate_frontend_code(session_id: str):
    print("********* generate_frontend_code : ", session_id)
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if active_sessions[session_id]["user_story_status"] != "completed":
        raise HTTPException(status_code=400, detail="User stories are not completed")
    
    if active_sessions[session_id]["functional_status"] != "completed":
        raise HTTPException(status_code=400, detail="Functional design documents are not completed")
    
    if active_sessions[session_id]["technical_status"] != "completed":
        raise HTTPException(status_code=400, detail="Technical design documents are not completed")
    
    if active_sessions[session_id]["frontend_status"] == "completed":
        raise HTTPException(status_code=400, detail="Frontend code is already completed")
    
    if active_sessions[session_id]["frontend_status"] != "pending_approval":
        raise HTTPException(status_code=400, detail="Frontend code is not pending approval")

    try:
        frontend_status = active_sessions[session_id]["frontend_status"]
        frontend_code = active_sessions[session_id]["frontend_code"]
        frontend_messages = active_sessions[session_id]["frontend_messages"]
        
        print("*** Frontend code generated ****")
        print("==================================")

        return CodeResponse.model_construct(
            session_id=session_id,
            code_type="frontend",
            status=frontend_status,
            code=frontend_code,
            messages=frontend_messages,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/code/frontend/review/{session_id}", response_model=CodeResponse)
async def review_frontend_code(session_id: str, request: OwnerFeedbackRequest):
    print("********* review_frontend_code : ", session_id)
    feedback = request.feedback

    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if active_sessions[session_id]["user_story_status"] != "completed":
        raise HTTPException(status_code=400, detail="User stories are not completed")
    
    if active_sessions[session_id]["functional_status"] != "completed":
        raise HTTPException(status_code=400, detail="Functional design documents are not completed")
    
    if active_sessions[session_id]["technical_status"] != "completed":
        raise HTTPException(status_code=400, detail="Technical design documents are not completed")
    
    if active_sessions[session_id]["frontend_status"] == "completed":
        raise HTTPException(status_code=400, detail="Frontend code is already completed")   
    
    if active_sessions[session_id]["frontend_status"] != "pending_approval":
        raise HTTPException(status_code=400, detail="Frontend code is not pending approval")

    try:   
        thread = {"configurable": {"thread_id": session_id}}
        document_state = sdlc_workflow.get_state(thread) 
        print("@@next node to call : ", document_state.next)
        print("@@document_state : ", document_state)

        sdlc_workflow.update_state(thread, { "frontend_messages" : HumanMessage(content=feedback)})

        document_state = None
        for event in sdlc_workflow.stream(None, thread, stream_mode="values"):
            document_state = event
            
        frontend_status = "completed" if document_state["frontend_status"] == 'approved' else document_state["frontend_status"]
        
        if frontend_status == "completed":
            backend_code = document_state["backend_code"]
            backend_status = document_state["backend_status"]
            backend_messages = document_state["backend_messages"]
        
        active_sessions[session_id] = {
            **active_sessions[session_id],    
            "frontend_code": document_state["frontend_code"],
            "frontend_messages": document_state["frontend_messages"],
            "frontend_status": frontend_status,
            "backend_code": backend_code if frontend_status == "completed" else None,
            "backend_messages": backend_messages if frontend_status == "completed" else None,
            "backend_status": backend_status if frontend_status == "completed" else None,
        } 
        
        print("**** Frontend review completed ****")
        print("==================================")
        
        return CodeResponse.model_construct(
            session_id=session_id,
            code_type="frontend",
            status=frontend_status,
            code=document_state["frontend_code"],
            messages=document_state["frontend_messages"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/code/backend/generate/{session_id}", response_model=CodeResponse)
async def generate_backend_code(session_id: str):
    print("********* generate_backend_code : ", session_id)
    
    validation(session_id, "backend_generate")

    try:
        backend_status = active_sessions[session_id]["backend_status"]
        backend_code = active_sessions[session_id]["backend_code"]
        backend_messages = active_sessions[session_id]["backend_messages"]
        
        print("*** Backend code generated ****")
        print("==================================")
        
        return CodeResponse.model_construct(
            session_id=session_id,
            code_type="backend",
            status=backend_status,
            code=backend_code,
            messages=backend_messages,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def validation(session_id: str, current_flow: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if active_sessions[session_id]["user_story_status"] != "completed":
        raise HTTPException(status_code=400, detail="User stories are not completed")

    if active_sessions[session_id]["functional_status"] != "completed":
        raise HTTPException(status_code=400, detail="Functional design documents are not completed")
    
    if active_sessions[session_id]["technical_status"] != "completed":
        raise HTTPException(status_code=400, detail="Technical design documents are not completed")
    
    if active_sessions[session_id]["frontend_status"] != "completed":
        raise HTTPException(status_code=400, detail="Frontend code is not completed")

    if current_flow == "backend_generate":
        if active_sessions[session_id]["backend_status"] == "completed":
            raise HTTPException(status_code=400, detail="Backend code is already completed")
        
        if active_sessions[session_id]["backend_status"] != "pending_approval":
            raise HTTPException(status_code=400, detail="Backend code is not pending approval")
    
    if current_flow == "backend_review":
        if active_sessions[session_id]["backend_status"] != "pending_approval":
            raise HTTPException(status_code=400, detail="Backend code is not pending approval")


@app.post("/code/backend/review/{session_id}", response_model=CodeResponse)
async def review_backend_code(session_id: str, request: OwnerFeedbackRequest):
    print("********* review_backend_code : ", session_id)
    feedback = request.feedback
    validation(session_id, "backend_review")
    try:   
        thread = {"configurable": {"thread_id": session_id}}
        document_state = sdlc_workflow.get_state(thread) 
        print("@@next node to call : ", document_state.next)
        print("@@document_state : ", document_state)
        
        sdlc_workflow.update_state(thread, { "backend_messages" : HumanMessage(content=feedback)})

        state = None
        for event in sdlc_workflow.stream(None, thread, stream_mode="values"):
            state = event
        
        print("** updated state : ", state)
        status = "completed" if state["backend_status"] == 'approved' else state["backend_status"]
        
        if status == "completed":
            security_reviews = state["security_reviews"]
            security_reviews_status = state["security_reviews_status"]
            security_reviews_messages = state["security_reviews_messages"]
        
        active_sessions[session_id] = {
            **active_sessions[session_id],    
            "backend_code": state["backend_code"],
            "backend_messages": state["backend_messages"],
            "backend_status": status,
            "security_reviews" : security_reviews if status == "completed" else None,
            "security_reviews_messages": security_reviews_messages if status == "completed" else None,
            "security_reviews_status": security_reviews_status if status == "completed" else None,
        } 
        
        print("**** Backend review completed ****")
        print("==================================")
        
        return CodeResponse.model_construct(
            session_id=session_id,
            code_type="backend",
            status=status,
            code=state["backend_code"],
            messages=state["backend_messages"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/security/review/get/{session_id}", response_model=SecurityReviewResponse)
# async def get_security_review(session_id : str):
#     print("********* get_security_review : ", session_id)
#     if session_id not in active_sessions:
#         raise HTTPException(status_code = 404, detail = "Session not found")
    
#     try:
#         reviews = [
#             SecurityReview(
#                 sec_id = "SEC-001",
#                 review = "Insecure password storage: Passwords are stored using bcryptjs with a salt of 10, which is relatively  low slat value. This makes it vulnerable to brute-force attacks.",
#                 file_path = "backend/src/controllers/authController.js",
#                 recommendation = "Increase the salt value to at least 12 and consider using more secure passwords hashing algorithms like Argon2 or PBKDF2. ",
#                 priority = "high"
#             ),
#             SecurityReview(
#                 sec_id = "SEC-002",
#                 review = "Lack of input validation : the register and login endpoints do not validate the user input, making them vulnerable  to SQL injection and cross site scripting attacks.",
#                 file_path = " backend/src/controllers/autheController.js",
#                 recommendation = "Implementation input validation inout a library like Joi and express-validator to ensure that the input conforms to expected formats.",
#                 priority = "medium"
#             )
#         ]
        
#         active_sessions[session_id] = {
#             **active_sessions[session_id],
#             "security_review": reviews,
#             "security_status": "pending_approval",
#             "security_messages": []
#         }
        
#         return SecurityReviewResponse.model_construct(
#             session_id = session_id,
#             status = "pending_approval",
#             reviews = reviews,
#             messages = []
#         )
        
#     except Exception as e:
#         raise HTTPException(status_code = 500, detail = str(e))


# @app.post("/security/review/review/{session_id}", response_model=SecurityReviewResponse)
# async def review_security_review(session_id: str, request: OwnerFeedbackRequest):
#     feedback = request.feedback

#     if session_id not in active_sessions:
#         raise HTTPException(status_code=404, detail="Session not found")

#     if active_sessions[session_id]["security_status"] != "pending_approval":
#         raise HTTPException(status_code=400, detail="Security review is not pending approval")

#     try:   
#         active_sessions[session_id] = {
#             **active_sessions[session_id],
#             "security_review": active_sessions[session_id]["security_review"],
#             "security_status": "completed",
#             "security_messages": []
#         } 

#         return SecurityReviewResponse.model_construct(
#             session_id=session_id,
#             status="completed",
#             reviews=active_sessions[session_id]["security_review"],
#             messages=[]
#         )

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



# @app.get("/test/cases/get/{session_id}", response_model=TestCasesResponse)
# async def get_test_cases(session_id : str):
#     print("********* get_test_cases : ", session_id)
#     if session_id not in active_sessions:
#         raise HTTPException(status_code = 404, detail = "Session not found")
    
#     try:
        
#         test_cases = [
#             TestCase(
#                 test_id = "TC-001",
#                 description = "Test GPS Processing function",
#                 steps = ["Input sample GPS data", "Process data using the GPS processing function", "Verify output matches expected format"],
#                 status = "draft"
#             ),
#         ]
        
#         active_sessions[session_id] = {
#             **active_sessions[session_id],
#             "test_cases": test_cases,
#             "test_cases_status": "pending_approval",
#             "test_cases_messages": []
#         }
        
#         return TestCasesResponse.model_construct(
#             session_id = session_id,
#             status = "pending_approval",
#             test_cases = test_cases,
#             messages=[]
#         )
        
#     except Exception as e:
#         raise HTTPException(status_code = 500, detail = str(e))


# @app.post("/test/cases/review/{session_id}", response_model=TestCasesResponse)
# async def review_test_cases(session_id: str, request: OwnerFeedbackRequest):
#     feedback = request.feedback

#     if session_id not in active_sessions:
#         raise HTTPException(status_code=404, detail="Session not found")

#     if active_sessions[session_id]["test_cases_status"] != "pending_approval":
#         raise HTTPException(status_code=400, detail="Test cases are not pending approval")

#     try:   
#         active_sessions[session_id] = {
#             **active_sessions[session_id],
#             "test_cases": active_sessions[session_id]["test_cases"],
#             "test_cases_status": "completed",
#             "test_cases_messages": []
#         } 

#         return TestCasesResponse.model_construct(
#             session_id=session_id,
#             status="completed",
#             test_cases=active_sessions[session_id]["test_cases"],
#             messages=[]
#         )

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/qa/testing/get/{session_id}", response_model=TestCasesResponse)
# async def get_qa_testing(session_id : str):
#     print("********* get_qa_testing : ", session_id)
#     if session_id not in active_sessions:
#         raise HTTPException(status_code = 404, detail = "Session not found")
    
#     try:
#         test_cases = [
#             TestCase(
#                 test_id = "TC-001",
#                 description = "Test GPS Processing function",
#                 steps = ["Input sample GPS data", "Process data using the GPS processing function", "Verify output matches expected format"],
#                 status = "pass"
#             ),
#         ]
        
#         active_sessions[session_id] = {
#             **active_sessions[session_id],
#             "test_cases": test_cases,
#             "test_cases_status": "passed",
#             "test_cases_messages": []
#         }
        
#         return TestCasesResponse.model_construct(
#             session_id = session_id,
#             status = "passed",
#             test_cases = test_cases,
#             messages=[]
#         )
        
#     except Exception as e:
#         raise HTTPException(status_code = 500, detail = str(e))
