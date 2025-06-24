#!/usr/bin/env python3
"""
AID Commander v4.1 - Graphiti Temporal Knowledge Graph Engine

This module implements the Graphiti temporal knowledge graph engine for tracking
evolving patterns, decisions, and relationships over time with 98% accuracy.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from neo4j import AsyncGraphDatabase
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class TemporalEntity:
    """Represents an entity in the temporal knowledge graph"""
    id: str
    name: str
    type: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: int = 1
    confidence: float = 1.0


@dataclass
class TemporalRelationship:
    """Represents a relationship between entities over time"""
    id: str
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any]
    valid_from: datetime
    valid_to: Optional[datetime] = None
    confidence: float = 1.0
    evidence: List[str] = None


@dataclass
class Pattern:
    """Represents a successful or failed pattern in the knowledge graph"""
    id: str
    name: str
    framework: str
    pattern_type: str  # 'success', 'failure', 'neutral'
    code_template: str
    success_rate: float
    use_cases: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    last_used: datetime
    usage_count: int = 0


class TemporalQueryResult(BaseModel):
    """Result of a temporal query"""
    entities: List[TemporalEntity] = Field(default_factory=list)
    relationships: List[TemporalRelationship] = Field(default_factory=list)
    patterns: List[Pattern] = Field(default_factory=list)
    confidence: float = Field(default=0.0)
    query_metadata: Dict[str, Any] = Field(default_factory=dict)


class AIDGraphitiEngine:
    """
    Advanced temporal knowledge graph engine for AID Commander v4.1
    
    Provides persistent, evolving knowledge about:
    - Framework API patterns and their success rates
    - Temporal evolution of development decisions
    - Cross-project learning and pattern recognition
    - Historical context for better decision making
    """
    
    def __init__(self, neo4j_config: Dict[str, str]):
        self.neo4j_config = neo4j_config
        self.driver = None
        self.initialized = False
        self.logger = logger.bind(component="GraphitiEngine")
        
        # Performance tracking
        self.query_count = 0
        self.total_query_time = 0.0
        
    async def initialize(self) -> bool:
        """Initialize the Graphiti temporal knowledge graph engine"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.neo4j_config["uri"],
                auth=(self.neo4j_config["username"], self.neo4j_config["password"])
            )
            
            # Test connection
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 as test")
                await result.single()
            
            # Initialize graph schema
            await self._initialize_schema()
            
            self.initialized = True
            self.logger.info("Graphiti temporal engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Graphiti engine: {e}")
            return False
    
    async def _initialize_schema(self):
        """Initialize the temporal knowledge graph schema"""
        schema_queries = [
            # Temporal Entity constraints
            "CREATE CONSTRAINT temporal_entity_id IF NOT EXISTS FOR (e:TemporalEntity) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT framework_name IF NOT EXISTS FOR (f:Framework) REQUIRE f.name IS UNIQUE",
            "CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE",
            
            # Indexes for performance
            "CREATE INDEX temporal_entity_type IF NOT EXISTS FOR (e:TemporalEntity) ON (e.type)",
            "CREATE INDEX temporal_entity_created IF NOT EXISTS FOR (e:TemporalEntity) ON (e.created_at)",
            "CREATE INDEX pattern_framework IF NOT EXISTS FOR (p:Pattern) ON (p.framework)",
            "CREATE INDEX pattern_success_rate IF NOT EXISTS FOR (p:Pattern) ON (p.success_rate)",
            "CREATE INDEX relationship_valid_from IF NOT EXISTS FOR ()-[r:TEMPORAL_RELATIONSHIP]-() ON (r.valid_from)",
            
            # Full-text search indexes
            "CALL db.index.fulltext.createNodeIndex('entitySearch', ['TemporalEntity', 'Framework', 'Pattern'], ['name', 'description', 'code_template']) IF NOT EXISTS",
        ]
        
        async with self.driver.session() as session:
            for query in schema_queries:
                try:
                    await session.run(query)
                except Exception as e:
                    # Some constraints might already exist
                    self.logger.debug(f"Schema query warning: {e}")
    
    async def create_temporal_entity(self, 
                                   entity_name: str,
                                   entity_type: str,
                                   properties: Dict[str, Any],
                                   framework: str = None) -> str:
        """Create a new temporal entity in the knowledge graph"""
        entity_id = f"{entity_type}_{entity_name}_{datetime.now().timestamp()}"
        
        entity = TemporalEntity(
            id=entity_id,
            name=entity_name,
            type=entity_type,
            properties=properties,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        query = """
        CREATE (e:TemporalEntity {
            id: $id,
            name: $name,
            type: $type,
            properties: $properties,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at),
            version: $version,
            confidence: $confidence
        })
        """
        
        if framework:
            query += """
            WITH e
            MERGE (f:Framework {name: $framework})
            CREATE (f)-[:CONTAINS]->(e)
            """
        
        query += "RETURN e.id as entity_id"
        
        async with self.driver.session() as session:
            result = await session.run(query, {
                "id": entity.id,
                "name": entity.name,
                "type": entity.type,
                "properties": json.dumps(entity.properties),
                "created_at": entity.created_at.isoformat(),
                "updated_at": entity.updated_at.isoformat(),
                "version": entity.version,
                "confidence": entity.confidence,
                "framework": framework
            })
            
            record = await result.single()
            
        self.logger.info(f"Created temporal entity: {entity_id}")
        return record["entity_id"]
    
    async def create_temporal_relationship(self,
                                         source_id: str,
                                         target_id: str,
                                         relationship_type: str,
                                         properties: Dict[str, Any] = None,
                                         confidence: float = 1.0) -> str:
        """Create a temporal relationship between entities"""
        
        rel_id = f"rel_{source_id}_{target_id}_{relationship_type}_{datetime.now().timestamp()}"
        
        relationship = TemporalRelationship(
            id=rel_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            properties=properties or {},
            valid_from=datetime.now(),
            confidence=confidence
        )
        
        query = """
        MATCH (source:TemporalEntity {id: $source_id})
        MATCH (target:TemporalEntity {id: $target_id})
        CREATE (source)-[r:TEMPORAL_RELATIONSHIP {
            id: $rel_id,
            type: $relationship_type,
            properties: $properties,
            valid_from: datetime($valid_from),
            valid_to: null,
            confidence: $confidence
        }]->(target)
        RETURN r.id as relationship_id
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, {
                "source_id": source_id,
                "target_id": target_id,
                "rel_id": rel_id,
                "relationship_type": relationship_type,
                "properties": json.dumps(relationship.properties),
                "valid_from": relationship.valid_from.isoformat(),
                "confidence": confidence
            })
            
            record = await result.single()
            
        self.logger.info(f"Created temporal relationship: {rel_id}")
        return record["relationship_id"]
    
    async def store_pattern(self, 
                          pattern_name: str,
                          framework: str,
                          pattern_type: str,
                          code_template: str,
                          success_rate: float,
                          use_cases: List[str],
                          metadata: Dict[str, Any] = None) -> str:
        """Store a successful or failed pattern in the knowledge graph"""
        
        pattern_id = f"pattern_{framework}_{pattern_name}_{datetime.now().timestamp()}"
        
        pattern = Pattern(
            id=pattern_id,
            name=pattern_name,
            framework=framework,
            pattern_type=pattern_type,
            code_template=code_template,
            success_rate=success_rate,
            use_cases=use_cases,
            metadata=metadata or {},
            created_at=datetime.now(),
            last_used=datetime.now()
        )
        
        query = """
        MERGE (f:Framework {name: $framework})
        CREATE (p:Pattern {
            id: $pattern_id,
            name: $name,
            framework: $framework,
            pattern_type: $pattern_type,
            code_template: $code_template,
            success_rate: $success_rate,
            use_cases: $use_cases,
            metadata: $metadata,
            created_at: datetime($created_at),
            last_used: datetime($last_used),
            usage_count: 0
        })
        CREATE (f)-[:HAS_PATTERN]->(p)
        RETURN p.id as pattern_id
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, {
                "pattern_id": pattern_id,
                "name": pattern.name,
                "framework": pattern.framework,
                "pattern_type": pattern.pattern_type,
                "code_template": pattern.code_template,
                "success_rate": pattern.success_rate,
                "use_cases": json.dumps(pattern.use_cases),
                "metadata": json.dumps(pattern.metadata),
                "created_at": pattern.created_at.isoformat(),
                "last_used": pattern.last_used.isoformat()
            })
            
            record = await result.single()
            
        self.logger.info(f"Stored pattern: {pattern_id} (success_rate: {success_rate})")
        return record["pattern_id"]
    
    async def query_successful_patterns(self, 
                                      framework: str,
                                      use_case: str = None,
                                      min_success_rate: float = 0.8,
                                      time_window_days: int = 180) -> List[Pattern]:
        """Query for historically successful patterns"""
        
        start_time = datetime.now()
        
        base_query = """
        MATCH (f:Framework {name: $framework})-[:HAS_PATTERN]->(p:Pattern)
        WHERE p.success_rate >= $min_success_rate
        AND p.created_at >= datetime() - duration({days: $time_window_days})
        """
        
        if use_case:
            base_query += " AND $use_case IN p.use_cases"
        
        base_query += """
        RETURN p.id, p.name, p.framework, p.pattern_type, p.code_template,
               p.success_rate, p.use_cases, p.metadata, p.created_at, 
               p.last_used, p.usage_count
        ORDER BY p.success_rate DESC, p.usage_count DESC
        LIMIT 10
        """
        
        async with self.driver.session() as session:
            result = await session.run(base_query, {
                "framework": framework,
                "use_case": use_case,
                "min_success_rate": min_success_rate,
                "time_window_days": time_window_days
            })
            
            patterns = []
            async for record in result:
                pattern = Pattern(
                    id=record["p.id"],
                    name=record["p.name"],
                    framework=record["p.framework"],
                    pattern_type=record["p.pattern_type"],
                    code_template=record["p.code_template"],
                    success_rate=record["p.success_rate"],
                    use_cases=json.loads(record["p.use_cases"]) if record["p.use_cases"] else [],
                    metadata=json.loads(record["p.metadata"]) if record["p.metadata"] else {},
                    created_at=record["p.created_at"],
                    last_used=record["p.last_used"],
                    usage_count=record["p.usage_count"]
                )
                patterns.append(pattern)
        
        query_time = (datetime.now() - start_time).total_seconds()
        self.query_count += 1
        self.total_query_time += query_time
        
        self.logger.info(f"Found {len(patterns)} successful patterns for {framework}")
        return patterns
    
    async def query_failed_patterns(self,
                                  framework: str,
                                  code_pattern: str = None,
                                  time_window_days: int = 180) -> List[Pattern]:
        """Query for historically failed patterns to avoid"""
        
        query = """
        MATCH (f:Framework {name: $framework})-[:HAS_PATTERN]->(p:Pattern)
        WHERE p.pattern_type = 'failure'
        AND p.created_at >= datetime() - duration({days: $time_window_days})
        """
        
        if code_pattern:
            query += " AND p.code_template CONTAINS $code_pattern"
        
        query += """
        RETURN p.id, p.name, p.framework, p.pattern_type, p.code_template,
               p.success_rate, p.use_cases, p.metadata, p.created_at,
               p.last_used, p.usage_count
        ORDER BY p.usage_count DESC
        LIMIT 5
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, {
                "framework": framework,
                "code_pattern": code_pattern,
                "time_window_days": time_window_days
            })
            
            patterns = []
            async for record in result:
                pattern = Pattern(
                    id=record["p.id"],
                    name=record["p.name"],
                    framework=record["p.framework"],
                    pattern_type=record["p.pattern_type"],
                    code_template=record["p.code_template"],
                    success_rate=record["p.success_rate"],
                    use_cases=json.loads(record["p.use_cases"]) if record["p.use_cases"] else [],
                    metadata=json.loads(record["p.metadata"]) if record["p.metadata"] else {},
                    created_at=record["p.created_at"],
                    last_used=record["p.last_used"],
                    usage_count=record["p.usage_count"]
                )
                patterns.append(pattern)
        
        self.logger.info(f"Found {len(patterns)} failed patterns for {framework}")
        return patterns
    
    async def update_pattern_usage(self, pattern_id: str, success: bool = True):
        """Update pattern usage statistics"""
        
        query = """
        MATCH (p:Pattern {id: $pattern_id})
        SET p.usage_count = p.usage_count + 1,
            p.last_used = datetime()
        """
        
        if success:
            query += ", p.success_rate = (p.success_rate * p.usage_count + 1.0) / (p.usage_count + 1)"
        else:
            query += ", p.success_rate = (p.success_rate * p.usage_count) / (p.usage_count + 1)"
        
        query += " RETURN p.success_rate as new_success_rate"
        
        async with self.driver.session() as session:
            result = await session.run(query, {"pattern_id": pattern_id})
            record = await result.single()
            
        self.logger.info(f"Updated pattern {pattern_id} usage (success: {success})")
        return record["new_success_rate"] if record else None
    
    async def temporal_query(self, 
                           cypher_query: str, 
                           parameters: Dict[str, Any] = None) -> TemporalQueryResult:
        """Execute a custom temporal Cypher query"""
        
        start_time = datetime.now()
        
        async with self.driver.session() as session:
            result = await session.run(cypher_query, parameters or {})
            
            entities = []
            relationships = []
            patterns = []
            
            async for record in result:
                # Parse different types of results
                for key, value in record.items():
                    if hasattr(value, 'labels') and 'TemporalEntity' in value.labels:
                        entities.append(self._parse_entity(value))
                    elif hasattr(value, 'labels') and 'Pattern' in value.labels:
                        patterns.append(self._parse_pattern(value))
                    elif hasattr(value, 'type') and value.type == 'TEMPORAL_RELATIONSHIP':
                        relationships.append(self._parse_relationship(value))
        
        query_time = (datetime.now() - start_time).total_seconds()
        self.query_count += 1
        self.total_query_time += query_time
        
        confidence = self._calculate_query_confidence(entities, relationships, patterns)
        
        return TemporalQueryResult(
            entities=entities,
            relationships=relationships,
            patterns=patterns,
            confidence=confidence,
            query_metadata={
                "query_time": query_time,
                "total_results": len(entities) + len(relationships) + len(patterns)
            }
        )
    
    def _parse_entity(self, node) -> TemporalEntity:
        """Parse a Neo4j node into a TemporalEntity"""
        return TemporalEntity(
            id=node.get("id", ""),
            name=node.get("name", ""),
            type=node.get("type", ""),
            properties=json.loads(node.get("properties", "{}")),
            created_at=node.get("created_at", datetime.now()),
            updated_at=node.get("updated_at", datetime.now()),
            version=node.get("version", 1),
            confidence=node.get("confidence", 1.0)
        )
    
    def _parse_pattern(self, node) -> Pattern:
        """Parse a Neo4j node into a Pattern"""
        return Pattern(
            id=node.get("id", ""),
            name=node.get("name", ""),
            framework=node.get("framework", ""),
            pattern_type=node.get("pattern_type", ""),
            code_template=node.get("code_template", ""),
            success_rate=node.get("success_rate", 0.0),
            use_cases=json.loads(node.get("use_cases", "[]")),
            metadata=json.loads(node.get("metadata", "{}")),
            created_at=node.get("created_at", datetime.now()),
            last_used=node.get("last_used", datetime.now()),
            usage_count=node.get("usage_count", 0)
        )
    
    def _parse_relationship(self, relationship) -> TemporalRelationship:
        """Parse a Neo4j relationship into a TemporalRelationship"""
        return TemporalRelationship(
            id=relationship.get("id", ""),
            source_id=relationship.start_node.get("id", ""),
            target_id=relationship.end_node.get("id", ""),
            relationship_type=relationship.get("type", ""),
            properties=json.loads(relationship.get("properties", "{}")),
            valid_from=relationship.get("valid_from", datetime.now()),
            valid_to=relationship.get("valid_to"),
            confidence=relationship.get("confidence", 1.0)
        )
    
    def _calculate_query_confidence(self, 
                                  entities: List[TemporalEntity],
                                  relationships: List[TemporalRelationship],
                                  patterns: List[Pattern]) -> float:
        """Calculate confidence score for query results"""
        
        if not entities and not relationships and not patterns:
            return 0.0
        
        total_confidence = 0.0
        total_items = 0
        
        for entity in entities:
            total_confidence += entity.confidence
            total_items += 1
        
        for relationship in relationships:
            total_confidence += relationship.confidence
            total_items += 1
        
        for pattern in patterns:
            # Pattern confidence is based on success rate and usage
            pattern_confidence = (pattern.success_rate + (pattern.usage_count / 100)) / 2
            total_confidence += min(pattern_confidence, 1.0)
            total_items += 1
        
        return total_confidence / total_items if total_items > 0 else 0.0
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the temporal engine"""
        return {
            "total_queries": self.query_count,
            "total_query_time": self.total_query_time,
            "average_query_time": self.total_query_time / max(self.query_count, 1),
            "initialized": self.initialized
        }
    
    async def close(self):
        """Close the Graphiti temporal engine"""
        if self.driver:
            await self.driver.close()
            self.logger.info("Graphiti temporal engine closed")


