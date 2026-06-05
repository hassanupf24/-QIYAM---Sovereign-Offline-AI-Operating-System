from typing import Dict, Any, List
from core.llm_engine import LLMEngine
from core.decision_intelligence.scenario_simulator import ScenarioSimulator, Scenario
from core.decision_intelligence.decision_scoring import DecisionScoringFramework, DecisionScore
import json
from config.logger import setup_logger

logger = setup_logger("core.decision_intelligence.decision_engine")

class DecisionEngine:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine
        self.simulator = ScenarioSimulator(self.llm)
        self.scorer = DecisionScoringFramework()

    async def generate_executive_decision(self, analysis_data: Dict[str, Any], proposed_scenarios: List[Scenario]) -> Dict[str, Any]:
        """
        Coordinates the simulator and scoring framework to produce a final, 
        ranked executive decision.
        """
        logger.info("Decision Engine activated. Running simulations...")
        
        # 1. Run Simulations
        simulation_results = await self.simulator.simulate(analysis_data, proposed_scenarios)
        
        # 2. Score and Rank Scenarios
        ranked_options = []
        for sim_result in simulation_results:
            # Map simulation outputs to scoring dimensions (in a real system, the LLM would extract these precise 1-10 scores)
            # Here we approximate mapping from the simulation result for demonstration
            roi_score = min(10.0, max(0.0, sim_result.projected_roi_percentage / 5.0)) # Example mapping
            risk_map = {"Low": 2.0, "Medium": 5.0, "High": 8.0}
            risk_score = risk_map.get(sim_result.risk_exposure_level, 8.0)
            
            # Create a mock DecisionScore for ranking (LLM should ideally generate these parameters)
            d_score = DecisionScore(
                roi_potential=roi_score,
                implementation_complexity=5.0, # Assumed baseline
                time_to_impact=6.0, # Assumed baseline
                operational_risk=risk_score,
                business_alignment=8.0 # Assumed baseline
            )
            
            final_score = self.scorer.calculate_weighted_score(d_score)
            
            ranked_options.append({
                "scenario_id": sim_result.scenario_id,
                "projected_roi": sim_result.projected_roi_percentage,
                "impact": sim_result.operational_impact_summary,
                "risk": sim_result.risk_exposure_level,
                "confidence": sim_result.confidence_score,
                "total_score": final_score
            })
            
        # Sort by total_score descending
        ranked_options.sort(key=lambda x: x["total_score"], reverse=True)
        
        best_option = ranked_options[0] if ranked_options else None
        
        # 3. Format Final Output Matrix
        final_report = {
            "executive_summary": "تم إجراء محاكاة للخيارات الاستراتيجية وتقييم المخاطر.",
            "problem_definition": analysis_data.get("problem_statement", "غير محدد"),
            "scenario_comparison_matrix": ranked_options,
            "recommended_action": best_option["scenario_id"] if best_option else "لا يوجد",
            "decision_rationale": f"حصل هذا الخيار على أعلى تقييم ({best_option['total_score']} / 100) بفضل العائد المتوقع وإدارة المخاطر.",
            "overall_confidence": best_option["confidence"] if best_option else 0.0
        }
        
        return final_report
