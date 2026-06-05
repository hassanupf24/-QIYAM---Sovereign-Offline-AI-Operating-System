from typing import List
from config.logger import setup_logger

logger = setup_logger("core.plugins.permission_manager")

class PermissionManager:
    def __init__(self):
        # A mock mapping of allowed permissions for the system
        # In a real system, this would be loaded from a highly secure config file.
        self.allowed_system_permissions = {
            "filesystem:read",
            "filesystem:tmp_write",
            "network:internal_api",
            "compute:sandbox_python"
        }
        
        self.banned_system_permissions = {
            "filesystem:root_write",
            "network:external_untrusted",
            "compute:host_shell"
        }

    def validate_permissions(self, requested_permissions: List[str], plugin_name: str) -> bool:
        """
        Evaluates a plugin's requested permissions against system policies.
        """
        for perm in requested_permissions:
            if perm in self.banned_system_permissions:
                logger.error(f"Plugin '{plugin_name}' requested BANNED permission: {perm}")
                return False
                
            if perm not in self.allowed_system_permissions:
                logger.warning(f"Plugin '{plugin_name}' requested UNKNOWN permission: {perm}. Denying.")
                return False
                
        logger.info(f"Permissions validated for plugin '{plugin_name}'.")
        return True
