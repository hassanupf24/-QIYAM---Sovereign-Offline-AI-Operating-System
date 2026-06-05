from typing import List
from core.visuals.visualization_engine import VisualizationRequest
from core.visuals.chart_generator import ChartGenerator
from config.logger import setup_logger

logger = setup_logger("core.visuals.dashboard_builder")

class DashboardBuilder:
    def __init__(self):
        self.generator = ChartGenerator()

    def build_executive_dashboard(self, requests: List[VisualizationRequest]) -> List[str]:
        """
        Takes multiple chart requests and generates them as a batch.
        In a more advanced implementation, this would stitch them into a single 
        grid image (like a 2x2 dashboard) using PIL or Matplotlib subplots.
        """
        logger.info(f"Building dashboard with {len(requests)} charts...")
        filepaths = []
        
        for req in requests:
            filepath = self.generator.generate_chart(req)
            filepaths.append(filepath)
            
        return filepaths
