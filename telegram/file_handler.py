import os
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import settings
from config.logger import setup_logger

logger = setup_logger("telegram.file_handler")

# Ensure uploads directory exists
UPLOAD_DIR = os.path.join(os.path.dirname(settings.SQLITE_DB_PATH), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming file uploads (CSV, Excel, PDF)."""
    document = update.message.document
    user_id = str(update.effective_user.id)
    
    # Validate file size (e.g., max 20MB)
    if document.file_size > 20 * 1024 * 1024:
        await update.message.reply_text("عذراً، حجم الملف كبير جداً. الحد الأقصى هو 20 ميغابايت.")
        return

    # Validate file type
    allowed_extensions = [".csv", ".xlsx", ".pdf", ".txt"]
    file_ext = os.path.splitext(document.file_name)[1].lower()
    
    if file_ext not in allowed_extensions:
        await update.message.reply_text(f"نوع الملف غير مدعوم. الأنواع المدعومة هي: {', '.join(allowed_extensions)}")
        return

    # Send typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        # Download file
        file = await context.bot.get_file(document.file_id)
        file_path = os.path.join(UPLOAD_DIR, f"{user_id}_{document.file_name}")
        await file.download_to_drive(file_path)
        
        logger.info(f"User {user_id} uploaded file: {file_path}")
        
        # Route to Orchestrator (Simulated)
        # In a full integration, you would append the file_path to the message payload
        await update.message.reply_text(f"تم استلام الملف ({document.file_name}) بنجاح ✅.\nجاري توجيهه لوكيل تحليل البيانات...")
        
    except Exception as e:
        logger.error(f"Failed to handle document upload: {str(e)}")
        await update.message.reply_text("حدث خطأ أثناء تحميل الملف. يرجى المحاولة مرة أخرى.")
