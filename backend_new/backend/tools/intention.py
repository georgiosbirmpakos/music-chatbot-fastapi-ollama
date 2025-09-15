# backend/tools/intention.py
from pathlib import Path
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import os

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

class IntentionResult(BaseModel):
    intention: Literal["generic", "suggestion", "modification"] = Field(...)
    reason: str = Field(...)

DEFAULT_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "intention_classifier.txt"

class IntentionClassifier:
    def __init__(self, prompt_path: Path | None = None, model: str = OPENAI_MODEL):
        self.model_name = model
        self.prompt_path = Path(prompt_path) if prompt_path else DEFAULT_PROMPT_PATH
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found at: {self.prompt_path}")

        raw_text = self.prompt_path.read_text(encoding="utf-8")
        # Escape all braces so JSON in the system prompt is treated literally
        safe_system = raw_text.replace("{", "{{").replace("}", "}}")

        self.llm = ChatOpenAI(model=self.model_name, temperature=0)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", safe_system),      # <— escaped
            ("user", "{user_input}"),
        ])
        self.chain = self.prompt | self.llm.with_structured_output(IntentionResult)

    def classify(self, user_input: str) -> IntentionResult:
        return self.chain.invoke({"user_input": user_input})
