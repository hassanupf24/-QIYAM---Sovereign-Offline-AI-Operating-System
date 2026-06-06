import json
from core.llm_engine import LLMEngine
from memory.graph_store import GraphStore
from config.logger import setup_logger

logger = setup_logger("agents.knowledge_agent")

class KnowledgeAgent:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine
        self.graph_store = GraphStore()
        
    async def extract_and_store(self, text: str, tenant_id: str):
        """
        Analyzes unstructured text, extracts knowledge triples (Subject, Relation, Object),
        and stores them in Neo4j under the specific tenant.
        """
        logger.info(f"KnowledgeAgent extracting from text in tenant {tenant_id}")
        
        system_prompt = """
You are a highly capable Knowledge Extraction AI.
Your task is to read the provided text and extract semantic relationships (triples) representing facts, events, or entities.
Focus on extracting: People, Organizations, Locations, Projects, and key Domain Concepts.

Output the extracted triples strictly as a JSON list of arrays, like this:
[
  ["Subject", "RELATION", "Object"],
  ["Khalid", "LEADS", "Vision 2030"]
]

Do not include any other text, markdown, or explanations outside the JSON array.
If no meaningful relationships are found, output an empty array: []
"""
        full_prompt = f"{system_prompt}\n\nText to analyze:\n{text}"
        
        try:
            response = await self.llm.generate(full_prompt)
            
            # Clean up response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
                
            triples = json.loads(response.strip())
            
            if not isinstance(triples, list):
                logger.warning("KnowledgeAgent output is not a list. Skipping.")
                return
                
            await self.graph_store.connect()
            
            count = 0
            for triple in triples:
                if len(triple) == 3:
                    subject, relation, object_entity = triple
                    # Normalize relation to uppercase with underscores
                    relation = relation.upper().replace(" ", "_")
                    await self.graph_store.add_entity_relation(subject, relation, object_entity, tenant_id)
                    count += 1
                    
            logger.info(f"Successfully extracted and stored {count} triples.")
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse KnowledgeAgent output as JSON: {response}")
        except Exception as e:
            logger.error(f"Knowledge extraction error: {str(e)}")
        finally:
            await self.graph_store.close()
