import base64
import os
from config.logger import setup_logger
from core.llm_engine import LLMEngine

logger = setup_logger("core.visuals.image_processor")

class ImageProcessor:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine
        logger.info("Initializing Image Processor (Vision Support)")

    def _encode_image_to_base64(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    async def analyze_image(self, image_path: str, prompt: str = "ماذا يوجد في هذه الصورة؟") -> str:
        """
        Uses a vision model (like LLaVA) to analyze the image and answer the prompt.
        """
        if not os.path.exists(image_path):
            logger.error(f"Image not found at path: {image_path}")
            return "عذراً، لم أتمكن من العثور على الصورة."

        logger.info(f"Analyzing image: {image_path} with prompt: {prompt}")
        
        try:
            base64_image = self._encode_image_to_base64(image_path)
            # Instruct the LLM engine to process with image
            response = await self.llm.generate_with_image(
                prompt=prompt, 
                system_prompt="أنت مساعد ذكي متخصص في تحليل الصور ومساعدة المستخدمين باللغة العربية.",
                base64_image=base64_image
            )
            return response
        except Exception as e:
            logger.error(f"Failed to analyze image: {str(e)}")
            return "عذراً، واجهت مشكلة أثناء تحليل الصورة."
