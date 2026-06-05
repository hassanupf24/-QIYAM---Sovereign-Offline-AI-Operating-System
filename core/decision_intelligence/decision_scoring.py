from pydantic import BaseModel, Field
from typing import Dict, Any

class DecisionScore(BaseModel):
    roi_potential: float = Field(..., ge=0.0, le=10.0, description="Return on investment potential (0-10)")
    implementation_complexity: float = Field(..., ge=0.0, le=10.0, description="Complexity of implementation (0=Easy, 10=Impossible)")
    time_to_impact: float = Field(..., ge=0.0, le=10.0, description="Speed of realizing benefits (0=Slow, 10=Immediate)")
    operational_risk: float = Field(..., ge=0.0, le=10.0, description="Risk of disruption or failure (0=Safe, 10=High Risk)")
    business_alignment: float = Field(..., ge=0.0, le=10.0, description="Alignment with core business goals (0-10)")

class DecisionScoringFramework:
    def __init__(self):
        # Default weights
        self.weights = {
            "roi_potential": 0.35,
            "implementation_complexity": -0.15, # Negative weight (higher complexity lowers score)
            "time_to_impact": 0.20,
            "operational_risk": -0.20,          # Negative weight
            "business_alignment": 0.10
        }

    def calculate_weighted_score(self, scores: DecisionScore) -> float:
        """
        Calculates a final weighted score (0 to 100) based on the input dimensions.
        """
        raw_score = (
            (scores.roi_potential * self.weights["roi_potential"]) +
            ((10.0 - scores.implementation_complexity) * abs(self.weights["implementation_complexity"])) +
            (scores.time_to_impact * self.weights["time_to_impact"]) +
            ((10.0 - scores.operational_risk) * abs(self.weights["operational_risk"])) +
            (scores.business_alignment * self.weights["business_alignment"])
        )
        
        # Normalize to 0-100 scale
        normalized_score = (raw_score / 10.0) * 100.0
        return round(normalized_score, 2)
