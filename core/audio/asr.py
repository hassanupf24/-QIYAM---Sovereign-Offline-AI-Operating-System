import os
from config.logger import setup_logger

logger = setup_logger("core.audio.asr")

class LocalASR:
    """
    Automatic Speech Recognition using faster-whisper.
    Requires GPU offloading for optimal real-time performance.
    """
    def __init__(self, model_size="large-v3", device="cuda", compute_type="float16"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def _load_model(self):
        try:
            from faster_whisper import WhisperModel
            if self.model is None:
                logger.info(f"Loading faster-whisper model '{self.model_size}' on {self.device} ({self.compute_type})...")
                # fallback to cpu if cuda fails
                try:
                    self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
                except Exception as e:
                    logger.warning(f"Failed to load Whisper on {self.device}. Falling back to CPU. Error: {e}")
                    self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
                logger.info("Whisper model loaded successfully.")
        except ImportError:
            logger.error("faster-whisper is not installed. Please install it to use Voice-to-Voice.")
            raise

    def transcribe_audio(self, file_path: str, language="ar") -> str:
        """
        Transcribes the given audio file path.
        Defaults to Arabic language for optimal performance.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        self._load_model()
        
        logger.info(f"Transcribing audio file: {file_path}")
        try:
            segments, info = self.model.transcribe(file_path, beam_size=5, language=language)
            logger.info(f"Detected language '{info.language}' with probability {info.language_probability}")
            
            transcript = ""
            for segment in segments:
                transcript += segment.text + " "
                
            return transcript.strip()
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

# Singleton instance
asr_engine = LocalASR()
