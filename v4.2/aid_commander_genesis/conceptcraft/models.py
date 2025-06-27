#!/usr/bin/env python3
"""
ConceptCraft AI Data Models

Pydantic models for representing concepts, stakeholders, stories, and validation
throughout the collaborative concept development process.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, validator


class StakeholderType(str, Enum):
    """Types of stakeholders in concept ecosystem."""
    PRIMARY = "primary"
    SECONDARY = "secondary" 
    TERTIARY = "tertiary"


class ValidationLevel(str, Enum):
    """Levels of concept validation completeness."""
    FOUNDATION = "foundation"        # Level 1 complete
    STRESS_TESTED = "stress_tested"  # Level 2 complete
    ENHANCED = "enhanced"           # Level 3 complete


class StakeholderStory(BaseModel):
    """Individual stakeholder story within concept ecosystem."""
    
    stakeholder_name: str = Field(..., description="Name of the stakeholder")
    stakeholder_type: StakeholderType = Field(..., description="Primary, secondary, or tertiary")
    role_description: str = Field(..., description="What role this stakeholder plays")
    
    # Core story elements
    current_situation: str = Field(..., description="Their current pain points/situation")
    pain_points: List[str] = Field(default_factory=list, description="Specific problems they face")
    goals: List[str] = Field(default_factory=list, description="What they want to achieve")
    
    # Enhanced experience with concept
    enhanced_experience: str = Field(..., description="How concept transforms their experience")
    value_delivered: str = Field(..., description="Specific value/outcome they receive")
    success_indicators: List[str] = Field(default_factory=list, description="How success is measured")
    
    # Story metadata
    story_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in story validity")
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)


class ChallengeResolution(BaseModel):
    """Challenge scenario and its resolution during stress-testing."""
    
    challenge_id: str = Field(..., description="Unique identifier for challenge")
    challenge_scenario: str = Field(..., description="Detailed challenge/failure scenario")
    affected_stakeholders: List[str] = Field(default_factory=list, description="Which stakeholders are impacted")
    
    # Resolution details
    solution_approach: str = Field(..., description="How the concept addresses this challenge")
    concept_evolution: str = Field(..., description="How the concept changed/improved")
    confidence_improvement: float = Field(default=0.0, description="Confidence gained from resolving this")
    
    # Metadata
    challenge_category: str = Field(default="", description="Type of challenge (technical, market, etc.)")
    severity_level: int = Field(default=5, ge=1, le=10, description="Challenge severity 1-10")
    resolution_quality: float = Field(default=0.8, ge=0.0, le=1.0, description="Quality of resolution")
    created_at: datetime = Field(default_factory=datetime.now)


class Enhancement(BaseModel):
    """Enhancement opportunity identified during amplification."""
    
    enhancement_id: str = Field(..., description="Unique identifier for enhancement")
    enhancement_type: str = Field(..., description="Type of enhancement (network effects, etc.)")
    description: str = Field(..., description="Detailed enhancement description")
    
    # Impact analysis
    stakeholder_benefits: Dict[str, str] = Field(default_factory=dict, description="How each stakeholder benefits")
    implementation_approach: str = Field(..., description="How this enhancement would work")
    success_amplification: str = Field(..., description="How this amplifies concept success")
    
    # Prioritization
    impact_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Potential impact 0-1")
    feasibility_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Implementation feasibility 0-1")
    innovation_level: float = Field(default=0.5, ge=0.0, le=1.0, description="How innovative/novel this is")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)


class StakeholderEcosystem(BaseModel):
    """Complete stakeholder ecosystem for a concept."""
    
    primary_stakeholders: List[StakeholderStory] = Field(default_factory=list)
    secondary_stakeholders: List[StakeholderStory] = Field(default_factory=list)
    tertiary_stakeholders: List[StakeholderStory] = Field(default_factory=list)
    
    def all(self) -> List[StakeholderStory]:
        """Get all stakeholders across all types."""
        return self.primary_stakeholders + self.secondary_stakeholders + self.tertiary_stakeholders
    
    def get_by_name(self, name: str) -> Optional[StakeholderStory]:
        """Find stakeholder by name."""
        for stakeholder in self.all():
            if stakeholder.stakeholder_name.lower() == name.lower():
                return stakeholder
        return None
    
    def count_by_type(self) -> Dict[str, int]:
        """Count stakeholders by type."""
        return {
            "primary": len(self.primary_stakeholders),
            "secondary": len(self.secondary_stakeholders), 
            "tertiary": len(self.tertiary_stakeholders),
            "total": len(self.all())
        }


class ConceptDocument(BaseModel):
    """Complete concept document with stories, challenges, and enhancements."""
    
    # Core concept identity
    concept_id: str = Field(..., description="Unique concept identifier")
    concept_name: str = Field(..., description="Name of the concept/product")
    concept_description: str = Field(..., description="Core value proposition")
    
    # Stakeholder ecosystem
    stakeholders: StakeholderEcosystem = Field(default_factory=StakeholderEcosystem)
    core_stories: List[StakeholderStory] = Field(default_factory=list, description="Most important stakeholder stories")
    
    # Validation and enhancement
    challenges_resolved: List[ChallengeResolution] = Field(default_factory=list)
    enhancements: List[Enhancement] = Field(default_factory=list)
    validation_level: ValidationLevel = Field(default=ValidationLevel.FOUNDATION)
    
    # Concept metadata
    market_category: str = Field(default="", description="Market category/positioning")
    target_market: List[str] = Field(default_factory=list, description="Primary target markets")
    competitive_differentiation: str = Field(default="", description="Key differentiators")
    
    # Success metrics and outcomes
    success_metrics: List[str] = Field(default_factory=list, description="How success will be measured")
    narrative_confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Overall story confidence")
    concept_maturity: float = Field(default=0.0, ge=0.0, le=1.0, description="Concept development completeness")
    
    # Development readiness
    prd_readiness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Ready for PRD development")
    technical_complexity: int = Field(default=5, ge=1, le=10, description="Estimated technical complexity")
    stakeholder_complexity: int = Field(default=1, ge=1, le=10, description="Stakeholder ecosystem complexity")
    
    # Timestamps and versioning
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    concept_version: str = Field(default="1.0.0", description="Concept version")
    
    @validator('core_stories', always=True)
    def set_core_stories_from_stakeholders(cls, v, values):
        """Automatically populate core stories from primary stakeholders if not set."""
        if not v and 'stakeholders' in values:
            return values['stakeholders'].primary_stakeholders[:3]  # Top 3 primary stakeholders
        return v
    
    def calculate_maturity_score(self) -> float:
        """Calculate concept maturity based on completeness."""
        score = 0.0
        
        # Stakeholder coverage (40% of score)
        stakeholder_count = len(self.stakeholders.all())
        if stakeholder_count >= 3:
            score += 0.4
        elif stakeholder_count >= 2:
            score += 0.3
        elif stakeholder_count >= 1:
            score += 0.2
        
        # Challenge resolution (30% of score)
        if len(self.challenges_resolved) >= 3:
            score += 0.3
        elif len(self.challenges_resolved) >= 2:
            score += 0.2
        elif len(self.challenges_resolved) >= 1:
            score += 0.1
        
        # Enhancement opportunities (20% of score)
        if len(self.enhancements) >= 2:
            score += 0.2
        elif len(self.enhancements) >= 1:
            score += 0.1
        
        # Validation level (10% of score)
        if self.validation_level == ValidationLevel.ENHANCED:
            score += 0.1
        elif self.validation_level == ValidationLevel.STRESS_TESTED:
            score += 0.07
        elif self.validation_level == ValidationLevel.FOUNDATION:
            score += 0.03
        
        self.concept_maturity = min(score, 1.0)
        return self.concept_maturity
    
    def calculate_prd_readiness(self) -> float:
        """Calculate readiness for PRD development."""
        readiness = 0.0
        
        # Must have validated stories
        if len(self.core_stories) >= 2:
            readiness += 0.3
        
        # Must have addressed challenges
        if len(self.challenges_resolved) >= 2:
            readiness += 0.3
        
        # Should have enhancement vision
        if len(self.enhancements) >= 1:
            readiness += 0.2
        
        # Should be at least stress-tested
        if self.validation_level in [ValidationLevel.STRESS_TESTED, ValidationLevel.ENHANCED]:
            readiness += 0.2
        
        self.prd_readiness_score = min(readiness, 1.0)
        return self.prd_readiness_score
    
    def get_summary(self) -> Dict[str, Any]:
        """Get concept summary for display/reporting."""
        return {
            "concept_name": self.concept_name,
            "concept_description": self.concept_description,
            "stakeholder_count": len(self.stakeholders.all()),
            "core_stories": len(self.core_stories),
            "challenges_resolved": len(self.challenges_resolved),
            "enhancements": len(self.enhancements),
            "validation_level": self.validation_level.value,
            "maturity_score": self.calculate_maturity_score(),
            "prd_readiness": self.calculate_prd_readiness(),
            "narrative_confidence": self.narrative_confidence
        }


class ConversationState(BaseModel):
    """State tracking for ConceptCraft AI conversation."""
    
    current_level: int = Field(default=1, ge=1, le=3, description="Current development level (1-3)")
    concept_document: Optional[ConceptDocument] = Field(default=None)
    
    # Level-specific state
    stakeholder_discovery_complete: bool = Field(default=False)
    challenge_stress_testing_complete: bool = Field(default=False)
    enhancement_exploration_complete: bool = Field(default=False)
    
    # Conversation metadata
    session_id: str = Field(..., description="Unique session identifier")
    user_mode: str = Field(default="adaptive", description="User interaction mode")
    conversation_turns: int = Field(default=0, description="Number of conversation turns")
    
    # Progress tracking
    level_1_progress: float = Field(default=0.0, ge=0.0, le=1.0)
    level_2_progress: float = Field(default=0.0, ge=0.0, le=1.0)
    level_3_progress: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Conversation history (simplified)
    key_decisions: List[str] = Field(default_factory=list, description="Important decisions made")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="Learned user preferences")
    
    # Timestamps
    session_started: datetime = Field(default_factory=datetime.now)
    last_interaction: datetime = Field(default_factory=datetime.now)
    
    def can_advance_to_level_2(self) -> bool:
        """Check if ready to advance to stress-testing."""
        return (
            self.stakeholder_discovery_complete and
            self.concept_document is not None and
            len(self.concept_document.core_stories) >= 2
        )
    
    def can_advance_to_level_3(self) -> bool:
        """Check if ready to advance to enhancement."""
        return (
            self.challenge_stress_testing_complete and
            self.concept_document is not None and
            len(self.concept_document.challenges_resolved) >= 2
        )
    
    def update_progress(self, level: int, progress: float):
        """Update progress for specific level."""
        if level == 1:
            self.level_1_progress = min(progress, 1.0)
        elif level == 2:
            self.level_2_progress = min(progress, 1.0)
        elif level == 3:
            self.level_3_progress = min(progress, 1.0)
        
        self.last_interaction = datetime.now()


class TemporalEntity(BaseModel):
    """Entity in temporal knowledge graph for pattern tracking."""
    
    entity_id: str = Field(..., description="Unique entity identifier")
    entity_name: str = Field(..., description="Human-readable name")
    entity_type: str = Field(..., description="Type of entity (concept, stakeholder, pattern)")
    
    properties: Dict[str, Any] = Field(default_factory=dict, description="Entity properties")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in entity")
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = Field(default=1, description="Entity version")


class TemporalRelationship(BaseModel):
    """Relationship between entities over time."""
    
    relationship_id: str = Field(..., description="Unique relationship identifier")
    source_entity_id: str = Field(..., description="Source entity")
    target_entity_id: str = Field(..., description="Target entity")
    relationship_type: str = Field(..., description="Type of relationship")
    
    properties: Dict[str, Any] = Field(default_factory=dict, description="Relationship properties")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Relationship confidence")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    
    valid_from: datetime = Field(default_factory=datetime.now)
    valid_to: Optional[datetime] = Field(default=None, description="When relationship ends")
    
    def is_active(self, at_time: Optional[datetime] = None) -> bool:
        """Check if relationship is active at given time."""
        check_time = at_time or datetime.now()
        
        if check_time < self.valid_from:
            return False
        
        if self.valid_to and check_time > self.valid_to:
            return False
        
        return True