
from langchain_anthropic import ChatAnthropic

class AnthropicLLM:
    def __init__(self, model_name):
        self.model_name = model_name
        pass

    def get(self):
        return ChatAnthropic(
            model= self.model_name,
            temperature=0,
            max_tokens=8000,
            max_retries=2
        )
    