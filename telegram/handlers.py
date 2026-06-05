from telegram import Update
from telegram.ext import ContextTypes
from core.orchestrator import Orchestrator
from config.logger import setup_logger

logger = setup_logger("telegram.handlers")
orchestrator = Orchestrator()

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Main entry point for user text messages. Routes them to the QIYAM Orchestrator.
    """
    user_id = str(update.effective_user.id)
    text = update.message.text
    chat_id = update.effective_chat.id
    
    logger.info(f"Received Telegram message from {user_id}: {text[:50]}...")
    
    # 1. Send "Typing..." action to show responsiveness
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    
    # 2. Multi-Agent Awareness (Optional Debug UX)
    # Inform user that system is processing
    processing_msg = await context.bot.send_message(chat_id=chat_id, text="🔍 جاري التحليل والمعالجة...")
    
    try:
        # 3. Route to QIYAM Orchestrator
        response = await orchestrator.process_message(text, user_id)
        
        # 4. Return Final Output
        await context.bot.delete_message(chat_id=chat_id, message_id=processing_msg.message_id)
        await context.bot.send_message(chat_id=chat_id, text=response)
        
    except Exception as e:
        logger.error(f"Error processing Telegram message: {str(e)}")
        await context.bot.delete_message(chat_id=chat_id, message_id=processing_msg.message_id)
        await context.bot.send_message(
            chat_id=chat_id, 
            text="عذراً، حدث خطأ داخلي أثناء المعالجة. يرجى المحاولة لاحقاً."
        )
