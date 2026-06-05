import httpx
from bs4 import BeautifulSoup
from config.logger import setup_logger

logger = setup_logger("tools.web_scraper")

class WebScraper:
    def __init__(self):
        logger.info("Initializing Web Scraper Tool")
        # In a real environment, we'd use a headless browser or a service like SearxNG
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def search(self, query: str) -> list:
        """
        Mock search function. In production, connects to a local SearxNG instance
        or a search API (e.g., DuckDuckGo) to get URLs.
        """
        logger.info(f"Searching web for: {query}")
        # Returning mock URLs for demonstration
        return [
            {"title": f"Result for {query} 1", "url": "https://example.com/1"},
            {"title": f"Result for {query} 2", "url": "https://example.com/2"}
        ]

    async def extract_text(self, url: str) -> str:
        """
        Fetches the HTML from the given URL and extracts clean text content.
        """
        logger.info(f"Extracting text from: {url}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=15.0)
                response.raise_for_status()
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts, styles, and empty tags
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
                
            text = soup.get_text(separator='\n', strip=True)
            
            # Limit the output length to avoid overwhelming the LLM context window
            return text[:4000]
            
        except Exception as e:
            logger.error(f"Failed to extract text from {url}: {str(e)}")
            return f"Error extracting content from {url}"
