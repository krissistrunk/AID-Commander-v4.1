#!/usr/bin/env python3
"""
Adaptive Intelligence Engine Core Implementation

Contextual intelligence system that analyzes project complexity and determines
optimal development approaches with cross-project learning.
"""

import asyncio
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

import structlog
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from .models import (
    ExecutionMode,
    ProjectComplexity,
    ConfidenceLevel,
    ComplexityAnalysis,
    ProjectContext,
    UserPreferences,
    DevelopmentRecommendation,
    CrossProjectPattern,
    AdaptiveDecision
)

# Import ConceptCraft models for analysis
from ..conceptcraft.models import ConceptDocument

logger = structlog.get_logger(__name__)


class AdaptiveIntelligenceEngine:
    """
    Adaptive Intelligence Engine for AID Commander Genesis
    
    Analyzes project complexity, user preferences, and cross-project patterns
    to recommend optimal development approaches with high confidence.
    """
    
    def __init__(self):
        self.logger = logger.bind(component="AdaptiveIntelligenceEngine")
        self.decision_storage = Path.home() / ".aid_genesis" / "adaptive_decisions"
        self.pattern_storage = Path.home() / ".aid_genesis" / "cross_project_patterns"
        
        # Create storage directories
        self.decision_storage.mkdir(parents=True, exist_ok=True)
        self.pattern_storage.mkdir(parents=True, exist_ok=True)
        
        # Analysis configuration
        self.complexity_weights = {
            "stakeholder_complexity": 0.30,
            "technical_complexity": 0.25,
            "business_complexity": 0.20,
            "integration_complexity": 0.15,
            "uncertainty_level": 0.10
        }
        
        # Mode selection thresholds
        self.mode_thresholds = {
            ExecutionMode.LIGHTWEIGHT: {"max_complexity": 4.0, "min_confidence": 0.7},
            ExecutionMode.HYBRID: {"max_complexity": 7.0, "min_confidence": 0.8},
            ExecutionMode.KNOWLEDGE_GRAPH: {"max_complexity": 10.0, "min_confidence": 0.9},
            ExecutionMode.CREATIVE: {"innovation_threshold": 0.7, "min_confidence": 0.6}
        }
        
        # Cross-project learning
        self.patterns: List[CrossProjectPattern] = []
        self.decisions: List[AdaptiveDecision] = []
        
        # Load historical data
        asyncio.create_task(self._load_historical_data())
    
    async def initialize(self) -> bool:
        """Initialize the Adaptive Intelligence Engine."""
        try:
            self.logger.info("Initializing Adaptive Intelligence Engine")
            await self._load_historical_data()
            await self._update_cross_project_patterns()
            return True
        except Exception as e:
            self.logger.error("Adaptive Intelligence initialization failed", error=str(e))
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on Adaptive Intelligence Engine."""
        return {
            "status": "available",
            "decision_storage": str(self.decision_storage),
            "pattern_storage": str(self.pattern_storage),
            "loaded_patterns": len(self.patterns),
            "historical_decisions": len(self.decisions),
            "storage_accessible": self.decision_storage.exists() and self.pattern_storage.exists()
        }
    
    async def analyze_concept_complexity(self, concept_document: ConceptDocument) -> ComplexityAnalysis:
        """
        Analyze complexity of a concept document across multiple dimensions.
        
        Args:
            concept_document: ConceptDocument from ConceptCraft AI
            
        Returns:
            ComplexityAnalysis with dimensional scores and overall assessment
        """
        
        self.logger.info("Analyzing concept complexity", concept_name=concept_document.concept_name)
        
        # Stakeholder complexity analysis
        stakeholder_complexity = self._analyze_stakeholder_complexity(concept_document)
        
        # Technical complexity estimation
        technical_complexity = self._estimate_technical_complexity(concept_document)
        
        # Business complexity analysis
        business_complexity = self._analyze_business_complexity(concept_document)
        
        # Integration complexity
        integration_complexity = self._estimate_integration_complexity(concept_document)
        
        # Story and narrative analysis
        story_richness = self._analyze_story_richness(concept_document)
        narrative_coherence = self._analyze_narrative_coherence(concept_document)
        stakeholder_alignment = self._analyze_stakeholder_alignment(concept_document)
        
        # Uncertainty and risk analysis
        uncertainty_level = self._analyze_uncertainty_level(concept_document)
        risk_factors = self._identify_risk_factors(concept_document)
        
        # Calculate overall complexity score
        complexity_score = (
            stakeholder_complexity * self.complexity_weights["stakeholder_complexity"] +
            technical_complexity * self.complexity_weights["technical_complexity"] +
            business_complexity * self.complexity_weights["business_complexity"] +
            integration_complexity * self.complexity_weights["integration_complexity"] +
            uncertainty_level * self.complexity_weights["uncertainty_level"]
        )
        
        # Determine analysis confidence
        analysis_confidence = self._calculate_analysis_confidence(
            concept_document, stakeholder_complexity, story_richness
        )
        
        complexity_analysis = ComplexityAnalysis(
            complexity_score=complexity_score,
            stakeholder_complexity=stakeholder_complexity,
            technical_complexity=technical_complexity,
            business_complexity=business_complexity,
            integration_complexity=integration_complexity,
            story_richness=story_richness,
            narrative_coherence=narrative_coherence,
            stakeholder_alignment=stakeholder_alignment,
            uncertainty_level=uncertainty_level,
            risk_factors=risk_factors,
            analysis_confidence=analysis_confidence
        )
        
        self.logger.info(
            "Complexity analysis complete",
            complexity_score=complexity_score,
            complexity_level=complexity_analysis.complexity_level.value,
            confidence=analysis_confidence
        )
        
        return complexity_analysis
    
    async def determine_execution_mode(
        self,
        concept_document: ConceptDocument,
        user_preferences: UserPreferences,
        project_constraints: Dict[str, Any] = None
    ) -> ExecutionMode:
        """
        Determine optimal execution mode based on concept complexity and user preferences.
        
        Args:
            concept_document: ConceptDocument from ConceptCraft AI
            user_preferences: User preferences and constraints
            project_constraints: Additional project constraints
            
        Returns:
            Recommended ExecutionMode
        """
        
        # Analyze complexity
        complexity_analysis = await self.analyze_concept_complexity(concept_document)
        
        # Create project context
        project_context = self._create_project_context(concept_document, project_constraints or {})
        
        # Generate recommendation
        recommendation = await self._generate_mode_recommendation(
            complexity_analysis, user_preferences, project_context
        )
        
        # Store decision for learning
        decision = AdaptiveDecision(
            decision_id=str(uuid.uuid4()),
            project_context=project_context,
            user_preferences=user_preferences,
            complexity_analysis=complexity_analysis,
            recommendation=recommendation,
            user_choice=recommendation.recommended_mode,  # Will be updated when user makes choice
            decision_rationale="AI recommendation accepted"
        )
        
        await self._store_decision(decision)
        
        return recommendation.recommended_mode
    
    async def generate_development_recommendation(
        self,
        concept_document: ConceptDocument,
        user_preferences: UserPreferences,
        project_constraints: Dict[str, Any] = None
    ) -> DevelopmentRecommendation:
        """
        Generate comprehensive development recommendation with rationale.
        
        Args:
            concept_document: ConceptDocument from ConceptCraft AI
            user_preferences: User preferences and constraints
            project_constraints: Additional project constraints
            
        Returns:
            DevelopmentRecommendation with detailed guidance
        """
        
        # Analyze complexity
        complexity_analysis = await self.analyze_concept_complexity(concept_document)
        
        # Create project context
        project_context = self._create_project_context(concept_document, project_constraints or {})
        
        # Generate comprehensive recommendation
        recommendation = await self._generate_mode_recommendation(
            complexity_analysis, user_preferences, project_context
        )
        
        return recommendation
    
    def _analyze_stakeholder_complexity(self, concept_document: ConceptDocument) -> float:
        """Analyze stakeholder ecosystem complexity."""
        
        stakeholder_count = len(concept_document.stakeholders.all())
        stakeholder_types = len({s.stakeholder_type for s in concept_document.stakeholders.all()})
        
        # Base complexity from count
        count_complexity = min(stakeholder_count / 3.0, 3.0)  # Scale 0-3
        
        # Additional complexity from type diversity
        type_complexity = min(stakeholder_types / 2.0, 2.0)  # Scale 0-2
        
        # Challenge resolution complexity
        challenge_complexity = min(len(concept_document.challenges_resolved) / 2.0, 2.0)  # Scale 0-2
        
        # Stakeholder alignment complexity (inverse of alignment)
        alignment_scores = [story.story_confidence for story in concept_document.core_stories]
        avg_alignment = np.mean(alignment_scores) if alignment_scores else 0.5
        alignment_complexity = (1.0 - avg_alignment) * 3.0  # Scale 0-3
        
        total_complexity = count_complexity + type_complexity + challenge_complexity + alignment_complexity
        
        return min(total_complexity, 10.0)
    
    def _estimate_technical_complexity(self, concept_document: ConceptDocument) -> float:
        """Estimate technical implementation complexity."""
        
        # Base complexity from concept maturity
        base_complexity = (1.0 - concept_document.concept_maturity) * 3.0
        
        # Complexity from enhancements (network effects, integrations)
        enhancement_complexity = 0.0
        for enhancement in concept_document.enhancements:
            if "network" in enhancement.enhancement_type.lower():
                enhancement_complexity += 1.5
            elif "integration" in enhancement.enhancement_type.lower():
                enhancement_complexity += 1.0
            else:
                enhancement_complexity += 0.5
        
        enhancement_complexity = min(enhancement_complexity, 4.0)
        
        # Complexity from stakeholder technology requirements
        tech_requirements = 0.0
        for story in concept_document.core_stories:
            if any(tech_word in story.enhanced_experience.lower() 
                  for tech_word in ["ai", "machine learning", "real-time", "api", "integration"]):
                tech_requirements += 0.5
        
        tech_requirements = min(tech_requirements, 3.0)
        
        total_complexity = base_complexity + enhancement_complexity + tech_requirements
        
        return min(total_complexity, 10.0)
    
    def _analyze_business_complexity(self, concept_document: ConceptDocument) -> float:
        """Analyze business logic and model complexity."""
        
        # Complexity from multiple value propositions
        value_complexity = len(set(story.value_delivered for story in concept_document.core_stories))
        value_complexity = min(value_complexity / 2.0, 3.0)  # Scale 0-3
        
        # Market positioning complexity
        market_complexity = 1.0  # Default moderate complexity
        if concept_document.competitive_differentiation:
            # More differentiation = more complex positioning
            market_complexity = min(len(concept_document.competitive_differentiation.split()) / 20.0, 2.0)
        
        # Success metrics complexity
        metrics_complexity = min(len(concept_document.success_metrics) / 3.0, 2.0)
        
        # Challenge resolution business impact
        business_challenge_complexity = 0.0
        for challenge in concept_document.challenges_resolved:
            if any(biz_word in challenge.solution_approach.lower()
                  for biz_word in ["business model", "revenue", "pricing", "market", "competition"]):
                business_challenge_complexity += 0.5
        
        business_challenge_complexity = min(business_challenge_complexity, 3.0)
        
        total_complexity = value_complexity + market_complexity + metrics_complexity + business_challenge_complexity
        
        return min(total_complexity, 10.0)
    
    def _estimate_integration_complexity(self, concept_document: ConceptDocument) -> float:
        """Estimate system integration complexity."""
        
        integration_complexity = 0.0
        
        # Look for integration keywords in stories and enhancements
        integration_keywords = [
            "api", "integration", "connect", "sync", "import", "export",
            "third-party", "platform", "system", "database", "crm", "erp"
        ]
        
        # Check stakeholder stories for integration needs
        for story in concept_document.core_stories:
            text = f"{story.enhanced_experience} {story.value_delivered}".lower()
            integration_mentions = sum(1 for keyword in integration_keywords if keyword in text)
            integration_complexity += min(integration_mentions * 0.5, 2.0)
        
        # Check enhancements for integration requirements
        for enhancement in concept_document.enhancements:
            text = f"{enhancement.description} {enhancement.implementation_approach}".lower()
            integration_mentions = sum(1 for keyword in integration_keywords if keyword in text)
            integration_complexity += min(integration_mentions * 0.3, 1.5)
        
        # Challenge resolutions that involve integration
        for challenge in concept_document.challenges_resolved:
            text = f"{challenge.solution_approach} {challenge.concept_evolution}".lower()
            integration_mentions = sum(1 for keyword in integration_keywords if keyword in text)
            integration_complexity += min(integration_mentions * 0.2, 1.0)
        
        return min(integration_complexity, 10.0)
    
    def _analyze_story_richness(self, concept_document: ConceptDocument) -> float:
        """Analyze richness and depth of stakeholder stories."""
        
        if not concept_document.core_stories:
            return 0.0
        
        story_scores = []
        for story in concept_document.core_stories:
            # Story completeness score
            completeness = 0.0
            if story.current_situation: completeness += 1.0
            if story.pain_points: completeness += min(len(story.pain_points) / 3.0, 1.0)
            if story.enhanced_experience: completeness += 1.0
            if story.value_delivered: completeness += 1.0
            if story.success_indicators: completeness += min(len(story.success_indicators) / 2.0, 1.0)
            
            # Story depth score (length and detail)
            detail_score = 0.0
            text_length = len(f"{story.current_situation} {story.enhanced_experience} {story.value_delivered}")
            detail_score = min(text_length / 200.0, 2.0)  # Scale based on text length
            
            story_score = (completeness + detail_score) / 2.0
            story_scores.append(story_score)
        
        avg_story_richness = np.mean(story_scores)
        
        # Scale to 0-10
        return min(avg_story_richness * 2.0, 10.0)
    
    def _analyze_narrative_coherence(self, concept_document: ConceptDocument) -> float:
        """Analyze coherence and consistency across stakeholder stories."""
        
        if len(concept_document.core_stories) < 2:
            return 5.0  # Default moderate score for single story
        
        # Check value alignment across stories
        value_keywords = []
        for story in concept_document.core_stories:
            story_keywords = story.value_delivered.lower().split()
            value_keywords.extend(story_keywords)
        
        # Calculate keyword overlap (simple coherence measure)
        unique_keywords = set(value_keywords)
        total_keywords = len(value_keywords)
        
        if total_keywords == 0:
            return 3.0
        
        # Higher overlap = higher coherence
        overlap_ratio = (total_keywords - len(unique_keywords)) / total_keywords
        coherence_score = overlap_ratio * 10.0
        
        # Check if concept description aligns with stories
        concept_words = set(concept_document.concept_description.lower().split())
        story_words = set()
        for story in concept_document.core_stories:
            story_words.update(story.value_delivered.lower().split())
        
        alignment_ratio = len(concept_words.intersection(story_words)) / max(len(concept_words), 1)
        alignment_score = alignment_ratio * 10.0
        
        # Average coherence and alignment
        final_score = (coherence_score + alignment_score) / 2.0
        
        return min(final_score, 10.0)
    
    def _analyze_stakeholder_alignment(self, concept_document: ConceptDocument) -> float:
        """Analyze alignment between stakeholder goals and concept value."""
        
        if not concept_document.core_stories:
            return 5.0
        
        alignment_scores = []
        for story in concept_document.core_stories:
            # Use story confidence as proxy for alignment
            alignment_scores.append(story.story_confidence)
        
        avg_alignment = np.mean(alignment_scores)
        
        # Check for conflicting stakeholder needs in challenges
        conflict_penalty = 0.0
        for challenge in concept_document.challenges_resolved:
            if any(conflict_word in challenge.challenge_scenario.lower()
                  for conflict_word in ["conflict", "disagree", "oppose", "resist", "against"]):
                conflict_penalty += 0.1
        
        final_alignment = max(avg_alignment - conflict_penalty, 0.0)
        
        return min(final_alignment * 10.0, 10.0)
    
    def _analyze_uncertainty_level(self, concept_document: ConceptDocument) -> float:
        """Analyze project uncertainty and risk level."""
        
        uncertainty_factors = 0.0
        
        # Low concept maturity = high uncertainty
        maturity_uncertainty = (1.0 - concept_document.concept_maturity) * 3.0
        uncertainty_factors += maturity_uncertainty
        
        # Unresolved challenges = uncertainty
        if len(concept_document.challenges_resolved) < 2:
            uncertainty_factors += 2.0
        
        # Low narrative confidence = uncertainty
        confidence_uncertainty = (1.0 - concept_document.narrative_confidence) * 2.0
        uncertainty_factors += confidence_uncertainty
        
        # Innovation level = uncertainty
        innovation_keywords = ["new", "novel", "innovative", "first", "revolutionary", "breakthrough"]
        innovation_mentions = 0
        for story in concept_document.core_stories:
            text = f"{story.enhanced_experience} {story.value_delivered}".lower()
            innovation_mentions += sum(1 for keyword in innovation_keywords if keyword in text)
        
        innovation_uncertainty = min(innovation_mentions * 0.5, 3.0)
        uncertainty_factors += innovation_uncertainty
        
        return min(uncertainty_factors, 10.0)
    
    def _identify_risk_factors(self, concept_document: ConceptDocument) -> List[str]:
        """Identify potential risk factors from concept analysis."""
        
        risks = []
        
        # Stakeholder complexity risks
        if len(concept_document.stakeholders.all()) > 5:
            risks.append("High stakeholder complexity - coordination challenges")
        
        # Technical risks
        if concept_document.technical_complexity > 7:
            risks.append("High technical complexity - implementation challenges")
        
        # Market risks
        if not concept_document.competitive_differentiation:
            risks.append("Unclear competitive differentiation")
        
        # Validation risks
        if len(concept_document.challenges_resolved) < 2:
            risks.append("Insufficient challenge stress-testing")
        
        # Success metrics risks
        if not concept_document.success_metrics:
            risks.append("Undefined success metrics")
        
        # Innovation risks
        innovation_level = self._estimate_innovation_level(concept_document)
        if innovation_level > 7:
            risks.append("High innovation risk - unproven approach")
        
        return risks
    
    def _estimate_innovation_level(self, concept_document: ConceptDocument) -> float:
        """Estimate innovation level of the concept."""
        
        innovation_keywords = [
            "new", "novel", "innovative", "first", "revolutionary", "breakthrough",
            "disrupted", "transform", "reinvent", "unprecedented"
        ]
        
        innovation_score = 0.0
        text_corpus = f"{concept_document.concept_description} "
        
        for story in concept_document.core_stories:
            text_corpus += f"{story.enhanced_experience} {story.value_delivered} "
        
        for enhancement in concept_document.enhancements:
            text_corpus += f"{enhancement.description} "
        
        text_corpus = text_corpus.lower()
        innovation_mentions = sum(1 for keyword in innovation_keywords if keyword in text_corpus)
        
        # Scale innovation score
        innovation_score = min(innovation_mentions / 3.0, 1.0) * 10.0
        
        return innovation_score
    
    def _calculate_analysis_confidence(
        self,
        concept_document: ConceptDocument,
        stakeholder_complexity: float,
        story_richness: float
    ) -> float:
        """Calculate confidence in complexity analysis."""
        
        confidence_factors = []
        
        # Story completeness factor
        story_completeness = story_richness / 10.0
        confidence_factors.append(story_completeness)
        
        # Concept maturity factor
        confidence_factors.append(concept_document.concept_maturity)
        
        # Validation level factor
        validation_scores = {
            "foundation": 0.6,
            "stress_tested": 0.8,
            "enhanced": 1.0
        }
        validation_confidence = validation_scores.get(concept_document.validation_level.value, 0.5)
        confidence_factors.append(validation_confidence)
        
        # Challenge resolution factor
        challenge_confidence = min(len(concept_document.challenges_resolved) / 3.0, 1.0)
        confidence_factors.append(challenge_confidence)
        
        # Narrative confidence factor
        confidence_factors.append(concept_document.narrative_confidence)
        
        # Calculate weighted average
        overall_confidence = np.mean(confidence_factors)
        
        return min(overall_confidence, 1.0)
    
    def _create_project_context(
        self,
        concept_document: ConceptDocument,
        constraints: Dict[str, Any]
    ) -> ProjectContext:
        """Create project context from concept document and constraints."""
        
        return ProjectContext(
            project_name=concept_document.concept_name,
            project_description=concept_document.concept_description,
            stakeholder_count=len(concept_document.stakeholders.all()),
            stakeholder_types=[s.stakeholder_type.value for s in concept_document.stakeholders.all()],
            technical_complexity=int(concept_document.technical_complexity),
            innovation_level=self._estimate_innovation_level(concept_document) / 10.0,
            timeline_constraints=constraints.get("timeline"),
            regulatory_requirements=constraints.get("regulatory", []),
            scalability_requirements=constraints.get("scalability", "moderate")
        )
    
    async def _generate_mode_recommendation(
        self,
        complexity_analysis: ComplexityAnalysis,
        user_preferences: UserPreferences,
        project_context: ProjectContext
    ) -> DevelopmentRecommendation:
        """Generate development mode recommendation with detailed rationale."""
        
        # Calculate mode scores
        mode_scores = {}
        
        # Lightweight mode scoring
        lightweight_score = self._score_lightweight_mode(
            complexity_analysis, user_preferences, project_context
        )
        mode_scores[ExecutionMode.LIGHTWEIGHT] = lightweight_score
        
        # Knowledge graph mode scoring
        kg_score = self._score_knowledge_graph_mode(
            complexity_analysis, user_preferences, project_context
        )
        mode_scores[ExecutionMode.KNOWLEDGE_GRAPH] = kg_score
        
        # Hybrid mode scoring
        hybrid_score = self._score_hybrid_mode(
            complexity_analysis, user_preferences, project_context
        )
        mode_scores[ExecutionMode.HYBRID] = hybrid_score
        
        # Creative mode scoring
        creative_score = self._score_creative_mode(
            complexity_analysis, user_preferences, project_context
        )
        mode_scores[ExecutionMode.CREATIVE] = creative_score
        
        # Select best mode
        recommended_mode = max(mode_scores, key=mode_scores.get)
        confidence_score = mode_scores[recommended_mode]
        
        # Generate rationale
        rationale = self._generate_recommendation_rationale(
            recommended_mode, complexity_analysis, user_preferences, mode_scores
        )
        
        # Identify alternatives
        sorted_modes = sorted(mode_scores.items(), key=lambda x: x[1], reverse=True)
        alternative_modes = [mode for mode, score in sorted_modes[1:3]]
        
        # Get cross-project patterns
        relevant_patterns = await self._get_relevant_patterns(complexity_analysis, recommended_mode)
        
        # Generate validation requirements
        validation_requirements = self._generate_validation_requirements(
            recommended_mode, complexity_analysis
        )
        
        # Estimate timeline
        estimated_timeline = self._estimate_timeline(
            recommended_mode, complexity_analysis, project_context
        )
        
        # Identify risks and mitigations
        risks, mitigations = self._identify_risks_and_mitigations(
            recommended_mode, complexity_analysis, project_context
        )
        
        # Success factors
        success_factors = self._identify_success_factors(
            recommended_mode, complexity_analysis, user_preferences
        )
        
        recommendation = DevelopmentRecommendation(
            recommended_mode=recommended_mode,
            confidence_score=confidence_score,
            rationale=rationale,
            alternative_modes=alternative_modes,
            validation_requirements=validation_requirements,
            estimated_timeline=estimated_timeline,
            identified_risks=risks,
            mitigation_strategies=mitigations,
            success_factors=success_factors,
            relevant_patterns=[p.pattern_name for p in relevant_patterns]
        )
        
        return recommendation
    
    def _score_lightweight_mode(
        self,
        complexity_analysis: ComplexityAnalysis,
        user_preferences: UserPreferences,
        project_context: ProjectContext
    ) -> float:
        """Score lightweight mode appropriateness."""
        
        score = 0.5  # Base score
        
        # Favor for low complexity
        if complexity_analysis.complexity_score <= 4.0:
            score += 0.3
        elif complexity_analysis.complexity_score <= 6.0:
            score += 0.1
        else:
            score -= 0.2
        
        # Favor for speed preference
        if user_preferences.speed_vs_quality > 0.6:
            score += 0.2
        
        # Favor for high user experience
        if user_preferences.ai_experience_level >= 7:
            score += 0.1
        
        # Favor for small teams
        if user_preferences.team_size <= 3:
            score += 0.1
        
        # Penalty for high uncertainty
        if complexity_analysis.uncertainty_level > 7.0:
            score -= 0.2
        
        return max(min(score, 1.0), 0.0)
    
    def _score_knowledge_graph_mode(
        self,
        complexity_analysis: ComplexityAnalysis,
        user_preferences: UserPreferences,
        project_context: ProjectContext
    ) -> float:
        """Score knowledge graph mode appropriateness."""
        
        score = 0.3  # Lower base score (more resource intensive)
        
        # Strong favor for high complexity
        if complexity_analysis.complexity_score >= 7.0:
            score += 0.4
        elif complexity_analysis.complexity_score >= 5.0:
            score += 0.2
        
        # Favor for enterprise validation needs
        if user_preferences.validation_level == "enterprise":
            score += 0.3
        elif user_preferences.validation_level == "high":
            score += 0.2
        
        # Favor for high confidence requirements
        if user_preferences.confidence_threshold >= 0.9:
            score += 0.2
        
        # Favor for quality over speed
        if user_preferences.speed_vs_quality < 0.4:
            score += 0.2
        
        # Favor for many stakeholders
        if project_context.stakeholder_count >= 5:
            score += 0.2
        
        # Penalty for tight time constraints
        if user_preferences.time_constraints == "tight":
            score -= 0.2
        
        return max(min(score, 1.0), 0.0)
    
    def _score_hybrid_mode(
        self,
        complexity_analysis: ComplexityAnalysis,
        user_preferences: UserPreferences,
        project_context: ProjectContext
    ) -> float:
        """Score hybrid mode appropriateness."""
        
        score = 0.6  # Higher base score (balanced approach)
        
        # Favor for moderate complexity
        if 4.0 <= complexity_analysis.complexity_score <= 7.0:
            score += 0.3
        
        # Favor for balanced preferences
        if 0.3 <= user_preferences.speed_vs_quality <= 0.7:
            score += 0.2
        
        # Favor for moderate team size
        if 2 <= user_preferences.team_size <= 5:
            score += 0.1
        
        # Favor for standard validation needs
        if user_preferences.validation_level == "standard":
            score += 0.1
        
        # Favor for moderate risk tolerance
        if 0.3 <= user_preferences.risk_tolerance <= 0.7:
            score += 0.1
        
        return max(min(score, 1.0), 0.0)
    
    def _score_creative_mode(
        self,
        complexity_analysis: ComplexityAnalysis,
        user_preferences: UserPreferences,
        project_context: ProjectContext
    ) -> float:
        """Score creative mode appropriateness."""
        
        score = 0.2  # Lower base score (experimental)
        
        # Strong favor for high innovation
        if project_context.innovation_level >= 0.7:
            score += 0.4
        elif project_context.innovation_level >= 0.5:
            score += 0.2
        
        # Favor for experimentation willingness
        if user_preferences.experimentation_willingness >= 0.7:
            score += 0.3
        
        # Favor for learning mode
        if user_preferences.learning_mode:
            score += 0.2
        
        # Favor for high risk tolerance
        if user_preferences.risk_tolerance >= 0.7:
            score += 0.2
        
        # Favor for solo developers (more flexibility)
        if user_preferences.team_size == 1:
            score += 0.1
        
        # Penalty for tight constraints
        if user_preferences.time_constraints == "tight" or user_preferences.budget_constraints == "tight":
            score -= 0.2
        
        return max(min(score, 1.0), 0.0)
    
    def _generate_recommendation_rationale(
        self,
        recommended_mode: ExecutionMode,
        complexity_analysis: ComplexityAnalysis,
        user_preferences: UserPreferences,
        mode_scores: Dict[ExecutionMode, float]
    ) -> str:
        """Generate human-readable rationale for recommendation."""
        
        rationale_parts = []
        
        # Mode-specific rationale
        if recommended_mode == ExecutionMode.LIGHTWEIGHT:
            rationale_parts.append(f"Lightweight mode recommended for moderate complexity ({complexity_analysis.complexity_score:.1f}/10)")
            if user_preferences.speed_vs_quality > 0.6:
                rationale_parts.append("matches your speed preference")
            if complexity_analysis.uncertainty_level < 5.0:
                rationale_parts.append("low uncertainty allows human-guided approach")
                
        elif recommended_mode == ExecutionMode.KNOWLEDGE_GRAPH:
            rationale_parts.append(f"Knowledge graph mode recommended for high complexity ({complexity_analysis.complexity_score:.1f}/10)")
            if user_preferences.confidence_threshold >= 0.9:
                rationale_parts.append("meets your high confidence requirements")
            if complexity_analysis.stakeholder_complexity > 6.0:
                rationale_parts.append("complex stakeholder ecosystem benefits from validation")
                
        elif recommended_mode == ExecutionMode.HYBRID:
            rationale_parts.append(f"Hybrid mode balances complexity ({complexity_analysis.complexity_score:.1f}/10) with efficiency")
            rationale_parts.append("provides validation where needed while maintaining development speed")
            
        elif recommended_mode == ExecutionMode.CREATIVE:
            rationale_parts.append("Creative mode enables innovation experimentation")
            if user_preferences.experimentation_willingness > 0.6:
                rationale_parts.append("matches your willingness to experiment")
        
        # Confidence explanation
        confidence = mode_scores[recommended_mode]
        if confidence > 0.8:
            rationale_parts.append(f"High confidence ({confidence:.1%}) in this recommendation")
        elif confidence > 0.6:
            rationale_parts.append(f"Moderate confidence ({confidence:.1%}) - consider alternatives")
        else:
            rationale_parts.append(f"Lower confidence ({confidence:.1%}) - manual selection recommended")
        
        return ". ".join(rationale_parts) + "."
    
    async def _get_relevant_patterns(
        self,
        complexity_analysis: ComplexityAnalysis,
        mode: ExecutionMode
    ) -> List[CrossProjectPattern]:
        """Get relevant cross-project patterns for current context."""
        
        relevant_patterns = []
        
        for pattern in self.patterns:
            # Check complexity range
            complexity_range = pattern.complexity_range
            if (complexity_range[0] <= complexity_analysis.complexity_score <= complexity_range[1] and
                mode in pattern.applicable_modes):
                relevant_patterns.append(pattern)
        
        # Sort by success rate
        relevant_patterns.sort(key=lambda p: p.success_rate, reverse=True)
        
        return relevant_patterns[:3]  # Top 3 most relevant patterns
    
    def _generate_validation_requirements(
        self,
        mode: ExecutionMode,
        complexity_analysis: ComplexityAnalysis
    ) -> List[str]:
        """Generate validation requirements based on mode and complexity."""
        
        requirements = []
        
        if mode == ExecutionMode.LIGHTWEIGHT:
            requirements.extend([
                "Human review of core features",
                "Stakeholder feedback validation",
                "Basic testing coverage"
            ])
            
        elif mode == ExecutionMode.KNOWLEDGE_GRAPH:
            requirements.extend([
                "Multi-layer validation with 92%+ confidence",
                "API existence verification through knowledge graphs",
                "Hallucination detection on generated code",
                "Cross-project pattern validation",
                "Comprehensive testing suite"
            ])
            
        elif mode == ExecutionMode.HYBRID:
            requirements.extend([
                "Adaptive validation based on feature complexity",
                "Knowledge graph validation for critical components",
                "Human review for creative elements",
                "Stakeholder story alignment verification"
            ])
            
        elif mode == ExecutionMode.CREATIVE:
            requirements.extend([
                "Innovation pattern validation",
                "Creative breakthrough verification",
                "Community feedback integration",
                "Experimental approach documentation"
            ])
        
        # Add complexity-based requirements
        if complexity_analysis.complexity_score > 7.0:
            requirements.append("Enterprise-grade validation protocols")
        
        if complexity_analysis.stakeholder_complexity > 6.0:
            requirements.append("Multi-stakeholder acceptance testing")
        
        return requirements
    
    def _estimate_timeline(
        self,
        mode: ExecutionMode,
        complexity_analysis: ComplexityAnalysis,
        project_context: ProjectContext
    ) -> str:
        """Estimate development timeline based on mode and complexity."""
        
        # Base timeline by mode
        base_timelines = {
            ExecutionMode.LIGHTWEIGHT: 5,      # days
            ExecutionMode.HYBRID: 10,          # days
            ExecutionMode.KNOWLEDGE_GRAPH: 20, # days
            ExecutionMode.CREATIVE: 15         # days
        }
        
        base_days = base_timelines[mode]
        
        # Adjust for complexity
        complexity_multiplier = 1.0 + (complexity_analysis.complexity_score / 10.0)
        adjusted_days = base_days * complexity_multiplier
        
        # Adjust for stakeholder count
        if project_context.stakeholder_count > 5:
            adjusted_days *= 1.2
        
        # Convert to timeline description
        if adjusted_days <= 7:
            return "5-7 days"
        elif adjusted_days <= 14:
            return "1-2 weeks"
        elif adjusted_days <= 30:
            return "2-4 weeks"
        else:
            return "1-2 months"
    
    def _identify_risks_and_mitigations(
        self,
        mode: ExecutionMode,
        complexity_analysis: ComplexityAnalysis,
        project_context: ProjectContext
    ) -> Tuple[List[str], List[str]]:
        """Identify risks and mitigation strategies."""
        
        risks = []
        mitigations = []
        
        # Mode-specific risks
        if mode == ExecutionMode.LIGHTWEIGHT:
            if complexity_analysis.complexity_score > 6.0:
                risks.append("May miss complex validation requirements")
                mitigations.append("Regular complexity reassessment with upgrade path")
                
        elif mode == ExecutionMode.KNOWLEDGE_GRAPH:
            risks.append("Higher resource requirements")
            mitigations.append("Phased implementation with core features first")
            
        elif mode == ExecutionMode.CREATIVE:
            risks.append("Experimental approach may not scale")
            mitigations.append("Proof-of-concept validation before full implementation")
        
        # Complexity-based risks
        if complexity_analysis.uncertainty_level > 7.0:
            risks.append("High uncertainty may impact delivery")
            mitigations.append("Iterative validation with frequent stakeholder feedback")
        
        if complexity_analysis.stakeholder_complexity > 6.0:
            risks.append("Stakeholder coordination challenges")
            mitigations.append("Dedicated stakeholder management and clear communication protocols")
        
        return risks, mitigations
    
    def _identify_success_factors(
        self,
        mode: ExecutionMode,
        complexity_analysis: ComplexityAnalysis,
        user_preferences: UserPreferences
    ) -> List[str]:
        """Identify key success factors for the recommended approach."""
        
        success_factors = []
        
        # Universal success factors
        success_factors.extend([
            "Clear stakeholder story alignment",
            "Regular progress validation",
            "Adaptive approach based on learning"
        ])
        
        # Mode-specific success factors
        if mode == ExecutionMode.LIGHTWEIGHT:
            success_factors.extend([
                "Strong human oversight and decision-making",
                "Effective stakeholder communication",
                "Rapid iteration and feedback cycles"
            ])
            
        elif mode == ExecutionMode.KNOWLEDGE_GRAPH:
            success_factors.extend([
                "Comprehensive validation at each step",
                "Knowledge graph accuracy and completeness",
                "Cross-project learning integration"
            ])
            
        elif mode == ExecutionMode.HYBRID:
            success_factors.extend([
                "Smart delegation between human and AI",
                "Context-aware validation selection",
                "Balanced speed and quality optimization"
            ])
            
        elif mode == ExecutionMode.CREATIVE:
            success_factors.extend([
                "Community feedback and collaboration",
                "Innovation pattern recognition",
                "Experimental approach documentation"
            ])
        
        # Complexity-based success factors
        if complexity_analysis.complexity_score > 7.0:
            success_factors.append("Enterprise-grade project management")
        
        if user_preferences.team_size > 3:
            success_factors.append("Effective team coordination and communication")
        
        return success_factors
    
    async def _load_historical_data(self):
        """Load historical decisions and patterns for learning."""
        try:
            # Load decisions
            for decision_file in self.decision_storage.glob("*.json"):
                try:
                    with open(decision_file, 'r') as f:
                        decision_data = json.load(f)
                        decision = AdaptiveDecision(**decision_data)
                        self.decisions.append(decision)
                except Exception as e:
                    self.logger.warning("Failed to load decision", file=str(decision_file), error=str(e))
            
            # Load patterns
            for pattern_file in self.pattern_storage.glob("*.json"):
                try:
                    with open(pattern_file, 'r') as f:
                        pattern_data = json.load(f)
                        pattern = CrossProjectPattern(**pattern_data)
                        self.patterns.append(pattern)
                except Exception as e:
                    self.logger.warning("Failed to load pattern", file=str(pattern_file), error=str(e))
                    
            self.logger.info(
                "Historical data loaded",
                decisions_count=len(self.decisions),
                patterns_count=len(self.patterns)
            )
            
        except Exception as e:
            self.logger.error("Failed to load historical data", error=str(e))
    
    async def _store_decision(self, decision: AdaptiveDecision):
        """Store decision for cross-project learning."""
        try:
            decision_file = self.decision_storage / f"{decision.decision_id}.json"
            with open(decision_file, 'w') as f:
                json.dump(decision.dict(), f, indent=2, default=str)
            
            self.decisions.append(decision)
            self.logger.info("Decision stored", decision_id=decision.decision_id)
            
        except Exception as e:
            self.logger.error("Failed to store decision", error=str(e))
    
    async def _update_cross_project_patterns(self):
        """Update cross-project patterns based on historical decisions."""
        # This would implement machine learning analysis of decisions
        # to identify successful patterns - placeholder for now
        self.logger.info("Cross-project patterns updated")


# Export main classes
__all__ = ["AdaptiveIntelligenceEngine", "ExecutionMode", "ComplexityAnalysis"]