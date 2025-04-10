from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from uuid import uuid4
from src.sdlccopilot.requests import ProjectRequirementsRequest, OwnerFeedbackRequest
from src.sdlccopilot.responses import UserStoriesResponse, DesignDocumentsResponse, CodeResponse, SecurityReviewResponse, SecurityReview, TestCasesResponse, TestCase
from src.sdlccopilot.prompts.functional_document import functional_document
from src.sdlccopilot.prompts.technical_document import technical_document
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

# Initialize FastAPI
app = FastAPI(title="User Stories Generator API")

# Initialize the user story workflow
# llm = GroqLLM(model_name="deepseek-r1-distill-llama-70b").get()
# if not llm:
#     raise Exception("Error: Groq LLM model could not be initialized.")

## Initialize the SDLC workflow
sdlc_graph_builder = SDLCGraphBuilder()
sdlc_workflow = sdlc_graph_builder.build()


# user_story_graph_builder = UserStoryGraphBuilder(llm)
# user_story_workflow = user_story_graph_builder.build()

# # Initialize the design document workflow
# design_document_graph_builder = DesignDocumentGraphBuilder()
# design_document_workflow = design_document_graph_builder.build()

# ## Initialize the code development workflow
# code_development_graph_builder = CodeDevelopmentGraphBuilder()
# code_development_workflow = code_development_graph_builder.build()

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

        user_story_messages = state["user_story_messages"]
        user_story_status = "completed" if state["user_story_status"] == 'approved' else state["user_story_status"]
        user_story = state["user_stories"]
        active_sessions[session_id] = {
            "project_requirements": project_requirements,
            "user_stories": user_story,
            "story_status": user_story_status,
            "story_messages": user_story_messages
        }

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

        active_sessions[session_id] = {
            **active_sessions[session_id],
            "user_stories": user_story,
            "story_status": user_story_status,
            "story_messages": user_story_messages
        }

        return UserStoriesResponse(
            session_id=session_id,
            project_requirements=active_sessions[session_id]["project_requirements"],
            status=user_story_status,
            user_stories=user_story,
            message=user_story_messages
        )    

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/documents/functional/generate/{session_id}", response_model=DesignDocumentsResponse)
# async def create_functional_design_documents(session_id: str):
#     if session_id not in active_sessions:
#         raise HTTPException(status_code=404, detail="Session not found")

#     try:    
#         initial_document_state = {
#             "functional_documents" : [],
#             "technical_documents" : [],
#             "document_type" : "functional",
#             "messages": [],
#             "functional_status": "in_progress",
#             "technical_status": "in_progress",
#             "revised_count" : 0,
#             "version" : 1.0
#         }

#         # Thread
#         thread = {"configurable": {"thread_id": session_id}}
#         document_state = None
#         for event in design_document_workflow.stream(initial_document_state, thread, stream_mode="values"):
#             document_state = event
        
#         print("********* document_state : ", document_state)
#         design_document_state = design_document_workflow.get_state(thread) 
#         print("@@design_document_state next node : ", design_document_state.next)

#         active_sessions[session_id] = {
#             **active_sessions[session_id],
#             "functional_documents": document_state["functional_documents"],
#             "technical_documents": document_state["technical_documents"],
#             "document_messages": document_state["messages"],
#             "functional_status": document_state["functional_status"],
#             "document_version": document_state["version"]
#         }

#         return DesignDocumentsResponse.model_construct(
#             session_id=session_id,
#             document_type=document_state["document_type"],
#             status=document_state["functional_status"],
#             document= functional_document,
#             messages=document_state["messages"]
#         )

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/documents/technical/generate/{session_id}", response_model=DesignDocumentsResponse)
# async def create_technical_design_documents(session_id: str):
#     if session_id not in active_sessions:
#         raise HTTPException(status_code=404, detail="Session not found")

#     try:    
#         initial_document_state = {
#             "technical_documents" : [],
#             "document_type" : "technical",
#             "technical_status" : "in_progress",
#             "revised_count" : 0
#         }

#         # Thread
#         thread = {"configurable": {"thread_id": session_id}}
#         document_state = None
#         for event in design_document_workflow.stream(initial_document_state, thread, stream_mode="values"):
#             document_state = event
        
