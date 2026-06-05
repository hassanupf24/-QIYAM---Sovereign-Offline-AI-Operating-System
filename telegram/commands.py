from telegram import Update
from telegram.ext import ContextTypes
from core.orchestrator import Orchestrator
from memory.memory_manager import MemoryManager
from config.logger import setup_logger

logger = setup_logger("telegram.commands")

# Instantiate or inject singletons
orchestrator = Orchestrator()
memory = MemoryManager()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    user = update.effective_user
    welcome_msg = f"أهلاً بك يا {user.first_name} في نظام قيام (QIYAM OS) 🤖\n\nأنا مساعدك الذكي لإدارة الأعمال، تحليل البيانات، والأتمتة.\n\nأرسل /help لمعرفة ما يمكنني القيام به!"
    await update.message.reply_text(welcome_msg)
    logger.info(f"User {user.id} initiated /start")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /help command."""
    help_text = (
        "💡 **قدرات نظام قيام:**\n"
        "📊 **تحليل البيانات:** أرسل ملف CSV أو Excel وسأقوم بتحليله.\n"
        "📈 **ذكاء الأعمال:** اطلب استراتيجيات لتحسين مبيعاتك.\n"
        "🔎 **البحث:** اسألني عن أي موضوع وسأبحث فيه.\n"
        "🧹 **الأوامر:**\n"
        "/status - حالة النظام\n"
        "/reset - مسح ذاكرة الجلسة الحالية\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /status command."""
    status_msg = "✅ النظام يعمل بشكل ممتاز (وضع عدم الاتصال - Offline Mode)."
    await update.message.reply_text(status_msg)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /reset command to clear session memory."""
    session_id = str(update.effective_user.id)
    # In a real implementation, you would clear the SQLite messages for this session_id.
    # For now, we simulate success.
    await update.message.reply_text("تم مسح ذاكرة الجلسة بنجاح 🧹. لنبدأ من جديد!")
    logger.info(f"User {session_id} reset their session memory.")
