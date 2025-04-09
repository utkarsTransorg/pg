from langgraph.graph import StateGraph, START, END
from src.sdlccopilot.states.document import DocumentState
from src.sdlccopilot.nodes.functional_document_nodes import create_design_documents, should_revise_design_documents, revised_design_documents, design_documents_review
from langgraph.checkpoint.memory import MemorySaver

class DesignDocumentGraphBuilder:
    def __init__(self):
        self.design_document_graph=StateGraph(DocumentState)

    def build(self):
        """
        Builds the design document graph.
        """
        self.design_document_graph.add_node("create_design_documents", create_design_documents)
        self.design_document_graph.add_node("design_documents_review", design_documents_review)
        self.design_document_graph.add_node("revised_design_documents", revised_design_documents)

        self.design_document_graph.add_edge(START, "create_design_documents")
        self.design_document_graph.add_edge("create_design_documents", "design_documents_review")
        self.design_document_graph.add_conditional_edges(
            "design_documents_review",
            should_revise_design_documents,
            {
                "feedback" : "revised_design_documents",
                "approved" : END
            }
        )
        self.design_document_graph.add_edge("revised_design_documents", "design_documents_review")
        memory = MemorySaver()
        design_document_workflow = self.design_document_graph.compile(checkpointer=memory, interrupt_before=['design_documents_review'])
        return design_document_workflow
