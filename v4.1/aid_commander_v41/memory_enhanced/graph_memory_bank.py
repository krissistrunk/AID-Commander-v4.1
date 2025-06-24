#!/usr/bin/env python3
"""
AID Commander v4.1 - Graph-Enhanced Memory Bank System

Extends the v4.0 Memory Bank with knowledge graph integration for enhanced
context retrieval, relationship tracking, and cross-project learning.
"""

import asyncio
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from pydantic import BaseModel, Field
import structlog

# Import v4.0 memory components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "v4"))
from memory_service import MemoryBank, MemoryContext
from ..knowledge_graph.graphiti.temporal_engine import AIDGraphitiEngine
from ..knowledge_graph.neo4j.graph_client import Neo4jClient

logger = structlog.get_logger(__name__)


@dataclass
class GraphMemoryRelationship:
    """Represents a relationship between memories in the knowledge graph"""
    source_memory_id: str
    target_memory_id: str
    relationship_type: str  # 'similar_decision', 'prerequisite', 'alternative', 'conflict'
    strength: float  # 0.0 to 1.0
    metadata: Dict[str, Any]
    created_at: datetime


@dataclass
class EnhancedMemoryContext:
    """Enhanced memory context with graph relationships"""
    # Base context from v4.0
    relevant_decisions: List[str]
    patterns: List[str]
    success_factors: List[str]
    warnings: List[str]
    confidence: float
    
    # Enhanced with graph data
    related_projects: List[str] = None
    decision_relationships: List[GraphMemoryRelationship] = None
    temporal_patterns: List[str] = None
    cross_framework_insights: List[str] = None
    success_probability: float = 0.0


