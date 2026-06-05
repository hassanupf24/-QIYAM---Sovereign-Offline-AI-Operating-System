from core.llm_engine import LLMEngine
from core.self_learning.feedback_handler import FeedbackSignal
from pydantic import BaseModel
import json
from config.logger import setup_logger

logger = setup_logger("core.self_learning.response_evaluator")

class EvaluationResult(BaseModel):
    score: float # 0.0 to 1.0
    correctness: float
    relevance: float
    actionability: float
    identified_flaw: str

class ResponseEvaluator:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine
        self.system_prompt = """
        You are an internal Quality Assurance Engine. Evaluate the provided Assistant Response against the User Prompt.
        Output strict JSON scoring these metrics from 0.0 to 1.0:
        {"correctness": 0.9, "relevance": 0.8, "actionability": 0.7, "identified_flaw": "Missing specific dates."}
        """

    async def evaluate_interaction(self, user_prompt: str, assistant_response: str, feedback: FeedbackSignal = None) -> EvaluationResult:
        """
        Combines deterministic feedback signals with LLM-based qualitative grading.
        """
        logger.info("Evaluating interaction quality...")
        
        # 1. LLM Self-Reflection Grading
        eval_prompt = f"User Prompt: {user_prompt}\nAssistant Response: {assistant_response}"
        try:
            llm_result = await self.llm.generate(eval_prompt, self.system_prompt)
            # Cleanup JSON
            llm_result = llm_result.strip()
            if llm_result.startswith("```json"): llm_result = llm_result[7:]
            if llm_result.endswith("```"): llm_result = llm_result[:-3]
            data = json.loads(llm_result)
        except Exception as e:
            logger.error(f"Failed LLM evaluation: {str(e)}")
            data = {"correctness": 0.5, "relevance": 0.5, "actionability": 0.5, "identified_flaw": "Evaluation error"}

        # 2. Integrate User Feedback (if any)
        final_score = (data.get("correctness", 0.5) + data.get("relevance", 0.5) + data.get("actionability", 0.5)) / 3.0
        
        if feedback and feedback.rating is not None:
            # User feedback heavily weights the final score (70% user, 30% LLM)
            final_score = (feedback.rating * 0.7) + (final_score * 0.3)
            
        return EvaluationResult(
            score=round(final_score, 2),
            correctness=data.get("correctness", 0.0),
            relevance=data.get("relevance", 0.0),
            actionability=data.get("actionability", 0.0),
            identified_flaw=data.get("identified_flaw", "None")
        )
