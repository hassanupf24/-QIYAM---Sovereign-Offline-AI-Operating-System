import chromadb
from typing import List, Dict, Any
from config.logger import setup_logger
from core.llm_engine import LLMEngine

logger = setup_logger("memory.chroma_store")

class ChromaStore:
    def __init__(self, llm_engine: LLMEngine):
        self.client = chromadb.PersistentClient(path="./data/chroma")
        self.llm = llm_engine
        # Create or get collection for documents
        self.collection = self.client.get_or_create_collection(
            name="qiyam_knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("ChromaDB initialized for Vector RAG.")

    async def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Embeds and adds documents to the vector store."""
        embeddings = []
        for doc in documents:
            emb = await self.llm.embed(doc)
            embeddings.append(emb)
            
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Added {len(documents)} documents to ChromaDB.")

    async def query_documents(self, query: str, tenant_id: str, n_results: int = 3) -> List[str]:
        """Queries the vector store for relevant documents, filtered by tenant."""
        query_embedding = await self.llm.embed(query)
        if not query_embedding:
            return []
            
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"tenant_id": tenant_id}
        )
        
        if not results['documents']:
            return []
            
        return results['documents'][0]
