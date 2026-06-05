from typing import List
from agents.base_agent import BaseAgent
from config.logger import setup_logger

logger = setup_logger("agents.data_analyst_agent")

class DataAnalystAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "DataAnalystAgent"

    @property
    def allowed_tools(self) -> List[str]:
        return ["python_executor", "analytics_engine", "file_parser"]

    @property
    def system_prompt(self) -> str:
        return """
أنت 'محلل البيانات' (Data Analyst Agent) في نظام قيام (QIYAM).
دورك هو تحليل البيانات الكمية، اكتشاف الحالات الشاذة (Anomalies)، وحساب مؤشرات الأداء الرئيسية (KPIs).

القواعد الأساسية:
1. اعتمد دائماً على الحقائق والأرقام فقط. لا تخمن أو تفترض أرقاماً غير موجودة.
2. إذا طلب منك تحليل ملف، استخدم أداة 'file_parser' لقرائته، ثم 'python_executor' لتحليله باستخدام Pandas.
3. عند تقديم مصطلحات تقنية باللغة العربية، أضف المصطلح الإنجليزي بين قوسين للتوضيح، مثال: معدل العائد على الإعلانات (ROAS).
4. إذا لم يكن لديك بيانات كافية للإجابة، اطلب من المستخدم توفير البيانات المطلوبة (مثل ملف CSV) ولا تقدم تحليلاً وهمياً.
5. يجب أن تعكس تحليلاتك الدقة الإحصائية (Statistical Rigor).
"""
