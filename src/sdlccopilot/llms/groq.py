from langchain_groq import ChatGroq
class GroqLLM:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def get(self):
        return ChatGroq(model=self.model_name)