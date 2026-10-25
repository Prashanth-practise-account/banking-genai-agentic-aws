
from langchain_ollama import ChatOllama


class LLMConnection:
    def __init__(self):
        self.model_name = "mistral:7b"
        self.temperature = 0
        self.llm = None

    def connect(self):
        self.llm = ChatOllama(
            model=self.model_name,
            temperature=self.temperature,
        )
        return self.llm

    def generate_response(self, prompt):
        response = self.llm.invoke(prompt)
        return response.content