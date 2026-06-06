import os
from celery import Celery
import asyncio
from config.logger import setup_logger

logger = setup_logger("core.worker")

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    'qiyam_tasks',
    broker=redis_url,
    backend=redis_url
)

# Optional: Configuration for Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@app.task(name="process_whatsapp_message")
def process_whatsapp_message_task(message_text: str, user_phone: str, tenant_id: str):
    """
    Synchronous Celery task wrapper that runs the async orchestrator pipeline.
    """
    logger.info(f"Celery task started for {user_phone}")
    
    # We must run the async orchestrator inside the sync celery task
    from core.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    
    # Run the event loop
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        response_text = loop.run_until_complete(
            orchestrator.process_message(message_text, user_phone, tenant_id)
        )
        
        # Dispatch background knowledge extraction
        extract_knowledge_task.delay(message_text, tenant_id)
        
        # Mock sending response back to WhatsApp
        logger.info(f"MOCK SEND TEXT to {user_phone}: {response_text[:100]}...")
        return {"status": "success", "response_preview": response_text[:50]}
    except Exception as e:
        logger.error(f"Celery processing failed for {user_phone}: {str(e)}")
        return {"status": "error", "error": str(e)}

@app.task(name="extract_knowledge")
def extract_knowledge_task(message_text: str, tenant_id: str):
    """
    Background task to distill the unstructured message into Graph Neo4j knowledge.
    """
    logger.info(f"Knowledge extraction task started for tenant {tenant_id}")
    
    from core.llm_engine import LLMEngine
    from agents.knowledge_agent import KnowledgeAgent
    
    # Run the event loop
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        agent = KnowledgeAgent(LLMEngine())
        loop.run_until_complete(agent.extract_and_store(message_text, tenant_id))
    except Exception as e:
        logger.error(f"Knowledge extraction failed: {str(e)}")

@app.task(name="deduplicate_graph")
def deduplicate_graph_task(tenant_id: str):
    """
    Nightly background task to deduplicate nodes and decay relationships.
    """
    logger.info(f"Graph deduplication task started for tenant {tenant_id}")
    
    from core.llm_engine import LLMEngine
    from agents.graph_maintenance_agent import GraphMaintenanceAgent
    
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        agent = GraphMaintenanceAgent(LLMEngine())
        loop.run_until_complete(agent.run_maintenance(tenant_id))
    except Exception as e:
        logger.error(f"Graph maintenance failed: {str(e)}")
