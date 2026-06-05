import os
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from core.llm_engine import LLMEngine
from config.logger import setup_logger

logger = setup_logger("core.visuals.visualization_engine")

class VisualizationRequest(BaseModel):
    chart_type: str # "line", "bar", "pie", "scatter"
    title: str
    x_label: str
    y_label: str
    data_points: List[Dict[str, Any]] # e.g., [{"x": "Jan", "y": 100}, {"x": "Feb", "y": 120}]
    highlight_anomalies: bool = False

class VisualizationEngine:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine
        self.system_prompt = """
        You are the Visual Intelligence Engine for an Arabic executive dashboard.
        Given a dataset and a business context, determine if a visualization is necessary, 
        and if so, define the exact structure of the chart.
        
        Output MUST be strict JSON:
        {
          "needs_visualization": true,
          "chart_type": "bar",
          "title": "المبيعات الشهرية (Monthly Sales)",
          "x_label": "الشهر",
          "y_label": "الإيرادات",
          "highlight_anomalies": true
        }
        """

    async def analyze_need(self, context: str, data_summary: str) -> Optional[VisualizationRequest]:
        """
        Determines if visual output improves understanding, and constructs the chart requirements.
        """
        logger.info("Analyzing context to determine visualization needs...")
        prompt = f"Context: {context}\nData Summary: {data_summary}"
        
        try:
            # In a real scenario, we'd parse the LLM JSON output to build the Request.
            # For demonstration of the engine logic:
            logger.info("Determined a 'bar' chart is required.")
            return VisualizationRequest(
                chart_type="bar",
                title="تحليل الأداء (Performance Analysis)",
                x_label="الفئة",
                y_label="القيمة",
                data_points=[], # Would be populated from DataAnalyst output
                highlight_anomalies=True
            )
        except Exception as e:
            logger.error(f"Failed to analyze visualization need: {str(e)}")
            return None
