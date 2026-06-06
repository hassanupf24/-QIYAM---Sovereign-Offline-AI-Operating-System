import re
from typing import Tuple
from config.logger import setup_logger

logger = setup_logger("security.guardrails")

class PromptGuardrail:
    def __init__(self):
        # Basic heuristic blocklist for common injection keywords in English and Arabic
        self.forbidden_patterns = [
            r"(?i)\bignore\s+(all|previous)\s+(instructions|prompts)\b",
            r"(?i)\bforget\s+about\s+your\s+role\b",
            r"(?i)\byou\s+are\s+now\b",
            r"(?i)\bbypass\b",
            r"(?i)\bos\.system\b",
            r"(?i)\bimport\s+os\b",
            r"(?i)\bsubprocess\b",
            r"تجاهل\s+جميع\s+التعليمات",
            r"انسى\s+دورك",
            r"أنت\s+الآن",
        ]
        self.compiled_patterns = [re.compile(p) for p in self.forbidden_patterns]

    def check_prompt(self, prompt: str) -> Tuple[bool, str]:
        """
        Validates the user prompt against known injection vectors.
        Returns (is_safe, reason)
        """
        for pattern in self.compiled_patterns:
            if pattern.search(prompt):
                logger.warning(f"Prompt injection detected! Matched pattern: {pattern.pattern}")
                return False, "تم اكتشاف محاولة حقن تعليمات (Prompt Injection). تم حظر الطلب."
        
        return True, ""
