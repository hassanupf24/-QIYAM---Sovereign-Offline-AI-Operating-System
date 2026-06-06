import os
from neo4j import AsyncGraphDatabase
from config.logger import setup_logger

logger = setup_logger("memory.graph_store")

class GraphStore:
    def __init__(self):
        # Read from environment or use default from docker-compose
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "qiyam_graph_123")
        self.driver = None

    async def connect(self):
        try:
            self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info("Successfully connected to Neo4j Graph Database.")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")

    async def close(self):
        if self.driver:
            await self.driver.close()

    async def add_entity_relation(self, subject: str, relation: str, object_entity: str, tenant_id: str):
        """
        Adds a semantic relationship between two entities within a specific tenant.
        e.g., add_entity_relation("User_123", "LIVES_IN", "Riyadh", "tenant_a")
        """
        if not self.driver:
            logger.warning("GraphStore not connected. Skipping relation addition.")
            return

        # Initialize relationship with confidence 1.0 if it doesn't exist
        query = (
            "MERGE (s:Entity {name: $subject, tenant_id: $tenant_id}) "
            "MERGE (o:Entity {name: $object_entity, tenant_id: $tenant_id}) "
            "MERGE (s)-[r:`" + relation + "`]->(o) "
            "ON CREATE SET r.confidence = 1.0, r.created_at = datetime() "
            "RETURN s, r, o"
        )
        try:
            async with self.driver.session() as session:
                await session.run(query, subject=subject, object_entity=object_entity, tenant_id=tenant_id)
                logger.info(f"Added Graph Relation [{tenant_id}]: {subject} -[{relation}]-> {object_entity}")
        except Exception as e:
            logger.error(f"Failed to add relation: {str(e)}")

    async def get_relations(self, entity_name: str, tenant_id: str) -> list:
        """
        Retrieves all relationships for a given entity, scoped to the tenant.
        """
        if not self.driver:
            return []

        query = (
            "MATCH (e:Entity {name: $entity_name, tenant_id: $tenant_id})-[r]->(o:Entity {tenant_id: $tenant_id}) "
            "RETURN type(r) AS relation, o.name AS target "
            "UNION "
            "MATCH (s:Entity {tenant_id: $tenant_id})-[r]->(e:Entity {name: $entity_name, tenant_id: $tenant_id}) "
            "RETURN type(r) AS relation, s.name AS target"
        )
        
        relations = []
        try:
            async with self.driver.session() as session:
                result = await session.run(query, entity_name=entity_name, tenant_id=tenant_id)
                async for record in result:
                    relations.append(f"({entity_name}) -[{record['relation']}]- ({record['target']})")
        except Exception as e:
            logger.error(f"Failed to retrieve relations: {str(e)}")
            
        return relations

    async def get_all_nodes(self, tenant_id: str) -> list:
        if not self.driver: return []
        query = "MATCH (n:Entity {tenant_id: $tenant_id}) RETURN n.name as name"
        nodes = []
        try:
            async with self.driver.session() as session:
                result = await session.run(query, tenant_id=tenant_id)
                async for record in result:
                    nodes.append(record["name"])
        except Exception as e:
            logger.error(f"Failed to get nodes: {e}")
        return nodes

    async def merge_nodes(self, tenant_id: str, keep_node: str, delete_node: str):
        if not self.driver: return
        # Using APOC for true refactor, or a manual cypher if APOC isn't installed.
        # Assuming APOC is installed in the Neo4j container:
        query = """
        MATCH (keep:Entity {name: $keep_node, tenant_id: $tenant_id})
        MATCH (del:Entity {name: $delete_node, tenant_id: $tenant_id})
        CALL apoc.refactor.mergeNodes([keep, del], {properties: 'overwrite', mergeRels: true})
        YIELD node
        RETURN node
        """
        try:
            async with self.driver.session() as session:
                await session.run(query, keep_node=keep_node, delete_node=delete_node, tenant_id=tenant_id)
                logger.info(f"Merged {delete_node} into {keep_node} for tenant {tenant_id}")
        except Exception as e:
            logger.error(f"Merge nodes failed: {e}")

    async def apply_decay(self, tenant_id: str):
        if not self.driver: return
        query = """
        MATCH ()-[r]->()
        WHERE r.confidence IS NOT NULL
        SET r.confidence = r.confidence * 0.9
        """
        try:
            async with self.driver.session() as session:
                await session.run(query)
                logger.info(f"Applied 10% decay to all relationship confidences for tenant {tenant_id}")
        except Exception as e:
            logger.error(f"Decay failed: {e}")
