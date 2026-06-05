import os
import subprocess
from config.logger import setup_logger

logger = setup_logger("core.voice.whatsapp_voice_handler")

class WhatsAppVoiceHandler:
    def __init__(self):
        logger.info("Initializing WhatsApp Voice Handler")

    def convert_ogg_to_wav(self, ogg_filepath: str) -> str:
        """
        WhatsApp sends voice notes in OGG (Opus) format.
        Whisper.cpp requires 16kHz WAV format. 
        Uses ffmpeg to securely convert the file offline.
        """
        if not os.path.exists(ogg_filepath):
            logger.error(f"OGG file not found: {ogg_filepath}")
            return ""

        wav_filepath = ogg_filepath.replace(".ogg", ".wav")
        logger.info(f"Converting {ogg_filepath} to 16kHz WAV...")
        
        try:
            # Standard ffmpeg command to convert audio to 16kHz mono WAV
            command = [
                "ffmpeg", "-y", "-i", ogg_filepath,
                "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
                wav_filepath
            ]
            
            # Execute synchronously as it is extremely fast
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            logger.info(f"Audio conversion successful: {wav_filepath}")
            return wav_filepath
            
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg conversion failed: {str(e)}")
            return ""
        except FileNotFoundError:
            logger.error("ffmpeg is not installed or not in PATH. Audio conversion will fail.")
            return ""
