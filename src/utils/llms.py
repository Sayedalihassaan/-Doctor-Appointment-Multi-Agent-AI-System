import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY is not set in .env file")

class LLMModel:
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        self.model_name = model_name

        self.llm = ChatGroq(
            model=self.model_name,
            temperature=0,
            max_tokens=1024,
        )

    def get_model(self):
        return self.llm

if __name__ == "__main__":
    llm = LLMModel().get_model()
    response = llm.invoke("Hi")
    print(response.content)
