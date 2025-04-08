
from langgraph.graph import StateGraph, START, END
from src.sdlccopilot.states.sdlc import SDLCState
from langgraph.checkpoint.memory import MemorySaver
from src.sdlccopilot.nodes.user_story_nodes import UserStoryNodes
from IPython.display import Image, display
from src.sdlccopilot.llms.gemini import GeminiLLM
from src.sdlccopilot.logger import logging

gemini_llm = GeminiLLM().get()

class SDLCGraphBuilder:
    def __init__(self):
        self.sdlc_graph_builder=StateGraph(SDLCState)

    def build(self):
        """
        Builds the SDLC graph.
        """
        logging.info("Building SDLC graph...")
        story_node = UserStoryNodes(gemini_llm)
        self.sdlc_graph_builder.add_node("process_project_requirements", story_node.process_project_requirements)
        self.sdlc_graph_builder.add_node("generate_user_stories", story_node.generate_user_stories)
        self.sdlc_graph_builder.add_node("review_user_stories", story_node.review_user_stories)
        self.sdlc_graph_builder.add_node("revised_user_stories", story_node.revised_user_stories)
        
        self.sdlc_graph_builder.add_edge(START, "process_project_requirements")
        self.sdlc_graph_builder.add_edge("process_project_requirements", "generate_user_stories")
        self.sdlc_graph_builder.add_edge("generate_user_stories", "review_user_stories")
        self.sdlc_graph_builder.add_conditional_edges(
            "review_user_stories", story_node.should_revise_user_stories, {'approved' : END, 'feedback' : 'revised_user_stories'}
        )
        
        self.sdlc_graph_builder.add_edge("revised_user_stories", "review_user_stories")
        memory = MemorySaver()
        sdlc_workflow = self.sdlc_graph_builder.compile(checkpointer=memory, interrupt_before=['review_user_stories'])
        logging.info("SDLC workflow built successfully !!!")
        return sdlc_workflow