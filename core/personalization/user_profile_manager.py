from pydantic import BaseModel, Field
from typing import Dict, Any, List
from datetime import datetime
from config.logger import setup_logger

logger = setup_logger("core.personalization.user_profile_manager")

class UserPreferences(BaseModel):
    preferred_language: str = "ar" # "ar", "en", "mixed"
    communication_tone: str = "professional" # "professional", "friendly", "direct"
    verbosity: str = "concise" # "concise", "detailed", "comprehensive"
    expertise_level: str = "intermediate" # "beginner", "intermediate", "expert"
    risk_tolerance: str = "medium" # "low", "medium", "high"
    domain_interests: List[str] = Field(default_factory=list)

class UserProfile(BaseModel):
    user_id: str
    preferences: UserPreferences
    interaction_count: int = 0
    last_active: datetime = datetime.utcnow()

class UserProfileManager:
    def __init__(self):
        logger.info("Initializing User Profile Manager")
        # In-memory cache to prevent constant DB hits
        self._profile_cache: Dict[str, UserProfile] = {}

    def get_profile(self, user_id: str) -> UserProfile:
        if user_id in self._profile_cache:
            return self._profile_cache[user_id]
        
        # If not in cache, we would normally fetch from ProfileStorage.
        # Returning default profile for now.
        return self._create_default_profile(user_id)

    def _create_default_profile(self, user_id: str) -> UserProfile:
        profile = UserProfile(user_id=user_id, preferences=UserPreferences())
        self._profile_cache[user_id] = profile
        return profile

    def update_preferences(self, user_id: str, new_preferences: Dict[str, Any]) -> UserProfile:
        profile = self.get_profile(user_id)
        
        # Dynamically update the Pydantic model
        update_data = profile.preferences.dict(exclude_unset=True)
        update_data.update(new_preferences)
        profile.preferences = UserPreferences(**update_data)
        
        self._profile_cache[user_id] = profile
        logger.info(f"Updated preferences for user {user_id}")
        return profile
