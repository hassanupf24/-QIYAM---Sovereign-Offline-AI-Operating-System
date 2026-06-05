from config.logger import setup_logger
from core.llm_engine import LLMEngine
from core.intent_classifier import IntentClassifier
from core.prompt_router import PromptRouter
from agents.critic_agent import CriticAgent

logger = setup_logger("core.orchestrator")

class Orchestrator:
    def __init__(self):
        logger.info("Initializing Orchestrator")
        self.llm_engine = LLMEngine()
        self.intent_classifier = IntentClassifier(self.llm_engine)
        self.prompt_router = PromptRouter()
        
        # Initialize memory and agents
        # TODO: self.memory_manager = MemoryManager()
        self.critic_agent = CriticAgent(self.llm_engine, memory_manager=None) # type: ignore (None temporary)

    async def process_message(self, message: str, user_id: str) -> str:
        logger.info(f"Processing message for user {user_id}")
        # 1. Retrieve Context (TODO: Memory System)
        
        # 2. Classify Intent
        classification = await self.intent_classifier.classify(message)
        
        # 3. Route to Agent
        target_agents = self.prompt_router.route(classification)
        
        # 4. Execute Target Agent (TODO: Agent Framework)
        # Mocking target agent execution for now
        draft_response = f"System understood intent as: {classification['intent']} (Language: {classification['language']}). Target agents: {target_agents}"
        
        # 5. Critic Agent Review
        logger.info("Sending draft response to CriticAgent for review.")
        critic_task = f"Please review this draft response to the user: '{draft_response}'"
        # We pass a dummy session_id for now
        final_response = await self.critic_agent.execute(session_id=user_id, task=critic_task)
        
        return final_response
