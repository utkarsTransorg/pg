from src.sdlccopilot.prompts.prompt_template import json_prompt_template
from src.sdlccopilot.prompts.user_story import generate_user_stories_system_prompt, revised_user_stories_system_prompt
from src.sdlccopilot.prompts.prompt_template import json_output_parser
from src.sdlccopilot.logger import logging

class UserStoryHelper:
    def __init__(self, llm):
        self.llm = llm
        
    def generate_user_stories_with_llm(self, project_title, project_description, requirements):
        logging.info("Generating user stories with LLM...")
        user_query =  f"Create a user stories for the this project title: {project_title} and description: {project_description} and requirements: {requirements}"
        chain = json_prompt_template | self.llm | json_output_parser
        response = chain.invoke({"system_prompt" : generate_user_stories_system_prompt, "human_query" : user_query})
        logging.info("User stories generated with LLM.")
        return response

    def revised_user_stories_with_llm(self, user_stories, user_feedback):
        logging.info("Revising user stories with LLM...")
        user_query =  f"user_feedback: {user_feedback} and user_stories: {user_stories}"
        chain = json_prompt_template | self.llm | json_output_parser
        response = chain.invoke({"system_prompt" : revised_user_stories_system_prompt, "human_query" : user_query})
        logging.info("User stories revised with LLM.")
        return response

