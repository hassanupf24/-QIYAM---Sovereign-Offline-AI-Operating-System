import os
import glob
from config.logger import setup_logger
from core.llm_engine import LLMEngine
# In production, we'd import chromadb here
# import chromadb

logger = setup_logger("tools.document_indexer")

class DocumentIndexer:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine
        self.supported_extensions = ['.txt', '.md', '.csv']
        logger.info("Initializing Document Indexer")
        
        # Mock ChromaDB Initialization
        # self.chroma_client = chromadb.PersistentClient(path="data/chroma")
        # self.collection = self.chroma_client.get_or_create_collection(name="personal_docs")

    async def _chunk_text(self, text: str, chunk_size: int = 500) -> list[str]:
        # Simple chunking by character length for demonstration
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    async def index_directory(self, directory_path: str) -> dict:
        """
        Scans a directory for supported files, chunks them, generates embeddings,
        and saves them to ChromaDB.
        """
        if not os.path.exists(directory_path):
            logger.error(f"Directory not found: {directory_path}")
            return {"status": "error", "message": "Directory not found"}

        logger.info(f"Indexing directory: {directory_path}")
        total_files = 0
        total_chunks = 0

        for ext in self.supported_extensions:
            # Look for files recursively
            search_pattern = os.path.join(directory_path, f"**/*{ext}")
            files = glob.glob(search_pattern, recursive=True)
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    chunks = await self._chunk_text(content)
                    
                    for i, chunk in enumerate(chunks):
                        # Generate embedding using LLM engine
                        embedding = await self.llm.embed(chunk)
                        
                        if embedding:
                            # Save to ChromaDB (Mocked)
                            # self.collection.add(
                            #     embeddings=[embedding],
                            #     documents=[chunk],
                            #     metadatas=[{"source": file_path, "chunk": i}],
                            #     ids=[f"{file_path}_{i}"]
                            # )
                            total_chunks += 1
                            
                    total_files += 1
                    logger.info(f"Indexed file: {file_path} ({len(chunks)} chunks)")
                    
                except Exception as e:
                    logger.error(f"Failed to index file {file_path}: {str(e)}")

        result = {
            "status": "success",
            "files_indexed": total_files,
            "chunks_added": total_chunks
        }
        logger.info(f"Indexing complete. {result}")
        return result