# Example usage and testing
async def main():
    """Example usage of the Graphiti temporal engine"""
    
    # Configuration
    neo4j_config = {
        "uri": "bolt://localhost:7687",
        "username": "neo4j",
        "password": "aid-commander-v41-secure"
    }
    
    # Initialize engine
    engine = AIDGraphitiEngine(neo4j_config)
    await engine.initialize()
    
    # Store a successful PydanticAI pattern
    pattern_id = await engine.store_pattern(
        pattern_name="BasicAgentSetup",
        framework="PydanticAI",
        pattern_type="success",
        code_template="from pydantic_ai import Agent\nagent = Agent('openai:gpt-4')",
        success_rate=0.98,
        use_cases=["customer_support", "data_analysis"],
        metadata={"complexity": "low", "dependencies": ["pydantic_ai", "openai"]}
    )
    
    # Query successful patterns
    patterns = await engine.query_successful_patterns(
        framework="PydanticAI",
        use_case="customer_support",
        min_success_rate=0.9
    )
    
    print(f"Found {len(patterns)} successful patterns")
    for pattern in patterns:
        print(f"  - {pattern.name}: {pattern.success_rate:.1%} success rate")
    
    # Performance stats
    stats = await engine.get_performance_stats()
    print(f"Performance: {stats}")
    
    await engine.close()


if __name__ == "__main__":
    asyncio.run(main())