
from langchain_core.messages import AIMessage
from src.sdlccopilot.states.story import UserStory, UserStoryState
from src.sdlccopilot.chains.user_story import UserStoryChain
from src.sdlccopilot.prompts.user_story import CONSTANT_USER_STORIES
from src.sdlccopilot.logger import logging

class UserStoryNodes:
    def __init__(self, llm): 
        self.llm = llm

    def process_project_requirements(self, state : UserStoryState) -> UserStoryState:
        logging.info("In process_project_requirements")
        return {
            **state,
            "user_stories_messages" : AIMessage(content="I've received your project requirements. I'll now generate user stories based on these requirements.")
        }

    def generate_user_stories(self, state : UserStoryState) -> UserStoryState:
        logging.info("In generate_user_stories")
        title = state['project_requirements']['title']
        description = state['project_requirements']['description']
        requirements = state['project_requirements']['requirements']
        # user_story_chain = UserStoryChain(self.llm)
        # user_stories = user_story_chain.get_user_story_from_llm(title, description, requirements)
        user_stories = CONSTANT_USER_STORIES
        logging.info(f"user_stories : {user_stories}")
        return {
            **state, 
            "status" : 'pending_approval',
            "user_stories" : user_stories,
            "user_stories_messages" : AIMessage(
                content = f"Based on your requirements, I've generated {len(user_stories)} user stories. Please review these user stories and provide feedback or type 'Approved' if you're satisfied."
            ),
            "revised_count" : 0
        }

    
    def user_stories_review(self, state : UserStoryState) -> UserStoryState:
        logging.info("In user_stories_review")
        user_message = state['user_stories_messages'][-1].content
        user_message = user_message.lower().strip()
        if user_message == "approved":
            return {
                **state,
                "user_stories_messages" : AIMessage(content="Great! Your user stories have been finalized. You can now proceed with your design process."),
                "status" : "completed"
            }
        else:
            return {
                **state,
                "user_stories_messages" :  AIMessage(content="I've received your feedback. I'll revise the user stories accordingly."),
                "status" : "feedback"
            }

    def revised_user_stories(self, state : UserStoryState) -> UserStoryState:
        logging.info("In revised_user_stories")
        if state['status'] == 'feedback':
            revised_count = state['revised_count'] + 1
            if revised_count == 3:
                return {
                    **state,
                    "user_stories_messages" :  AIMessage(
                        content = f"User stories have been revision maxed out. Please review the user stories and continue with the next step."
                    ),
                    "status" : "completed"
                }
        
            revised_user_story = UserStory(
                story_id = "IND-101",
                title = f"Revised User Story {revised_count}",
                description = "As a user, I want to log in using email and password.",
                acceptance_criteria = ["User can input email and password", "System validates credentials", "User is redirected after login"],
            )
            revised_user_stories = [revised_user_story]
            return {
                **state, 
                "user_stories" : revised_user_stories,
                "user_stories_messages" : AIMessage(
                    content = "I've revised the user stories based on your feedback.\n\nPlease review these updated user stories and provide additional feedback or type 'Approved' if you're satisfied."),
                "status" : "pending_approval",
                "revised_count" : revised_count
            }



# ## User stories 
# def process_project_requirements(state : UserStoryState) -> UserStoryState:
#     print("In process_project_requirements")
#     return {
#         **state,
#         "user_stories_messages" : AIMessage(content="I've received your project requirements. I'll now generate user stories based on these requirements.")
#     }

# def generate_user_stories(state : UserStoryState) -> UserStoryState:
#     print("In generate_user_stories")
#     # TODO - LLM call to generate the user stories
#     # user_story = UserStory(
#     #     story_id = "US-101",
#     #     title = "User Login",
#     #     description = "As a user, I want to log in using email and password.",
#     #     acceptance_criteria = ["User can input email and password", "System validates credentials", "User is redirected after login"],
#     # )
#     # generated_stories = [user_story]

