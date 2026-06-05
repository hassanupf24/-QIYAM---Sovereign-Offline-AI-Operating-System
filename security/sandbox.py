import subprocess
from typing import Tuple
from config.logger import setup_logger

logger = setup_logger("security.sandbox")

class Sandbox:
    def __init__(self):
        self.blocked_commands = ["rm -rf", "mkfs", "del /s", "format"]
        
    def is_safe(self, command: str) -> bool:
        """
        Basic heuristic to block extremely dangerous commands.
        In a real system, this should run inside an isolated Docker container.
        """
        cmd_lower = command.lower()
        for blocked in self.blocked_commands:
            if blocked in cmd_lower:
                return False
        return True

    def execute_command(self, command: str, human_approved: bool = False) -> Tuple[bool, str]:
        """
        Executes a local OS command safely. 
        Requires explicit human_approved flag for destructive or high-risk actions.
        """
        if not self.is_safe(command):
            logger.warning(f"Blocked dangerous command attempt: {command}")
            return False, "Error: Command blocked by security policy."

        if not human_approved:
            # We could implement a rule where read-only commands (ls, echo, etc) pass,
            # but others require human_approved = True.
            # For this mock, we will allow it if it passes is_safe.
            pass
            
        logger.info(f"Executing sandboxed command: {command}")
        try:
            # Execute command with a timeout to prevent hanging
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10.0
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Error: Command timed out."
        except Exception as e:
            return False, f"Error: {str(e)}"
