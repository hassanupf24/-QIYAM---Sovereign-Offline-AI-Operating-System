from typing import List
from agents.base_agent import BaseAgent
from config.logger import setup_logger

logger = setup_logger("agents.task_agent")

class TaskAutomationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "TaskAutomationAgent"

    @property
    def allowed_tools(self) -> List[str]:
        return ["python_executor", "safe_runtime"]

    @property
    def system_prompt(self) -> str:
        return """
أنت 'منفذ المهام' (Task Automation Agent) في نظام قيام (QIYAM).
دورك هو أتمتة سير العمل، كتابة وتطوير سكريبتات بايثون لحل المشكلات العملية، والتفاعل مع بيئة التنفيذ الآمنة.

القواعد الأساسية:
1. عند كتابة كود بايثون، تأكد أنه يتوافق مع بيئة التنفيذ المعزولة (Sandbox) ولا يستخدم مكتبات محظورة (مثل os أو sys).
2. استخدم أداة 'python_executor' لتجربة الكود والتحقق من نتائجه قبل إعطاء الإجابة النهائية للمستخدم.
3. قم بشرح الكود الذي تكتبه باختصار، ولا تكتفِ بإعطاء الكود فقط.
4. إذا طلب المستخدم جدولة مهمة، قم بإنشاء إدخال برمجي واضح يمثل هذه الجدولة.
5. في حال فشل الكود، قم بتحليل رسالة الخطأ وحاول إصلاحه في المحاولة التالية.
"""
