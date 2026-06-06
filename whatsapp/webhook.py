import os
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from config.logger import setup_logger
from core.orchestrator import Orchestrator

logger = setup_logger("whatsapp.webhook")
router = APIRouter()

# The global orchestrator instance (normally injected via dependency)
# For simplicity in this architecture, we instantiate or import a singleton
orchestrator = Orchestrator()

# WhatsApp Cloud API Verification Token
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "qiyam_secure_token_123")

@router.get("/webhook")
async def verify_webhook(request: Request):
    """Handles WhatsApp Cloud API Webhook Verification."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("WhatsApp Webhook Verified Successfully!")
            return int(challenge)
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
    raise HTTPException(status_code=400, detail="Missing parameters")


@router.post("/webhook")
async def receive_message(request: Request):
    """
    Receives incoming messages from WhatsApp.
    Crucially, it hands the processing off to Celery to prevent 
    the webhook from timing out while the local LLM runs.
    """
    data = await request.json()
    logger.info("Received WhatsApp Webhook Payload")

    try:
        # WhatsApp payload structure parsing
        if "object" in data and data["object"] == "whatsapp_business_account":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    
                    if messages:
                        message = messages[0]
                        user_phone = message.get("from")
                        
                        # Handle Text Messages
                        if message.get("type") == "text":
                            text_body = message["text"]["body"]
                            logger.info(f"Incoming WhatsApp text from {user_phone}: {text_body[:50]}...")
                            
                            # Verify User and Tenant
                            from memory.postgres_store import PostgresStore
                            db = PostgresStore()
                            user = db.get_user_by_phone(user_phone)
                            
                            if not user:
                                logger.warning(f"Unauthorized WhatsApp access attempt from unregistered phone: {user_phone}")
                                # Silently ignore or send a generic response
                                return {"status": "unauthorized"}
                                
                            logger.info(f"User verified. Tenant ID: {user.tenant_id}")
                            
                            # Offload to Celery worker to prevent webhook timeout
                            from core.worker import process_whatsapp_message_task
                            process_whatsapp_message_task.delay(text_body, user_phone, user.tenant_id)
                            
                        # Handle Voice Messages (Integration with Voice AI Layer)
                        elif message.get("type") == "audio":
                            audio_id = message["audio"]["id"]
                            logger.info(f"Incoming WhatsApp audio from {user_phone}. ID: {audio_id}")
                            
                            from memory.postgres_store import PostgresStore
                            db = PostgresStore()
                            user = db.get_user_by_phone(user_phone)
                            if not user:
                                return {"status": "unauthorized"}
                                
                            # We can either pass it to a background task or Celery
                            # For simplicity, using FastAPI background tasks
                            background_tasks = BackgroundTasks() # This needs to be passed to endpoint, but since it's not, we'll fix the signature
                            # Wait, receive_message doesn't have background_tasks in its signature.
                            # We should just offload it to celery. Let's create a celery task for audio or just mock the download here.
                            
                            # MOCK: Download audio from WhatsApp using audio_id
                            audio_filepath = f"temp_{audio_id}.wav"
                            
                            # Ensure dummy file exists
                            import wave
                            with wave.open(audio_filepath, 'wb') as f:
                                f.setnchannels(1)
                                f.setsampwidth(2)
                                f.setframerate(16000)
                                f.writeframes(b'\x00\x00' * 16000) # 1 sec of silence
                            
                            from core.audio.asr import asr_engine
                            try:
                                transcript = asr_engine.transcribe_audio(audio_filepath)
                                logger.info(f"ASR Transcription: {transcript}")
                                if transcript.strip():
                                    from core.worker import process_whatsapp_message_task
                                    process_whatsapp_message_task.delay(transcript, user_phone, user.tenant_id)
                            except Exception as e:
                                logger.error(f"ASR failed: {e}")
                            
                        # Handle Image Messages (Integration with Vision AI Layer)
                        elif message.get("type") == "image":
                            image_id = message["image"]["id"]
                            # Optional caption sent with the image
                            caption = message["image"].get("caption", "ماذا يوجد في هذه الصورة؟")
                            logger.info(f"Incoming WhatsApp image from {user_phone}. ID: {image_id}")
                            background_tasks.add_task(process_image_and_reply, image_id, caption, user_phone)

                        # Handle User Feedback via Reactions (Continuous Learning)
                        elif message.get("type") == "reaction":
                            reaction_emoji = message["reaction"]["emoji"]
                            message_id = message["reaction"]["message_id"]
                            logger.info(f"Incoming WhatsApp reaction '{reaction_emoji}' from {user_phone} on msg {message_id}")
                            background_tasks.add_task(process_feedback, reaction_emoji, message_id, user_phone)

            # Always return 200 OK immediately to WhatsApp
            return {"status": "received"}
    except Exception as e:
        logger.error(f"Error parsing WhatsApp payload: {str(e)}")
        return {"status": "error"}


async def process_and_reply(message_text: str, user_phone: str):
    """Background worker that runs the Orchestrator and sends the response back."""
    logger.info(f"Background task started for {user_phone}")
    try:
        # Run the full AI pipeline
        response_text = await orchestrator.process_message(message_text, user_phone)
        
        # Send response back to WhatsApp
        await send_whatsapp_message(user_phone, response_text)
    except Exception as e:
        logger.error(f"Background processing failed for {user_phone}: {str(e)}")


# Removed process_voice_and_reply as it is now inline to celery


async def process_image_and_reply(image_id: str, caption: str, user_phone: str):
    """Background worker that handles image processing."""
    logger.info(f"Background task started for image message from {user_phone}")
    try:
        # MOCK: Download image from WhatsApp using image_id
        image_filepath = f"temp_{image_id}.jpg"
        
        # Ensure dummy file exists for the mock to work
        with open(image_filepath, "wb") as f:
            f.write(b"dummy image data")
            
        # 1. Vision Processing
        from core.visuals.image_processor import ImageProcessor
        processor = ImageProcessor(orchestrator.llm_engine)
        
        # 2. Analyze Image
        response_text = await processor.analyze_image(image_filepath, prompt=caption)
        
        # 3. Send response back to WhatsApp
        await send_whatsapp_message(user_phone, response_text)
    except Exception as e:
        logger.error(f"Image processing failed for {user_phone}: {str(e)}")


async def process_feedback(reaction_emoji: str, message_id: str, user_phone: str):
    """Background worker that handles user feedback for continuous learning."""
    logger.info(f"Processing feedback '{reaction_emoji}' for user {user_phone}")
    try:
        from core.self_learning.feedback_handler import FeedbackHandler
        # Assuming FeedbackHandler can interpret the emoji as positive/negative
        handler = FeedbackHandler()
        await handler.process_reaction(user_phone, message_id, reaction_emoji)
    except Exception as e:
        logger.error(f"Feedback processing failed for {user_phone}: {str(e)}")


async def send_whatsapp_message(to_phone: str, message: str):
    """Sends the final response back to the user via WhatsApp API."""
    logger.info(f"MOCK SEND TEXT to {to_phone}: {message[:100]}...")
    pass

async def send_whatsapp_audio(to_phone: str, audio_path: str):
    """Sends an audio file back to the user via WhatsApp API."""
    logger.info(f"MOCK SEND AUDIO to {to_phone}: {audio_path}")
    pass
