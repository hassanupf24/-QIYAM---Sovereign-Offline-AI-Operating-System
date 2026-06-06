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
1. استخرج المعلومات كما هي من الملفات ومن سياق الرسم البياني المعرفي (Knowledge Graph Context) إن وجد، ولا تخترع أو تهلوس بيانات غير موجودة.
2. عند كتابة الملخصات، استخدم تنسيق النقاط (Bullet points) لتسهيل القراءة.
3. إذا طلب منك تلخيص ملف، استخدم أداة 'file_parser' لاستخراج النصوص قبل الإجابة.
4. حافظ على نبرة أكاديمية أو مهنية بحسب طبيعة السؤال، لكن كن واضحاً ومباشراً.
5. إذا تضمن النص مفاهيم معقدة باللغة العربية، بسطها بطريقة واضحة للمستخدم.
"""

    async def execute(self, session_id: str, task: str, tenant_id: str = None) -> str:
        """Overrides base execute to inject Graph RAG context."""
        logger.info(f"ResearchAgent executing with Graph RAG for session {session_id} in tenant {tenant_id}")
        
        graph_context = ""
        if tenant_id:
            try:
                from memory.graph_store import GraphStore
                import re
                
                # Extremely naive entity extraction for keyword lookup
                # In production, this would use a fast local NER model
                words = re.findall(r'\b\w{3,}\b', task)
                
                store = GraphStore()
                await store.connect()
                
                relations = []
                # Query top 3 longest words as potential entities
                potential_entities = sorted(words, key=len, reverse=True)[:3]
                
                for entity in potential_entities:
                    entity_rels = await store.get_relations(entity, tenant_id)
                    relations.extend(entity_rels)
                    
                await store.close()
                
                # Deduplicate and format
                relations = list(set(relations))
                if relations:
                    graph_context = "\n[سياق الرسم البياني المعرفي المستخرج من المحادثات السابقة]:\n" + "\n".join(relations)
            except Exception as e:
                logger.error(f"Failed to fetch Graph RAG context: {e}")
                
        augmented_task = task
        if graph_context:
            augmented_task = f"{task}\n\n{graph_context}"
            
        return await super().execute(session_id, augmented_task, tenant_id)

