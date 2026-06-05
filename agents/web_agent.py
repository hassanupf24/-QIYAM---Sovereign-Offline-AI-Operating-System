from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from tools.web_scraper import WebScraper

class WebAgent(BaseAgent):
    def __init__(self, llm_engine, memory_manager):
        super().__init__(llm_engine, memory_manager)
        self.scraper = WebScraper()

    @property
    def name(self) -> str:
        return "WebSurfer"

    @property
    def system_prompt(self) -> str:
        return """You are the Web Surfing Agent.
Your job is to search the internet for real-time information to answer the user's question.
If the information is not available in your training data, you MUST use your tools.

Available tools:
1. "search": Searches the web. Params: {"query": "search terms"}
2. "read_url": Extracts text from a specific URL. Params: {"url": "https://..."}

Always provide a well-structured Arabic summary of your findings.
"""

    @property
    def allowed_tools(self) -> List[str]:
        return ["search", "read_url"]

    async def _handle_tool_call(self, action: str, params: Dict[str, Any]) -> str:
        if action not in self.allowed_tools:
            return f"Error: Tool '{action}' not permitted."

        if action == "search":
            query = params.get("query", "")
            results = await self.scraper.search(query)
            return f"Search results for '{query}': {results}"
            
        elif action == "read_url":
            url = params.get("url", "")
            content = await self.scraper.extract_text(url)
            return f"Content of {url}: {content}"
            
        return "Unknown action."
