# backend/chains/classes/music_rag_chain_class.py
from typing import List, Dict, Tuple
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
import faiss

def _parse_row(row: str) -> Dict[str, str]:
    # Expect: "Title: X | Artist: Y | Decade: 1970s | Genre: rock | Mood: ballad"
    parts = {}
    for kv in row.split(" | "):
        if ": " in kv:
            k, v = kv.split(": ", 1)
            parts[k.strip()] = v.strip()
    return parts

class MusicRAGChain:
    def __init__(self, music_data: list[str], embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            encode_kwargs={"normalize_embeddings": True}
        )

        docs: List[Document] = []
        for row in music_data:
            meta = _parse_row(row)
            text = " | ".join([f"{k}: {meta.get(k,'')}" for k in ["Title","Artist","Decade","Genre","Mood"]])
            docs.append(Document(page_content=text, metadata=meta))

        # Cosine sim FAISS (normalize + IndexFlatIP)
        dim = len(self.embeddings.embed_query("test"))
        index = faiss.IndexFlatIP(dim)
        self.vectorstore = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore({}),
            index_to_docstore_id={},
        )
        self.vectorstore.add_documents(docs)

    def _mmr(self, query: str, k: int, fetch_k: int = 40):
        # Diversify results (helps avoid 60s entries for a 70s rock ballad query)
        return self.vectorstore.max_marginal_relevance_search(query, k=k, fetch_k=fetch_k)

    def recommend_songs(
        self,
        query: str,
        top_k: int = 10,
        require_decade: str | None = None,
        require_genre: str | None = None,
        require_mood: str | None = None,
    ) -> str:
        # 1) fetch more than needed
        docs = self.vectorstore.similarity_search(query, k=top_k * 10)

        # 2) strict filter by metadata
        filtered = []
        for d in docs:
            m = d.metadata
            if require_decade and m.get("Decade", "").lower() != require_decade.lower():
                continue
            if require_genre and require_genre.lower() not in m.get("Genre", "").lower():
                continue
            if require_mood and require_mood.lower() not in m.get("Mood", "").lower():
                continue
            filtered.append(d)

        # fallback: if filtering is too strict, use original docs
        final_docs = filtered if filtered else docs

        # 3) dedupe
        seen = set()
        results = []
        for d in final_docs:
            a = d.metadata.get("Artist", "").strip()
            t = d.metadata.get("Title", "").strip()
            key = (a.lower(), t.lower())
            if key not in seen:
                seen.add(key)
                results.append(d)
            if len(results) >= top_k:
                break

        # 4) format
        return "\n".join(
            f"{i+1}. {d.metadata.get('Artist','?')} – {d.metadata.get('Title','?')} ({d.metadata.get('Decade','?')})"
            for i, d in enumerate(results)
        )