#         print("********* technical document_state : ", document_state)
#         design_document_state = design_document_workflow.get_state(thread) 
#         print("@@technical next node : ", design_document_state.next)

#         active_sessions[session_id] = {
#             **active_sessions[session_id],
#             "technical_documents": document_state["technical_documents"],
#             "document_messages": document_state["messages"],
#             "technical_status": document_state["technical_status"],
#             "document_version": document_state["version"]
#         }

#         return DesignDocumentsResponse.model_construct(
#             session_id=session_id,
#             document_type=document_state["document_type"],
#             status=document_state["technical_status"],
#             document=technical_document,
#             messages=document_state["messages"]
#         )

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/documents/functional/review/{session_id}", response_model=DesignDocumentsResponse)
# async def review_functional_design_documents(session_id: str, request: OwnerFeedbackRequest):
#     feedback = request.feedback
#     if session_id not in active_sessions:
#         raise HTTPException(status_code=404, detail="Session not found")

#     if active_sessions[session_id]["functional_status"] != "pending_approval":
#         raise HTTPException(status_code=400, detail="Functional design documents are not pending approval")

#     try:   
#         thread = {"configurable": {"thread_id": session_id}}
#         document_state = design_document_workflow.get_state(thread) 
#         print("@@next node to call : ", document_state.next)
#         print("@@document_state : ", document_state)

#         design_document_workflow.update_state(thread, { "messages" : HumanMessage(content=feedback)})

#         document_state = None
#         for event in design_document_workflow.stream(None, thread, stream_mode="values"):
#             document_state = event
        
#         print("********* functional document_state : ", document_state)
#         active_sessions[session_id] = {
#             **active_sessions[session_id],
#             "functional_documents": document_state["functional_documents"],
#             "technical_documents": document_state["technical_documents"],
#             "document_messages": document_state["messages"],
#             "functional_status": document_state["functional_status"],
#             "technical_status": document_state["technical_status"],
#             "document_version": document_state["version"]
#         }
#         return DesignDocumentsResponse.model_construct(
#             session_id=session_id,
#             document_type=document_state["document_type"],
#             status=document_state["functional_status"],
#             # Todo
#             document = functional_document,
#             messages=document_state["messages"]
#         )

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    

# @app.post("/documents/technical/review/{session_id}", response_model=DesignDocumentsResponse)
# async def review_technical_design_documents(session_id: str, request: OwnerFeedbackRequest):
#     feedback = request.feedback

#     if session_id not in active_sessions:
#         raise HTTPException(status_code=404, detail="Session not found")

#     if active_sessions[session_id]["technical_status"] != "pending_approval":
#         raise HTTPException(status_code=400, detail="Technical design documents are not pending approval")

#     try:   
#         thread = {"configurable": {"thread_id": session_id}}
#         document_state = design_document_workflow.get_state(thread) 
#         print("@@next node to call : ", document_state.next)
#         print("@@document_state : ", document_state)

#         design_document_workflow.update_state(thread, { "messages" : HumanMessage(content=feedback)})

#         document_state = None
#         for event in design_document_workflow.stream(None, thread, stream_mode="values"):
#             document_state = event
        
#         print("********* technical document_state : ", document_state)
#         active_sessions[session_id] = {
#             **active_sessions[session_id],
#             "technical_documents": document_state["technical_documents"],
#             "document_messages": document_state["messages"],
#             "technical_status": document_state["technical_status"],
#             "document_version": document_state["version"]
#         }

#         return DesignDocumentsResponse.model_construct(
#             session_id=session_id,
#             document_type=document_state["document_type"],
#             status=document_state["technical_status"],
#             document= technical_document,
#             messages=document_state["messages"]
#         )

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    

# ## Code Development
# @app.post("/code/frontend/generate/{session_id}", response_model=CodeResponse)
# async def generate_frontend_code(session_id: str):
#     print("********* generate_frontend_code : ", session_id)
#     if session_id not in active_sessions:
#         raise HTTPException(status_code=404, detail="Session not found")

#     try:
#         initial_code_state = {
#             "code_type" : "frontend",
#             "frontend_code" : "",
#             "backend_code" : "",
#             "frontend_status" : "in_progress",
#             "backend_status" : "pending",
#             "frontend_messages" : [],
#             "backend_messages" : [],
#             "revised_count" : 0
#         }

