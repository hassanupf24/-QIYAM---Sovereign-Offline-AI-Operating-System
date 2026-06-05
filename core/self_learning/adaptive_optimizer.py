from core.llm_engine import LLMEngine
from core.self_learning.response_evaluator import EvaluationResult
from pydantic import BaseModel
import json
from config.logger import setup_logger

logger = setup_logger("core.self_learning.adaptive_optimizer")

class OptimizationLesson(BaseModel):
    trigger_pattern: str
    recommended_prompt_addition: str
    routing_adjustment_suggestion: str

class AdaptiveOptimizer:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine
        self.system_prompt = """
        You are the Adaptive Improvement Engine. Analyze a failed or low-scoring interaction.
        Generate an optimization lesson to prevent this failure in the future.
        Output strict JSON:
        {
          "trigger_pattern": "Brief description of the user intent that failed",
          "recommended_prompt_addition": "A rule to add to the system prompt to fix this",
          "routing_adjustment_suggestion": "Agent X should be used instead of Agent Y (or None)"
        }
        """

    async def generate_lesson(self, user_prompt: str, failed_response: str, evaluation: EvaluationResult) -> OptimizationLesson:
        """
        Creates a 'Lesson Learned' from a low-scoring interaction.
        """
        logger.info(f"Generating optimization lesson for identified flaw: {evaluation.identified_flaw}")
        
        prompt = f"""
        User Prompt: {user_prompt}
        Failed Response: {failed_response}
        Identified Flaw: {evaluation.identified_flaw}
        Score: {evaluation.score}
        """
        
        try:
            response = await self.llm.generate(prompt, self.system_prompt)
            # Cleanup JSON
            response = response.strip()
            if response.startswith("```json"): response = response[7:]
            if response.endswith("```"): response = response[:-3]
            data = json.loads(response)
            
            return OptimizationLesson(
                trigger_pattern=data.get("trigger_pattern", ""),
                recommended_prompt_addition=data.get("recommended_prompt_addition", ""),
                routing_adjustment_suggestion=data.get("routing_adjustment_suggestion", "None")
            )
        except Exception as e:
            logger.error(f"Failed to generate lesson: {str(e)}")
            return OptimizationLesson(
                trigger_pattern="Unknown error",
                recommended_prompt_addition="Maintain strict constraints.",
                routing_adjustment_suggestion="None"
            )
