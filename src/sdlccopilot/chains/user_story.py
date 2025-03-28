from langchain_core.output_parsers import JsonOutputParser 
from src.sdlccopilot.prompts.user_story import generate_user_story_prompt, generate_user_story_system_prompt
from src.sdlccopilot.logger import logging

output_parser = JsonOutputParser()

class UserStoryChain:
    def __init__(self, llm):
        self.llm = llm

    def get_user_story_from_llm(self, title, description, requirements):
        logging.info(f"title : {title}")
        logging.info(f"description : {description}")
        logging.info(f"requirements : {requirements}")

        user_query =  f"Create a user story for the this project title: {title} and description: {description} and requirements: {requirements}"
        logging.info(f"user_query : {user_query}")
        chain = generate_user_story_prompt | self.llm | output_parser
        response = chain.invoke({"system_prompt" : generate_user_story_system_prompt, "human_query" : user_query})
        logging.info(f"response : {response}")
        return response

