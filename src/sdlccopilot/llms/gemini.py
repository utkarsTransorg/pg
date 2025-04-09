
from langchain_google_genai import ChatGoogleGenerativeAI

class GeminiLLM:
    def __init__(self, model_name):
        self.model_name = model_name
        pass

    def get(self):
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )