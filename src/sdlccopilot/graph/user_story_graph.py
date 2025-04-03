from langgraph.graph import StateGraph, START, END
from src.sdlccopilot.states.story import UserStoryState
from langgraph.checkpoint.memory import MemorySaver
from src.sdlccopilot.nodes.user_story_nodes import UserStoryNodes
from typing import Literal

class UserStoryGraphBuilder:
    def __init__(self, llm):
        self.llm = llm
        self.graph_builder=StateGraph(UserStoryState)

    def should_revise_user_stories(self, state : UserStoryState) -> Literal["approved", "feedback"]:
        return "approved" if state["status"] == "approved" else "feedback"   

    def build(self):
        """
        Builds the user story graph.
        """
        story_nodes = UserStoryNodes(self.llm)
        self.graph_builder.add_node("process_project_requirements", story_nodes.process_project_requirements)
        self.graph_builder.add_node("generate_user_stories", story_nodes.generate_user_stories)
        self.graph_builder.add_node("user_stories_review", story_nodes.user_stories_review)
        self.graph_builder.add_node("revised_user_stories", story_nodes.revised_user_stories)
        
        self.graph_builder.add_edge(START, "process_project_requirements")
        self.graph_builder.add_edge("process_project_requirements", "generate_user_stories")
        self.graph_builder.add_edge("generate_user_stories", "user_stories_review")
        self.graph_builder.add_conditional_edges(
            "user_stories_review", self.should_revise_user_stories, {'approved' : END, 'feedback' : 'revised_user_stories'}
        )

        self.graph_builder.add_edge("revised_user_stories", "user_stories_review")
        memory = MemorySaver()
        user_story_workflow = self.graph_builder.compile(checkpointer=memory, interrupt_before=['user_stories_review'])
        return user_story_workflow
