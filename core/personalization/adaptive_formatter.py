from core.personalization.user_profile_manager import UserProfile
from config.logger import setup_logger

logger = setup_logger("core.personalization.adaptive_formatter")

class AdaptiveFormatter:
    def __init__(self):
        logger.info("Initializing Adaptive Formatter")

    def generate_persona_instructions(self, profile: UserProfile) -> str:
        """
        Translates user preferences into direct LLM prompt instructions.
        These are injected into the agent's system prompt at runtime.
        """
        prefs = profile.preferences
        
        instructions = [
            "\n[USER PERSONALIZATION INSTRUCTIONS]"
        ]
        
        # 1. Tone
        if prefs.communication_tone == "professional":
            instructions.append("- Tone: Strictly professional, academic, and respectful.")
        elif prefs.communication_tone == "friendly":
            instructions.append("- Tone: Warm, friendly, and conversational. Use appropriate emojis occasionally.")
        elif prefs.communication_tone == "direct":
            instructions.append("- Tone: Extremely direct. No pleasantries. Get straight to the point.")
            
        # 2. Verbosity
        if prefs.verbosity == "concise":
            instructions.append("- Length: Keep answers extremely concise. Use bullet points heavily. Avoid long paragraphs.")
        elif prefs.verbosity == "comprehensive":
            instructions.append("- Length: Provide comprehensive, detailed answers. Explain the 'why' behind everything.")
            
        # 3. Expertise
        if prefs.expertise_level == "beginner":
            instructions.append("- Expertise Level: The user is a beginner. Avoid heavy jargon. Explain technical terms with simple analogies.")
        elif prefs.expertise_level == "expert":
            instructions.append("- Expertise Level: The user is an expert. Skip basic explanations. Use advanced technical terminology directly.")
            
        # 4. Language Modifiers
        if prefs.preferred_language == "mixed":
            instructions.append("- Language: The user prefers a mix of Arabic and English. Ensure technical terms are kept in English.")
            
        return "\n".join(instructions)
