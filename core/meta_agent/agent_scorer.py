from typing import Dict, Any
from core.meta_agent.telemetry_module import TelemetryModule
from config.logger import setup_logger

logger = setup_logger("core.meta_agent.agent_scorer")

class AgentScorer:
    def __init__(self, telemetry: TelemetryModule):
        self.telemetry = telemetry
        # Default baseline scores if an agent has no history
        self.baseline_scores = {
            "DataAnalystAgent": 0.8,
            "BusinessIntelligenceAgent": 0.8,
            "ResearchAgent": 0.8,
            "TaskAutomationAgent": 0.8,
            "SecurityAgent": 0.9 # High default priority
        }

    def calculate_agent_score(self, agent_name: str) -> float:
        """
        Calculates a dynamic reliability score (0.0 to 1.0) based on historical telemetry.
        """
        metrics = self.telemetry.get_agent_metrics(agent_name)
        
        if metrics["total_executions"] < 5:
            # Not enough data, return baseline
            return self.baseline_scores.get(agent_name, 0.5)
            
        # Weighting: 70% success rate, 30% speed penalty
        success_rate = metrics["success_rate"]
        
        # Penalize if average latency exceeds 15 seconds (15000ms)
        latency = metrics["avg_latency_ms"]
        speed_score = max(0.0, 1.0 - (latency / 15000.0))
        
        final_score = (success_rate * 0.7) + (speed_score * 0.3)
        return round(final_score, 3)