class GraphEnhancedMemoryBank(MemoryBank):
    """
    Enhanced memory bank with knowledge graph integration
    
    Provides:
    - Relationship tracking between decisions
    - Cross-project learning and pattern recognition
    - Temporal evolution of decision effectiveness
    - Framework-aware memory clustering
    - Enhanced context retrieval through graph traversal
    """
    
    def __init__(self, 
                 project_path: str,
                 graphiti_engine: AIDGraphitiEngine,
                 neo4j_client: Optional[Neo4jClient] = None):
        
        # Initialize base memory bank
        super().__init__(project_path)
        
        # Knowledge graph integration
        self.graphiti_engine = graphiti_engine
        self.neo4j_client = neo4j_client
        
        # Enhanced memory database schema
        self.graph_memory_db = None
        self.graph_initialized = False
        
        self.logger = logger.bind(component="GraphMemoryBank", project=project_path)
    
    async def initialize(self) -> bool:
        """Initialize enhanced memory bank with graph integration"""
        
        try:
            # Initialize base memory bank
            base_initialized = super().initialize()
            if not base_initialized:
                return False
            
            # Initialize graph-enhanced database
            await self._initialize_graph_memory_db()
            
            # Initialize knowledge graph schemas
            await self._initialize_graph_schemas()
            
            self.graph_initialized = True
            self.logger.info("Graph-enhanced memory bank initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize graph-enhanced memory bank: {e}")
            return False
    
    async def _initialize_graph_memory_db(self):
        """Initialize enhanced SQLite database with graph relationship tables"""
        
        graph_db_path = self.memory_dir / "graph_memory.db"
        self.graph_memory_db = sqlite3.connect(str(graph_db_path))
        
        # Create graph relationship table
        self.graph_memory_db.execute("""
            CREATE TABLE IF NOT EXISTS memory_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_memory_id TEXT NOT NULL,
                target_memory_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                strength REAL NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (source_memory_id) REFERENCES memories (id),
                FOREIGN KEY (target_memory_id) REFERENCES memories (id)
            )
        """)
        
        # Create cross-project memory index
        self.graph_memory_db.execute("""
            CREATE TABLE IF NOT EXISTS cross_project_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT NOT NULL,
                project_path TEXT NOT NULL,
                framework TEXT,
                decision_type TEXT,
                success_score REAL,
                created_at TIMESTAMP,
                INDEX(framework),
                INDEX(decision_type),
                INDEX(success_score)
            )
        """)
        
        # Create temporal pattern tracking
        self.graph_memory_db.execute("""
            CREATE TABLE IF NOT EXISTS temporal_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT NOT NULL,
                pattern_description TEXT,
                framework TEXT,
                success_rate REAL,
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP
            )
        """)
        
        self.graph_memory_db.commit()
    
    async def _initialize_graph_schemas(self):
        """Initialize knowledge graph schemas for memory integration"""
        
        if self.neo4j_client:
            # Create memory-specific nodes and relationships in Neo4j
            memory_schema_queries = [
                # Memory nodes
                "CREATE CONSTRAINT memory_id IF NOT EXISTS FOR (m:Memory) REQUIRE m.id IS UNIQUE",
                "CREATE CONSTRAINT project_path IF NOT EXISTS FOR (p:Project) REQUIRE p.path IS UNIQUE",
                
                # Indexes for performance
                "CREATE INDEX memory_framework IF NOT EXISTS FOR (m:Memory) ON (m.framework)",
                "CREATE INDEX memory_decision_type IF NOT EXISTS FOR (m:Memory) ON (m.decision_type)",
                "CREATE INDEX memory_created_at IF NOT EXISTS FOR (m:Memory) ON (m.created_at)",
                
                # Project relationship indexes
                "CREATE INDEX project_framework IF NOT EXISTS FOR ()-[r:USED_IN_PROJECT]-() ON (r.framework)",
            ]
            
            async with self.neo4j_client.session() as session:
                for query in memory_schema_queries:
                    try:
                        await session.run(query)
                    except Exception as e:
                        self.logger.debug(f"Schema query warning: {e}")
    
    async def store_decision_with_graph(self,
                                      decision: str,
                                      context: str,
                                      outcome: str,
                                      rationale: str,
                                      framework: Optional[str] = None,
                                      decision_type: Optional[str] = None,
                                      success_score: float = 0.5) -> str:
        """Store decision with enhanced graph relationship tracking"""
        
        # Store in base memory bank
        memory_id = await super().store_decision(decision, context, outcome, rationale)
        
        try:
            # Store in cross-project index
            self.graph_memory_db.execute("""
                INSERT INTO cross_project_memories 
                (memory_id, project_path, framework, decision_type, success_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (memory_id, self.project_path, framework, decision_type, success_score, datetime.now()))
            
            # Create temporal entity in Graphiti
            if self.graphiti_engine:
                temporal_entity_id = await self.graphiti_engine.create_temporal_entity(
                    entity_name=f"memory_{memory_id}",
                    entity_type="ProjectMemory",
                    properties={
                        "decision": decision,
                        "context": context,
                        "outcome": outcome,
                        "rationale": rationale,
                        "framework": framework,
                        "decision_type": decision_type,
                        "success_score": success_score,
                        "project_path": self.project_path
                    },
                    framework=framework
                )
            
            # Create memory node in Neo4j
            if self.neo4j_client:
                await self._create_memory_node_in_neo4j(
                    memory_id, decision, context, outcome, rationale,
                    framework, decision_type, success_score
                )
            
            # Find and create relationships with similar memories
            await self._create_memory_relationships(memory_id, decision, framework, decision_type)
            
            self.graph_memory_db.commit()
            
            self.logger.info(f"Stored decision with graph enhancement: {memory_id}")
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Failed to store decision with graph enhancement: {e}")
            return memory_id  # Return base memory ID even if graph enhancement fails
    
    async def _create_memory_node_in_neo4j(self,
                                         memory_id: str,
                                         decision: str,
                                         context: str,
                                         outcome: str,
                                         rationale: str,
                                         framework: Optional[str],
                                         decision_type: Optional[str],
                                         success_score: float):
        """Create memory node in Neo4j knowledge graph"""
        
        query = """
        MERGE (p:Project {path: $project_path})
        CREATE (m:Memory {
            id: $memory_id,
            decision: $decision,
            context: $context,
            outcome: $outcome,
            rationale: $rationale,
            framework: $framework,
            decision_type: $decision_type,
            success_score: $success_score,
            created_at: datetime(),
            project_path: $project_path
        })
        CREATE (m)-[:BELONGS_TO]->(p)
        """
        
        if framework:
            query += """
            MERGE (f:Framework {name: $framework})
            CREATE (m)-[:USES_FRAMEWORK]->(f)
            """
        
        async with self.neo4j_client.session() as session:
            await session.run(query, {
                "memory_id": memory_id,
                "decision": decision,
                "context": context,
                "outcome": outcome,
                "rationale": rationale,
                "framework": framework,
                "decision_type": decision_type,
                "success_score": success_score,
                "project_path": self.project_path
            })
    
    async def _create_memory_relationships(self,
                                         memory_id: str,
                                         decision: str,
                                         framework: Optional[str],
                                         decision_type: Optional[str]):
        """Create relationships between similar memories"""
        
        # Find similar memories in current project
        similar_memories = await self._find_similar_memories(
            decision, framework, decision_type, limit=5
        )
        
        for similar_memory in similar_memories:
            if similar_memory["memory_id"] != memory_id:
                # Calculate relationship strength
                strength = await self._calculate_relationship_strength(
                    decision, similar_memory["decision"]
                )
                
                if strength > 0.3:  # Only create significant relationships
                    relationship = GraphMemoryRelationship(
                        source_memory_id=memory_id,
                        target_memory_id=similar_memory["memory_id"],
                        relationship_type="similar_decision",
                        strength=strength,
                        metadata={
                            "framework": framework,
                            "decision_type": decision_type,
                            "similarity_score": strength
                        },
                        created_at=datetime.now()
                    )
                    
                    await self._store_memory_relationship(relationship)
    
    async def _find_similar_memories(self,
                                   decision: str,
                                   framework: Optional[str],
                                   decision_type: Optional[str],
                                   limit: int = 10) -> List[Dict[str, Any]]:
        """Find similar memories using FTS and filters"""
        
        query = """
            SELECT m.memory_id, m.decision, m.framework, m.decision_type, m.success_score
            FROM cross_project_memories m
            WHERE 1=1
        """
        params = []
        
        if framework:
            query += " AND m.framework = ?"
            params.append(framework)
        
        if decision_type:
            query += " AND m.decision_type = ?"
            params.append(decision_type)
        
        query += " ORDER BY m.success_score DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.graph_memory_db.execute(query, params)
        return [
            {
                "memory_id": row[0],
                "decision": row[1],
                "framework": row[2],
                "decision_type": row[3],
                "success_score": row[4]
            }
            for row in cursor.fetchall()
        ]
    
    async def _calculate_relationship_strength(self, 
                                             decision1: str, 
                                             decision2: str) -> float:
        """Calculate relationship strength between two decisions"""
        
        # Simple word-based similarity
        words1 = set(decision1.lower().split())
        words2 = set(decision2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    async def _store_memory_relationship(self, relationship: GraphMemoryRelationship):
        """Store memory relationship in database"""
        
        self.graph_memory_db.execute("""
            INSERT INTO memory_relationships 
            (source_memory_id, target_memory_id, relationship_type, strength, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            relationship.source_memory_id,
            relationship.target_memory_id,
            relationship.relationship_type,
            relationship.strength,
            json.dumps(relationship.metadata),
            relationship.created_at,
            relationship.created_at
        ))
    
    async def get_enhanced_context(self, 
                                 query: str,
                                 framework: Optional[str] = None,
                                 include_cross_project: bool = True) -> EnhancedMemoryContext:
        """Get enhanced memory context with graph relationships"""
        
        # Get base context from v4.0
        base_context = await super().get_relevant_context(query)
        
        # Get graph-enhanced context
        related_projects = []
        decision_relationships = []
        temporal_patterns = []
        cross_framework_insights = []
        
        try:
            # Find related decisions through graph relationships
            if include_cross_project:
                related_projects = await self._get_related_projects(query, framework)
                cross_framework_insights = await self._get_cross_framework_insights(query)
            
            # Get decision relationships
            decision_relationships = await self._get_decision_relationships(query, framework)
            
            # Get temporal patterns from Graphiti
            if self.graphiti_engine:
                temporal_patterns = await self._get_temporal_patterns(query, framework)
            
            # Calculate enhanced success probability
            success_probability = await self._calculate_success_probability(
                query, framework, decision_relationships
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get enhanced context: {e}")
        
        return EnhancedMemoryContext(
            relevant_decisions=base_context.relevant_decisions,
            patterns=base_context.patterns,
            success_factors=base_context.success_factors,
            warnings=base_context.warnings,
            confidence=base_context.confidence,
            related_projects=related_projects,
            decision_relationships=decision_relationships,
            temporal_patterns=temporal_patterns,
            cross_framework_insights=cross_framework_insights,
            success_probability=success_probability
        )
    
    async def _get_related_projects(self, 
                                  query: str, 
                                  framework: Optional[str]) -> List[str]:
        """Get related projects that dealt with similar issues"""
        
        query_sql = """
            SELECT DISTINCT project_path, COUNT(*) as relevance_count
            FROM cross_project_memories m
            WHERE m.project_path != ?
        """
        params = [self.project_path]
        
        if framework:
            query_sql += " AND m.framework = ?"
            params.append(framework)
        
        query_sql += """
            GROUP BY project_path
            ORDER BY relevance_count DESC
            LIMIT 5
        """
        
        cursor = self.graph_memory_db.execute(query_sql, params)
        return [row[0] for row in cursor.fetchall()]
    
    async def _get_decision_relationships(self, 
                                        query: str,
                                        framework: Optional[str]) -> List[GraphMemoryRelationship]:
        """Get decision relationships relevant to the query"""
        
        # Find memories relevant to the query first
        relevant_memories = await self._find_similar_memories(query, framework, None, limit=10)
        
        if not relevant_memories:
            return []
        
        memory_ids = [mem["memory_id"] for mem in relevant_memories]
        placeholders = ",".join("?" * len(memory_ids))
        
        query_sql = f"""
            SELECT source_memory_id, target_memory_id, relationship_type, strength, metadata, created_at
            FROM memory_relationships
            WHERE source_memory_id IN ({placeholders}) OR target_memory_id IN ({placeholders})
            ORDER BY strength DESC
            LIMIT 10
        """
        
        cursor = self.graph_memory_db.execute(query_sql, memory_ids + memory_ids)
        
        relationships = []
        for row in cursor.fetchall():
            relationships.append(GraphMemoryRelationship(
                source_memory_id=row[0],
                target_memory_id=row[1],
                relationship_type=row[2],
                strength=row[3],
                metadata=json.loads(row[4]) if row[4] else {},
                created_at=datetime.fromisoformat(row[5])
            ))
        
        return relationships
    
    async def _get_temporal_patterns(self, 
                                   query: str, 
                                   framework: Optional[str]) -> List[str]:
        """Get temporal patterns from Graphiti"""
        
        if not self.graphiti_engine or not framework:
            return []
        
        try:
            patterns = await self.graphiti_engine.query_successful_patterns(
                framework=framework,
                min_success_rate=0.7,
                time_window_days=180
            )
            
            # Convert patterns to string descriptions
            pattern_descriptions = []
            for pattern in patterns[:5]:  # Top 5 patterns
                pattern_descriptions.append(
                    f"{pattern.name}: {pattern.success_rate:.1%} success rate "
                    f"(used {pattern.usage_count} times)"
                )
            
            return pattern_descriptions
            
        except Exception as e:
            self.logger.error(f"Failed to get temporal patterns: {e}")
            return []
    
    async def _get_cross_framework_insights(self, query: str) -> List[str]:
        """Get insights from similar decisions across different frameworks"""
        
        query_sql = """
            SELECT framework, decision_type, AVG(success_score) as avg_success, COUNT(*) as count
            FROM cross_project_memories
            WHERE framework IS NOT NULL
            GROUP BY framework, decision_type
            HAVING count >= 2
            ORDER BY avg_success DESC
            LIMIT 5
        """
        
        cursor = self.graph_memory_db.execute(query_sql)
        
        insights = []
        for row in cursor.fetchall():
            framework, decision_type, avg_success, count = row
            insights.append(
                f"{framework} {decision_type}: {avg_success:.1%} avg success "
                f"({count} decisions)"
            )
        
        return insights
    
    async def _calculate_success_probability(self,
                                           query: str,
                                           framework: Optional[str],
                                           relationships: List[GraphMemoryRelationship]) -> float:
        """Calculate success probability based on historical data"""
        
        if not framework:
            return 0.5  # Neutral when no framework context
        
        # Get historical success rates for similar decisions
        query_sql = """
            SELECT AVG(success_score) as avg_success, COUNT(*) as count
            FROM cross_project_memories
            WHERE framework = ?
        """
        
        cursor = self.graph_memory_db.execute(query_sql, [framework])
        row = cursor.fetchone()
        
        if row and row[1] > 0:  # Has historical data
            base_probability = row[0]
            
            # Adjust based on relationship strength
            if relationships:
                relationship_boost = sum(rel.strength for rel in relationships) / len(relationships)
                return min(0.95, base_probability + (relationship_boost * 0.2))
            
            return base_probability
        
        return 0.5  # Neutral default
    
    async def get_cross_project_learnings(self, 
                                        framework: str,
                                        decision_type: Optional[str] = None) -> Dict[str, Any]:
        """Get learnings from across all projects using the same framework"""
        
        query_sql = """
            SELECT 
                COUNT(*) as total_decisions,
                AVG(success_score) as avg_success,
                COUNT(DISTINCT project_path) as project_count,
                decision_type,
                MAX(created_at) as latest_decision
            FROM cross_project_memories
            WHERE framework = ?
        """
        params = [framework]
        
        if decision_type:
            query_sql += " AND decision_type = ?"
            params.append(decision_type)
        
        query_sql += " GROUP BY decision_type ORDER BY avg_success DESC"
        
        cursor = self.graph_memory_db.execute(query_sql, params)
        
        learnings = {
            "framework": framework,
            "decision_types": [],
            "overall_stats": {}
        }
        
        total_decisions = 0
        total_success = 0.0
        
        for row in cursor.fetchall():
            decision_data = {
                "decision_type": row[3],
                "total_decisions": row[0],
                "avg_success": row[1],
                "project_count": row[2],
                "latest_decision": row[4]
            }
            learnings["decision_types"].append(decision_data)
            
            total_decisions += row[0]
            total_success += row[1] * row[0]
        
        if total_decisions > 0:
            learnings["overall_stats"] = {
                "total_decisions": total_decisions,
                "avg_success_rate": total_success / total_decisions,
                "frameworks_analyzed": 1
            }
        
        return learnings
    
    async def optimize_decision_with_graph(self, 
                                         decision_intent: str,
                                         framework: str) -> Dict[str, Any]:
        """Optimize a decision using graph-enhanced memory insights"""
        
        # Get enhanced context
        context = await self.get_enhanced_context(
            decision_intent, framework, include_cross_project=True
        )
        
        # Get cross-project learnings
        learnings = await self.get_cross_project_learnings(framework)
        
        # Generate optimization recommendations
        recommendations = []
        
        # Based on success probability
        if context.success_probability > 0.8:
            recommendations.append("✅ High success probability based on historical data")
        elif context.success_probability < 0.4:
            recommendations.append("⚠️  Low success probability - consider alternative approaches")
        
        # Based on temporal patterns
        if context.temporal_patterns:
            recommendations.append(f"📈 Consider proven patterns: {context.temporal_patterns[0]}")
        
        # Based on cross-framework insights
        if context.cross_framework_insights:
            recommendations.append(f"🔄 Cross-framework insight: {context.cross_framework_insights[0]}")
        
        # Based on related projects
        if context.related_projects:
            recommendations.append(f"🔗 Related project experience available from {len(context.related_projects)} projects")
        
        return {
            "decision_intent": decision_intent,
            "framework": framework,
            "success_probability": context.success_probability,
            "confidence": context.confidence,
            "recommendations": recommendations,
            "related_projects": context.related_projects[:3],  # Top 3
            "temporal_patterns": context.temporal_patterns[:3],  # Top 3
            "cross_framework_insights": context.cross_framework_insights[:3],  # Top 3
            "learnings_summary": learnings["overall_stats"]
        }
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the graph-enhanced memory bank"""
        
        base_stats = super().get_performance_stats()
        
        # Add graph-specific stats
        cursor = self.graph_memory_db.execute("SELECT COUNT(*) FROM memory_relationships")
        relationship_count = cursor.fetchone()[0]
        
        cursor = self.graph_memory_db.execute("SELECT COUNT(DISTINCT project_path) FROM cross_project_memories")
        project_count = cursor.fetchone()[0]
        
        cursor = self.graph_memory_db.execute("SELECT COUNT(DISTINCT framework) FROM cross_project_memories WHERE framework IS NOT NULL")
        framework_count = cursor.fetchone()[0]
        
        base_stats.update({
            "graph_initialized": self.graph_initialized,
            "memory_relationships": relationship_count,
            "cross_project_memories": project_count,
            "frameworks_tracked": framework_count
        })
        
        return base_stats
    
    def close(self):
        """Close enhanced memory bank connections"""
        super().close()
        
        if self.graph_memory_db:
            self.graph_memory_db.close()
            self.logger.info("Graph-enhanced memory bank closed")


# Example usage
async def main():
    """Example usage of graph-enhanced memory bank"""
    
    # This would be properly configured in production
    print("Graph-enhanced memory bank example")
    print("Configure Graphiti and Neo4j clients, then use enhanced memory features...")


if __name__ == "__main__":
    asyncio.run(main())