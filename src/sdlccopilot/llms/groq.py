from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
import os 

os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
os.environ['LANGSMITH_API_KEY'] = os.getenv("LANGSMITH_API_KEY")
os.environ['LANGSMITH_PROJECT'] = os.getenv("LANGSMITH_PROJECT")
os.environ['LANGSMITH_TRACING'] = os.getenv("LANGSMITH_TRACING")

class GroqLLM:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def get(self):
        return ChatGroq(model=self.model_name)
    
