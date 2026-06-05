import uuid
from typing import Dict, Any, List
from core.meta_agent.telemetry_module import TelemetryModule
from core.meta_agent.agent_scorer import AgentScorer
from core.meta_agent.routing_engine import DynamicRoutingEngine, RoutingPlan
from config.logger import setup_logger

logger = setup_logger("core.meta_agent.meta_agent")

class MetaAgent:
    def __init__(self):
        logger.info("Initializing Meta-Agent Controller")
        self.telemetry = TelemetryModule()
        self.scorer = AgentScorer(self.telemetry)
        self.router = DynamicRoutingEngine(self.scorer)

    def optimize_workflow(self, classification_result: Dict[str, Any]) -> RoutingPlan:
        """
        Takes the output from the IntentClassifier and constructs an optimized,
        latency-aware execution path.
        """
        primary_intent = classification_result.get("intent", "general_chat")
        secondary_intents = []
        if "secondary_intent" in classification_result:
            secondary_intents.append(classification_result["secondary_intent"])
            
        return self.router.generate_routing_plan(primary_intent, secondary_intents)

    def record_agent_execution(self, session_id: str, task: str, agent_name: str) -> str:
        """Starts a telemetry trace. Returns the trace_id."""
        trace_id = str(uuid.uuid4())
        self.telemetry.start_trace(trace_id, session_id, task, agent_name)
        return trace_id

    def finalize_agent_execution(self, trace_id: str, success: bool, tokens: int = 0, error: str = None) -> None:
        """Closes a telemetry trace, updating the agent's historical score."""
        self.telemetry.end_trace(trace_id, success, tokens, error)
        
    def get_system_health_report(self) -> Dict[str, Any]:
        """Provides an observability dashboard summary."""
        report = {}
        for agent in self.scorer.baseline_scores.keys():
            report[agent] = {
                "health_score": self.scorer.calculate_agent_score(agent),
                "metrics": self.telemetry.get_agent_metrics(agent)
            }
        return report
