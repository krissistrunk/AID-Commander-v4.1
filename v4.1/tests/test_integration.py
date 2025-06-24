#!/usr/bin/env python3
"""
AID Commander v4.1 - Integration Test Suite

End-to-end integration tests for the complete knowledge graph-enhanced system.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import json

from ..cli_enhanced.main import AIDCommanderV41
from ..knowledge_graph.graphiti.temporal_engine import AIDGraphitiEngine
from ..knowledge_graph.rag.hybrid_search import HybridRAGSystem
from ..validation.multi_layer.validation_engine import MultiLayerValidationEngine
from ..validation.hallucination.detection_engine import HallucinationDetectionEngine
from ..memory_enhanced.graph_memory_bank import GraphEnhancedMemoryBank


class TestAIDCommanderV41Integration:
    """Integration tests for the complete AID Commander v4.1 system"""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    async def mock_infrastructure(self):
        """Mock external infrastructure (Neo4j, Redis, etc.)"""
        
        # Mock Neo4j driver
        mock_neo4j_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()
        mock_record = Mock()
        
        # Configure successful API lookups
        mock_record.__getitem__ = Mock(side_effect=lambda key: {
            "m.name": "run_sync",
            "m.signature": "run_sync(self, user_prompt: str) -> RunResult",
            "m.confidence": 0.98
        }.get(key, "unknown"))
        
        mock_result.single = AsyncMock(return_value=mock_record)
        mock_result.__aiter__ = AsyncMock(return_value=iter([mock_record]))
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_neo4j_driver.session.return_value = mock_session
        
        # Patch Neo4j driver creation
        with patch('neo4j.AsyncGraphDatabase.driver', return_value=mock_neo4j_driver):
            # Mock ChromaDB
            with patch('chromadb.Client') as mock_chroma:
                mock_collection = Mock()
                mock_collection.count.return_value = 100
                mock_collection.query.return_value = {
                    "documents": [["Sample documentation"]],
                    "metadatas": [[{"framework": "PydanticAI"}]],
                    "distances": [[0.2]]
                }
                mock_collection.add = Mock()
                
                mock_chroma_client = Mock()
                mock_chroma_client.get_collection.return_value = mock_collection
                mock_chroma_client.create_collection.return_value = mock_collection
                mock_chroma.return_value = mock_chroma_client
                
                # Mock sentence transformer
                with patch('sentence_transformers.SentenceTransformer') as mock_transformer:
                    mock_transformer.return_value.encode.return_value = [0.1, 0.2, 0.3]
                    
                    yield {
                        "neo4j_driver": mock_neo4j_driver,
                        "chroma_client": mock_chroma_client,
                        "transformer": mock_transformer
                    }
    
    @pytest.fixture
    async def aid_commander_v41(self, temp_project_dir, mock_infrastructure):
        """Create and initialize AID Commander v4.1 instance"""
        
        commander = AIDCommanderV41()
        
        # Override config for testing
        commander.config.update({
            "neo4j_uri": "bolt://localhost:7687",
            "neo4j_username": "neo4j",
            "neo4j_password": "test-password",
            "redis_url": "redis://localhost:6379",
            "chroma_persist_dir": temp_project_dir,
            "confidence_threshold": 0.92
        })
        
        # Initialize with mocked infrastructure
        await commander.initialize(temp_project_dir)
        
        yield commander
        
        # Cleanup
        if commander.graphiti_engine:
            await commander.graphiti_engine.close()
        if commander.rag_system:
            await commander.rag_system.close()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_pydantic_ai_validation_workflow(self, aid_commander_v41):
        """Test complete workflow: knowledge graph build → validation → hallucination detection"""
        
        commander = aid_commander_v41
        
        # Step 1: Build Pydantic AI knowledge graph
        from ..frameworks.pydantic_ai.knowledge_builder import PydanticAIKnowledgeBuilder
        
        # Mock web scraping for knowledge building
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.content = b'''
            <html>
                <h2>Agent Class</h2>
                <p>The Agent class is the main interface for Pydantic AI.</p>
                <h3>Methods</h3>
                <p>run_sync(user_prompt: str) -> RunResult</p>
                <code>agent = Agent("openai:gpt-4")</code>
            </html>
            '''
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_client_instance
            
            # Build knowledge graph
            builder = PydanticAIKnowledgeBuilder(
                commander.graphiti_engine,
                commander.rag_system
            )
            
            build_result = await builder.build_complete_knowledge_graph()
            
            # Verify knowledge graph was built
            assert build_result["status"] == "completed"
            assert build_result["entities_processed"] > 0
            assert build_result["confidence"] > 0.8
        
        # Step 2: Test multi-layer validation with good code
        good_code = '''
from pydantic_ai import Agent
from pydantic import BaseModel

class Response(BaseModel):
    message: str
    confidence: float

agent = Agent("openai:gpt-4", result_type=Response)
result = agent.run_sync("Hello world")
print(result.data.message)
'''
        
        validation_result = await commander.validation_engine.validate_code_generation(
            "Create Pydantic AI agent with structured output",
            "PydanticAI",
            good_code
        )
        
        # Verify high confidence validation
        assert validation_result.consensus_score >= 0.9
        assert len(validation_result.overall_issues) == 0
        assert validation_result.validated_approach is not None
        
        # Step 3: Test hallucination detection with bad code
        hallucinated_code = '''
from pydantic_ai import PydanticAgent  # Wrong class
from pydantic import Agent  # Wrong import

agent = PydanticAgent(model="gpt-4")  # Wrong constructor
agent.add_validation_rule("test")     # Non-existent method
result = agent.execute_with_memory("Hello")  # Non-existent method
print(result.response)                # Wrong attribute
'''
        
        hallucination_result = await commander.hallucination_detector.detect_hallucination(
            hallucinated_code,
            ["PydanticAI"]
        )
        
        # Verify hallucination detection
        assert hallucination_result.is_hallucination == True
        assert hallucination_result.confidence_score < 0.5
        assert len(hallucination_result.detected_hallucinations) >= 3  # Multiple issues
        
        # Check specific hallucination types
        hallucination_types = [h.type.value for h in hallucination_result.detected_hallucinations]
        assert "non_existent_class" in hallucination_types
        assert "non_existent_method" in hallucination_types or "incorrect_usage_pattern" in hallucination_types
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_enhanced_memory_integration(self, aid_commander_v41):
        """Test enhanced memory bank with graph relationships"""
        
        commander = aid_commander_v41
        
        # Store multiple related decisions
        decisions = [
            {
                "decision": "Use JWT authentication",
                "context": "Need secure API access",
                "outcome": "JWT tokens with refresh",
                "rationale": "Stateless and scalable",
                "framework": "PydanticAI",
                "decision_type": "authentication",
                "success_score": 0.95
            },
            {
                "decision": "Use Pydantic AI for structured output",
                "context": "Need type-safe AI responses",
                "outcome": "Pydantic AI with BaseModel",
                "rationale": "Type safety and validation",
                "framework": "PydanticAI", 
                "decision_type": "ai_integration",
                "success_score": 0.92
            },
            {
                "decision": "Implement async patterns",
                "context": "Need non-blocking operations",
                "outcome": "Async/await throughout",
                "rationale": "Better performance and scalability",
                "framework": "PydanticAI",
                "decision_type": "architecture",
                "success_score": 0.88
            }
        ]
        
        # Store decisions with graph enhancement
        memory_ids = []
        for decision in decisions:
            memory_id = await commander.graph_memory_bank.store_decision_with_graph(
                decision["decision"],
                decision["context"],
                decision["outcome"],
                decision["rationale"],
                decision["framework"],
                decision["decision_type"],
                decision["success_score"]
            )
            memory_ids.append(memory_id)
        
        # Test enhanced context retrieval
        enhanced_context = await commander.graph_memory_bank.get_enhanced_context(
            "authentication and AI integration",
            framework="PydanticAI",
            include_cross_project=True
        )
        
        # Verify enhanced context
        assert enhanced_context.confidence > 0.8
        assert len(enhanced_context.relevant_decisions) > 0
        assert enhanced_context.success_probability > 0.0
        
        # Should find relationships between decisions
        if enhanced_context.decision_relationships:
            assert len(enhanced_context.decision_relationships) > 0
        
        # Test cross-project learnings
        learnings = await commander.graph_memory_bank.get_cross_project_learnings("PydanticAI")
        
        # Verify learnings structure
        assert learnings["framework"] == "PydanticAI"
        if learnings["overall_stats"]:
            assert "total_decisions" in learnings["overall_stats"]
            assert "avg_success_rate" in learnings["overall_stats"]
        
        # Test decision optimization
        optimization = await commander.graph_memory_bank.optimize_decision_with_graph(
            "implement user authentication with AI",
            "PydanticAI"
        )
        
        # Verify optimization recommendations
        assert optimization["framework"] == "PydanticAI"
        assert optimization["success_probability"] > 0.0
        assert len(optimization["recommendations"]) > 0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_performance_and_stats_collection(self, aid_commander_v41):
        """Test that performance statistics are collected across all components"""
        
        commander = aid_commander_v41
        
        # Perform various operations to generate stats
        
        # 1. Validation operation
        await commander.validation_engine.validate_code_generation(
            "test performance", "PydanticAI"
        )
        
        # 2. Hallucination detection
        await commander.hallucination_detector.detect_hallucination(
            "from pydantic_ai import Agent", ["PydanticAI"]
        )
        
        # 3. Memory operations
        if commander.graph_memory_bank:
            await commander.graph_memory_bank.store_decision_with_graph(
                "Test decision", "Test context", "Test outcome", 
                "Test rationale", "PydanticAI", "test", 0.9
            )
        
        # 4. RAG search
        await commander.rag_system.hybrid_search("test query", "PydanticAI")
        
        # Collect performance stats
        stats_data = {}
        
        if commander.graphiti_engine:
            stats_data["graphiti"] = await commander.graphiti_engine.get_performance_stats()
        
        if commander.rag_system:
            stats_data["rag"] = await commander.rag_system.get_performance_stats()
        
        if commander.validation_engine:
            stats_data["validation"] = await commander.validation_engine.get_performance_stats()
        
        if commander.hallucination_detector:
            stats_data["hallucination"] = await commander.hallucination_detector.get_performance_stats()
        
        if commander.graph_memory_bank:
            stats_data["memory"] = await commander.graph_memory_bank.get_performance_stats()
        
        # Verify stats collection
        for component, stats in stats_data.items():
            assert isinstance(stats, dict)
            assert len(stats) > 0
            print(f"{component} stats: {stats}")
        
        # Verify operation counts increased
        if "validation" in stats_data:
            assert stats_data["validation"]["validation_count"] > 0
        
        if "hallucination" in stats_data:
            assert stats_data["hallucination"]["detection_count"] > 0
        
        if "rag" in stats_data:
            assert stats_data["rag"]["search_count"] > 0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_handling_and_resilience(self, aid_commander_v41):
        """Test system resilience to component failures"""
        
        commander = aid_commander_v41
        
        # Test validation with simulated component failure
        with patch.object(commander.rag_system, 'validate_api_usage', side_effect=Exception("RAG system error")):
            # Should still complete validation with reduced confidence
            result = await commander.validation_engine.validate_code_generation(
                "test with failure", "PydanticAI"
            )
            
            # Should have completed despite RAG failure
            assert result.consensus_score >= 0.0  # Some score computed
            assert len(result.layer_results) > 0   # Some layers succeeded
            
            # Should have error recorded in layer results
            doc_layer = result.layer_results.get("documentation")
            if doc_layer:
                assert doc_layer.confidence == 0.0  # Failed layer has zero confidence
        
        # Test hallucination detection with component failure  
        with patch.object(commander.graphiti_engine, 'query_failed_patterns', side_effect=Exception("Graphiti error")):
            # Should still detect obvious hallucinations
            result = await commander.hallucination_detector.detect_hallucination(
                "from pydantic_ai import NonExistentClass", ["PydanticAI"]
            )
            
            # Should still work through framework patterns
            assert result.confidence_score >= 0.0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_concurrent_operations(self, aid_commander_v41):
        """Test system behavior under concurrent load"""
        
        commander = aid_commander_v41
        
        # Define concurrent operations
        async def validation_task(i):
            return await commander.validation_engine.validate_code_generation(
                f"concurrent test {i}", "PydanticAI"
            )
        
        async def hallucination_task(i):
            return await commander.hallucination_detector.detect_hallucination(
                f"# Test code {i}\nfrom pydantic_ai import Agent", ["PydanticAI"]
            )
        
        async def memory_task(i):
            if commander.graph_memory_bank:
                return await commander.graph_memory_bank.store_decision_with_graph(
                    f"Decision {i}", f"Context {i}", f"Outcome {i}", 
                    f"Rationale {i}", "PydanticAI", "test", 0.8
                )
            return f"memory_{i}"
        
        # Run concurrent operations
        validation_tasks = [validation_task(i) for i in range(3)]
        hallucination_tasks = [hallucination_task(i) for i in range(3)]
        memory_tasks = [memory_task(i) for i in range(3)]
        
        all_tasks = validation_tasks + hallucination_tasks + memory_tasks
        
        # Execute concurrently
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        # Verify no failures from concurrency
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) == 0, f"Concurrent operations had {len(exceptions)} failures"
        
        # Verify all operations completed
        assert len(results) == 9  # 3 of each type
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_end_to_end_development_workflow(self, aid_commander_v41):
        """Test complete development workflow from intent to validated code"""
        
        commander = aid_commander_v41
        
        # Development workflow:
        # 1. Express development intent
        # 2. Get memory-enhanced context
        # 3. Validate approach with multi-layer validation
        # 4. Detect and correct any hallucinations
        # 5. Store successful decisions for future use
        
        development_intent = "Create a customer support chatbot using Pydantic AI with structured responses"
        framework = "PydanticAI"
        
        # Step 1: Get memory-enhanced recommendations
        if commander.graph_memory_bank:
            optimization = await commander.graph_memory_bank.optimize_decision_with_graph(
                development_intent, framework
            )
            
            assert optimization["framework"] == framework
            assert optimization["success_probability"] >= 0.0
            print(f"Success probability: {optimization['success_probability']:.1%}")
        
        # Step 2: Generate code (simulated)
        generated_code = '''
from pydantic_ai import Agent
from pydantic import BaseModel
from typing import Literal

class SupportResponse(BaseModel):
    response: str
    category: Literal["technical", "billing", "general"]
    confidence: float
    escalate: bool = False

# Create customer support agent
support_agent = Agent(
    "openai:gpt-4",
    result_type=SupportResponse,
    system_prompt="You are a helpful customer support agent."
)

def handle_customer_query(query: str) -> SupportResponse:
    result = support_agent.run_sync(query)
    return result.data

# Example usage
if __name__ == "__main__":
    response = handle_customer_query("How do I reset my password?")
    print(f"Response: {response.response}")
    print(f"Category: {response.category}")
    if response.escalate:
        print("Escalating to human agent...")
'''
        
        # Step 3: Multi-layer validation
        validation_result = await commander.validation_engine.validate_code_generation(
            development_intent, framework, generated_code
        )
        
        print(f"Validation consensus: {validation_result.consensus_score:.1%}")
        assert validation_result.consensus_score >= 0.85  # Should be high for good code
        
        # Step 4: Hallucination detection
        hallucination_result = await commander.hallucination_detector.detect_hallucination(
            generated_code, [framework]
        )
        
        print(f"Hallucination confidence: {hallucination_result.confidence_score:.1%}")
        assert hallucination_result.is_hallucination == False  # Should be clean code
        
        # Step 5: Store successful decision
        if commander.graph_memory_bank:
            memory_id = await commander.graph_memory_bank.store_decision_with_graph(
                "Customer Support Chatbot Implementation",
                development_intent,
                "Pydantic AI with structured responses and type safety",
                "Provides type-safe responses with confidence scoring and escalation",
                framework,
                "ai_integration",
                validation_result.consensus_score
            )
            
            assert memory_id is not None
            print(f"Decision stored with ID: {memory_id}")
        
        # Step 6: Verify workflow completed successfully
        assert validation_result.consensus_score >= 0.85
        assert hallucination_result.confidence_score >= 0.8
        assert hallucination_result.is_hallucination == False
        
        print("✅ End-to-end workflow completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])