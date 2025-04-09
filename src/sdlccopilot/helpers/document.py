from src.sdlccopilot.prompts.prompt_template import prompt_template
from src.sdlccopilot.prompts.document import functional_document_system_prompt, revised_functional_document_system_prompt, technical_document_system_prompt, revised_technical_document_system_prompt
from src.sdlccopilot.logger import logging

class DocumentHelper:
    def __init__(self, llm):
        self.llm = llm

    def generate_functional_document_from_llm(self, user_stories):
        logging.info("Generating functional document with LLM...")
        user_query =  f"Create a functional documents for the user stories: {user_stories}."
        chain = prompt_template | self.llm 
        response = chain.invoke({"system_prompt" : functional_document_system_prompt, "human_query" : user_query})
        logging.info("Functional document generated with LLM.")
        return response.content
    
    def revised_functional_document_from_llm(self, functional_document, user_feedback):
        logging.info("Revising functional document with LLM...")
        user_query =  f"Revise the functional document : {functional_document} and by following the user feedback: {user_feedback}. and return the complete revised functional document. "
        chain = prompt_template | self.llm 
        response = chain.invoke({"system_prompt" : revised_functional_document_system_prompt, "human_query" : user_query})
        logging.info("Functional document revised with LLM.")
        return response.content

    def generate_technical_document_from_llm(self, functional_document, user_stories):
        logging.info("Generating technical document with LLM...")
        user_query =  f"Create technical documents for the user stories: {user_stories} and the functional document: {functional_document}"
        chain = prompt_template | self.llm 
        response = chain.invoke({"system_prompt" : technical_document_system_prompt, "human_query" : user_query})
        logging.info("Technical document generated with LLM.")
        return response.content

    def revised_technical_document_from_llm(self, technical_document, user_feedback):
        logging.info("Revising technical document with LLM...")
        user_query =  f"Revise the technical document: {technical_document} and by following the user feedback: {user_feedback}."
        chain = prompt_template | self.llm 
        response = chain.invoke({"system_prompt" : revised_technical_document_system_prompt, "human_query" : user_query})
        logging.info("Technical document revised with LLM.")
        return response.content