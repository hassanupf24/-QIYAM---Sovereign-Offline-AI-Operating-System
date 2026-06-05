from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from security.sandbox import Sandbox
from config.logger import setup_logger

logger = setup_logger("agents.computer_agent")

class ComputerAgent(BaseAgent):
    def __init__(self, llm_engine, memory_manager):
        super().__init__(llm_engine, memory_manager)
        self.sandbox = Sandbox()

    @property
    def name(self) -> str:
        return "ComputerOperator"

    @property
    def system_prompt(self) -> str:
        return """You are the Computer Use Agent.
Your job is to execute local operating system commands to help the user manage their computer.
You must exercise extreme caution.

Available tools:
1. "run_command": Executes a bash/powershell command on the host. Params: {"command": "the command to run"}

Always summarize the output of the command for the user in Arabic.
"""

    @property
    def allowed_tools(self) -> List[str]:
        return ["run_command"]

    async def _handle_tool_call(self, action: str, params: Dict[str, Any]) -> str:
        if action not in self.allowed_tools:
            return f"Error: Tool '{action}' not permitted."

        if action == "run_command":
            command = params.get("command", "")
            logger.info(f"ComputerAgent attempting to run: {command}")
            
            # NOTE: In a real environment, we should prompt the user for permission
            # before running this through the orchestrator. For now, we simulate approval.
            human_approved = True 
            
            success, output = self.sandbox.execute_command(command, human_approved)
            return f"Command execution {'succeeded' if success else 'failed'}. Output: {output}"
            
        return "Unknown action."
