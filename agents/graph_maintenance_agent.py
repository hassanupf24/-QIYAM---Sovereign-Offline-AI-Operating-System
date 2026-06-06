from typing import List
from config.logger import setup_logger
from memory.graph_store import GraphStore
from core.llm_engine import LLMEngine
import json

logger = setup_logger("agents.graph_maintenance")

class GraphMaintenanceAgent:
    """
    Nightly maintenance agent.
    Deduplicates nodes and decays relationship confidences.
    """
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine
        self.graph = GraphStore()

    async def run_maintenance(self, tenant_id: str):
        logger.info(f"Starting Graph Maintenance for tenant {tenant_id}")
        await self.graph.connect()
        try:
            # 1. Decay Confidence
            await self.graph.apply_decay(tenant_id)
            
            # 2. Node Deduplication
            nodes = await self.graph.get_all_nodes(tenant_id)
            if len(nodes) < 2:
                return
                
            # Naive approach: send a subset to the LLM to find duplicates
            # In production, we'd use vector embeddings to find similar nodes first.
            prompt = f"""
            Analyze the following list of entities and identify duplicates (e.g. 'Vision_2030' and 'Vision2030').
            Return a JSON array of objects with 'keep' and 'delete'.
            Entities: {nodes[:50]} # Limiting to 50 for demo
            
            Format strictly as:
            [ {{"keep": "canonical_name", "delete": "duplicate_name"}} ]
            """
            
            response = await self.llm.generate(prompt, "You are a data cleanliness AI. Output ONLY JSON.")
            
            # Parse JSON
            try:
                # Find brackets in case LLM added backticks
                start = response.find('[')
                end = response.rfind(']') + 1
                if start != -1 and end != -1:
                    json_str = response[start:end]
                    merges = json.loads(json_str)
                    
                    for merge in merges:
                        keep = merge.get("keep")
                        delete = merge.get("delete")
                        if keep and delete and keep in nodes and delete in nodes and keep != delete:
                            await self.graph.merge_nodes(tenant_id, keep, delete)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse LLM deduplication output: {response}")

        finally:
            await self.graph.close()
        logger.info(f"Graph Maintenance complete for {tenant_id}")
