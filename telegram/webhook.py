import os
from fastapi import APIRouter, Request, BackgroundTasks
from config.logger import setup_logger
from core.orchestrator import orchestrator

logger = setup_logger("telegram.webhook")
router = APIRouter()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "mock_telegram_token")

@router.post("/telegram/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receives incoming messages from Telegram, identical in concept to WhatsApp.
    """
    try:
        update = await request.json()
        
        if "message" in update:
            message = update["message"]
            chat_id = str(message["chat"]["id"])
            
            if "text" in message:
                text = message["text"]
                logger.info(f"Incoming Telegram text from {chat_id}: {text}")
                
                # We use the same background processing as WhatsApp
                background_tasks.add_task(process_and_reply_telegram, text, chat_id)
                
            elif "voice" in message:
                voice_id = message["voice"]["file_id"]
                logger.info(f"Incoming Telegram voice from {chat_id}: {voice_id}")
                # We'd route this to process_voice_and_reply, similar to WhatsApp
                
            elif "photo" in message:
                photo_id = message["photo"][-1]["file_id"]
                caption = message.get("caption", "ماذا يوجد في هذه الصورة؟")
                logger.info(f"Incoming Telegram photo from {chat_id}: {photo_id}")
                # We'd route this to process_image_and_reply
                
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {str(e)}")
        return {"ok": False, "error": str(e)}

async def process_and_reply_telegram(message_text: str, chat_id: str):
    """Background worker that runs the Orchestrator and sends the response back to Telegram."""
    logger.info(f"Telegram Background task started for {chat_id}")
    try:
        # Run the full AI pipeline
        response_text = await orchestrator.process_message(message_text, chat_id)
        
        # Send response back to Telegram
        await send_telegram_message(chat_id, response_text)
    except Exception as e:
        logger.error(f"Telegram Background processing failed for {chat_id}: {str(e)}")

async def send_telegram_message(chat_id: str, text: str):
    """Mocks sending a message back to Telegram."""
    # In production, uses httpx to POST to https://api.telegram.org/bot{TOKEN}/sendMessage
    logger.info(f"MOCK SEND TELEGRAM to {chat_id}: {text[:100]}...")
