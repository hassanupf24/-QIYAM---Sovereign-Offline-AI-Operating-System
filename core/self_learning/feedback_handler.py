from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from config.logger import setup_logger
from memory.postgres_store import PostgresStore

logger = setup_logger("core.self_learning.feedback_handler")

class FeedbackSignal(BaseModel):
    session_id: str
    message_id: str
    is_explicit: bool
    rating: Optional[float] = None  # 0.0 to 1.0
    text_feedback: Optional[str] = None
    implicit_signal: Optional[str] = None # e.g., "abandonment", "rapid_followup", "task_completed"
    timestamp: datetime = datetime.utcnow()

class FeedbackHandler:
    def __init__(self):
        logger.info("Initializing Feedback Handler")
        self.db = PostgresStore()

    def process_explicit_feedback(self, session_id: str, message_id: str, rating: float, comments: str = None) -> FeedbackSignal:
        """Processes direct user ratings (e.g., thumbs up/down, 5-star rating)."""
        logger.info(f"Received explicit feedback for message {message_id}: Rating {rating}")
        return FeedbackSignal(
            session_id=session_id,
            message_id=message_id,
            is_explicit=True,
            rating=rating,
            text_feedback=comments
        )

    def analyze_implicit_behavior(self, session_id: str, message_id: str, time_spent_sec: float, next_action: str) -> FeedbackSignal:
        """
        Analyzes user behavior to infer satisfaction.
        e.g., if user immediately asks the exact same question again -> failure.
        """
        inferred_rating = 0.5 # Neutral baseline
        signal_type = "neutral"
        
        if next_action == "session_closed" and time_spent_sec < 5.0:
            # User left immediately after seeing response
            inferred_rating = 0.2
            signal_type = "abandonment"
        elif next_action == "proceed_to_next_step":
            # User accepted the output and moved forward
            inferred_rating = 0.9
            signal_type = "task_completed"
        elif next_action == "correction_prompt":
            # User said "No, I meant..."
            inferred_rating = 0.1
            signal_type = "rapid_correction"
            
        logger.info(f"Inferred implicit feedback for {message_id}: {signal_type} ({inferred_rating})")
        return FeedbackSignal(
            session_id=session_id,
            message_id=message_id,
            is_explicit=False,
            rating=inferred_rating,
            implicit_signal=signal_type
        )

    async def process_reaction(self, user_phone: str, message_id: str, emoji: str) -> None:
        """Processes a WhatsApp reaction (emoji) as feedback."""
        rating = 0
        # Map common emojis to ratings (1 for pos, -1 for neg)
        if emoji in ["👍", "❤️", "🔥", "💯", "👏", "✅"]:
            rating = 1
        elif emoji in ["👎", "😡", "❌", "⛔", "🤬"]:
            rating = -1
            
        if rating == 0:
            logger.info(f"Ignored neutral feedback emoji: {emoji}")
            return
            
        user = self.db.get_user_by_phone(user_phone)
        if not user:
            logger.warning(f"Feedback from unknown user {user_phone} ignored.")
            return
            
        try:
            # Assuming message_id passed from webhook is our internal integer ID
            internal_msg_id = int(message_id)
            self.db.add_message_feedback(
                message_id=internal_msg_id,
                user_id=user.id,
                tenant_id=user.tenant_id,
                rating=rating
            )
            logger.info(f"Saved reaction feedback: Rating={rating} for message={message_id}")
        except ValueError:
            logger.error(f"Cannot parse message_id {message_id} to internal integer ID.")
        except Exception as e:
            logger.error(f"Failed to save message feedback: {e}")
