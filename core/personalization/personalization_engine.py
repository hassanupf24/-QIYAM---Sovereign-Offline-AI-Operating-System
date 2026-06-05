from typing import Dict, Any
from core.personalization.user_profile_manager import UserProfileManager
from core.personalization.profile_storage import ProfileStorage
from core.personalization.adaptive_formatter import AdaptiveFormatter
from config.logger import setup_logger

logger = setup_logger("core.personalization.personalization_engine")

class PersonalizationEngine:
    def __init__(self):
        self.profile_manager = UserProfileManager()
        self.storage = ProfileStorage()
        self.formatter = AdaptiveFormatter()
        
    def initialize_user(self, user_id: str) -> None:
        """Loads the user's profile into memory, or creates one if it doesn't exist."""
        profile = self.storage.load_profile(user_id)
        if profile:
            self.profile_manager._profile_cache[user_id] = profile
            logger.info(f"Loaded existing profile for {user_id}")
        else:
            profile = self.profile_manager.get_profile(user_id)
            self.storage.save_profile(profile)
            logger.info(f"Created new profile for {user_id}")
            
    def get_system_prompt_modifiers(self, user_id: str) -> str:
        """
        Returns the specific instructions to append to the LLM system prompt
        to force it to adapt to the user's style.
        """
        profile = self.profile_manager.get_profile(user_id)
        return self.formatter.generate_persona_instructions(profile)
        
    def adapt_to_feedback(self, user_id: str, inferred_preferences: Dict[str, Any]) -> None:
        """
        Called by the Self-Learning loop to dynamically update the user's profile
        based on observed behaviors (e.g., they keep asking for shorter answers).
        """
        profile = self.profile_manager.update_preferences(user_id, inferred_preferences)
        self.storage.save_profile(profile)
        
    def delete_user_data(self, user_id: str) -> bool:
        """Fulfills privacy requirements."""
        # Remove from memory
        if user_id in self.profile_manager._profile_cache:
            del self.profile_manager._profile_cache[user_id]
        # Remove from disk
        return self.storage.delete_profile(user_id)
