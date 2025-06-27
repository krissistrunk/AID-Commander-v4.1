#!/usr/bin/env python3
"""
ConceptCraft AI Core Implementation

Story-driven product concept development through systematic collaborative storytelling.
Implements the 3-level process: Foundation → Stress-Testing → Enhancement.
"""

import asyncio
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

import structlog
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text

from .models import (
    ConceptDocument,
    ConversationState,
    StakeholderStory,
    StakeholderEcosystem,
    StakeholderType,
    ChallengeResolution,
    Enhancement,
    ValidationLevel
)

logger = structlog.get_logger(__name__)


class ConceptCraftAI:
    """
    ConceptCraft AI: Story-Driven Product Concept Development System
    
    Transforms vague ideas into PRD-ready concepts through systematic collaborative
    storytelling and stakeholder discovery using a 3-level adaptive process.
    """
    
    def __init__(self):
        self.logger = logger.bind(component="ConceptCraftAI")
        self.session_storage = Path.home() / ".aid_genesis" / "conceptcraft_sessions"
        self.session_storage.mkdir(parents=True, exist_ok=True)
        
        # AI behavior configuration
        self.collaboration_principles = {
            "always_offer_options": True,
            "never_leave_blank_questions": True,
            "incremental_building": True,
            "specific_over_abstract": True,
            "story_coherence": True
        }
        
        # Level transition criteria
        self.level_criteria = {
            1: {"min_stakeholders": 2, "min_stories": 2},
            2: {"min_challenges": 2, "min_resolutions": 2},
            3: {"min_enhancements": 1, "concept_maturity": 0.7}
        }
    
    async def initialize(self) -> bool:
        """Initialize ConceptCraft AI system."""
        try:
            self.logger.info("Initializing ConceptCraft AI")
            # Any initialization logic here
            return True
        except Exception as e:
            self.logger.error("ConceptCraft AI initialization failed", error=str(e))
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on ConceptCraft AI system."""
        return {
            "status": "available",
            "session_storage": str(self.session_storage),
            "storage_accessible": self.session_storage.exists(),
            "principles_loaded": len(self.collaboration_principles) > 0
        }
    
    async def develop_concept(
        self,
        initial_idea: str,
        interactive_mode: bool = True,
        console: Optional[Console] = None,
        user_mode: str = "adaptive"
    ) -> Optional[ConceptDocument]:
        """
        Main concept development workflow through 3-level collaborative process.
        
        Args:
            initial_idea: User's initial idea or problem description
            interactive_mode: Whether to use interactive CLI prompts
            console: Rich console for output (if interactive)
            user_mode: User interaction mode (creative, enterprise, startup, adaptive)
        
        Returns:
            ConceptDocument if successful, None if incomplete
        """
        
        # Initialize conversation state
        session_id = str(uuid.uuid4())
        conversation_state = ConversationState(
            session_id=session_id,
            user_mode=user_mode
        )
        
        if console:
            console.print(Panel(
                "[bold cyan]🧠 ConceptCraft AI: Collaborative Concept Development[/bold cyan]\n\n"
                "I'll guide you through a 3-level collaborative storytelling process:\n"
                "• [green]Level 1: Story Foundation[/green] - Discover stakeholders and build narratives\n"
                "• [yellow]Level 2: Story Stress-Testing[/yellow] - Challenge scenarios and solutions\n" 
                "• [magenta]Level 3: Story Enhancement[/magenta] - Innovation and amplification\n\n"
                "We'll build your concept together through collaborative thinking!",
                title="Welcome to ConceptCraft AI"
            ))
        
        try:
            # Level 1: Story Foundation
            concept_document = await self._level_1_story_foundation(
                initial_idea, conversation_state, console
            )
            
            if not concept_document:
                return None
            
            conversation_state.concept_document = concept_document
            conversation_state.stakeholder_discovery_complete = True
            
            # Level 2: Story Stress-Testing
            if self._should_advance_to_level_2(conversation_state, console):
                concept_document = await self._level_2_stress_testing(
                    concept_document, conversation_state, console
                )
                
                if concept_document:
                    conversation_state.concept_document = concept_document
                    conversation_state.challenge_stress_testing_complete = True
            
            # Level 3: Story Enhancement
            if self._should_advance_to_level_3(conversation_state, console):
                concept_document = await self._level_3_enhancement(
                    concept_document, conversation_state, console
                )
                
                if concept_document:
                    conversation_state.concept_document = concept_document
                    conversation_state.enhancement_exploration_complete = True
            
            # Finalize concept
            if concept_document:
                concept_document.calculate_maturity_score()
                concept_document.calculate_prd_readiness()
                
                # Save session
                await self._save_session(conversation_state)
                
                if console:
                    self._display_concept_completion(concept_document, console)
            
            return concept_document
            
        except Exception as e:
            self.logger.error("Concept development failed", error=str(e))
            if console:
                console.print(f"[red]Concept development encountered an error: {str(e)}[/red]")
            return None
    
    async def _level_1_story_foundation(
        self,
        initial_idea: str,
        conversation_state: ConversationState,
        console: Optional[Console]
    ) -> Optional[ConceptDocument]:
        """
        Level 1: Story Foundation - Co-Creative Discovery
        
        Build validated stakeholder narratives through collaborative storytelling.
        """
        
        if console:
            console.print(Panel(
                "[bold green]Level 1: Story Foundation - Co-Creative Discovery[/bold green]\n\n"
                "Let's discover your stakeholders through guided options and examples.\n"
                "We'll co-create user stories with specific scenarios and build a\n"
                "comprehensive narrative foundation incrementally.",
                title="🎯 Building Story Foundation"
            ))
        
        # Create initial concept
        concept_id = str(uuid.uuid4())
        concept_name = await self._extract_concept_name(initial_idea, console)
        concept_description = await self._refine_concept_description(initial_idea, console)
        
        concept_document = ConceptDocument(
            concept_id=concept_id,
            concept_name=concept_name,
            concept_description=concept_description,
            validation_level=ValidationLevel.FOUNDATION
        )
        
        # Stakeholder discovery through collaborative storytelling
        stakeholder_ecosystem = await self._discover_stakeholder_ecosystem(
            initial_idea, concept_name, console
        )
        
        concept_document.stakeholders = stakeholder_ecosystem
        concept_document.core_stories = stakeholder_ecosystem.primary_stakeholders[:3]
        
        # Validate story foundation
        if len(concept_document.core_stories) >= 2:
            conversation_state.update_progress(1, 1.0)
            return concept_document
        else:
            if console:
                console.print("[yellow]Story foundation incomplete. Need at least 2 core stakeholder stories.[/yellow]")
            return None
    
    async def _level_2_stress_testing(
        self,
        concept_document: ConceptDocument,
        conversation_state: ConversationState,
        console: Optional[Console]
    ) -> Optional[ConceptDocument]:
        """
        Level 2: Story Stress-Testing - Systematic Challenge
        
        Generate specific challenge scenarios and guide collaborative problem-solving.
        """
        
        if console:
            console.print(Panel(
                "[bold yellow]Level 2: Story Stress-Testing - Systematic Challenge[/bold yellow]\n\n"
                "Now I'll challenge your concept with 'what could go wrong' scenarios.\n"
                "We'll test stakeholder conflicts, edge cases, and competitive responses\n"
                "to strengthen your concept through challenge resolution.",
                title="🎯 Stress-Testing Your Concept"
            ))
        
        # Generate challenge scenarios based on stakeholder stories
        challenge_scenarios = await self._generate_challenge_scenarios(concept_document, console)
        
        challenges_resolved = []
        for i, scenario in enumerate(challenge_scenarios[:3], 1):  # Limit to 3 main challenges
            if console:
                console.print(f"\n[bold]Challenge Scenario #{i}:[/bold]")
                console.print(scenario["description"])
            
            resolution = await self._collaborate_on_challenge_resolution(
                scenario, concept_document, console
            )
            
            if resolution:
                challenges_resolved.append(resolution)
                # Update concept based on resolution
                concept_document = await self._evolve_concept_from_resolution(
                    concept_document, resolution
                )
        
        concept_document.challenges_resolved = challenges_resolved
        concept_document.validation_level = ValidationLevel.STRESS_TESTED
        
        if len(challenges_resolved) >= 2:
            conversation_state.update_progress(2, 1.0)
            return concept_document
        else:
            if console:
                console.print("[yellow]Stress-testing incomplete. Need at least 2 resolved challenges.[/yellow]")
            return concept_document  # Return partial progress
    
    async def _level_3_enhancement(
        self,
        concept_document: ConceptDocument,
        conversation_state: ConversationState,
        console: Optional[Console]
    ) -> Optional[ConceptDocument]:
        """
        Level 3: Story Enhancement - Innovation Amplification
        
        Collaborate on enhanced success scenarios and network effects.
        """
        
        if console:
            console.print(Panel(
                "[bold magenta]Level 3: Story Enhancement - Innovation Amplification[/bold magenta]\n\n"
                "Let's make your concept extraordinary! We'll explore network effects,\n"
                "systemic improvements, and innovation opportunities that amplify\n"
                "your concept toward optimal outcomes.",
                title="🚀 Amplifying Your Concept"
            ))
        
        # Generate enhancement opportunities
        enhancement_opportunities = await self._generate_enhancement_opportunities(
            concept_document, console
        )
        
        enhancements = []
        for opportunity in enhancement_opportunities[:2]:  # Focus on top 2 enhancements
            enhancement = await self._develop_enhancement(
                opportunity, concept_document, console
            )
            
            if enhancement:
                enhancements.append(enhancement)
        
        concept_document.enhancements = enhancements
        concept_document.validation_level = ValidationLevel.ENHANCED
        
        if len(enhancements) >= 1:
            conversation_state.update_progress(3, 1.0)
            return concept_document
        else:
            if console:
                console.print("[yellow]Enhancement incomplete. No enhancements developed.[/yellow]")
            return concept_document  # Return partial progress
    
    async def _extract_concept_name(self, initial_idea: str, console: Optional[Console]) -> str:
        """Extract or generate concept name from initial idea."""
        # Simple extraction logic - in real implementation, would use NLP
        words = initial_idea.split()
        if len(words) <= 3:
            suggested_name = " ".join(words).title()
        else:
            # Extract key nouns or create portmanteau
            suggested_name = "YourConcept"  # Placeholder
        
        if console:
            concept_name = Prompt.ask(
                f"What should we call your concept? (suggested: {suggested_name})",
                default=suggested_name
            )
            return concept_name
        else:
            return suggested_name
    
    async def _refine_concept_description(self, initial_idea: str, console: Optional[Console]) -> str:
        """Refine and clarify the core concept description."""
        if console:
            console.print(f"\n[bold]Initial idea:[/bold] {initial_idea}")
            refined_description = Prompt.ask(
                "How would you describe the core value this concept provides?",
                default=initial_idea
            )
            return refined_description
        else:
            return initial_idea
    
    async def _discover_stakeholder_ecosystem(
        self,
        initial_idea: str,
        concept_name: str,
        console: Optional[Console]
    ) -> StakeholderEcosystem:
        """Discover stakeholder ecosystem through collaborative exploration."""
        
        ecosystem = StakeholderEcosystem()
        
        if console:
            console.print(f"\n[bold]Let's discover who would be affected by {concept_name}.[/bold]")
            
            # Primary stakeholder discovery
            console.print("\n[bold cyan]Primary Stakeholder Discovery[/bold cyan]")
            console.print("Who is the main person this concept serves?")
            
            primary_options = [
                "End user who directly benefits from the solution",
                "Business decision-maker who would purchase/adopt",
                "Professional who would use this in their work",
                "Consumer with a specific problem to solve"
            ]
            
            for i, option in enumerate(primary_options, 1):
                console.print(f"{i}) {option}")
            
            choice = Prompt.ask("Choose the option that best fits, or describe someone different", default="1")
            
            # Create primary stakeholder story
            primary_stakeholder = await self._create_stakeholder_story(
                choice, StakeholderType.PRIMARY, concept_name, console
            )
            
            if primary_stakeholder:
                ecosystem.primary_stakeholders.append(primary_stakeholder)
            
            # Secondary stakeholder discovery
            if Confirm.ask("\nShould we explore other people affected by this concept?"):
                secondary_stakeholder = await self._discover_secondary_stakeholder(
                    primary_stakeholder, concept_name, console
                )
                
                if secondary_stakeholder:
                    ecosystem.secondary_stakeholders.append(secondary_stakeholder)
        
        return ecosystem
    
    async def _create_stakeholder_story(
        self,
        stakeholder_description: str,
        stakeholder_type: StakeholderType,
        concept_name: str,
        console: Optional[Console]
    ) -> Optional[StakeholderStory]:
        """Create detailed stakeholder story through collaborative building."""
        
        if console:
            # Get stakeholder name
            stakeholder_name = Prompt.ask("What should we call this person?", default="Alex")
            
            # Build current situation
            console.print(f"\n[bold]Let's build {stakeholder_name}'s story:[/bold]")
            current_situation = Prompt.ask(
                f"What's {stakeholder_name}'s current situation/challenge?"
            )
            
            # Pain points
            pain_points = []
            console.print(f"\nWhat specific problems does {stakeholder_name} face?")
            for i in range(3):
                pain_point = Prompt.ask(f"Pain point {i+1} (or press Enter to skip)", default="")
                if pain_point:
                    pain_points.append(pain_point)
                else:
                    break
            
            # Enhanced experience with concept
            enhanced_experience = Prompt.ask(
                f"\nHow does {concept_name} transform {stakeholder_name}'s experience?"
            )
            
            # Value delivered
            value_delivered = Prompt.ask(
                f"What specific value does {stakeholder_name} receive?"
            )
            
            return StakeholderStory(
                stakeholder_name=stakeholder_name,
                stakeholder_type=stakeholder_type,
                role_description=stakeholder_description,
                current_situation=current_situation,
                pain_points=pain_points,
                enhanced_experience=enhanced_experience,
                value_delivered=value_delivered
            )
        
        return None
    
    async def _discover_secondary_stakeholder(
        self,
        primary_stakeholder: StakeholderStory,
        concept_name: str,
        console: Optional[Console]
    ) -> Optional[StakeholderStory]:
        """Discover secondary stakeholders in the ecosystem."""
        
        if console:
            console.print(f"\n[bold cyan]Secondary Stakeholder Discovery[/bold cyan]")
            console.print(f"Who else is affected when {primary_stakeholder.stakeholder_name} uses {concept_name}?")
            
            secondary_options = [
                f"Colleagues/team members who work with {primary_stakeholder.stakeholder_name}",
                f"Manager/supervisor who cares about {primary_stakeholder.stakeholder_name}'s performance",
                f"Family/friends who are impacted by {primary_stakeholder.stakeholder_name}'s experience",
                f"Service provider who supports {primary_stakeholder.stakeholder_name}",
                "Someone completely different"
            ]
            
            for i, option in enumerate(secondary_options, 1):
                console.print(f"{i}) {option}")
            
            choice = Prompt.ask("Choose an option or describe someone different", default="1")
            
            return await self._create_stakeholder_story(
                choice, StakeholderType.SECONDARY, concept_name, console
            )
        
        return None
    
    async def _generate_challenge_scenarios(
        self,
        concept_document: ConceptDocument,
        console: Optional[Console]
    ) -> List[Dict[str, Any]]:
        """Generate challenge scenarios for stress-testing."""
        
        scenarios = []
        
        # Common challenge categories
        challenge_types = [
            {
                "type": "adoption_resistance",
                "description": f"Some stakeholders resist adopting {concept_document.concept_name}",
                "template": "What if {stakeholder} finds {concept} difficult to use or unnecessary?"
            },
            {
                "type": "scale_problems", 
                "description": f"{concept_document.concept_name} faces scaling challenges",
                "template": "What happens when {concept} becomes popular but can't handle demand?"
            },
            {
                "type": "competitive_response",
                "description": f"Competitors respond to {concept_document.concept_name}",
                "template": "How does {concept} remain valuable when competitors copy the approach?"
            }
        ]
        
        # Generate specific scenarios based on stakeholder stories
        for challenge_type in challenge_types:
            if concept_document.core_stories:
                stakeholder = concept_document.core_stories[0]
                scenario = {
                    "id": str(uuid.uuid4()),
                    "type": challenge_type["type"],
                    "description": f"Challenge: {stakeholder.stakeholder_name} encounters {challenge_type['description'].lower()}. "
                                 f"Specific scenario: {challenge_type['template'].format(stakeholder=stakeholder.stakeholder_name, concept=concept_document.concept_name)}"
                }
                scenarios.append(scenario)
        
        return scenarios
    
    async def _collaborate_on_challenge_resolution(
        self,
        scenario: Dict[str, Any],
        concept_document: ConceptDocument,
        console: Optional[Console]
    ) -> Optional[ChallengeResolution]:
        """Collaborate with user to resolve challenge scenario."""
        
        if console:
            console.print(f"\n[yellow]{scenario['description']}[/yellow]")
            
            console.print("\nHow should your concept handle this challenge?")
            console.print("If you're not sure, here are some solution approaches:")
            
            # Offer solution direction options
            solution_options = [
                "Modify the concept to prevent this problem",
                "Add features that address this specific scenario",
                "Change the target audience to avoid this issue", 
                "Accept this as a limitation and work around it"
            ]
            
            for i, option in enumerate(solution_options, 1):
                console.print(f"{i}) {option}")
            
            approach = Prompt.ask("Choose an approach or describe your solution")
            
            solution_description = Prompt.ask(
                "Describe specifically how your concept addresses this challenge"
            )
            
            concept_evolution = Prompt.ask(
                "How does your concept change or improve based on this solution?"
            )
            
            return ChallengeResolution(
                challenge_id=scenario["id"],
                challenge_scenario=scenario["description"],
                affected_stakeholders=[story.stakeholder_name for story in concept_document.core_stories],
                solution_approach=solution_description,
                concept_evolution=concept_evolution,
                challenge_category=scenario["type"],
                confidence_improvement=0.1  # Each resolved challenge adds confidence
            )
        
        return None
    
    async def _evolve_concept_from_resolution(
        self,
        concept_document: ConceptDocument,
        resolution: ChallengeResolution
    ) -> ConceptDocument:
        """Evolve concept based on challenge resolution."""
        
        # In a full implementation, this would use the resolution to update
        # concept description, stakeholder stories, etc.
        concept_document.narrative_confidence += resolution.confidence_improvement
        concept_document.concept_description += f" {resolution.concept_evolution}"
        
        return concept_document
    
    async def _generate_enhancement_opportunities(
        self,
        concept_document: ConceptDocument,
        console: Optional[Console]
    ) -> List[Dict[str, Any]]:
        """Generate enhancement opportunities for amplification."""
        
        opportunities = [
            {
                "type": "network_effects",
                "title": "Network Effects",
                "description": f"What if {concept_document.concept_name} becomes more valuable as more people use it?"
            },
            {
                "type": "ecosystem_benefits",
                "title": "Ecosystem Benefits", 
                "description": f"How could {concept_document.concept_name} create win-win outcomes for all stakeholders?"
            },
            {
                "type": "innovation_multipliers",
                "title": "Innovation Opportunities",
                "description": f"What unexpected capabilities could {concept_document.concept_name} enable?"
            }
        ]
        
        return opportunities
    
    async def _develop_enhancement(
        self,
        opportunity: Dict[str, Any],
        concept_document: ConceptDocument,
        console: Optional[Console]
    ) -> Optional[Enhancement]:
        """Develop specific enhancement from opportunity."""
        
        if console:
            console.print(f"\n[bold magenta]{opportunity['title']}[/bold magenta]")
            console.print(opportunity["description"])
            
            enhancement_description = Prompt.ask(
                f"How could we implement {opportunity['title'].lower()} for {concept_document.concept_name}?"
            )
            
            implementation_approach = Prompt.ask(
                "How would this enhancement actually work?"
            )
            
            success_amplification = Prompt.ask(
                "How does this amplify your concept's success?"
            )
            
            return Enhancement(
                enhancement_id=str(uuid.uuid4()),
                enhancement_type=opportunity["type"],
                description=enhancement_description,
                implementation_approach=implementation_approach,
                success_amplification=success_amplification,
                impact_score=0.8,  # Default high impact
                feasibility_score=0.7,  # Default moderate feasibility
                innovation_level=0.9   # Default high innovation
            )
        
        return None
    
    def _should_advance_to_level_2(
        self,
        conversation_state: ConversationState,
        console: Optional[Console]
    ) -> bool:
        """Check if should advance to Level 2 stress-testing."""
        
        if not conversation_state.can_advance_to_level_2():
            return False
        
        if console:
            return Confirm.ask(
                "\n[bold]Your story foundation is solid! Ready to stress-test your concept "
                "with challenge scenarios?[/bold]"
            )
        
        return True
    
    def _should_advance_to_level_3(
        self,
        conversation_state: ConversationState,
        console: Optional[Console]
    ) -> bool:
        """Check if should advance to Level 3 enhancement."""
        
        if not conversation_state.can_advance_to_level_3():
            return False
        
        if console:
            return Confirm.ask(
                "\n[bold]Great work resolving challenges! Ready to explore enhancement "
                "opportunities to make your concept extraordinary?[/bold]"
            )
        
        return True
    
    def _display_concept_completion(self, concept_document: ConceptDocument, console: Console):
        """Display concept completion summary."""
        
        summary = concept_document.get_summary()
        
        completion_table = Table(title=f"🎉 {concept_document.concept_name} - Concept Complete!")
        completion_table.add_column("Aspect", style="cyan")
        completion_table.add_column("Achievement", style="green")
        
        completion_table.add_row("Concept Name", concept_document.concept_name)
        completion_table.add_row("Core Description", concept_document.concept_description[:80] + "...")
        completion_table.add_row("Stakeholders Mapped", f"{summary['stakeholder_count']} stakeholders")
        completion_table.add_row("Stories Developed", f"{summary['core_stories']} core stories")
        completion_table.add_row("Challenges Resolved", f"{summary['challenges_resolved']} challenges")
        completion_table.add_row("Enhancements Added", f"{summary['enhancements']} enhancements")
        completion_table.add_row("Validation Level", summary['validation_level'].title())
        completion_table.add_row("Concept Maturity", f"{summary['maturity_score']:.1%}")
        completion_table.add_row("PRD Readiness", f"{summary['prd_readiness']:.1%}")
        completion_table.add_row("Narrative Confidence", f"{summary['narrative_confidence']:.1%}")
        
        console.print(completion_table)
        
        console.print(Panel(
            "[bold green]✅ Your concept is ready for PRD development![/bold green]\n\n"
            "You now have a story-rich concept document with:\n"
            "• Validated stakeholder narratives\n"
            "• Stress-tested challenge resolutions\n"
            "• Enhancement opportunities for amplification\n"
            "• Clear path to technical requirements\n\n"
            "[bold]Next Steps:[/bold]\n"
            "1. Generate story-enhanced PRD\n"
            "2. Begin development planning\n"
            "3. Use stakeholder stories to guide feature priorities",
            title="🚀 Concept Development Complete"
        ))
    
    async def _save_session(self, conversation_state: ConversationState):
        """Save conversation session for later reference."""
        try:
            session_file = self.session_storage / f"{conversation_state.session_id}.json"
            
            session_data = {
                "session_id": conversation_state.session_id,
                "concept_document": conversation_state.concept_document.dict() if conversation_state.concept_document else None,
                "conversation_state": conversation_state.dict(),
                "saved_at": datetime.now().isoformat()
            }
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
                
            self.logger.info("Session saved", session_id=conversation_state.session_id)
            
        except Exception as e:
            self.logger.error("Failed to save session", error=str(e))


# Export main classes
__all__ = ["ConceptCraftAI", "ConceptDocument", "StakeholderStory", "ChallengeResolution", "Enhancement"]