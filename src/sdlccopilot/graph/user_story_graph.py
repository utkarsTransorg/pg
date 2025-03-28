from langgraph.graph import StateGraph, START, END
from src.sdlccopilot.states.story import UserStoryState
from src.sdlccopilot.nodes.user_story_nodes import process_project_requirements, generate_user_stories, user_stories_review, should_revise_user_stories, revised_user_stories
from langgraph.checkpoint.memory import MemorySaver

class UserStoryGraphBuilder:
    def __init__(self):
        self.graph_builder=StateGraph(UserStoryState)

    def build(self):
        """
        Builds the user story graph.
        """
        self.graph_builder.add_node("process_project_requirements", process_project_requirements)
        self.graph_builder.add_node("generate_user_stories", generate_user_stories)
        self.graph_builder.add_node("user_stories_review", user_stories_review)
        self.graph_builder.add_node("should_revise_user_stories", should_revise_user_stories)
        self.graph_builder.add_node("revised_user_stories", revised_user_stories)
        
        self.graph_builder.add_edge(START, "process_project_requirements")
        self.graph_builder.add_edge("process_project_requirements", "generate_user_stories")
        self.graph_builder.add_edge("generate_user_stories", "user_stories_review")
        self.graph_builder.add_conditional_edges(
        "user_stories_review", should_revise_user_stories, {'approved' : END, 'feedback' : 'revised_user_stories'}
        )

        self.graph_builder.add_edge("revised_user_stories", "user_stories_review")
        memory = MemorySaver()
        user_story_workflow = self.graph_builder.compile(checkpointer=memory, interrupt_before=['user_stories_review'])
        return user_story_workflow
