from langgraph.graph import StateGraph, START, END
from src.sdlccopilot.states.code import CodeState
from src.sdlccopilot.nodes.code_development_nodes import generate_code, code_review, should_fix_code, fix_code
from langgraph.checkpoint.memory import MemorySaver

class CodeDevelopmentGraphBuilder:
    def __init__(self):
        self.code_development_graph=StateGraph(CodeState)

    def build(self):
        """
        Builds the code development graph.
        """
        self.code_development_graph.add_node("generate_code", generate_code)
        self.code_development_graph.add_node("code_review", code_review) 
        self.code_development_graph.add_node("fix_code", fix_code)

        self.code_development_graph.add_edge(START, "generate_code")
        self.code_development_graph.add_edge("generate_code", "code_review")
        self.code_development_graph.add_conditional_edges(
            "code_review",
            should_fix_code, 
            {
                "feedback" : "fix_code",
                "approved" : END
            }
        )
        self.code_development_graph.add_edge("fix_code", "code_review")
        memory = MemorySaver()
        code_workflow = self.code_development_graph.compile(checkpointer=memory, interrupt_before=['code_review'])
        return code_workflow

# if __name__ == "__main__":
    # builder = CodeDevelopmentGraphBuilder()
    # workflow = builder.build()
    # print(display(Image(workflow.get_graph().draw_mermaid_png())))

