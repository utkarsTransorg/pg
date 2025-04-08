from src.sdlccopilot.graph.sdlc_graph import SDLCGraphBuilder
from IPython.display import Image, display
from langchain_core.messages import HumanMessage
from src.sdlccopilot.logger import logging

if __name__ == "__main__":
    logging.info("***** Starting the workflow test *****")
    builder = SDLCGraphBuilder()
    sdlc_workflow = builder.build()
    
    project_title = "PayMate: Your Ultimate Payment Companion"
    project_description = "PayMate is a comprehensive payment application that allows users to perform seamless transactions using the Unified Payments Interface (UPI). Beyond basic payments, PayMate offers features such as quick loans, bill payments, and a user-friendly interface, making it a one-stop solution for all financial needs."
    requirements = ["Implement multi-factor authentication, including biometrics (fingerprint and facial recognition) and MPIN, to secure user accounts.​", "Enable users to link multiple bank accounts and perform instant fund transfers using UPI.", "Provide users with access to instant micro-loans with minimal documentation.", "Allow users to pay utility bills such as electricity, water, gas, and broadband directly through the app."]
    
    project_requirements = {
        "title" : project_title,
        "description" : project_description,
        "requirements" : requirements
    }

    ## 1. User Story Generation
    
    logging.info("** 1. User Story Generation **")
    initial_story_state = {
        "project_requirements" : project_requirements,
        "user_stories": [],
        "user_story_messages": HumanMessage(content=f"{project_requirements}"),
        "user_story_status": "in_progress",
        "revised_count" : 0,
    }
    # Thread
    thread = {"configurable": {"thread_id": "111"}}

    state = None
    for event in sdlc_workflow.stream(initial_story_state, thread, stream_mode="values"):
        state = event

    logging.info("** User Story Generated Successfully **")
    
    user_feedback = "In above user stories, add a user story for buy insurance from the app and return all the user stories"
    logging.info("** User Feedback : ", user_feedback)
    sdlc_workflow.update_state(thread, { "user_story_messages" : HumanMessage(content=f'{user_feedback}')})

    for event in sdlc_workflow.stream(None, thread, stream_mode="values"):
        state = event
    
    logging.info("** User Feedback Applied Successfully **")

    logging.info("** Approving User Stories **")
    sdlc_workflow.update_state(thread, { "user_story_messages" : HumanMessage(content='Approved'), "revised_count" : 0})

    for event in sdlc_workflow.stream(None, thread, stream_mode="values"):
        state = event

    logging.info("** User Stories Approved Successfully **")
    # print(display(Image(workflow.get_graph().draw_mermaid_png())))