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

    async def add_entity_relation(self, subject: str, relation: str, object_entity: str):
        """
        Adds a semantic relationship between two entities.
        e.g., add_entity_relation("User_123", "LIVES_IN", "Riyadh")
        """
        if not self.driver:
            logger.warning("GraphStore not connected. Skipping relation addition.")
            return

        query = (
            "MERGE (s:Entity {name: $subject}) "
            "MERGE (o:Entity {name: $object_entity}) "
            "MERGE (s)-[r:`" + relation + "`]->(o) "
            "RETURN s, r, o"
        )
        try:
            async with self.driver.session() as session:
                await session.run(query, subject=subject, object_entity=object_entity)
                logger.info(f"Added Graph Relation: {subject} -[{relation}]-> {object_entity}")
        except Exception as e:
            logger.error(f"Failed to add relation: {str(e)}")

    async def get_relations(self, entity_name: str) -> list:
        """
        Retrieves all relationships for a given entity.
        """
        if not self.driver:
            return []

        query = (
            "MATCH (e:Entity {name: $entity_name})-[r]->(o) "
            "RETURN type(r) AS relation, o.name AS target "
            "UNION "
            "MATCH (s)-[r]->(e:Entity {name: $entity_name}) "
            "RETURN type(r) AS relation, s.name AS target"
        )
        
        relations = []
        try:
            async with self.driver.session() as session:
                result = await session.run(query, entity_name=entity_name)
                async for record in result:
                    relations.append(f"({entity_name}) -[{record['relation']}]- ({record['target']})")
        except Exception as e:
            logger.error(f"Failed to retrieve relations: {str(e)}")
            
        return relations
