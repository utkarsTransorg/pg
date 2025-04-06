from langchain_core.prompts import PromptTemplate 
from langchain_core.output_parsers import JsonOutputParser 
output_parser = JsonOutputParser()

generate_user_story_prompt = PromptTemplate(
    template="{system_prompt} \n {format_instruction} \n {human_query} \n",
    input_variables= ["system_prompt", "human_query",],
    partial_variables={"format_instruction" : output_parser.get_format_instructions()}
)

generate_user_stories_system_prompt = """
**ROLE & OBJECTIVE**

You are an expert Agile Product Owner. Your task is to analyze structured project requirements and generate clear, actionable 4 to 6 user stories ready for development. Return the OUTPUT in the JSON format only. 

---

**TASK BREAKDOWN:**
1. **Analyze** project requirements, objectives, and user needs.
2. **Extract** core features and define user roles.
3. **Decompose** requirements into independent, testable user stories.
4. **Generate** user stories using:
   - **As a [user], I want [goal], so that [value].**
   - Clear, testable **acceptance criteria**.
5. **Prioritize** based on business impact and feasibility.

---

**DESIRED OUTPUT TEMPLATE IN LIST OF JSON**
```json
[
    {
        "story_id"="US-001",
        "title"="Manage Shopping Cart",
        "description"="As a shopper, I want to modify my cart before checkout.",
        "acceptance_criteria"=[
            "User can add/remove items.",
            "User can update item quantity.",
            "Cart updates reflect in real-time.",
            "User can see the total price of the cart."
        ]
    }
]
```

---

**GUIDELINES:**
✅ Align with project requirements.
✅ Use concise, clear language.
✅ Ensure user stories are independent and testable.
✅ Prioritize based on business impact.
✅ The **acceptance criteria must be between 2 to 4 points**—no more, no less.  
🚫 Avoid vagueness, missing criteria, or unnecessary technical details.
"""


revised_user_stories_system_prompt = """
# **ROLE & OBJECTIVE**  
You are an expert Agile Product Owner. Your task is to analyze the user stories based on user feedback and refine user stories with existing user stories and return the output in the JSON format only. 

---

TASK BREAKDOWN:  
1. Analyze `user_story` and `user_feedback`.  
2. Identify gaps and improve clarity.  
3. Ensure user stories follow:  
   - "As a [user], I want [goal], so that [value]."  
   - **2 to 4** clear, testable acceptance criteria.  

---

**DESIRED OUTPUT TEMPLATE IN LIST OF JSON**  
```json
[
    {  
        "story_id": "US-001",  
        "title": "Manage Shopping Cart",  
        "description": "As a shopper, I want to modify my cart before checkout, so that I can finalize my purchase conveniently.",  
        "acceptance_criteria": [  
            "User can add/remove items.",  
            "User can update item quantity.",  
            "Cart updates reflect in real-time.",  
            "User can see the total price of the cart."
        ]  
    }  
]  
```

---

GUIDELINES:  
✅ Ensure stories are clear, independent, and testable.  
✅ Incorporate feedback without losing business goals.  
✅ Acceptance criteria must be **2 to 4** points.  
🚫 Avoid unnecessary technical details or vague requirements.  
"""


CONSTANT_USER_STORIES = [
        {
            "story_id": "US-001",
            "title": "Enable Multi-Factor Authentication",
            "description": "As a user, I want to secure my account with multi-factor authentication so that my financial data remains protected.",
            "acceptance_criteria": [
                "User can enable biometric authentication (fingerprint and facial recognition).",
                "User can set up an MPIN for additional security.",
                "System requires MFA for every login.",
                "User can opt out of biometric authentication for individual sessions.",
                "System automatically logs out after 5 minutes of inactivity."
            ]
        },
        {
            "story_id": "US-002",
            "title": "Link Multiple Bank Accounts",
            "description": "As a user, I want to link multiple bank accounts to my PayMate profile so that I can manage all my financial transactions in one place.",
            "acceptance_criteria": [
                "User can add multiple bank accounts to their profile.",
                "User can select a default account for transactions.",
                "User can remove or edit linked accounts.",
                "System displays real-time UPI IDs for each linked account.",
                "User receives a confirmation message after linking/unlinking an account."
            ]
        },
        {
            "story_id": "US-003",
            "title": "Perform Instant Fund Transfers",
            "description": "As a user, I want to transfer funds instantly using UPI so that I can send money to anyone quickly and securely.",
            "acceptance_criteria": [
                "User can send money to any UPI ID.",
                "User can send money to a mobile number linked to a UPI account.",
                "User can scan a QR code to initiate a transfer.",
                "System confirms the transfer in real-time.",
                "User receives a transaction receipt post-transfer."
            ]
        },
        {
            "story_id": "US-004",
            "title": "Access Instant Micro-Loans",
            "description": "As a user, I want to apply for an instant micro-loan so that I can meet urgent financial needs without hassle.",
            "acceptance_criteria": [
                "User can view available loan options with terms and conditions.",
                "User can apply for a micro-loan with minimal documentation.",
                "System provides instant approval status.",
                "Approved loan amount is disbursed immediately to the user's linked account.",
                "User can view repayment options and due dates."
            ]
        },
        {
            "story_id": "US-005",
            "title": "Pay Utility Bills",
            "description": "As a user, I want to pay my utility bills directly through the app so that I can manage all my payments in one place.",
            "acceptance_criteria": [
                "User can add utility bill payees (e.g., electricity, water, gas, broadband).",
                "User can view pending bills and due dates.",
                "User can make payments using their linked bank account or UPI.",
                "System sends a confirmation upon successful payment.",
                "User can view a history of past utility payments."
            ]
        },
        {
            "story_id": "US-006",
            "title": "View Transaction History",
            "description": "As a user, I want to view my transaction history so that I can keep track of all my financial activities.",
            "acceptance_criteria": [
                "User can view a detailed list of all transactions (payments, transfers, loans, bill payments).",
                "User can filter transactions by date range, type, or amount.",
                "User can search for specific transactions.",
                "User can download transaction statements in PDF or CSV format.",
                "System updates the transaction history in real-time."
            ]
        },
        {
            "story_id": "US-007",
            "title": "Manage User Profile",
            "description": "As a user, I want to manage my profile information so that my details are up-to-date and secure.",
            "acceptance_criteria": [
                "User can edit personal details (name, email, mobile number).",
                "User can change their MPIN or biometric authentication settings.",
                "User can update their default bank account.",
                "User can view their account creation date and last login time.",
                "System requires authentication for profile changes."
            ]
        },
        {
            "story_id": "US-008",
            "title": "Access Customer Support",
            "description": "As a user, I want to access customer support directly through the app so that I can resolve any issues quickly.",
            "acceptance_criteria": [
                "User can chat with a live customer support agent.",
                "User can raise a support ticket for unresolved issues.",
                "User can view a list of frequently asked questions (FAQs).",
                "User can call a customer support hotline.",
                "System provides an estimated response time for support inquiries."
            ]
        },
        {
            "story_id": "US-009",
            "title": "Receive Transaction Notifications",
            "description": "As a user, I want to receive notifications for all transactions so that I can stay informed about my financial activities.",
            "acceptance_criteria": [
                "User receives a push notification for every successful transaction.",
                "User receives an email confirmation for every transaction.",
                "User can customize notification preferences (e.g., disable specific types of notifications).",
                "User can view a history of past notifications in the app.",
                "System sends notifications in real-time."
            ]
        }
    ]
