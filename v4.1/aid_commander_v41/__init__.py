#!/usr/bin/env python3
"""
AID Commander v4.1 - Knowledge Graph-Enhanced Development Orchestrator

Main package initialization for AID Commander v4.1 with knowledge graph integration,
hallucination detection, and multi-layer validation system.
"""

# Lazy imports to avoid heavy dependency loading on package import
def _get_cli_main():
    from .cli.main import AIDCommanderV41, main
    return AIDCommanderV41, main

def _get_graphiti():
    from .knowledge_graph.graphiti.temporal_engine import AIDGraphitiEngine
    return AIDGraphitiEngine

def _get_rag():
    from .knowledge_graph.rag.hybrid_search import HybridRAGSystem
    return HybridRAGSystem

def _get_validation():
    from .validation.multi_layer.validation_engine import MultiLayerValidationEngine
    return MultiLayerValidationEngine

def _get_hallucination():
    from .validation.hallucination.detection_engine import HallucinationDetectionEngine
    return HallucinationDetectionEngine

def _get_memory():
    from .memory_enhanced.graph_memory_bank import GraphEnhancedMemoryBank
    return GraphEnhancedMemoryBank

# Module-level getters for backward compatibility
def get_commander():
    """Get AIDCommanderV41 class with lazy loading"""
    AIDCommanderV41, _ = _get_cli_main()
    return AIDCommanderV41

# Expose main through module-level function
def main():
    """Run AID Commander v4.1 CLI"""
    _, main_func = _get_cli_main()
    return main_func()

__version__ = "4.1.0"
__title__ = "AID Commander v4.1"
__description__ = "Knowledge Graph-Enhanced Development Orchestrator with 92%+ Success Certainty"
__author__ = "AID Commander Team"
__license__ = "MIT"

__all__ = [
    "get_commander",
    "main",
    "_get_cli_main",
    "_get_graphiti", 
    "_get_rag",
    "_get_validation",
    "_get_hallucination",
    "_get_memory"
]