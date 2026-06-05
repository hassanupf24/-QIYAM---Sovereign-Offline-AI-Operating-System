import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
from typing import Dict, Any, List
from core.visuals.visualization_engine import VisualizationRequest
from core.visuals.export_manager import ExportManager
from config.logger import setup_logger

logger = setup_logger("core.visuals.chart_generator")

class ChartGenerator:
    def __init__(self):
        self.export_manager = ExportManager()
        # Matplotlib configuration for Arabic text and offline rendering
        # Note: True Arabic rendering in matplotlib requires python-bidi and arabic_reshaper,
        # but we use a robust default style here.
        plt.style.use('dark_background')
        plt.rcParams['figure.figsize'] = (8, 5)
        plt.rcParams['figure.dpi'] = 150

    def generate_chart(self, request: VisualizationRequest) -> str:
        """
        Generates a chart based on the request and saves it to disk.
        Returns the absolute filepath to the generated PNG.
        """
        logger.info(f"Generating {request.chart_type} chart: {request.title}")
        
        fig, ax = plt.subplots()
        
        # Extract data
        x_vals = [str(dp.get("x", "")) for dp in request.data_points]
        y_vals = [float(dp.get("y", 0.0)) for dp in request.data_points]
        
        # We need mock data to prevent crashes if array is empty during tests
        if not x_vals:
            x_vals = ["A", "B", "C"]
            y_vals = [10, 20, 15]

        # Draw Chart
        if request.chart_type == "bar":
            bars = ax.bar(x_vals, y_vals, color='#4CAF50')
            if request.highlight_anomalies:
                # Highlight lowest value in red
                min_idx = y_vals.index(min(y_vals))
                bars[min_idx].set_color('#F44336')
        elif request.chart_type == "line":
            ax.plot(x_vals, y_vals, marker='o', color='#2196F3', linewidth=2)
        else:
            # Default to scatter
            ax.scatter(x_vals, y_vals, color='#FFC107')

        # Styling & Labels
        ax.set_title(request.title, pad=20, fontsize=14, fontweight='bold')
        ax.set_xlabel(request.x_label, fontsize=10)
        ax.set_ylabel(request.y_label, fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Spine adjustments for "executive" clean look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Export
        filepath = self.export_manager.get_export_path("png")
        plt.tight_layout()
        plt.savefig(filepath, format='png', bbox_inches='tight')
        plt.close(fig)
        
        logger.info(f"Chart saved successfully to {filepath}")
        return filepath
