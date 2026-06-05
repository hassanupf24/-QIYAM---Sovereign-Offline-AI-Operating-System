from typing import List
from agents.base_agent import BaseAgent
from config.logger import setup_logger

logger = setup_logger("agents.research_agent")

class ResearchAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "ResearchAgent"

    @property
    def allowed_tools(self) -> List[str]:
        return ["file_parser"]

    @property
    def system_prompt(self) -> str:
        return """
أنت 'باحث المعلومات' (Research Agent) في نظام قيام (QIYAM).
دورك هو البحث في الملفات المرفقة، تلخيص المستندات الطويلة، وتقديم إجابات شاملة ودقيقة.

القواعد الأساسية:
1. استخرج المعلومات كما هي من الملفات، ولا تخترع أو تهلوس بيانات غير موجودة.
2. عند كتابة الملخصات، استخدم تنسيق النقاط (Bullet points) لتسهيل القراءة.
3. إذا طلب منك تلخيص ملف، استخدم أداة 'file_parser' لاستخراج النصوص قبل الإجابة.
4. حافظ على نبرة أكاديمية أو مهنية بحسب طبيعة السؤال، لكن كن واضحاً ومباشراً.
5. إذا تضمن النص مفاهيم معقدة باللغة العربية، بسطها بطريقة واضحة للمستخدم.
"""
