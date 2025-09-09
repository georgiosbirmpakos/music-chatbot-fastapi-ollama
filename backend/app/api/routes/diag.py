from fastapi import APIRouter
from dotenv import load_dotenv, find_dotenv
import os, logging, traceback
from langchain_openai import ChatOpenAI

router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True}

@router.get("/env")
def env():
    load_dotenv(find_dotenv())
    return {
        "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "model": os.getenv("MODEL_NAME", "gpt-4o-mini"),
        "cwd": os.getcwd(),
    }

@router.get("/llm-ping")
def llm_ping():
    try:
        llm = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"), temperature=0, timeout=30)
        out = llm.invoke("Say pong only.")
        content = out.content if hasattr(out, "content") else str(out)
        return {"pong": content}
    except Exception as e:
        logging.error("LLM ping failed: %s\n%s", e, traceback.format_exc())
        return {"error": str(e)}
