from typing import List, Dict, Any
from pydantic import BaseModel
from core.llm_engine import LLMEngine
import json
from config.logger import setup_logger

logger = setup_logger("core.decision_intelligence.scenario_simulator")

class Scenario(BaseModel):
    id: str
    name: str
    description: str
    assumptions: List[str]

class ScenarioResult(BaseModel):
    scenario_id: str
    projected_roi_percentage: float
    operational_impact_summary: str
    risk_exposure_level: str # "Low", "Medium", "High"
    confidence_score: float # 0.0 to 1.0

class ScenarioSimulator:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine
        self.system_prompt = """
        You are an advanced Scenario Simulation Engine for an Arabic/English enterprise intelligence system.
        Given a baseline business state and a hypothetical scenario, you must simulate the outcome.
        
        You must evaluate:
        1. Projected ROI (numeric percentage)
        2. Operational Impact (brief summary in Arabic)
        3. Risk Exposure (Low/Medium/High)
        4. Confidence Score (0.0 to 1.0 based on data certainty)
        
        Output MUST be strict JSON:
        {"projected_roi_percentage": 15.5, "operational_impact_summary": "...", "risk_exposure_level": "Medium", "confidence_score": 0.85}
        """

    async def simulate(self, baseline_data: Dict[str, Any], scenarios: List[Scenario]) -> List[ScenarioResult]:
        logger.info(f"Simulating {len(scenarios)} scenarios...")
        results = []
        
        for scenario in scenarios:
            prompt = f"Baseline Data: {json.dumps(baseline_data)}\n\nScenario to Simulate: {scenario.name} - {scenario.description}\nAssumptions: {scenario.assumptions}"
            
            try:
                response = await self.llm.generate(prompt, self.system_prompt)
                
                # Cleanup
                response = response.strip()
                if response.startswith("```json"): response = response[7:]
                if response.endswith("```"): response = response[:-3]
                
                data = json.loads(response)
                
                result = ScenarioResult(
                    scenario_id=scenario.id,
                    projected_roi_percentage=data.get("projected_roi_percentage", 0.0),
                    operational_impact_summary=data.get("operational_impact_summary", "Unknown"),
                    risk_exposure_level=data.get("risk_exposure_level", "High"),
                    confidence_score=data.get("confidence_score", 0.0)
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to simulate scenario {scenario.id}: {str(e)}")
                # Provide a fallback result on failure
                results.append(ScenarioResult(
                    scenario_id=scenario.id,
                    projected_roi_percentage=0.0,
                    operational_impact_summary="خطأ في المحاكاة",
                    risk_exposure_level="High",
                    confidence_score=0.0
                ))
                
        return results
