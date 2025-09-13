import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv() 

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. See README for setup.")
    print("OpenAI Key Loaded")
    return OpenAI(api_key=api_key)
