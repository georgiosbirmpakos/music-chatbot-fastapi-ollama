from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def get_mood_to_songs_chain():
    prompt = PromptTemplate.from_file("prompts/suggest_songs.txt", input_variables=["mood"])
    llm = ChatOllama(model="gemma3:4b")
    return LLMChain(llm=llm, prompt=prompt)
