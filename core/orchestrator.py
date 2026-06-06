from typing import TypedDict, Annotated, Sequence
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from config.logger import setup_logger
from core.llm_engine import LLMEngine
from core.intent_classifier import IntentClassifier
from security.guardrails import PromptGuardrail

# Import agents
from agents.critic_agent import CriticAgent
from agents.data_analyst_agent import DataAnalystAgent
from agents.research_agent import ResearchAgent

logger = setup_logger("core.orchestrator")

# Define the state for the LangGraph
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    session_id: str
    tenant_id: str
    intent: str
    next_node: str

class Orchestrator:
    def __init__(self):
        logger.info("Initializing LangGraph Orchestrator")
        self.llm_engine = LLMEngine()
        self.intent_classifier = IntentClassifier(self.llm_engine)
        self.guardrails = PromptGuardrail()
        
        # Initialize agents
        self.critic_agent = CriticAgent(self.llm_engine, memory_manager=None) # type: ignore
        self.data_analyst = DataAnalystAgent(self.llm_engine, memory_manager=None) # type: ignore
        self.researcher = ResearchAgent(self.llm_engine, memory_manager=None) # type: ignore
        
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("classify_intent", self._node_classify_intent)
        workflow.add_node("data_analyst", self._node_data_analyst)
        workflow.add_node("researcher", self._node_researcher)
        workflow.add_node("critic", self._node_critic)
        
        # Define edges
        workflow.set_entry_point("classify_intent")
        
        # Conditional routing based on intent
        workflow.add_conditional_edges(
            "classify_intent",
            lambda x: x["next_node"],
            {
                "data_analyst": "data_analyst",
                "researcher": "researcher",
                "critic": "critic" # direct fallback
            }
        )
        
        # Agents route to critic for review
        workflow.add_edge("data_analyst", "critic")
        workflow.add_edge("researcher", "critic")
        workflow.add_edge("critic", END)
        
        return workflow.compile()

    async def _node_classify_intent(self, state: AgentState):
        last_message = state["messages"][-1].content
        classification = await self.intent_classifier.classify(last_message)
        intent = classification.get("intent", "general_chat")
        
        # Simple routing logic
        if intent in ["analyze_data", "compute_kpi", "trend_analysis"]:
            next_node = "data_analyst"
        else:
            next_node = "researcher"
            
        return {"intent": intent, "next_node": next_node}

    async def _node_data_analyst(self, state: AgentState):
        last_message = state["messages"][-1].content
        response = await self.data_analyst.execute(state["session_id"], last_message, tenant_id=state.get("tenant_id"))
        return {"messages": [AIMessage(content=response)]}

    async def _node_researcher(self, state: AgentState):
        last_message = state["messages"][-1].content
        response = await self.researcher.execute(state["session_id"], last_message, tenant_id=state.get("tenant_id"))
        return {"messages": [AIMessage(content=response)]}

    async def _node_critic(self, state: AgentState):
        # Critic reviews the last generated message
        last_message = state["messages"][-1].content
        review_task = f"Please review this draft response to the user: '{last_message}'"
        final_response = await self.critic_agent.execute(state["session_id"], review_task)
        return {"messages": [AIMessage(content=final_response)]}

    async def process_message(self, message: str, user_id: str, tenant_id: str = "default_tenant") -> str:
        logger.info(f"Processing message for user {user_id} in tenant {tenant_id}")
        
        # 1. Guardrails Check
        is_safe, reason = self.guardrails.check_prompt(message)
        if not is_safe:
            return reason
            
        # 2. Execute Graph
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "session_id": user_id,
            "tenant_id": tenant_id,
            "intent": "",
            "next_node": ""
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        
        # The last message is from the Critic node
        return final_state["messages"][-1].content
