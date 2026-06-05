from core.llm_engine import LLMEngine
from core.self_learning.feedback_handler import FeedbackHandler, FeedbackSignal
from core.self_learning.response_evaluator import ResponseEvaluator, EvaluationResult
from core.self_learning.adaptive_optimizer import AdaptiveOptimizer, OptimizationLesson
from config.logger import setup_logger

logger = setup_logger("core.self_learning.learning_engine")

class LearningEngine:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine
        self.feedback_handler = FeedbackHandler()
        self.evaluator = ResponseEvaluator(self.llm)
        self.optimizer = AdaptiveOptimizer(self.llm)
        
        # In a real implementation, this would connect to SQLite/ChromaDB
        self.learned_lessons_store = [] 

    async def process_interaction_cycle(self, session_id: str, message_id: str, user_prompt: str, assistant_response: str, implicit_action: str = None) -> None:
        """
        Runs the full offline self-improvement loop for a single interaction.
        """
        logger.info(f"Starting learning cycle for message {message_id}")
        
        # 1. Gather Feedback
        feedback = None
        if implicit_action:
            feedback = self.feedback_handler.analyze_implicit_behavior(session_id, message_id, 2.0, implicit_action)
            
        # 2. Evaluate Response
        evaluation = await self.evaluator.evaluate_interaction(user_prompt, assistant_response, feedback)
        logger.info(f"Interaction scored: {evaluation.score}")
        
        # 3. Optimize if score is below threshold
        if evaluation.score < 0.6:
            logger.warning(f"Low score detected ({evaluation.score}). Triggering adaptive optimizer.")
            lesson = await self.optimizer.generate_lesson(user_prompt, assistant_response, evaluation)
            
            # 4. Store Lesson
            self.learned_lessons_store.append(lesson)
            logger.info(f"Lesson stored: {lesson.recommended_prompt_addition}")
            
            # FUTURE: Orchestrator will query `learned_lessons_store` during prompt generation 
            # to dynamically inject `recommended_prompt_addition` into the system prompt.
