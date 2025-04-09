from src.sdlccopilot.prompts.prompt_template import prompt_template
from src.sdlccopilot.prompts.code import CODE_SYSTEM_PROMPT, FRONTEND_PROMPT, BACKEND_PROMPT
from src.sdlccopilot.logger import logging

class CodeHelper:
    def __init__(self, llm):
        self.llm = llm
    
    def generate_frontend_code_from_llm(self, user_stories):
        logging.info("Generating frontend code with LLM...")
        user_query =  f"Analyze these user stories {user_stories} and generate a frontend react + vite code. {FRONTEND_PROMPT}."
        chain = prompt_template | self.llm 
        response = chain.invoke({"system_prompt" : CODE_SYSTEM_PROMPT, "human_query" : user_query})
        logging.info("Frontend code generated with LLM.")
        return response.content

    def revised_frontend_code_from_llm(self, code, user_feedback):
        logging.info("Revising frontend code with LLM...")
        user_query =  f"Analyze this React frontend code: {code} and revise it according to user feedback: {user_feedback} and {FRONTEND_PROMPT}."
        chain = prompt_template | self.llm 
        response = chain.invoke({"system_prompt" : CODE_SYSTEM_PROMPT, "human_query" : user_query})
        logging.info("Frontend code revised with LLM.")
        return response.content
    
    def generate_backend_code_from_llm(self, user_stories):
        logging.info("Generating backend code with LLM...")
        user_query =  f"Analyze these user stories {user_stories} and generate a nodejs backend code. {BACKEND_PROMPT}."
        chain = prompt_template | self.llm 
        response = chain.invoke({"system_prompt" : CODE_SYSTEM_PROMPT, "human_query" : user_query})
        logging.info("Backend code generated with LLM.")
        return response.content
    
    def revised_backend_code_from_llm(self, code, user_feedback):
        logging.info("Revising backend code with LLM...")
        user_query =  f"Analyze this backend code: {code} and revise it according to user feedback: {user_feedback} and {BACKEND_PROMPT}."
        chain = prompt_template | self.llm 
        response = chain.invoke({"system_prompt" : CODE_SYSTEM_PROMPT, "human_query" : user_query})
        logging.info("Backend code revised with LLM.")
        return response.content


