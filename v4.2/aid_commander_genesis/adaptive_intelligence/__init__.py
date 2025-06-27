#!/usr/bin/env python3
"""
Adaptive Intelligence Engine for AID Commander Genesis

Contextual intelligence system that determines optimal development approaches
based on project complexity, stakeholder dynamics, and user preferences.

Core capabilities:
- Concept complexity analysis
- Execution mode determination  
- Progressive enhancement recommendations
- Cross-project pattern recognition
"""

from .core import AdaptiveIntelligenceEngine, ExecutionMode, ComplexityAnalysis
from .models import ProjectContext, UserPreferences, DevelopmentRecommendation

__all__ = [
    "AdaptiveIntelligenceEngine",
    "ExecutionMode", 
    "ComplexityAnalysis",
    "ProjectContext",
    "UserPreferences",
    "DevelopmentRecommendation"
]