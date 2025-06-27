#!/usr/bin/env python3
"""
Adaptive Intelligence Engine Data Models

Models for representing project context, user preferences, complexity analysis,
and development recommendations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, validator


class ExecutionMode(str, Enum):
    """Available execution modes for development orchestration."""
    LIGHTWEIGHT = "lightweight"           # Human-guided with AI assistance
    KNOWLEDGE_GRAPH = "knowledge_graph"   # Full validation with 92%+ confidence  
    HYBRID = "hybrid"                     # Adaptive combination
    CREATIVE = "creative"                 # Innovation-focused experimentation


class ProjectComplexity(str, Enum):
    """Project complexity levels."""
    SIMPLE = "simple"         # 1-2 stakeholders, straightforward requirements
    MODERATE = "moderate"     # 3-5 stakeholders, some complexity
    COMPLEX = "complex"       # 6+ stakeholders, enterprise dynamics
    ENTERPRISE = "enterprise" # 10+ stakeholders, organizational complexity


class ConfidenceLevel(str, Enum):
    """Confidence levels for recommendations."""
    LOW = "low"           # < 70% confidence
    MODERATE = "moderate" # 70-85% confidence  
    HIGH = "high"         # 85-95% confidence
    VERY_HIGH = "very_high" # > 95% confidence


class UserPreferences(BaseModel):
    """User preferences and constraints for development approach."""
    
    # Development preferences
    preferred_mode: Optional[ExecutionMode] = Field(default=None, description="User's preferred execution mode")
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0, description="Risk tolerance 0-1")
    speed_vs_quality: float = Field(default=0.5, ge=0.0, le=1.0, description="Speed preference 0=quality, 1=speed")
    
    # Experience and skills
    ai_experience_level: int = Field(default=5, ge=1, le=10, description="AI development experience 1-10")
    technical_expertise: int = Field(default=5, ge=1, le=10, description="Technical expertise 1-10")
    project_management_experience: int = Field(default=5, ge=1, le=10, description="PM experience 1-10")
    
    # Resource constraints
    time_constraints: str = Field(default="moderate", description="Time constraints: tight, moderate, flexible")
    budget_constraints: str = Field(default="moderate", description="Budget constraints: tight, moderate, flexible")
    team_size: int = Field(default=1, ge=1, description="Team size")
    
    # Validation preferences
    validation_level: str = Field(default="standard", description="standard, high, enterprise")
    confidence_threshold: float = Field(default=0.85, ge=0.0, le=1.0, description="Minimum confidence threshold")
    
    # Learning and growth
    learning_mode: bool = Field(default=False, description="Whether user wants to learn from process")
    experimentation_willingness: float = Field(default=0.5, ge=0.0, le=1.0, description="Willingness to try new approaches")


class ProjectContext(BaseModel):
    """Context information about the current project."""
    
    # Basic project info
    project_name: str = Field(..., description="Project name")
    project_description: str = Field(..., description="Project description")
    project_type: str = Field(default="product", description="Type: product, service, platform, etc.")
    
    # Complexity indicators
    stakeholder_count: int = Field(default=1, ge=1, description="Number of stakeholders")
    stakeholder_types: List[str] = Field(default_factory=list, description="Types of stakeholders")
    technical_complexity: int = Field(default=5, ge=1, le=10, description="Technical complexity 1-10")
    integration_requirements: List[str] = Field(default_factory=list, description="Required integrations")
    
    # Business context
    market_maturity: str = Field(default="unknown", description="Market maturity: emerging, growing, mature")
    competitive_landscape: str = Field(default="unknown", description="Competitive landscape assessment")
    business_model: str = Field(default="unknown", description="Business model type")
    
    # Constraints and requirements
    timeline_constraints: Optional[str] = Field(default=None, description="Timeline constraints")
    regulatory_requirements: List[str] = Field(default_factory=list, description="Regulatory constraints")
    scalability_requirements: str = Field(default="moderate", description="Scalability needs")
    
    # Innovation aspects
    innovation_level: float = Field(default=0.5, ge=0.0, le=1.0, description="How innovative/novel this is")
    disruption_potential: float = Field(default=0.5, ge=0.0, le=1.0, description="Potential for market disruption")
    
    # Historical data
    similar_projects_count: int = Field(default=0, ge=0, description="Number of similar projects done")
    previous_success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Success rate in similar projects")


class ComplexityAnalysis(BaseModel):
    """Analysis of project complexity across multiple dimensions."""
    
    # Overall scores
    complexity_score: float = Field(..., ge=0.0, le=10.0, description="Overall complexity 0-10")
    complexity_level: ProjectComplexity = Field(..., description="Categorized complexity level")
    
    # Dimensional analysis
    stakeholder_complexity: float = Field(..., ge=0.0, le=10.0, description="Stakeholder ecosystem complexity")
    technical_complexity: float = Field(..., ge=0.0, le=10.0, description="Technical implementation complexity") 
    business_complexity: float = Field(..., ge=0.0, le=10.0, description="Business logic complexity")
    integration_complexity: float = Field(..., ge=0.0, le=10.0, description="System integration complexity")
    
    # Story and narrative analysis
    story_richness: float = Field(..., ge=0.0, le=10.0, description="Richness of stakeholder stories")
    narrative_coherence: float = Field(..., ge=0.0, le=10.0, description="Story coherence and consistency")
    stakeholder_alignment: float = Field(..., ge=0.0, le=10.0, description="Stakeholder goal alignment")
    
    # Risk and uncertainty
    uncertainty_level: float = Field(..., ge=0.0, le=10.0, description="Project uncertainty level")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    
    # Confidence and recommendations
    analysis_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this analysis")
    confidence_level: ConfidenceLevel = Field(..., description="Categorized confidence level")
    
    # Metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    analysis_version: str = Field(default="1.0.0", description="Analysis algorithm version")
    
    @validator('complexity_level', always=True)
    def set_complexity_level(cls, v, values):
        """Automatically set complexity level based on score."""
        if 'complexity_score' in values:
            score = values['complexity_score']
            if score <= 3.0:
                return ProjectComplexity.SIMPLE
            elif score <= 6.0:
                return ProjectComplexity.MODERATE  
            elif score <= 8.0:
                return ProjectComplexity.COMPLEX
            else:
                return ProjectComplexity.ENTERPRISE
        return v
    
    @validator('confidence_level', always=True) 
    def set_confidence_level(cls, v, values):
        """Automatically set confidence level based on score."""
        if 'analysis_confidence' in values:
            confidence = values['analysis_confidence']
            if confidence < 0.70:
                return ConfidenceLevel.LOW
            elif confidence < 0.85:
                return ConfidenceLevel.MODERATE
            elif confidence < 0.95:
                return ConfidenceLevel.HIGH
            else:
                return ConfidenceLevel.VERY_HIGH
        return v


class DevelopmentRecommendation(BaseModel):
    """Recommendation for development approach and execution mode."""
    
    # Core recommendation
    recommended_mode: ExecutionMode = Field(..., description="Recommended execution mode")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation")
    rationale: str = Field(..., description="Explanation of why this mode is recommended")
    
    # Alternative options
    alternative_modes: List[ExecutionMode] = Field(default_factory=list, description="Alternative modes to consider")
    mode_tradeoffs: Dict[str, str] = Field(default_factory=dict, description="Tradeoffs between modes")
    
    # Execution details
    validation_requirements: List[str] = Field(default_factory=list, description="Required validation steps")
    estimated_timeline: Optional[str] = Field(default=None, description="Estimated timeline")
    resource_requirements: List[str] = Field(default_factory=list, description="Required resources")
    
    # Risk and mitigation
    identified_risks: List[str] = Field(default_factory=list, description="Potential risks")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation approaches")
    success_factors: List[str] = Field(default_factory=list, description="Key success factors")
    
    # Progressive enhancement
    enhancement_path: List[str] = Field(default_factory=list, description="Path for progressive enhancement")
    scaling_considerations: List[str] = Field(default_factory=list, description="Scaling considerations")
    
    # Cross-project learning
    relevant_patterns: List[str] = Field(default_factory=list, description="Relevant patterns from other projects")
    learning_opportunities: List[str] = Field(default_factory=list, description="Learning opportunities")
    
    # Metadata
    recommendation_timestamp: datetime = Field(default_factory=datetime.now)
    recommender_version: str = Field(default="1.0.0", description="Recommendation engine version")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get recommendation summary for display."""
        return {
            "recommended_mode": self.recommended_mode.value,
            "confidence": f"{self.confidence_score:.1%}",
            "rationale": self.rationale,
            "timeline": self.estimated_timeline or "To be determined",
            "key_requirements": self.validation_requirements[:3],
            "main_risks": self.identified_risks[:2],
            "success_factors": self.success_factors[:3]
        }


