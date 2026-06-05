import json
import math
from typing import Dict, List
from core.llm_engine import LLMEngine
from config.logger import setup_logger

logger = setup_logger("core.intent_classifier")

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

class IntentClassifier:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine
        self.intent_examples = {
            "analyze_data": ["احسب المعدل", "تحليل بيانات", "ارسم رسم بياني", "جدول إكسيل"],
            "compute_kpi": ["مؤشرات الأداء", "أرباح الشركة", "KPI", "مبيعات"],
            "summarize": ["لخص هذا", "أعطني الزبدة", "ملخص مقال"],
            "research": ["ابحث عن", "معلومات حول", "من هو", "تاريخ"],
            "schedule": ["ذكرني", "موعد", "غدا في الساعة", "جدول"],
            "general_chat": ["مرحبا", "كيف حالك", "شكرا", "صباح الخير"]
        }
        self.intent_embeddings: Dict[str, List[List[float]]] = {}
        self._embeddings_loaded = False

    async def _load_embeddings(self):
        if self._embeddings_loaded:
            return
        logger.info("Loading intent embeddings for Semantic Router...")
        for intent, examples in self.intent_examples.items():
            self.intent_embeddings[intent] = []
            for ex in examples:
                emb = await self.llm.embed(ex)
                if emb:
                    self.intent_embeddings[intent].append(emb)
        self._embeddings_loaded = True

    async def classify(self, message: str) -> dict:
        logger.info("Classifying intent via Semantic Router...")
        await self._load_embeddings()
        
        try:
            msg_emb = await self.llm.embed(message)
            if not msg_emb:
                return {"intent": "general_chat", "confidence": 0.0, "language": "ar"}

            best_intent = "general_chat"
            best_score = -1.0

            for intent, embs in self.intent_embeddings.items():
                for emb in embs:
                    score = cosine_similarity(msg_emb, emb)
                    if score > best_score:
                        best_score = score
                        best_intent = intent

            logger.info(f"Classified intent: {best_intent} with confidence {best_score}")
            return {"intent": best_intent, "confidence": best_score, "language": "ar"}
            
        except Exception as e:
            logger.error(f"Error during semantic classification: {str(e)}")
            return {"intent": "general_chat", "confidence": 0.0, "language": "unknown"}
