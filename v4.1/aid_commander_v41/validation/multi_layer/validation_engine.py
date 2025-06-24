#!/usr/bin/env python3
"""
AID Commander v4.1 - Multi-Layer Validation Engine

Implements the 6-layer validation system for 92%+ certainty in code generation:
1. Structural Validation (Neo4j)
2. Temporal Validation (Graphiti) 
3. Documentation Validation (RAG)
4. Memory Validation (Enhanced v4.0)
5. Type Safety Validation (Pydantic AI)
6. Consensus Validation (Multi-source agreement)
"""

import asyncio
import json
import ast
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field
import structlog

from ...knowledge_graph.graphiti.temporal_engine import AIDGraphitiEngine, Pattern
from ...knowledge_graph.rag.hybrid_search import HybridRAGSystem, ValidationResult as RAGValidationResult
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "v4"))
from memory_service import MemoryBank, MemoryContext

logger = structlog.get_logger(__name__)


class ValidationLayer(Enum):
    """Enum for validation layer types"""
    STRUCTURAL = "structural"
    TEMPORAL = "temporal" 
    DOCUMENTATION = "documentation"
    MEMORY = "memory"
    TYPE_SAFETY = "type_safety"
    CONSENSUS = "consensus"


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue found during analysis"""
    layer: ValidationLayer
    severity: ValidationSeverity
    issue_type: str
    description: str
    code_location: Optional[str] = None
    suggestion: Optional[str] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = None


@dataclass
class LayerValidationResult:
    """Result from a single validation layer"""
    layer: ValidationLayer
    confidence: float
    issues: List[ValidationIssue]
    validated_items: List[str]
    metadata: Dict[str, Any]
    processing_time: float


class ValidationResult(BaseModel):
    """Comprehensive validation result from all layers"""
    consensus_score: float = Field(description="Overall consensus score (0.0-1.0)")
    layer_results: Dict[str, LayerValidationResult] = Field(default_factory=dict)
    overall_issues: List[ValidationIssue] = Field(default_factory=list)
    validated_approach: Optional[str] = Field(default=None)
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    processing_time: float = Field(default=0.0)


@dataclass
class CodeAnalysis:
    """Analysis of code structure for validation"""
    imports: List[str]
    classes: List[str]
    methods: List[str]
    function_calls: List[str]
    api_calls: List[Dict[str, str]]
    frameworks: List[str]
    patterns: List[str]
    ast_tree: Optional[ast.AST] = None


class MultiLayerValidationEngine:
    """
    Advanced multi-layer validation engine achieving 92%+ certainty
    
    The engine runs 6 independent validation layers in parallel and
    calculates consensus to ensure bulletproof code generation.
    """
    
    def __init__(self,
                 graphiti_engine: AIDGraphitiEngine,
                 rag_system: HybridRAGSystem,
                 memory_bank: MemoryBank,
                 confidence_threshold: float = 0.92):
        
        self.graphiti_engine = graphiti_engine
        self.rag_system = rag_system
        self.memory_bank = memory_bank
        self.confidence_threshold = confidence_threshold
        
        # Initialize validators
        self.validators = {
            ValidationLayer.STRUCTURAL: StructuralValidator(graphiti_engine),
            ValidationLayer.TEMPORAL: TemporalValidator(graphiti_engine),
            ValidationLayer.DOCUMENTATION: DocumentationValidator(rag_system),
            ValidationLayer.MEMORY: MemoryValidator(memory_bank),
            ValidationLayer.TYPE_SAFETY: TypeSafetyValidator(),
            ValidationLayer.CONSENSUS: ConsensusValidator()
        }
        
        # Performance tracking
        self.validation_count = 0
        self.total_validation_time = 0.0
        
        self.logger = logger.bind(component="MultiLayerValidator")
    
    async def validate_code_generation(self, 
                                     code_intent: str,
                                     framework: str,
                                     generated_code: Optional[str] = None) -> ValidationResult:
        """
        Comprehensive multi-layer validation of code generation intent or generated code
        """
        
        start_time = datetime.now()
        self.logger.info(f"Starting multi-layer validation for {framework}")
        
        try:
            # Step 1: Analyze code structure if generated code provided
            code_analysis = None
            if generated_code:
                code_analysis = await self._analyze_code_structure(generated_code)
            
            # Step 2: Run all validation layers in parallel
            layer_tasks = []
            
            for layer, validator in self.validators.items():
                if layer == ValidationLayer.CONSENSUS:
                    continue  # Consensus runs after other layers
                
                task = self._run_validation_layer(
                    validator, layer, code_intent, framework, code_analysis
                )
                layer_tasks.append(task)
            
            layer_results = await asyncio.gather(*layer_tasks, return_exceptions=True)
            
            # Step 3: Process layer results
            processed_results = {}
            for i, (layer, _) in enumerate([item for item in self.validators.items() if item[0] != ValidationLayer.CONSENSUS]):
                if isinstance(layer_results[i], Exception):
                    self.logger.error(f"Layer {layer} failed: {layer_results[i]}")
                    processed_results[layer.value] = LayerValidationResult(
                        layer=layer,
                        confidence=0.0,
                        issues=[ValidationIssue(
                            layer=layer,
                            severity=ValidationSeverity.CRITICAL,
                            issue_type="layer_failure",
                            description=f"Validation layer failed: {layer_results[i]}"
                        )],
                        validated_items=[],
                        metadata={"error": str(layer_results[i])},
                        processing_time=0.0
                    )
                else:
                    processed_results[layer.value] = layer_results[i]
            
            # Step 4: Run consensus validation
            consensus_result = await self.validators[ValidationLayer.CONSENSUS].validate(
                code_intent, framework, code_analysis, processed_results
            )
            processed_results[ValidationLayer.CONSENSUS.value] = consensus_result
            
            # Step 5: Calculate final validation result
            validation_result = await self._calculate_final_result(
                processed_results, code_intent, framework
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            validation_result.processing_time = processing_time
            
            self.validation_count += 1
            self.total_validation_time += processing_time
            
            self.logger.info(f"Multi-layer validation completed: {validation_result.consensus_score:.1%} confidence")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Multi-layer validation failed: {e}")
            raise
    
    async def _analyze_code_structure(self, code: str) -> CodeAnalysis:
        """Analyze code structure using AST parsing"""
        
        try:
            tree = ast.parse(code)
            
            imports = []
            classes = []
            methods = []
            function_calls = []
            api_calls = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(f"from {node.module} import {', '.join([alias.name for alias in node.names])}")
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    methods.append(node.name)
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        obj_name = ast.unparse(node.func.value) if hasattr(ast, 'unparse') else 'unknown'
                        method_name = node.func.attr
                        function_calls.append(f"{obj_name}.{method_name}")
                        api_calls.append({
                            "object": obj_name,
                            "method": method_name,
                            "full_call": f"{obj_name}.{method_name}"
                        })
                    elif isinstance(node.func, ast.Name):
                        function_calls.append(node.func.id)
            
            # Detect frameworks from imports
            frameworks = []
            for imp in imports:
                if 'pydantic_ai' in imp:
                    frameworks.append('PydanticAI')
                elif 'fastapi' in imp:
                    frameworks.append('FastAPI')
                elif 'django' in imp:
                    frameworks.append('Django')
            
            # Extract patterns
            patterns = []
            for api_call in api_calls:
                patterns.append(f"{api_call['object']}.{api_call['method']} pattern")
            
            return CodeAnalysis(
                imports=imports,
                classes=classes,
                methods=methods,
                function_calls=function_calls,
                api_calls=api_calls,
                frameworks=frameworks,
                patterns=patterns,
                ast_tree=tree
            )
            
        except Exception as e:
            self.logger.error(f"Failed to analyze code structure: {e}")
            return CodeAnalysis(
                imports=[], classes=[], methods=[], function_calls=[],
                api_calls=[], frameworks=[], patterns=[]
            )
    
    async def _run_validation_layer(self,
                                  validator,
                                  layer: ValidationLayer,
                                  code_intent: str,
                                  framework: str,
                                  code_analysis: Optional[CodeAnalysis]) -> LayerValidationResult:
        """Run a single validation layer"""
        
        start_time = datetime.now()
        
        try:
            result = await validator.validate(code_intent, framework, code_analysis)
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Validation layer {layer} failed: {e}")
            
            return LayerValidationResult(
                layer=layer,
                confidence=0.0,
                issues=[ValidationIssue(
                    layer=layer,
                    severity=ValidationSeverity.CRITICAL,
                    issue_type="validation_error",
                    description=f"Layer validation failed: {e}"
                )],
                validated_items=[],
                metadata={"error": str(e)},
                processing_time=processing_time
            )
    
    async def _calculate_final_result(self,
                                    layer_results: Dict[str, LayerValidationResult],
                                    code_intent: str,
                                    framework: str) -> ValidationResult:
        """Calculate final validation result with consensus scoring"""
        
        # Weight factors for each layer
        layer_weights = {
            ValidationLayer.STRUCTURAL.value: 0.25,    # Critical - API must exist
            ValidationLayer.TEMPORAL.value: 0.20,      # Important - proven patterns
            ValidationLayer.DOCUMENTATION.value: 0.20, # Important - documented usage
            ValidationLayer.MEMORY.value: 0.15,        # Useful - past decisions
            ValidationLayer.TYPE_SAFETY.value: 0.15,   # Useful - type compliance
            ValidationLayer.CONSENSUS.value: 0.05      # Meta - cross-validation
        }
        
        # Calculate weighted consensus score
        weighted_score = 0.0
        total_weight = 0.0
        confidence_breakdown = {}
        
        for layer_name, result in layer_results.items():
            weight = layer_weights.get(layer_name, 0.0)
            weighted_score += result.confidence * weight
            total_weight += weight
            confidence_breakdown[layer_name] = result.confidence
        
        consensus_score = weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Collect all issues
        all_issues = []
        for result in layer_results.values():
            all_issues.extend(result.issues)
        
        # Sort issues by severity
        severity_order = {
            ValidationSeverity.CRITICAL: 0,
            ValidationSeverity.HIGH: 1,
            ValidationSeverity.MEDIUM: 2,
            ValidationSeverity.LOW: 3,
            ValidationSeverity.INFO: 4
        }
        all_issues.sort(key=lambda x: severity_order[x.severity])
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            layer_results, consensus_score, framework
        )
        
        # Generate validated approach if consensus is sufficient
        validated_approach = None
        if consensus_score >= self.confidence_threshold:
            validated_approach = await self._generate_validated_approach(
                code_intent, framework, layer_results
            )
        
        return ValidationResult(
            consensus_score=consensus_score,
            layer_results=layer_results,
            overall_issues=all_issues,
            validated_approach=validated_approach,
            confidence_breakdown=confidence_breakdown,
            recommendations=recommendations
        )
    
    async def _generate_recommendations(self,
                                      layer_results: Dict[str, LayerValidationResult],
                                      consensus_score: float,
                                      framework: str) -> List[str]:
        """Generate actionable recommendations based on validation results"""
        
        recommendations = []
        
        # Low consensus score recommendations
        if consensus_score < 0.5:
            recommendations.append("⚠️  Very low confidence - consider alternative approach")
            recommendations.append("🔍 Review API documentation for correct usage patterns")
        elif consensus_score < self.confidence_threshold:
            recommendations.append("📈 Moderate confidence - review and refine approach")
        
        # Layer-specific recommendations
        structural_result = layer_results.get(ValidationLayer.STRUCTURAL.value)
        if structural_result and structural_result.confidence < 0.8:
            recommendations.append("🏗️  Verify API methods exist in framework documentation")
        
        temporal_result = layer_results.get(ValidationLayer.TEMPORAL.value)
        if temporal_result and temporal_result.confidence < 0.8:
            recommendations.append("⏳ Consider using proven patterns from successful projects")
        
        doc_result = layer_results.get(ValidationLayer.DOCUMENTATION.value)
        if doc_result and doc_result.confidence < 0.8:
            recommendations.append("📚 Cross-reference with official framework documentation")
        
        memory_result = layer_results.get(ValidationLayer.MEMORY.value)
        if memory_result and memory_result.confidence < 0.8:
            recommendations.append("🧠 Review past project decisions for similar use cases")
        
        # Issue-based recommendations
        critical_issues = [issue for result in layer_results.values() for issue in result.issues if issue.severity == ValidationSeverity.CRITICAL]
        if critical_issues:
            recommendations.append("🚨 Address critical validation issues before proceeding")
        
        return recommendations
    
    async def _generate_validated_approach(self,
                                         code_intent: str,
                                         framework: str,
                                         layer_results: Dict[str, LayerValidationResult]) -> str:
        """Generate a validated approach based on successful validation"""
        
        approach_parts = [
            f"# Validated approach for: {code_intent}",
            f"# Framework: {framework}",
            f"# Validation confidence: {self._calculate_consensus_score(layer_results):.1%}",
            ""
        ]
        
        # Extract validated patterns from temporal layer
        temporal_result = layer_results.get(ValidationLayer.TEMPORAL.value)
        if temporal_result and temporal_result.validated_items:
            approach_parts.append("# Proven patterns:")
            for item in temporal_result.validated_items[:3]:
                approach_parts.append(f"# ✅ {item}")
            approach_parts.append("")
        
        # Extract validated APIs from structural layer
        structural_result = layer_results.get(ValidationLayer.STRUCTURAL.value)
        if structural_result and structural_result.validated_items:
            approach_parts.append("# Validated APIs:")
            for item in structural_result.validated_items[:5]:
                approach_parts.append(f"# ✅ {item}")
            approach_parts.append("")
        
        # Add framework-specific validated template
        if framework == "PydanticAI":
            approach_parts.extend([
                "from pydantic_ai import Agent",
                "from pydantic import BaseModel",
                "",
                "# Validated agent creation pattern",
                "agent = Agent('openai:gpt-4')  # Correct model format",
                "",
                "# Validated synchronous usage",
                "result = agent.run_sync(user_prompt)",
                "response = result.data  # Correct data access",
                "",
                "# Validated asynchronous usage", 
                "# result = await agent.run(user_prompt)",
                "# response = result.data"
            ])
        
        return "\n".join(approach_parts)
    
    def _calculate_consensus_score(self, layer_results: Dict[str, LayerValidationResult]) -> float:
        """Calculate consensus score from layer results"""
        layer_weights = {
            ValidationLayer.STRUCTURAL.value: 0.25,
            ValidationLayer.TEMPORAL.value: 0.20,
            ValidationLayer.DOCUMENTATION.value: 0.20,
            ValidationLayer.MEMORY.value: 0.15,
            ValidationLayer.TYPE_SAFETY.value: 0.15,
            ValidationLayer.CONSENSUS.value: 0.05
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for layer_name, result in layer_results.items():
            weight = layer_weights.get(layer_name, 0.0)
            weighted_score += result.confidence * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the validation engine"""
        return {
            "validation_count": self.validation_count,
            "total_validation_time": self.total_validation_time,
            "average_validation_time": self.total_validation_time / max(self.validation_count, 1),
            "confidence_threshold": self.confidence_threshold
        }


