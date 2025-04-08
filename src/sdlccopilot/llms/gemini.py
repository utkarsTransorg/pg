
from langchain_google_genai import ChatGoogleGenerativeAI

class GeminiLLM:
    def __init__(self):
        pass

    def get(self):
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )