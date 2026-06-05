from typing import List, Dict, Any
from core.meta_agent.agent_scorer import AgentScorer
from config.logger import setup_logger

logger = setup_logger("core.meta_agent.routing_engine")

class RoutingPlan:
    def __init__(self, steps: List[str], estimated_complexity: str):
        self.steps = steps # List of agent names in sequential order
        self.estimated_complexity = estimated_complexity # "Low", "Medium", "High"

class DynamicRoutingEngine:
    def __init__(self, scorer: AgentScorer):
        self.scorer = scorer
        # Static mapping fallback
        self.intent_map = {
            "analyze_data": "DataAnalystAgent",
            "trend_analysis": "BusinessIntelligenceAgent",
            "research": "ResearchAgent",
            "schedule": "TaskAutomationAgent"
        }

    def generate_routing_plan(self, primary_intent: str, secondary_intents: List[str]) -> RoutingPlan:
        """
        Constructs a multi-agent execution sequence optimized for latency and success rate.
        """
        logger.info(f"Generating dynamic routing plan for intent: {primary_intent}")
        steps = []
        
        # Determine Primary Agent
        primary_agent = self.intent_map.get(primary_intent, "ResearchAgent")
        
        # Check Agent Health
        health_score = self.scorer.calculate_agent_score(primary_agent)
        if health_score < 0.4:
            logger.warning(f"Agent {primary_agent} health is critically low ({health_score}). Rerouting to fallback.")
            # Fallback to general Research Agent if the specialized agent is failing
            primary_agent = "ResearchAgent"
            
        steps.append(primary_agent)
        
        # Handle Secondary Intents (Sequential Chaining)
        for intent in secondary_intents:
            sec_agent = self.intent_map.get(intent)
            if sec_agent and sec_agent not in steps:
                # Only add to chain if its health is acceptable
                if self.scorer.calculate_agent_score(sec_agent) >= 0.5:
                    steps.append(sec_agent)
                    
        # Complexity Estimation
        complexity = "Low"
        if len(steps) > 2:
            complexity = "High"
        elif len(steps) == 2:
            complexity = "Medium"
            
        logger.info(f"Generated Plan: {steps} | Complexity: {complexity}")
        return RoutingPlan(steps=steps, estimated_complexity=complexity)
