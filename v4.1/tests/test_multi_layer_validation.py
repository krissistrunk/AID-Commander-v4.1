#!/usr/bin/env python3
"""
AID Commander v4.1 - Multi-Layer Validation Test Suite

Comprehensive tests for the 6-layer validation system with 92%+ consensus scoring.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from pathlib import Path

from ..validation.multi_layer.validation_engine import (
    MultiLayerValidationEngine,
    ValidationLayer,
    ValidationSeverity,
    ValidationIssue,
    LayerValidationResult,
    ValidationResult,
    CodeAnalysis,
    StructuralValidator,
    TemporalValidator,
    DocumentationValidator,
    MemoryValidator,
    TypeSafetyValidator,
    ConsensusValidator
)
from ..knowledge_graph.graphiti.temporal_engine import AIDGraphitiEngine, Pattern
from ..knowledge_graph.rag.hybrid_search import HybridRAGSystem, ValidationResult as RAGValidationResult
from ...v4.memory_service import MemoryBank, MemoryContext


class TestMultiLayerValidationEngine:
    """Test suite for the multi-layer validation engine"""
    
    @pytest.fixture
    async def mock_graphiti_engine(self):
        """Create mock Graphiti engine"""
        engine = Mock(spec=AIDGraphitiEngine)
        engine.query_successful_patterns = AsyncMock(return_value=[
            Pattern(
                id="pattern1",
                name="BasicAgentSetup",
                framework="PydanticAI",
                pattern_type="success",
                code_template="agent = Agent('openai:gpt-4')",
                success_rate=0.98,
                use_cases=["customer_support"],
                metadata={},
                created_at=datetime.now(),
                last_used=datetime.now(),
                usage_count=50
            )
        ])
        engine.query_failed_patterns = AsyncMock(return_value=[])
        engine.neo4j_driver = Mock()
        return engine
    
    @pytest.fixture
    async def mock_rag_system(self):
        """Create mock RAG system"""
        system = Mock(spec=HybridRAGSystem)
        mock_validation = RAGValidationResult(
            is_valid=True,
            confidence=0.95,
            api_structure=[{
                "class_name": "Agent",
                "method_name": "run_sync",
                "signature": "run_sync(self, user_prompt: str) -> RunResult",
                "confidence": 0.98
            }],
            documentation_examples=[],
            issues=[],
            suggestions=[]
        )
        system.validate_api_usage = AsyncMock(return_value=mock_validation)
        return system
    
    @pytest.fixture
    async def mock_memory_bank(self):
        """Create mock memory bank"""
        bank = Mock(spec=MemoryBank)
        mock_context = MemoryContext(
            relevant_decisions=["Use JWT authentication", "Prefer async patterns"],
            patterns=["Agent initialization pattern", "Error handling pattern"],
            success_factors=["Type safety", "Documentation"],
            warnings=["Avoid synchronous calls in async context"],
            confidence=0.85
        )
        bank.get_relevant_context = AsyncMock(return_value=mock_context)
        return bank
    
    @pytest.fixture
    async def validation_engine(self, mock_graphiti_engine, mock_rag_system, mock_memory_bank):
        """Create multi-layer validation engine"""
        return MultiLayerValidationEngine(
            mock_graphiti_engine,
            mock_rag_system,
            mock_memory_bank,
            confidence_threshold=0.92
        )
    
    @pytest.mark.asyncio
    async def test_basic_code_validation_high_confidence(self, validation_engine):
        """Test validation of high-quality code achieves high confidence"""
        
        code_intent = "Create a Pydantic AI agent for customer support"
        framework = "PydanticAI"
        generated_code = '''
from pydantic_ai import Agent
from pydantic import BaseModel

class SupportResponse(BaseModel):
    response: str
    confidence: float

agent = Agent("openai:gpt-4", result_type=SupportResponse)
result = agent.run_sync("How can I help you?")
print(result.data.response)
'''
        
        # Run validation
        result = await validation_engine.validate_code_generation(
            code_intent, framework, generated_code
        )
        
        # Assertions
        assert result.consensus_score >= 0.9, f"Expected high consensus, got {result.consensus_score:.1%}"
        assert ValidationLayer.STRUCTURAL.value in result.layer_results
        assert ValidationLayer.TEMPORAL.value in result.layer_results
        assert ValidationLayer.DOCUMENTATION.value in result.layer_results
        assert ValidationLayer.MEMORY.value in result.layer_results
        assert ValidationLayer.TYPE_SAFETY.value in result.layer_results
        assert ValidationLayer.CONSENSUS.value in result.layer_results
        
        # Check that most layers have high confidence
        high_confidence_layers = [
            layer for layer, result_data in result.layer_results.items()
            if result_data.confidence >= 0.8
        ]
        assert len(high_confidence_layers) >= 4, "Expected at least 4 layers with high confidence"
        
        # Should have validated approach since confidence is high
        assert result.validated_approach is not None
        assert "Agent" in result.validated_approach
    
    @pytest.mark.asyncio
    async def test_hallucinated_code_validation_low_confidence(self, validation_engine):
        """Test validation of hallucinated code achieves low confidence"""
        
        code_intent = "Create a Pydantic AI agent"
        framework = "PydanticAI"
        hallucinated_code = '''
from pydantic_ai import PydanticAgent  # Wrong class

agent = PydanticAgent(model="gpt-4")   # Wrong parameters
agent.add_validation_rule("test")      # Non-existent method
result = agent.execute_with_memory("Hello")  # Non-existent method
print(result.response)                 # Wrong attribute
'''
        
        # Mock RAG system to return validation failures
        mock_validation = RAGValidationResult(
            is_valid=False,
            confidence=0.1,
            api_structure=[],
            documentation_examples=[],
            issues=["API not found", "Method does not exist"],
            suggestions=["Use Agent class", "Use run_sync method"]
        )
        validation_engine.rag_system.validate_api_usage.return_value = mock_validation
        
        # Run validation
        result = await validation_engine.validate_code_generation(
            code_intent, framework, hallucinated_code
        )
        
        # Assertions
        assert result.consensus_score < 0.5, f"Expected low consensus, got {result.consensus_score:.1%}"
        assert len(result.overall_issues) > 0, "Expected validation issues to be found"
        
        # Check for critical issues
        critical_issues = [
            issue for issue in result.overall_issues
            if issue.severity == ValidationSeverity.CRITICAL
        ]
        assert len(critical_issues) > 0, "Expected critical issues for hallucinated code"
        
        # Should have recommendations for improvement
        assert len(result.recommendations) > 0
        assert any("confidence" in rec.lower() for rec in result.recommendations)
    
    @pytest.mark.asyncio
    async def test_consensus_calculation_weights(self, validation_engine):
        """Test that consensus calculation uses proper layer weights"""
        
        # Create mock layer results with known confidence values
        mock_layer_results = {
            ValidationLayer.STRUCTURAL.value: LayerValidationResult(
                layer=ValidationLayer.STRUCTURAL,
                confidence=1.0,  # 25% weight
                issues=[],
                validated_items=["Agent.run_sync"],
                metadata={},
                processing_time=0.1
            ),
            ValidationLayer.TEMPORAL.value: LayerValidationResult(
                layer=ValidationLayer.TEMPORAL,
                confidence=0.8,  # 20% weight
                issues=[],
                validated_items=["Pattern match"],
                metadata={},
                processing_time=0.1
            ),
            ValidationLayer.DOCUMENTATION.value: LayerValidationResult(
                layer=ValidationLayer.DOCUMENTATION,
                confidence=0.9,  # 20% weight
                issues=[],
                validated_items=["API documented"],
                metadata={},
                processing_time=0.1
            ),
            ValidationLayer.MEMORY.value: LayerValidationResult(
                layer=ValidationLayer.MEMORY,
                confidence=0.7,  # 15% weight
                issues=[],
                validated_items=["Memory context"],
                metadata={},
                processing_time=0.1
            ),
            ValidationLayer.TYPE_SAFETY.value: LayerValidationResult(
                layer=ValidationLayer.TYPE_SAFETY,
                confidence=0.8,  # 15% weight
                issues=[],
                validated_items=["Type annotations"],
                metadata={},
                processing_time=0.1
            ),
            ValidationLayer.CONSENSUS.value: LayerValidationResult(
                layer=ValidationLayer.CONSENSUS,
                confidence=0.9,  # 5% weight
                issues=[],
                validated_items=["High agreement"],
                metadata={},
                processing_time=0.1
            )
        }
        
        # Calculate expected consensus score
        # (1.0 * 0.25) + (0.8 * 0.20) + (0.9 * 0.20) + (0.7 * 0.15) + (0.8 * 0.15) + (0.9 * 0.05)
        expected_score = 0.25 + 0.16 + 0.18 + 0.105 + 0.12 + 0.045
        # = 0.86
        
        # Test internal consensus calculation
        calculated_score = validation_engine._calculate_consensus_score(mock_layer_results)
        
        assert abs(calculated_score - expected_score) < 0.01, \
            f"Expected consensus {expected_score:.3f}, got {calculated_score:.3f}"
    
    @pytest.mark.asyncio
    async def test_code_analysis_accuracy(self, validation_engine):
        """Test that code analysis correctly extracts structure"""
        
        code = '''
import asyncio
from pydantic_ai import Agent
from pydantic import BaseModel
from typing import Optional

class UserResponse(BaseModel):
    name: str
    age: int
    email: Optional[str] = None

async def create_agent() -> Agent:
    return Agent("openai:gpt-4", result_type=UserResponse)

def main():
    agent = Agent("openai:gpt-4")
    result = agent.run_sync("Hello")
    data = result.data
    
    # Another call
    asyncio.run(process_async())

async def process_async():
    agent = await create_agent()
    result = await agent.run("Async hello")
    return result.data
'''
        
        analysis = await validation_engine._analyze_code_structure(code)
        
        # Check imports
        assert "asyncio" in analysis.imports
        assert any("from pydantic_ai import Agent" in imp for imp in analysis.imports)
        assert any("from pydantic import BaseModel" in imp for imp in analysis.imports)
        
        # Check classes
        assert "UserResponse" in analysis.classes
        
        # Check methods
        assert "create_agent" in analysis.methods
        assert "main" in analysis.methods
        assert "process_async" in analysis.methods
        
        # Check API calls
        api_calls = {call["full_call"] for call in analysis.api_calls}
        assert "agent.run_sync" in api_calls
        assert "agent.run" in api_calls
        assert "asyncio.run" in api_calls
        
        # Check frameworks
        assert "PydanticAI" in analysis.frameworks
    
    @pytest.mark.asyncio
    async def test_validation_performance_tracking(self, validation_engine):
        """Test that validation engine tracks performance metrics"""
        
        # Get initial stats
        initial_stats = await validation_engine.get_performance_stats()
        initial_count = initial_stats["validation_count"]
        
        # Run validation
        await validation_engine.validate_code_generation(
            "test validation", "PydanticAI"
        )
        
        # Check updated stats
        final_stats = await validation_engine.get_performance_stats()
        assert final_stats["validation_count"] == initial_count + 1
        assert final_stats["total_validation_time"] >= initial_stats["total_validation_time"]
        assert final_stats["average_validation_time"] > 0


class TestIndividualValidators:
    """Test suite for individual validation layer components"""
    
    @pytest.fixture
    async def mock_graphiti_engine(self):
        """Create mock Graphiti engine with Neo4j driver"""
        engine = Mock(spec=AIDGraphitiEngine)
        
        # Mock Neo4j driver and session
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()
        mock_record = Mock()
        
        # Configure successful API validation
        mock_record.__getitem__ = Mock(side_effect=lambda key: {
            "m.name": "run_sync",
            "m.signature": "run_sync(self, user_prompt: str) -> RunResult",
            "m.confidence": 0.98
        }[key])
        
        mock_result.single = AsyncMock(return_value=mock_record)
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_driver.session.return_value = mock_session
        
        engine.neo4j_driver = mock_driver
        return engine
    
    @pytest.mark.asyncio
    async def test_structural_validator(self, mock_graphiti_engine):
        """Test structural validation against Neo4j knowledge graph"""
        
        validator = StructuralValidator(mock_graphiti_engine)
        
        # Create code analysis with API calls
        code_analysis = CodeAnalysis(
            imports=["from pydantic_ai import Agent"],
            classes=["Agent"],
            methods=[],
            function_calls=["agent.run_sync"],
            api_calls=[{
                "object": "agent",
                "method": "run_sync",
                "full_call": "agent.run_sync"
            }],
            frameworks=["PydanticAI"],
            patterns=[]
        )
        
        # Run validation
        result = await validator.validate(
            "test validation", "PydanticAI", code_analysis
        )
        
        # Assertions
        assert result.layer == ValidationLayer.STRUCTURAL
        assert result.confidence > 0.9  # Should be high since API exists
        assert len(result.validated_items) > 0
        assert "agent.run_sync" in result.validated_items
        assert len(result.issues) == 0  # No issues for valid API
    
    @pytest.mark.asyncio
    async def test_structural_validator_invalid_api(self, mock_graphiti_engine):
        """Test structural validation with invalid API"""
        
        # Configure Neo4j to return no results (API doesn't exist)
        mock_session = Mock()
        mock_result = Mock()
        mock_result.single = AsyncMock(return_value=None)  # No record found
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_graphiti_engine.neo4j_driver.session.return_value = mock_session
        
        validator = StructuralValidator(mock_graphiti_engine)
        
        # Code analysis with non-existent API
        code_analysis = CodeAnalysis(
            imports=["from pydantic_ai import Agent"],
            classes=["Agent"],
            methods=[],
            function_calls=["agent.add_validation_rule"],
            api_calls=[{
                "object": "agent",
                "method": "add_validation_rule",
                "full_call": "agent.add_validation_rule"
            }],
            frameworks=["PydanticAI"],
            patterns=[]
        )
        
        # Run validation
        result = await validator.validate(
            "test validation", "PydanticAI", code_analysis
        )
        
        # Assertions
        assert result.layer == ValidationLayer.STRUCTURAL
        assert result.confidence < 0.5  # Should be low since API doesn't exist
        assert len(result.issues) > 0
        assert any(issue.issue_type == "non_existent_api" for issue in result.issues)
    
    @pytest.mark.asyncio
    async def test_temporal_validator(self, mock_graphiti_engine):
        """Test temporal validation using Graphiti patterns"""
        
        # Mock successful patterns
        successful_pattern = Pattern(
            id="pattern1",
            name="AgentSetup",
            framework="PydanticAI",
            pattern_type="success",
            code_template="agent = Agent('openai:gpt-4')",
            success_rate=0.95,
            use_cases=["customer_support"],
            metadata={},
            created_at=datetime.now(),
            last_used=datetime.now(),
            usage_count=100
        )
        
        mock_graphiti_engine.query_successful_patterns.return_value = [successful_pattern]
        mock_graphiti_engine.query_failed_patterns.return_value = []
        
        validator = TemporalValidator(mock_graphiti_engine)
        
        # Code analysis with matching pattern
        code_analysis = CodeAnalysis(
            imports=["from pydantic_ai import Agent"],
            classes=[],
            methods=[],
            function_calls=[],
            api_calls=[],
            frameworks=["PydanticAI"],
            patterns=["Agent initialization pattern"]
        )
        
        # Run validation
        result = await validator.validate(
            "agent setup", "PydanticAI", code_analysis
        )
        
        # Assertions
        assert result.layer == ValidationLayer.TEMPORAL
        assert result.confidence >= 0.8  # High confidence due to successful patterns
        assert result.metadata["successful_patterns_found"] == 1
        assert result.metadata["failed_patterns_found"] == 0
    
    @pytest.mark.asyncio
    async def test_documentation_validator(self):
        """Test documentation validation using RAG system"""
        
        # Mock RAG system
        mock_rag_system = Mock(spec=HybridRAGSystem)
        
        # Mock search result
        mock_search_result = Mock()
        mock_search_result.confidence = 0.9
        mock_search_result.api_references = []
        mock_rag_system.hybrid_search = AsyncMock(return_value=mock_search_result)
        
        # Mock API validation
        mock_api_validation = RAGValidationResult(
            is_valid=True,
            confidence=0.95,
            api_structure=[],
            documentation_examples=[],
            issues=[],
            suggestions=[]
        )
        mock_rag_system.validate_api_usage = AsyncMock(return_value=mock_api_validation)
        
        validator = DocumentationValidator(mock_rag_system)
        
        # Code analysis
        code_analysis = CodeAnalysis(
            imports=["from pydantic_ai import Agent"],
            classes=[],
            methods=[],
            function_calls=[],
            api_calls=[{
                "object": "agent",
                "method": "run_sync",
                "full_call": "agent.run_sync"
            }],
            frameworks=["PydanticAI"],
            patterns=[]
        )
        
        # Run validation
        result = await validator.validate(
            "agent usage", "PydanticAI", code_analysis
        )
        
        # Assertions
        assert result.layer == ValidationLayer.DOCUMENTATION
        assert result.confidence > 0.9  # High confidence due to good documentation
        assert len(result.validated_items) > 0
        assert "agent.run_sync" in result.validated_items
    
    @pytest.mark.asyncio
    async def test_memory_validator(self):
        """Test memory validation using memory bank"""
        
        # Mock memory bank
        mock_memory_bank = Mock(spec=MemoryBank)
        mock_context = MemoryContext(
            relevant_decisions=["Use Pydantic AI for structured output", "Prefer async patterns"],
            patterns=["Agent setup pattern", "Error handling pattern"],
            success_factors=["Type safety", "Proper error handling"],
            warnings=["Avoid blocking calls in async context"],
            confidence=0.88
        )
        mock_memory_bank.get_relevant_context = AsyncMock(return_value=mock_context)
        
        validator = MemoryValidator(mock_memory_bank)
        
        # Run validation
        result = await validator.validate(
            "PydanticAI agent setup", "PydanticAI", None
        )
        
        # Assertions
        assert result.layer == ValidationLayer.MEMORY
        assert result.confidence == 0.88  # Matches memory context confidence
        assert len(result.validated_items) > 0
        assert any("Memory decision" in item for item in result.validated_items)
        assert result.metadata["relevant_decisions"] == 2
        assert result.metadata["warnings"] == 1
    
    @pytest.mark.asyncio
    async def test_type_safety_validator(self):
        """Test type safety validation"""
        
        validator = TypeSafetyValidator()
        
        # Code with type annotations and error handling
        typed_code = '''
from typing import Optional
from pydantic_ai import Agent

async def create_agent() -> Agent:
    try:
        return Agent("openai:gpt-4")
    except Exception as e:
        print(f"Error: {e}")
        raise

def process_result(result: str) -> Optional[str]:
    return result if result else None
'''
        
        # Parse code
        import ast
        tree = ast.parse(typed_code)
        
        code_analysis = CodeAnalysis(
            imports=["from typing import Optional", "from pydantic_ai import Agent"],
            classes=[],
            methods=["create_agent", "process_result"],
            function_calls=[],
            api_calls=[],
            frameworks=["PydanticAI"],
            patterns=[],
            ast_tree=tree
        )
        
        # Run validation
        result = await validator.validate(
            "typed code", "PydanticAI", code_analysis
        )
        
        # Assertions
        assert result.layer == ValidationLayer.TYPE_SAFETY
        assert result.confidence > 0.8  # High confidence due to type annotations and error handling
        assert len(result.validated_items) > 0
        assert "Type annotations present" in result.validated_items
    
    @pytest.mark.asyncio
    async def test_consensus_validator(self):
        """Test consensus validation across layers"""
        
        validator = ConsensusValidator()
        
        # Mock layer results with good agreement
        layer_results = {
            "structural": LayerValidationResult(
                layer=ValidationLayer.STRUCTURAL,
                confidence=0.95,
                issues=[],
                validated_items=["API exists"],
                metadata={},
                processing_time=0.1
            ),
            "temporal": LayerValidationResult(
                layer=ValidationLayer.TEMPORAL,
                confidence=0.90,
                issues=[],
                validated_items=["Pattern match"],
                metadata={},
                processing_time=0.1
            ),
            "documentation": LayerValidationResult(
                layer=ValidationLayer.DOCUMENTATION,
                confidence=0.92,
                issues=[],
                validated_items=["Well documented"],
                metadata={},
                processing_time=0.1
            )
        }
        
        # Run validation
        result = await validator.validate(
            "test", "PydanticAI", None, layer_results
        )
        
        # Assertions
        assert result.layer == ValidationLayer.CONSENSUS
        assert result.confidence > 0.8  # High confidence due to good agreement
        assert len(result.issues) == 0  # No disagreement issues
        assert result.metadata["layer_count"] == 3
        assert result.metadata["confidence_std_dev"] < 0.1  # Low standard deviation = good agreement
    
    @pytest.mark.asyncio
    async def test_consensus_validator_high_disagreement(self):
        """Test consensus validation with high layer disagreement"""
        
        validator = ConsensusValidator()
        
        # Mock layer results with poor agreement
        layer_results = {
            "structural": LayerValidationResult(
                layer=ValidationLayer.STRUCTURAL,
                confidence=0.1,  # Very low
                issues=[],
                validated_items=[],
                metadata={},
                processing_time=0.1
            ),
            "temporal": LayerValidationResult(
                layer=ValidationLayer.TEMPORAL,
                confidence=0.9,  # Very high
                issues=[],
                validated_items=[],
                metadata={},
                processing_time=0.1
            ),
            "documentation": LayerValidationResult(
                layer=ValidationLayer.DOCUMENTATION,
                confidence=0.5,  # Medium
                issues=[],
                validated_items=[],
                metadata={},
                processing_time=0.1
            )
        }
        
        # Run validation
        result = await validator.validate(
            "test", "PydanticAI", None, layer_results
        )
        
        # Assertions
        assert result.layer == ValidationLayer.CONSENSUS
        assert result.confidence < 0.8  # Lower confidence due to disagreement
        assert len(result.issues) > 0  # Should flag disagreement
        assert any(issue.issue_type == "layer_disagreement" for issue in result.issues)
        assert result.metadata["confidence_std_dev"] > 0.3  # High standard deviation


class TestValidationAccuracyBenchmark:
    """Benchmark tests for validation accuracy"""
    
    @pytest.mark.asyncio
    async def test_92_percent_consensus_accuracy(self, validation_engine):
        """Test that validation achieves 92%+ consensus for good code"""
        
        high_quality_code_cases = [
            # (code_intent, framework, code, description)
            (
                "Create basic Pydantic AI agent",
                "PydanticAI",
                '''
from pydantic_ai import Agent
agent = Agent("openai:gpt-4")
result = agent.run_sync("Hello")
''',
                "Basic agent usage"
            ),
            (
                "Create structured output agent",
                "PydanticAI", 
                '''
from pydantic_ai import Agent
from pydantic import BaseModel

class Response(BaseModel):
    message: str
    confidence: float

agent = Agent("openai:gpt-4", result_type=Response)
result = agent.run_sync("Hello")
print(result.data.message)
''',
                "Structured output with type safety"
            ),
            (
                "Create async agent",
                "PydanticAI",
                '''
import asyncio
from pydantic_ai import Agent

async def main():
    agent = Agent("openai:gpt-4")
    result = await agent.run("Hello")
    return result.data

asyncio.run(main())
''',
                "Async pattern usage"
            )
        ]
        
        consensus_scores = []
        
        for intent, framework, code, description in high_quality_code_cases:
            result = await validation_engine.validate_code_generation(
                intent, framework, code
            )
            
            consensus_scores.append(result.consensus_score)
            print(f"{description}: {result.consensus_score:.1%} consensus")
        
        # Calculate average consensus
        avg_consensus = sum(consensus_scores) / len(consensus_scores)
        print(f"Average consensus for high-quality code: {avg_consensus:.1%}")
        
        # Assert 92%+ average consensus for good code
        assert avg_consensus >= 0.92, f"Average consensus {avg_consensus:.1%} is below 92% threshold"
        
        # Assert all individual cases meet threshold
        low_consensus_cases = [score for score in consensus_scores if score < 0.85]
        assert len(low_consensus_cases) == 0, f"Found {len(low_consensus_cases)} cases below 85% consensus"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])