class CrossProjectPattern(BaseModel):
    """Pattern identified from cross-project analysis."""
    
    pattern_id: str = Field(..., description="Unique pattern identifier")
    pattern_name: str = Field(..., description="Human-readable pattern name")
    pattern_description: str = Field(..., description="Description of the pattern")
    
    # Pattern characteristics
    pattern_type: str = Field(..., description="Type of pattern: success, failure, approach")
    complexity_range: List[float] = Field(..., description="Complexity range where pattern applies")
    stakeholder_types: List[str] = Field(default_factory=list, description="Relevant stakeholder types")
    
    # Success metrics
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Success rate of this pattern")
    sample_size: int = Field(..., ge=1, description="Number of projects in analysis")
    confidence_interval: List[float] = Field(..., description="95% confidence interval")
    
    # Applicability  
    applicable_modes: List[ExecutionMode] = Field(default_factory=list, description="Applicable execution modes")
    required_conditions: List[str] = Field(default_factory=list, description="Conditions for pattern to apply")
    contraindications: List[str] = Field(default_factory=list, description="When not to use this pattern")
    
    # Implementation guidance
    implementation_steps: List[str] = Field(default_factory=list, description="How to implement this pattern")
    common_pitfalls: List[str] = Field(default_factory=list, description="Common implementation mistakes")
    success_indicators: List[str] = Field(default_factory=list, description="Signs the pattern is working")
    
    # Metadata
    first_observed: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    pattern_version: str = Field(default="1.0.0")


