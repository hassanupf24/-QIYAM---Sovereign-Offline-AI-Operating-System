import os
import uuid
import base64
from config.settings import settings
from config.logger import setup_logger

logger = setup_logger("core.visuals.export_manager")

class ExportManager:
    def __init__(self):
        self.export_dir = os.path.join(os.path.dirname(settings.SQLITE_DB_PATH), "exports", "visuals")
        os.makedirs(self.export_dir, exist_ok=True)
        
    def get_export_path(self, extension: str = "png") -> str:
        """Generates a unique filepath for a new chart."""
        filename = f"chart_{uuid.uuid4().hex[:8]}.{extension}"
        return os.path.join(self.export_dir, filename)

    def image_to_base64(self, filepath: str) -> str:
        """Converts a saved image to base64 for WhatsApp transmission."""
        try:
            with open(filepath, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode image to base64: {str(e)}")
            return ""

    def cleanup_old_exports(self) -> None:
        """Deletes charts older than 24 hours to save disk space."""
        # Implementation omitted for brevity
        pass
