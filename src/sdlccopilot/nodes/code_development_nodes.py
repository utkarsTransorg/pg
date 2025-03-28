from typing import Literal
from src.sdlccopilot.prompts.frontend_code import frontend_code
from src.sdlccopilot.prompts.backend_code import backend_code
from src.sdlccopilot.states.code import CodeState
from langchain_core.messages import AIMessage

def generate_code(state : CodeState) -> CodeState:
    print("In generate_code")
    code_type = state.code_type.lower()

    generate_code = ''
    if code_type == 'frontend' :
        generate_code = frontend_code
    else:
        generate_code = backend_code

    return {
        "code_type" : code_type,
        f"{code_type}_code" : generate_code,
        f"{code_type}_status": 'pending_approval',
        f"{code_type}_messages": AIMessage(
            content=f"Please review above {code_type} design document and provide feedback or type 'Approved' if you're satisfied."
        ),
    }

def code_review(state : CodeState) -> CodeState:
    print("In code_review")

    message_content = ''
    if state.code_type == 'frontend':
        message_content = state.frontend_messages[-1].content.lower().strip()
    else : 
        message_content = state.backend_messages[-1].content.lower().strip()

    print("user feedback:", message_content)
    approved = message_content == "approved"
    code_type = state.code_type.lower()

    return {
        f"{code_type}_messages":AIMessage(
            content="Great! Code have been finalized. You can now proceed with next steps."
            if approved else
            "I've received your feedback. I'll revise the design documents accordingly."),
        f"{code_type}_status": "completed" if approved else "feedback"
    }


def should_fix_code(state : CodeState) -> Literal["feedback", "approved"]:
    print("In should_fix_code")
    if state.code_type == 'frontend':
        return "feedback" if state.frontend_status == "feedback" else "approved"
    
    if state.code_type == 'backend':
        return "feedback" if state.backend_status == "feedback" else "approved"
    
    return "approved"


def fix_code(state : CodeState) -> CodeState:
    print("In fix_code")

    code_type = None
    if state.frontend_status == 'feedback':
        code_type = "frontend"
    elif state.backend_status == 'feedback':
        code_type = "backend"

    if not code_type:
        return state  # No feedback status, return state unchanged

    revised_count = state.revised_count + 1
    print("revised_count :", revised_count)

    if revised_count == 3:
        return {
            "messages": AIMessage(
                content="Code have been revision maxed out. Please review the above code and continue with the next step."
            ),
            f"{code_type}_status": "completed"
        }
    
    revised_code = ''
    if code_type == 'frontend' :
        revised_code = "console.log('Revised frontend')"
    else:
        revised_code = "print('Revised backend!')"

    return {
        f"{code_type}_code": revised_code,
        f"{code_type}_messages": AIMessage(
            content=f"Please review above revised {code_type} code and provide additional feedback or type 'Approved' if you're satisfied."
        ),
        f"{code_type}_status": "pending_approval",
        "revised_count": revised_count
    }