#         thread = {"configurable": {"thread_id": session_id}}
#         code_state = None
#         for event in code_development_workflow.stream(initial_code_state, thread, stream_mode="values"):
#             code_state = event

#         print("********* code_state : ", code_state)
#         code_document_state = code_development_workflow.get_state(thread) 
#         print("@@code next node : ", code_document_state.next)

#         active_sessions[session_id] = {
#             **active_sessions[session_id],
#             "frontend_code": code_state["frontend_code"],
#             "frontend_messages": code_state["frontend_messages"],
#             "frontend_status": code_state["frontend_status"],
#         }

#         return CodeResponse.model_construct(
#             session_id=session_id,
#             code_type="frontend",
#             status=code_state["frontend_status"],
#             code=code_state["frontend_code"],
#             messages=code_state["frontend_messages"],
#         )
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @app.post("/code/frontend/review/{session_id}", response_model=CodeResponse)
# async def review_frontend_code(session_id: str, request: OwnerFeedbackRequest):
#     print("********* review_frontend_code : ", session_id)
#     feedback = request.feedback

#     if session_id not in active_sessions:
#         raise HTTPException(status_code=404, detail="Session not found")

#     if active_sessions[session_id]["frontend_status"] != "pending_approval":
#         raise HTTPException(status_code=400, detail="Frontend code is not pending approval")

#     try:   
#         active_sessions[session_id] = {
#             **active_sessions[session_id],    
#             "frontend_code": active_sessions[session_id]["frontend_code"],
#             "frontend_messages": active_sessions[session_id]["frontend_messages"],
#             "frontend_status": "completed",
#         } 
        
#         return CodeResponse.model_construct(
#             session_id=session_id,
#             code_type="frontend",
#             status="completed",
#             code=active_sessions[session_id]["frontend_code"],
#             messages=active_sessions[session_id]["frontend_messages"],
#         )

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/code/backend/generate/{session_id}", response_model=CodeResponse)
# async def generate_backend_code(session_id: str):
#     print("********* generate_backend_code : ", session_id)
#     if session_id not in active_sessions:
#         raise HTTPException(status_code=404, detail="Session not found")

#     try:
#         initial_code_state = {
#             "code_type" : "backend",
#             "backend_code" : "",
#             "backend_status" : "in_progress",
#             "backend_messages" : [],
#             "revised_count" : 0
#         }

#         thread = {"configurable": {"thread_id": session_id}}
#         code_state = None
#         for event in code_development_workflow.stream(initial_code_state, thread, stream_mode="values"):
#             code_state = event

#         print("********* code_state : ", code_state)
#         code_document_state = code_development_workflow.get_state(thread) 
#         print("@@code next node : ", code_document_state.next)

#         active_sessions[session_id] = {
#             **active_sessions[session_id],
#             "backend_code": code_state["backend_code"],
#             "backend_messages": code_state["backend_messages"],
#             "backend_status": code_state["backend_status"],
#         }

#         return CodeResponse.model_construct(
#             session_id=session_id,
#             code_type="backend",
#             status=code_state["backend_status"],
#             code=code_state["backend_code"],
#             messages=code_state["backend_messages"],
#         )
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/code/backend/review/{session_id}", response_model=CodeResponse)
# async def review_backend_code(session_id: str, request: OwnerFeedbackRequest):
#     print("********* review_backend_code : ", session_id)
#     feedback = request.feedback

#     if session_id not in active_sessions:
#         raise HTTPException(status_code=404, detail="Session not found")

#     if active_sessions[session_id]["backend_status"] != "pending_approval":
#         raise HTTPException(status_code=400, detail="Backend code is not in pending approval")

#     try:   
#         active_sessions[session_id] = {
#             **active_sessions[session_id],    
#             "backend_code": active_sessions[session_id]["backend_code"],
#             "backend_messages": active_sessions[session_id]["backend_messages"],
#             "backend_status": "completed",
#         } 
        
#         return CodeResponse.model_construct(
#             session_id=session_id,
#             code_type="backend",
#             status="completed",
#             code=active_sessions[session_id]["backend_code"],
#             messages=active_sessions[session_id]["backend_messages"],
#         )

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

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
