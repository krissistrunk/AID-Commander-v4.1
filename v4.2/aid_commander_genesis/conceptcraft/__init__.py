#!/usr/bin/env python3
"""
ConceptCraft AI Integration for AID Commander Genesis

Story-driven product concept development platform that transforms vague ideas 
into PRD-ready concepts through systematic collaborative storytelling.

Core methodology:
- Level 1: Story Foundation (Co-Creative Discovery)
- Level 2: Story Stress-Testing (Systematic Challenge)  
- Level 3: Story Enhancement (Innovation Amplification)
"""

from .core import ConceptCraftAI, ConceptDocument, StakeholderStory, ChallengeResolution, Enhancement
from .models import (
    ConversationState,
    TemporalEntity,
    TemporalRelationship,
    ValidationLevel,
    StakeholderType
)

__all__ = [
    "ConceptCraftAI",
    "ConceptDocument", 
    "StakeholderStory",
    "ChallengeResolution",
    "Enhancement",
    "ConversationState",
    "TemporalEntity",
    "TemporalRelationship", 
    "ValidationLevel",
    "StakeholderType"
]