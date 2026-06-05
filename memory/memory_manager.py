from typing import List, Dict, Any, Optional
from memory.sqlite_store import SQLiteStore
from config.logger import setup_logger

logger = setup_logger("memory.memory_manager")

class MemoryManager:
    def __init__(self):
        logger.info("Initializing Memory Manager")
        self.short_term = SQLiteStore()
        # set of session_ids that are currently in incognito mode
        self.incognito_sessions = set()
        # TODO: Initialize Vector Store (ChromaDB) for long-term semantic memory
        
    def toggle_incognito(self, session_id: str) -> bool:
        """Toggles incognito mode for a session. Returns the new state."""
        if session_id in self.incognito_sessions:
            self.incognito_sessions.remove(session_id)
            logger.info(f"Incognito mode disabled for session {session_id}")
            return False
        else:
            self.incognito_sessions.add(session_id)
            logger.info(f"Incognito mode enabled for session {session_id}")
            return True

    def ensure_session(self, session_id: str, user_id: str) -> None:
        """Ensures a session exists for the given user."""
        self.short_term.create_session(session_id, user_id)
        
    def add_interaction(self, session_id: str, user_message: str, assistant_response: str) -> None:
        """Saves a complete interaction to short-term memory."""
        if session_id in self.incognito_sessions:
            logger.info(f"Session {session_id} is in incognito mode. Interaction not saved.")
            return

        self.short_term.add_message(session_id, "user", user_message)
        self.short_term.add_message(session_id, "assistant", assistant_response)
        
        # Trigger summarization logic if context gets too long
        # self._check_summarization_threshold(session_id)

    def get_context(self, session_id: str, query: str = None) -> str:
        """
        Retrieves context to inject into the LLM prompt.
        Combines recent conversation history (short-term) + semantic search (long-term).
        """
        recent_messages = self.short_term.get_recent_messages(session_id, limit=15)
        
        context_str = "Recent Conversation History:\n"
        for msg in recent_messages:
            context_str += f"{msg['role'].capitalize()}: {msg['content']}\n"
            
        # TODO: Perform semantic search on vector store using 'query' and append
        
        return context_str.strip()