# Individual validator implementations
class StructuralValidator:
    """Validates API structure against Neo4j knowledge graph"""
    
    def __init__(self, graphiti_engine: AIDGraphitiEngine):
        self.graphiti_engine = graphiti_engine
        self.logger = logger.bind(component="StructuralValidator")
    
    async def validate(self, 
                     code_intent: str,
                     framework: str,
                     code_analysis: Optional[CodeAnalysis]) -> LayerValidationResult:
        """Validate against Neo4j API structure"""
        
        issues = []
        validated_items = []
        
        if code_analysis:
            # Validate API calls against knowledge graph
            for api_call in code_analysis.api_calls:
                validation = await self._validate_api_call(
                    api_call, framework
                )
                
                if validation["exists"]:
                    validated_items.append(f"{api_call['object']}.{api_call['method']}")
                else:
                    issues.append(ValidationIssue(
                        layer=ValidationLayer.STRUCTURAL,
                        severity=ValidationSeverity.CRITICAL,
                        issue_type="non_existent_api",
                        description=f"API {api_call['full_call']} not found in {framework}",
                        suggestion=f"Use validated alternative: {validation.get('suggestion', 'Unknown')}"
                    ))
        
        # Calculate confidence based on validation results
        if code_analysis and code_analysis.api_calls:
            confidence = len(validated_items) / len(code_analysis.api_calls)
        else:
            confidence = 0.8  # Neutral when no specific APIs to validate
        
        return LayerValidationResult(
            layer=ValidationLayer.STRUCTURAL,
            confidence=confidence,
            issues=issues,
            validated_items=validated_items,
            metadata={"framework": framework},
            processing_time=0.0
        )
    
    async def _validate_api_call(self, api_call: Dict[str, str], framework: str) -> Dict[str, Any]:
        """Validate specific API call against knowledge graph"""
        
        # Query Neo4j for API existence
        query = """
        MATCH (f:Framework {name: $framework})
        -[:CONTAINS]->(c:Class)
        -[:HAS_METHOD]->(m:Method)
        WHERE c.name = $class_name AND m.name = $method_name
        RETURN m.name, m.signature, m.confidence
        """
        
        try:
            async with self.graphiti_engine.neo4j_driver.session() as session:
                result = await session.run(query, {
                    "framework": framework,
                    "class_name": api_call["object"],
                    "method_name": api_call["method"]
                })
                
                record = await result.single()
                if record:
                    return {
                        "exists": True,
                        "signature": record["m.signature"],
                        "confidence": record["m.confidence"]
                    }
                else:
                    # Try to find similar methods
                    similar_query = """
                    MATCH (f:Framework {name: $framework})
                    -[:CONTAINS]->(c:Class)
                    -[:HAS_METHOD]->(m:Method)
                    WHERE m.name CONTAINS $method_name OR c.name = $class_name
                    RETURN m.name, c.name
                    LIMIT 3
                    """
                    
                    similar_result = await session.run(similar_query, {
                        "framework": framework,
                        "class_name": api_call["object"],
                        "method_name": api_call["method"]
                    })
                    
                    suggestions = []
                    async for similar_record in similar_result:
                        suggestions.append(f"{similar_record['c.name']}.{similar_record['m.name']}")
                    
                    return {
                        "exists": False,
                        "suggestion": suggestions[0] if suggestions else "Check documentation"
                    }
                    
        except Exception as e:
            self.logger.error(f"Failed to validate API call: {e}")
            return {"exists": False, "error": str(e)}


