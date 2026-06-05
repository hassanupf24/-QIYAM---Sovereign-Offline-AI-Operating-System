from typing import Dict, Any, Tuple
from core.voice.speech_to_text import SpeechToText
from core.voice.text_to_speech import TextToSpeech
from core.voice.whatsapp_voice_handler import WhatsAppVoiceHandler
from config.logger import setup_logger

logger = setup_logger("core.voice.voice_processor")

class VoiceProcessor:
    def __init__(self):
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.whatsapp_handler = WhatsAppVoiceHandler()

    async def process_incoming_voice(self, ogg_filepath: str) -> str:
        """
        Pipeline: OGG -> WAV -> Whisper.cpp STT -> Text
        """
        logger.info("Processing incoming WhatsApp voice note...")
        
        # 1. Convert WhatsApp format to Whisper format
        wav_filepath = self.whatsapp_handler.convert_ogg_to_wav(ogg_filepath)
        if not wav_filepath:
            return "عذراً، لم أتمكن من معالجة المقطع الصوتي."
            
        # 2. Transcribe
        transcription = await self.stt.transcribe(wav_filepath)
        
        return transcription

    async def generate_voice_response(self, text_response: str) -> str:
        """
        Pipeline: Text -> Arabic TTS -> WAV Filepath
        """
        logger.info("Generating voice response for agent output...")
        
        # In a real system, we might want to strip markdown formatting or emojis
        # before passing it to the TTS engine to avoid weird spoken artifacts.
        clean_text = text_response.replace("*", "").replace("#", "")
        
        audio_filepath = await self.tts.synthesize(clean_text)
        return audio_filepath