#     generated_stories = [
#         {
#             "id": "US-101",
#             "title": "User Authentication",
#             "description": "As a user, I want to log in securely using multi-factor authentication, including biometrics and MPIN.",
#             "acceptance_criteria": [
#             "User can log in using email and password",
#             "User is prompted for MPIN after entering credentials",
#             "User can enable biometric authentication for faster login",
#             "Login fails if incorrect MPIN or biometric authentication fails"
#             ]
#         },
#         {
#             "id": "US-102",
#             "title": "Bank Account Linking",
#             "description": "As a user, I want to link multiple bank accounts to the app so that I can manage transactions easily.",
#             "acceptance_criteria": [
#             "User can enter bank details and verify account ownership",
#             "System fetches bank details using UPI integration",
#             "User can link multiple bank accounts",
#             "Linked accounts are displayed on the dashboard"
#             ]
#         },
#         {
#             "id": "US-103",
#             "title": "UPI Fund Transfer",
#             "description": "As a user, I want to send and receive money instantly using UPI.",
#             "acceptance_criteria": [
#             "User can enter the recipient’s UPI ID or phone number",
#             "System verifies the recipient's details before initiating the transaction",
#             "User can enter the amount and confirm payment using MPIN",
#             "Transaction status (success/failure) is displayed to the user"
#             ]
#         },
#         {
#             "id": "US-104",
#             "title": "Instant Micro-Loan Access",
#             "description": "As a user, I want to apply for an instant micro-loan with minimal documentation.",
#             "acceptance_criteria": [
#             "User can check loan eligibility in the app",
#             "System fetches minimal documentation (e.g., Aadhaar, PAN) for verification",
#             "User can select loan amount and tenure",
#             "Loan disbursal status is shown after approval"
#             ]
#         },
#         {
#             "id": "US-105",
#             "title": "Utility Bill Payments",
#             "description": "As a user, I want to pay my utility bills directly through the app.",
#             "acceptance_criteria": [
#             "User can choose a biller (electricity, water, gas, broadband, etc.)",
#             "User enters bill details or fetches outstanding bill using linked accounts",
#             "System processes the bill payment via UPI or linked bank account",
#             "Confirmation receipt is generated after a successful transaction"
#             ]
#         },
#         {
#             "id": "US-106",
#             "title": "Transaction History",
#             "description": "As a user, I want to view my past transactions in the app.",
#             "acceptance_criteria": [
#             "User can see a list of past transactions sorted by date",
#             "Each transaction shows the amount, recipient, and status",
#             "User can filter transactions by type (UPI, loan, bill payment, etc.)",
#             "User can download transaction history in PDF format"
#             ]
#         },
#         {
#             "id": "US-107",
#             "title": "Push Notifications",
#             "description": "As a user, I want to receive notifications for successful and failed transactions.",
#             "acceptance_criteria": [
#             "User receives a push notification for each completed transaction",
#             "User is notified of failed transactions with the reason",
#             "Notifications include transaction amount and status",
#             "User can disable notifications in settings"
#             ]
#         },
#         {
#             "id": "US-108",
#             "title": "QR Code Payments",
#             "description": "As a user, I want to scan a QR code to make instant payments.",
#             "acceptance_criteria": [
#             "User can open a QR scanner within the app",
#             "System fetches recipient details from the QR code",
#             "User can enter the amount and confirm payment using MPIN or biometrics",
#             "Payment confirmation is displayed after a successful transaction"
#             ]
#         },
#         {
#             "id": "US-109",
#             "title": "Customer Support Chat",
#             "description": "As a user, I want to chat with customer support for transaction-related queries.",
#             "acceptance_criteria": [
#             "User can access a chat feature in the app",
#             "User can choose a predefined query or type a custom query",
#             "System provides automated responses for common questions",
#             "User can connect with a live agent if the issue is unresolved"
#             ]
#         },
#         {
#             "id": "US-110",
#             "title": "Profile Management",
#             "description": "As a user, I want to manage my profile details and app settings.",
#             "acceptance_criteria": [
#             "User can update personal details such as name, email, and phone number",
#             "User can change MPIN and enable/disable biometric authentication",
#             "User can manage linked bank accounts",
#             "Settings changes are saved and reflected immediately"
#             ]
#         }
#     ]
#     return {
#         **state, 
#         "status" : 'pending_approval',
#         "user_stories" : generated_stories,
#         "user_stories_messages" : AIMessage(
#             content = "Please review above user stories and provide feedback or type 'Approved' if you're satisfied."
#         ),
#         "revised_count" : 0
#     }

# def user_stories_review(state : UserStoryState) -> UserStoryState:
#     print("In user_stories_review")
#     user_message = state['user_stories_messages'][-1].content
#     user_message = user_message.lower().strip()
#     print("user_message : ", user_message)  
#     if user_message == "approved":
#         return {
#             **state,
#             "user_stories_messages" : AIMessage(content="Great! Your user stories have been finalized. You can now proceed with your next step."),
#             "status" : "completed"
#         }
#     else:
#         return {
#             **state,
#             "user_stories_messages" :  AIMessage(content="I've received your feedback. I'll revise the user stories accordingly."),
#             "status" : "feedback"
#         }

# def should_revise_user_stories(state : UserStoryState) -> Literal["approved", "feedback"]:
#     print("In should_revise_user_stories")
#     print("state : ", state)
#     return "approved" if state["status"] == "approved" else "feedback"   

# def revised_user_stories(state : UserStoryState) -> UserStoryState:
#     print("In revised_user_stories")
#     print("state : ", state)
#     if state['status'] == 'feedback':
#         revised_count = state['revised_count'] + 1
#         print("revised_count : ", revised_count)
#         if revised_count == 3:
#             return {
#                 **state,
#                 "user_stories_messages" :  AIMessage(
#                     content = f"User stories have been revision maxed out. Please review the user stories and continue with the next step."
#                 ),
#                 "status" : "completed"
#             }
       
#         revised_user_story = UserStory(
#             story_id = "IND-101",
#             title = f"Revised User Story {revised_count}",
#             description = "As a user, I want to log in using email and password.",
#             acceptance_criteria = ["User can input email and password", "System validates credentials", "User is redirected after login"],
#         )
#         revised_user_stories = [revised_user_story]

#         return {
#             **state, 
#             "user_stories" : revised_user_stories,
#             "user_stories_messages" : AIMessage(
#                 content = "Please review above revised user stories and provide feedback or type 'Approved' if you're satisfied."),
#             "status" : "pending_approval",
#             "revised_count" : revised_count
#         }
