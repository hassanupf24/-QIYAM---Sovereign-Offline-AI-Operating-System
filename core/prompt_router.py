from typing import List, Type
from agents.base_agent import BaseAgent
from config.logger import setup_logger

logger = setup_logger("core.prompt_router")

class PromptRouter:
    def __init__(self):
        # Map intents to the agent class name or identifier that handles them
        self.intent_to_agent_map = {
            "analyze_data": ["DataAnalystAgent"],
            "compute_kpi": ["DataAnalystAgent"],
            "trend_analysis": ["BusinessIntelligenceAgent"],
            "summarize": ["ResearchAgent"],
            "research": ["ResearchAgent"],
            "schedule": ["TaskAutomationAgent"],
            "general_chat": ["ResearchAgent"] # Fallback for now
        }

    def route(self, classification: dict) -> List[str]:
        """
        Determines which agents need to be invoked based on the intent.
        Supports returning multiple agents if a chain is required.
        """
        intent = classification.get("intent", "general_chat")
        confidence = classification.get("confidence", 0.0)
        
        logger.info(f"Routing intent '{intent}' (confidence: {confidence})")
        
        # If confidence is too low, we might want to ask the user for clarification, 
        # but for now we route to the default mapping or fallback.
        agents = self.intent_to_agent_map.get(intent, ["ResearchAgent"])
        
        logger.info(f"Selected agents: {agents}")
        return agents