class AdaptiveDecision(BaseModel):
    """Record of an adaptive intelligence decision for learning."""
    
    decision_id: str = Field(..., description="Unique decision identifier")
    project_context: ProjectContext = Field(..., description="Project context at time of decision")
    user_preferences: UserPreferences = Field(..., description="User preferences")
    complexity_analysis: ComplexityAnalysis = Field(..., description="Complexity analysis")
    
    # Decision details
    recommendation: DevelopmentRecommendation = Field(..., description="Recommendation made")
    user_choice: ExecutionMode = Field(..., description="Mode actually chosen by user")
    decision_rationale: str = Field(..., description="Why user made their choice")
    
    # Outcome tracking
    project_success: Optional[bool] = Field(default=None, description="Whether project succeeded")
    success_metrics: Dict[str, float] = Field(default_factory=dict, description="Measured success metrics")
    lessons_learned: List[str] = Field(default_factory=list, description="Lessons from this decision")
    
    # Timing
    decision_timestamp: datetime = Field(default_factory=datetime.now)
    project_completion: Optional[datetime] = Field(default=None, description="When project completed")
    
    def update_outcome(self, success: bool, metrics: Dict[str, float], lessons: List[str]):
        """Update decision outcome for learning."""
        self.project_success = success
        self.success_metrics = metrics
        self.lessons_learned = lessons
        if success is not None:
            self.project_completion = datetime.now()