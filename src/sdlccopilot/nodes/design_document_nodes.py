from typing_extensions import Literal
from langchain_core.messages import AIMessage
from src.sdlccopilot.states.document import DocumentState, DocumentSection

## Design documents
def create_design_documents(state: DocumentState) -> DocumentState:
    print("In create_design_documents")

    doc_type = state.document_type.lower()
    is_functional = doc_type == "functional"

    # Define common sections
    document1 = DocumentSection(
        title="INTRODUCTION" if is_functional else "INTRODUCTION & PURPOSE",
        content="This document defines the functional requirements for the Password Reset Feature of the User Management System."
        if is_functional else
        "This document outlines the technical design for the Password Reset functionality as defined in the Functional Specification Document (FSD)."
    )

    document2 = DocumentSection(
        title="BUSINESS CONTEXT",
        content="The business needs a secure mechanism for users to recover access to their accounts without compromising security, improving customer satisfaction and retention.",
    )

    documents = [document1, document2]

    return {
        f"{doc_type}_documents": documents,
        f"{doc_type}_status": 'pending_approval',
        "messages": AIMessage(
            content=f"Please review above {doc_type} design document and provide feedback or type 'Approved' if you're satisfied."
        ),
        "revised_count": 0,
    }

def design_documents_review(state: DocumentState) -> DocumentState:
    print("In design_documents_review")
    message_content = state.messages[-1].content.lower().strip()
    print("user feedback:", message_content)

    approved = message_content == "approved"
    doc_type = state.document_type

    response = {
        "messages": AIMessage(
            content="Great! Your design documents have been finalized. You can now proceed with your next step."
            if approved else
            "I've received your feedback. I'll revise the design documents accordingly."
        ),
        f"{doc_type}_status": "completed" if approved else "feedback"
    }

    return response


def should_revise_design_documents(state: DocumentState) -> Literal["feedback", "approved"]:
    print("In should_revise_design_documents")
    if state.document_type == "functional":
        return "feedback" if state.functional_status == "feedback" else "approved"
    
    if state.document_type == "technical":
        return "feedback" if state.technical_status == "feedback" else "approved"
    
    return "approved"  # Default fallback


def revised_design_documents(state: DocumentState) -> DocumentState:
    print("In revised_design_documents")
    print("state :", state)

    doc_type = None
    if state.functional_status == 'feedback':
        doc_type = "functional"
    elif state.technical_status == 'feedback':
        doc_type = "technical"

    if not doc_type:
        return state  # No feedback status, return state unchanged

    revised_count = state.revised_count + 1
    print("revised_count :", revised_count)

    if revised_count == 3:
        return {
            "messages": AIMessage(
                content="Design documents have been revision maxed out. Please review the above documents and continue with the next step."
            ),
            f"{doc_type}_status": "completed"
        }

    # Define document details dynamically
    document_data = {
        "functional": DocumentSection(
                title = f"Revised Functional Design Document : FUNCTIONAL REQUIREMENTS",
                content = """
                FR-1: The system shall provide a "Forgot Password" option on the login page.  
                FR-2: The system shall send a time-limited reset link to the user's registered email address.  
                FR-3: The system shall validate new passwords against password policy rules.  
                FR-4: The system shall notify users of successful password reset and redirect them to the login page.
            """),
        "technical": DocumentSection(
                title = f"Revised Technical Design Document : MODULES & COMPONENTS DESIGN",
                content = """
                - **Auth API Module:** Exposes RESTful endpoints for password reset request and confirmation  
                - **Token Service Module:** Generates, hashes, stores, and validates password reset tokens  
                - **Notification Service:** Sends password reset links securely via AWS SES  
                - **Audit Logging Module:** Captures all user-initiated reset activities for security auditing
            """,
            )
    }

    doc_info = document_data[doc_type]
    revised_document = DocumentSection(title=doc_info.title, content=doc_info.content)

    return {
        f"{doc_type}_documents": [revised_document],
        "messages": AIMessage(
            content=f"Please review above revised {doc_type} design documents and provide additional feedback or type 'Approved' if you're satisfied."
        ),
        f"{doc_type}_status": "pending_approval",
        "revised_count": revised_count
    }
