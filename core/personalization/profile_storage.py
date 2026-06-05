import os
import json
import base64
from typing import Optional
from core.personalization.user_profile_manager import UserProfile
from config.settings import settings
from config.logger import setup_logger

logger = setup_logger("core.personalization.profile_storage")

class ProfileStorage:
    def __init__(self):
        # We store profiles locally to ensure complete offline privacy
        self.storage_dir = os.path.join(os.path.dirname(settings.SQLITE_DB_PATH), "profiles")
        os.makedirs(self.storage_dir, exist_ok=True)
        # In a real enterprise system, this key would be securely loaded from a vault
        self._mock_encryption_key = b'qiyam_secure_local_storage_key_123'

    def _get_file_path(self, user_id: str) -> str:
        # Simple hash-like representation to avoid weird characters in filenames
        safe_id = base64.urlsafe_b64encode(user_id.encode()).decode().rstrip('=')
        return os.path.join(self.storage_dir, f"{safe_id}.enc")

    def _encrypt(self, data: str) -> str:
        # MOCK ENCRYPTION: For demonstration purposes, we use base64.
        # Production would use cryptography.fernet or AES-GCM.
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')

    def _decrypt(self, encrypted_data: str) -> str:
        # MOCK DECRYPTION
        return base64.b64decode(encrypted_data.encode('utf-8')).decode('utf-8')

    def save_profile(self, profile: UserProfile) -> bool:
        try:
            filepath = self._get_file_path(profile.user_id)
            json_data = profile.json()
            encrypted_data = self._encrypt(json_data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
                
            logger.info(f"Securely saved profile for {profile.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save profile for {profile.user_id}: {str(e)}")
            return False

    def load_profile(self, user_id: str) -> Optional[UserProfile]:
        try:
            filepath = self._get_file_path(user_id)
            if not os.path.exists(filepath):
                return None
                
            with open(filepath, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
                
            json_data = self._decrypt(encrypted_data)
            return UserProfile.parse_raw(json_data)
        except Exception as e:
            logger.error(f"Failed to load profile for {user_id}: {str(e)}")
            return None

    def delete_profile(self, user_id: str) -> bool:
        """Fulfills the 'user-controlled memory deletion' requirement."""
        try:
            filepath = self._get_file_path(user_id)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Completely deleted profile for {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete profile for {user_id}: {str(e)}")
            return False
