import time
import json
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from config.logger import setup_logger

logger = setup_logger("core.meta_agent.telemetry_module")

class ExecutionTrace(BaseModel):
    trace_id: str
    session_id: str
    task_type: str
    agent_name: str
    start_time: float
    end_time: Optional[float] = None
    latency_ms: Optional[float] = None
    success: bool = False
    tokens_used: int = 0
    error_message: Optional[str] = None

class TelemetryModule:
    def __init__(self):
        logger.info("Initializing Telemetry & Observability Module")
        self.traces: List[ExecutionTrace] = []

    def start_trace(self, trace_id: str, session_id: str, task_type: str, agent_name: str) -> ExecutionTrace:
        trace = ExecutionTrace(
            trace_id=trace_id,
            session_id=session_id,
            task_type=task_type,
            agent_name=agent_name,
            start_time=time.time()
        )
        self.traces.append(trace)
        return trace

    def end_trace(self, trace_id: str, success: bool, tokens: int = 0, error: str = None) -> None:
        for trace in reversed(self.traces):
            if trace.trace_id == trace_id:
                trace.end_time = time.time()
                trace.latency_ms = (trace.end_time - trace.start_time) * 1000
                trace.success = success
                trace.tokens_used = tokens
                trace.error_message = error
                logger.info(f"[TRACE] Agent: {trace.agent_name} | Latency: {trace.latency_ms:.2f}ms | Success: {success}")
                return
        logger.warning(f"Trace ID {trace_id} not found for closure.")

    def get_agent_metrics(self, agent_name: str) -> Dict[str, Any]:
        """Calculates average latency and success rate for a specific agent."""
        agent_traces = [t for t in self.traces if t.agent_name == agent_name and t.end_time is not None]
        if not agent_traces:
            return {"avg_latency_ms": 0.0, "success_rate": 0.0, "total_executions": 0}
            
        successes = sum(1 for t in agent_traces if t.success)
        total_latency = sum(t.latency_ms for t in agent_traces if t.latency_ms)
        
        return {
            "avg_latency_ms": total_latency / len(agent_traces),
            "success_rate": successes / len(agent_traces),
            "total_executions": len(agent_traces)
        }