class TemporalValidator:
    """Validates against temporal patterns in Graphiti"""
    
    def __init__(self, graphiti_engine: AIDGraphitiEngine):
        self.graphiti_engine = graphiti_engine
        self.logger = logger.bind(component="TemporalValidator")
    
    async def validate(self,
                     code_intent: str,
                     framework: str, 
                     code_analysis: Optional[CodeAnalysis]) -> LayerValidationResult:
        """Validate against temporal patterns"""
        
        issues = []
        validated_items = []
        
        # Query successful patterns
        successful_patterns = await self.graphiti_engine.query_successful_patterns(
            framework=framework,
            min_success_rate=0.8,
            time_window_days=180
        )
        
        # Query failed patterns
        failed_patterns = await self.graphiti_engine.query_failed_patterns(
            framework=framework,
            time_window_days=180
        )
        
        if code_analysis:
            # Check if patterns match successful ones
            for pattern in code_analysis.patterns:
                for success_pattern in successful_patterns:
                    if self._pattern_similarity(pattern, success_pattern.code_template) > 0.7:
                        validated_items.append(f"Pattern: {success_pattern.name}")
                        break
                
                # Check against failed patterns
                for fail_pattern in failed_patterns:
                    if self._pattern_similarity(pattern, fail_pattern.code_template) > 0.8:
                        issues.append(ValidationIssue(
                            layer=ValidationLayer.TEMPORAL,
                            severity=ValidationSeverity.HIGH,
                            issue_type="historically_failed_pattern",
                            description=f"Pattern similar to historically failed: {fail_pattern.name}",
                            suggestion="Use alternative approach from successful patterns"
                        ))
        
        # Calculate confidence based on pattern matches
        confidence = 0.8  # Base confidence
        if successful_patterns:
            confidence = min(0.95, confidence + (len(validated_items) * 0.1))
        if issues:
            confidence = max(0.2, confidence - (len(issues) * 0.2))
        
        return LayerValidationResult(
            layer=ValidationLayer.TEMPORAL,
            confidence=confidence,
            issues=issues,
            validated_items=validated_items,
            metadata={
                "successful_patterns_found": len(successful_patterns),
                "failed_patterns_found": len(failed_patterns)
            },
            processing_time=0.0
        )
    
    def _pattern_similarity(self, pattern1: str, pattern2: str) -> float:
        """Calculate similarity between two patterns"""
        # Simple word-based similarity
        words1 = set(pattern1.lower().split())
        words2 = set(pattern2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0


class DocumentationValidator:
    """Validates against documentation using RAG system"""
    
    def __init__(self, rag_system: HybridRAGSystem):
        self.rag_system = rag_system
        self.logger = logger.bind(component="DocumentationValidator")
    
    async def validate(self,
                     code_intent: str,
                     framework: str,
                     code_analysis: Optional[CodeAnalysis]) -> LayerValidationResult:
        """Validate against documentation"""
        
        issues = []
        validated_items = []
        
        # Search documentation for intent
        search_result = await self.rag_system.hybrid_search(
            query=f"{framework} {code_intent}",
            framework=framework,
            max_results=5
        )
        
        if code_analysis:
            # Validate each API call against documentation
            for api_call in code_analysis.api_calls:
                validation = await self.rag_system.validate_api_usage(
                    api_call=api_call["full_call"],
                    framework=framework
                )
                
                if validation.is_valid:
                    validated_items.append(api_call["full_call"])
                else:
                    issues.append(ValidationIssue(
                        layer=ValidationLayer.DOCUMENTATION,
                        severity=ValidationSeverity.MEDIUM,
                        issue_type="undocumented_usage",
                        description=f"API usage not well documented: {api_call['full_call']}",
                        suggestion="Check official documentation for correct usage"
                    ))
        
        # Base confidence on search results and validations
        confidence = search_result.confidence
        if code_analysis and code_analysis.api_calls:
            validation_rate = len(validated_items) / len(code_analysis.api_calls)
            confidence = (confidence + validation_rate) / 2
        
        return LayerValidationResult(
            layer=ValidationLayer.DOCUMENTATION,
            confidence=confidence,
            issues=issues,
            validated_items=validated_items,
            metadata={
                "search_confidence": search_result.confidence,
                "api_references_found": len(search_result.api_references)
            },
            processing_time=0.0
        )


class MemoryValidator:
    """Validates against memory bank decisions"""
    
    def __init__(self, memory_bank: MemoryBank):
        self.memory_bank = memory_bank
        self.logger = logger.bind(component="MemoryValidator")
    
    async def validate(self,
                     code_intent: str,
                     framework: str,
                     code_analysis: Optional[CodeAnalysis]) -> LayerValidationResult:
        """Validate against memory decisions"""
        
        issues = []
        validated_items = []
        
        # Get relevant memory context
        memory_context = await self.memory_bank.get_relevant_context(
            f"{framework} {code_intent}"
        )
        
        # Check if we have relevant past decisions
        if memory_context.relevant_decisions:
            for decision in memory_context.relevant_decisions:
                if framework.lower() in decision.lower():
                    validated_items.append(f"Memory decision: {decision[:50]}...")
        
        # Check for warnings or patterns to avoid
        if memory_context.warnings:
            for warning in memory_context.warnings:
                if framework.lower() in warning.lower():
                    issues.append(ValidationIssue(
                        layer=ValidationLayer.MEMORY,
                        severity=ValidationSeverity.MEDIUM,
                        issue_type="memory_warning",
                        description=f"Past experience warning: {warning[:100]}...",
                        suggestion="Consider alternative based on memory"
                    ))
        
        return LayerValidationResult(
            layer=ValidationLayer.MEMORY,
            confidence=memory_context.confidence,
            issues=issues,
            validated_items=validated_items,
            metadata={
                "relevant_decisions": len(memory_context.relevant_decisions),
                "success_factors": len(memory_context.success_factors),
                "warnings": len(memory_context.warnings)
            },
            processing_time=0.0
        )


class TypeSafetyValidator:
    """Validates type safety and structure"""
    
    def __init__(self):
        self.logger = logger.bind(component="TypeSafetyValidator")
    
    async def validate(self,
                     code_intent: str,
                     framework: str,
                     code_analysis: Optional[CodeAnalysis]) -> LayerValidationResult:
        """Validate type safety"""
        
        issues = []
        validated_items = []
        
        if code_analysis and code_analysis.ast_tree:
            # Check for type annotations
            has_type_annotations = self._check_type_annotations(code_analysis.ast_tree)
            if has_type_annotations:
                validated_items.append("Type annotations present")
            
            # Check for proper error handling
            has_error_handling = self._check_error_handling(code_analysis.ast_tree)
            if not has_error_handling:
                issues.append(ValidationIssue(
                    layer=ValidationLayer.TYPE_SAFETY,
                    severity=ValidationSeverity.LOW,
                    issue_type="missing_error_handling",
                    description="No error handling detected",
                    suggestion="Add try/except blocks for robustness"
                ))
            
            # Check for async/await consistency
            async_consistency = self._check_async_consistency(code_analysis.ast_tree)
            if not async_consistency:
                issues.append(ValidationIssue(
                    layer=ValidationLayer.TYPE_SAFETY,
                    severity=ValidationSeverity.MEDIUM,
                    issue_type="async_inconsistency",
                    description="Inconsistent async/await usage",
                    suggestion="Ensure async functions are awaited"
                ))
        
        # Calculate confidence based on checks
        confidence = 0.8  # Base confidence
        if validated_items:
            confidence += 0.1
        if issues:
            confidence -= len(issues) * 0.1
        
        confidence = max(0.0, min(1.0, confidence))
        
        return LayerValidationResult(
            layer=ValidationLayer.TYPE_SAFETY,
            confidence=confidence,
            issues=issues,
            validated_items=validated_items,
            metadata={"checks_performed": ["type_annotations", "error_handling", "async_consistency"]},
            processing_time=0.0
        )
    
    def _check_type_annotations(self, tree: ast.AST) -> bool:
        """Check if type annotations are present"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.returns or any(arg.annotation for arg in node.args.args):
                    return True
        return False
    
    def _check_error_handling(self, tree: ast.AST) -> bool:
        """Check if error handling is present"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                return True
        return False
    
    def _check_async_consistency(self, tree: ast.AST) -> bool:
        """Check async/await consistency"""
        async_functions = []
        await_calls = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                async_functions.append(node.name)
            elif isinstance(node, ast.Await):
                await_calls.append(node)
        
        # Simple consistency check
        return len(async_functions) == 0 or len(await_calls) > 0


class ConsensusValidator:
    """Validates consensus across all layers"""
    
    def __init__(self):
        self.logger = logger.bind(component="ConsensusValidator")
    
    async def validate(self,
                     code_intent: str,
                     framework: str,
                     code_analysis: Optional[CodeAnalysis],
                     layer_results: Dict[str, LayerValidationResult]) -> LayerValidationResult:
        """Calculate consensus validation"""
        
        issues = []
        validated_items = []
        
        # Calculate agreement between layers
        confidence_values = [result.confidence for result in layer_results.values()]
        confidence_std = self._calculate_std_dev(confidence_values)
        
        # High standard deviation indicates disagreement
        if confidence_std > 0.3:
            issues.append(ValidationIssue(
                layer=ValidationLayer.CONSENSUS,
                severity=ValidationSeverity.MEDIUM,
                issue_type="layer_disagreement",
                description=f"High disagreement between validation layers (std: {confidence_std:.2f})",
                suggestion="Review individual layer results for conflicts"
            ))
        
        # Check for critical issues across layers
        critical_issues = []
        for result in layer_results.values():
            critical_issues.extend([issue for issue in result.issues if issue.severity == ValidationSeverity.CRITICAL])
        
        if critical_issues:
            issues.append(ValidationIssue(
                layer=ValidationLayer.CONSENSUS,
                severity=ValidationSeverity.CRITICAL,
                issue_type="critical_consensus_failure",
                description=f"Multiple layers report critical issues ({len(critical_issues)} total)",
                suggestion="Address critical issues before proceeding"
            ))
        
        # Consensus confidence is inverse of disagreement
        consensus_confidence = max(0.0, 1.0 - confidence_std)
        
        if confidence_values:
            validated_items.append(f"Layer agreement: {consensus_confidence:.1%}")
        
        return LayerValidationResult(
            layer=ValidationLayer.CONSENSUS,
            confidence=consensus_confidence,
            issues=issues,
            validated_items=validated_items,
            metadata={
                "confidence_std_dev": confidence_std,
                "layer_count": len(layer_results),
                "critical_issues": len(critical_issues)
            },
            processing_time=0.0
        )
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation of confidence values"""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5


# Example usage
async def main():
    """Example usage of the multi-layer validation engine"""
    
    # This would be properly configured in production
    print("Multi-layer validation engine example")
    print("Configure components and run validation...")


if __name__ == "__main__":
    asyncio.run(main())