from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from app.core.config import DEFAULT_MODEL_NAME

class MoodToSongsChain:
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME, prompt_path: str = "prompts/suggest_songs.txt"):
        self.llm = ChatOllama(model=model_name)
        self.prompt = PromptTemplate.from_file(prompt_path, input_variables=["mood"])
        self.chain: Runnable = self.prompt | self.llm

    def get_songs(self, mood: str) -> list[str]:
        result = self.chain.invoke({"mood": mood})
        return [line.strip("•- ").strip() for line in result.content.strip().splitlines() if line.strip()]
