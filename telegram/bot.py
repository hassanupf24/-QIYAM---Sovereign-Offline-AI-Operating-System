import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.commands import start_command, help_command, status_command, reset_command
from telegram.handlers import handle_text_message
from telegram.file_handler import handle_document
from config.logger import setup_logger

logger = setup_logger("telegram.bot")

def main():
    """Starts the Telegram Bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set!")
        return

    logger.info("Initializing Telegram Bot API...")
    
    # Create the application
    application = Application.builder().token(token).build()

    # Register Command Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("reset", reset_command))

    # Register Message Handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Register File Handlers (CSV, PDF, etc.)
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    logger.info("Telegram Bot is running in polling mode...")
    
    # Start polling
    # In production, you might want to use run_webhook() mapped to a FastAPI endpoint instead
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
