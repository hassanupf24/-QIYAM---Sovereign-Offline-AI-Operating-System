from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
from core.llm_engine import LLMEngine
from memory.memory_manager import MemoryManager
from config.logger import setup_logger

logger = setup_logger("agents.base_agent")

class BaseAgent(ABC):
    def __init__(self, llm_engine: LLMEngine, memory_manager: MemoryManager):
        self.llm = llm_engine
        self.memory = memory_manager
        
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        pass
        
    @property
    @abstractmethod
    def allowed_tools(self) -> List[str]:
        pass

    def _build_full_prompt(self, task: str, session_id: str) -> str:
        """Constructs the prompt including agent persona and memory context."""
        context = self.memory.get_context(session_id)
        
        # Inject Dynamic Persona if available
        persona_modifier = ""
        try:
            from core.personalization.personalization_engine import PersonalizationEngine
            engine = PersonalizationEngine()
            persona_modifier = engine.get_system_prompt_modifiers(session_id)
        except Exception as e:
            logger.warning(f"Could not load persona modifiers: {e}")
        
        full_prompt = f"""
{self.system_prompt}

{persona_modifier}

You must output your response in strict JSON format. 
If you need to use a tool, use this format:
{{"action": "tool_name", "params": {{"key": "value"}}}}
If you want to answer the user directly, use this format:
{{"answer": "Your final response here in Arabic."}}

{context}

Current Task: {task}
"""
        return full_prompt.strip()

    async def _handle_tool_call(self, action: str, params: Dict[str, Any]) -> str:
        """Executes a tool if permitted."""
        if action not in self.allowed_tools:
            return f"Error: Tool '{action}' is not permitted for agent {self.name}."
            
        logger.info(f"Agent {self.name} executing tool '{action}' with params {params}")
        # Implementation of actual tool dispatch will happen in the specific agents or via safe_runtime
        # For now, return a mock result
        return f"Mock result for tool {action}"

    async def execute(self, session_id: str, task: str) -> str:
        """The core ReAct loop for the agent."""
        logger.info(f"Executing task on {self.name} for session {session_id}")
        
        max_iterations = 3
        current_task = task
        
        for iteration in range(max_iterations):
            prompt = self._build_full_prompt(current_task, session_id)
            
            try:
                response = await self.llm.generate(prompt)
                
                # Clean up potential markdown wrappers
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                if response.endswith("```"):
                    response = response[:-3]
                    
                parsed_response = json.loads(response)
                
                if "answer" in parsed_response:
                    return parsed_response["answer"]
                    
                elif "action" in parsed_response:
                    action = parsed_response["action"]
                    params = parsed_response.get("params", {})
                    
                    tool_result = await self._handle_tool_call(action, params)
                    
                    # Feed the tool result back into the task for the next iteration
                    current_task = f"Tool '{action}' returned: {tool_result}. Continue solving the original task: {task}"
                else:
                    return "Error: Agent output missing 'answer' or 'action' keys."
                    
            except json.JSONDecodeError:
                logger.error(f"Agent {self.name} failed to output valid JSON. Raw: {response}")
                return "عذراً، حدث خطأ في معالجة طلبك (تنسيق غير صالح)."
            except Exception as e:
                logger.error(f"Execution error in {self.name}: {str(e)}")
                return "عذراً، حدث خطأ داخلي أثناء التنفيذ."
                
        return "عذراً، استغرق التنفيذ وقتاً أطول من المتوقع."
