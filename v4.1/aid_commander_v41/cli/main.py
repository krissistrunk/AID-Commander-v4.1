#!/usr/bin/env python3
"""
AID Commander v4.1 - Enhanced CLI with Knowledge Graph Commands

Main CLI entry point with comprehensive knowledge graph integration,
hallucination detection, and multi-layer validation commands.
"""

import asyncio
import sys
import json
import logging
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
import structlog

# Import v4.1 components
from ..knowledge_graph.graphiti.temporal_engine import AIDGraphitiEngine
from ..knowledge_graph.rag.hybrid_search import HybridRAGSystem
from ..frameworks.pydantic_ai.knowledge_builder import PydanticAIKnowledgeBuilder
from ..validation.multi_layer.validation_engine import MultiLayerValidationEngine
from ..validation.hallucination.detection_engine import HallucinationDetectionEngine
from ..memory_enhanced.graph_memory_bank import GraphEnhancedMemoryBank

# Import v4.0 base CLI
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "v4"))
from aid_commander import AIDCommanderV4

console = Console()
logger = structlog.get_logger(__name__)


class AIDCommanderV41:
    """
    AID Commander v4.1 - Knowledge Graph-Enhanced Development Orchestrator
    
    Provides bulletproof AI development with 92%+ certainty through:
    - Multi-layer validation system
    - AI hallucination detection
    - Knowledge graph intelligence
    - Enhanced memory bank with cross-project learning
    """
    
    def __init__(self):
        self.console = console
        self.v4_commander = None
        
        # v4.1 specific components
        self.graphiti_engine = None
        self.rag_system = None
        self.validation_engine = None
        self.hallucination_detector = None
        self.graph_memory_bank = None
        
        # Configuration
        self.config = self._load_config()
        self.initialized = False
    
    def _load_config(self) -> dict:
        """Load v4.1 configuration"""
        return {
            "neo4j_uri": "bolt://localhost:7687",
            "neo4j_username": "neo4j", 
            "neo4j_password": "aid-commander-v41-secure",
            "redis_url": "redis://localhost:6379",
            "chroma_persist_dir": "./chroma_db",
            "confidence_threshold": 0.92,
            "hallucination_threshold": 0.3
        }
    
    async def initialize(self, project_path: Optional[str] = None) -> bool:
        """Initialize AID Commander v4.1 with all knowledge graph components"""
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            # Initialize base v4.0 commander
            init_task = progress.add_task("Initializing AID Commander v4.0 base...", total=None)
            self.v4_commander = AIDCommanderV4()
            if project_path:
                await self.v4_commander.initialize_project(project_path)
            progress.update(init_task, description="✅ AID Commander v4.0 base initialized")
            
            # Initialize Graphiti temporal engine
            graphiti_task = progress.add_task("Initializing Graphiti temporal engine...", total=None)
            neo4j_config = {
                "uri": self.config["neo4j_uri"],
                "username": self.config["neo4j_username"],
                "password": self.config["neo4j_password"]
            }
            self.graphiti_engine = AIDGraphitiEngine(neo4j_config)
            await self.graphiti_engine.initialize()
            progress.update(graphiti_task, description="✅ Graphiti temporal engine ready")
            
            # Initialize RAG system
            rag_task = progress.add_task("Initializing hybrid RAG system...", total=None)
            chroma_config = {"persist_directory": self.config["chroma_persist_dir"]}
            self.rag_system = HybridRAGSystem(chroma_config, neo4j_config)
            await self.rag_system.initialize()
            progress.update(rag_task, description="✅ Hybrid RAG system ready")
            
            # Initialize graph-enhanced memory bank
            memory_task = progress.add_task("Initializing graph-enhanced memory...", total=None)
            if project_path:
                self.graph_memory_bank = GraphEnhancedMemoryBank(
                    project_path, self.graphiti_engine, None
                )
                await self.graph_memory_bank.initialize()
            progress.update(memory_task, description="✅ Graph-enhanced memory ready")
            
            # Initialize validation engine
            validation_task = progress.add_task("Initializing multi-layer validation...", total=None)
            self.validation_engine = MultiLayerValidationEngine(
                self.graphiti_engine,
                self.rag_system,
                self.graph_memory_bank,
                confidence_threshold=self.config["confidence_threshold"]
            )
            progress.update(validation_task, description="✅ Multi-layer validation ready")
            
            # Initialize hallucination detector
            hallucination_task = progress.add_task("Initializing hallucination detector...", total=None)
            self.hallucination_detector = HallucinationDetectionEngine(
                self.validation_engine,
                self.graphiti_engine,
                self.rag_system
            )
            progress.update(hallucination_task, description="✅ Hallucination detector ready")
        
        self.initialized = True
        
        # Display initialization summary
        self.console.print(Panel.fit(
            "[bold green]🎉 AID Commander v4.1 Initialized Successfully![/bold green]\n\n"
            "✅ Knowledge Graph Intelligence Active\n"
            "✅ Multi-Layer Validation System Online\n"
            "✅ AI Hallucination Detection Ready\n"
            "✅ Enhanced Memory Bank Connected\n\n"
            f"[bold]Confidence Threshold:[/bold] {self.config['confidence_threshold']:.1%}\n"
            f"[bold]Target Success Rate:[/bold] 97%+",
            title="🧠 AID Commander v4.1",
            border_style="green"
        ))
        
        return True


# CLI Groups
@click.group()
@click.version_option(version="4.1.0", prog_name="AID Commander")
@click.pass_context
def cli(ctx):
    """
    🧠 AID Commander v4.1 - Knowledge Graph-Enhanced Development Orchestrator
    
    Transform your development workflow with 92%+ certainty through:
    • Multi-layer validation system
    • AI hallucination detection  
    • Knowledge graph intelligence
    • Enhanced memory bank
    """
    ctx.ensure_object(dict)
    ctx.obj['commander'] = AIDCommanderV41()


@cli.group()
@click.pass_context
def kg(ctx):
    """🧠 Knowledge Graph commands for framework analysis and validation"""
    pass


@cli.group() 
@click.pass_context
def validate(ctx):
    """🔍 Multi-layer validation commands with 92%+ certainty"""
    pass


@cli.group()
@click.pass_context  
def detect(ctx):
    """🚨 Hallucination detection and correction commands"""
    pass


@cli.group()
@click.pass_context
def memory(ctx):
    """🧠 Enhanced memory commands with cross-project learning"""
    pass


# Core Commands
@cli.command()
@click.option('--project-path', '-p', default='.', help='Project directory path')
@click.option('--with-knowledge-graphs', '-kg', is_flag=True, help='Initialize with knowledge graph support')
@click.pass_context
async def init(ctx, project_path: str, with_knowledge_graphs: bool):
    """🚀 Initialize AID Commander v4.1 with optional knowledge graphs"""
    
    commander = ctx.obj['commander']
    
    if with_knowledge_graphs:
        console.print("[bold blue]🧠 Initializing with full knowledge graph support...[/bold blue]")
        success = await commander.initialize(project_path)
    else:
        console.print("[yellow]⚠️  Initializing without knowledge graphs (limited functionality)[/yellow]")
        success = await commander.initialize()
    
    if success:
        console.print("[bold green]✅ AID Commander v4.1 initialized successfully![/bold green]")
    else:
        console.print("[bold red]❌ Initialization failed![/bold red]")
        sys.exit(1)


# Knowledge Graph Commands
@kg.command('add-framework')
@click.argument('framework_name')
@click.option('--docs-url', '-d', help='Framework documentation URL')
@click.option('--local-docs', '-l', help='Local documentation path')
@click.pass_context
async def add_framework(ctx, framework_name: str, docs_url: str, local_docs: str):
    """📚 Add framework knowledge graph (e.g., pydantic-ai, fastapi)"""
    
    commander = ctx.obj['commander']
    if not commander.initialized:
        console.print("[red]❌ Please run 'aid-commander-v41 init --with-knowledge-graphs' first[/red]")
        return
    
    console.print(f"[blue]🔧 Building knowledge graph for {framework_name}...[/blue]")
    
    if framework_name.lower() == 'pydantic-ai':
        builder = PydanticAIKnowledgeBuilder(
            commander.graphiti_engine,
            commander.rag_system
        )
        result = await builder.build_complete_knowledge_graph()
        
        # Display results
        table = Table(title=f"📊 {framework_name} Knowledge Graph Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Entities Processed", str(result["entities_processed"]))
        table.add_row("Validation Patterns", str(result["validation_patterns"]))
        table.add_row("Success Patterns", str(result["success_patterns"]))
        table.add_row("Confidence", f"{result['confidence']:.1%}")
        table.add_row("Build Time", f"{result['build_time_seconds']:.2f}s")
        
        console.print(table)
        console.print(f"[bold green]✅ {framework_name} knowledge graph built successfully![/bold green]")
    else:
        console.print(f"[yellow]⚠️  Framework {framework_name} not yet supported. Available: pydantic-ai[/yellow]")


@kg.command('query-api')
@click.argument('api_call')
@click.option('--framework', '-f', required=True, help='Framework name')
@click.pass_context
async def query_api(ctx, api_call: str, framework: str):
    """🔍 Query knowledge graph for API validation"""
    
    commander = ctx.obj['commander']
    if not commander.initialized:
        console.print("[red]❌ Please initialize with knowledge graphs first[/red]")
        return
    
    console.print(f"[blue]🔍 Validating API: {api_call} in {framework}...[/blue]")
    
    validation = await commander.rag_system.validate_api_usage(api_call, framework)
    
    # Display validation results
    if validation.is_valid:
        console.print(f"[bold green]✅ API Valid: {validation.confidence:.1%} confidence[/bold green]")
        
        if validation.api_structure:
            table = Table(title="📋 API Structure")
            table.add_column("Class", style="cyan")
            table.add_column("Method", style="green")
            table.add_column("Signature", style="yellow")
            
            for api in validation.api_structure:
                table.add_row(
                    api.get("class_name", ""),
                    api.get("method_name", ""),
                    api.get("signature", "")
                )
            console.print(table)
    else:
        console.print(f"[bold red]❌ API Invalid: {validation.confidence:.1%} confidence[/bold red]")
        
        if validation.issues:
            console.print("[bold red]Issues:[/bold red]")
            for issue in validation.issues:
                console.print(f"  • {issue}")
        
        if validation.suggestions:
            console.print("[bold yellow]Suggestions:[/bold yellow]")
            for suggestion in validation.suggestions:
                console.print(f"  • {suggestion}")


@kg.command('search-patterns')
@click.argument('query')
@click.option('--framework', '-f', help='Filter by framework')
@click.option('--min-success-rate', '-s', default=0.8, help='Minimum success rate')
@click.pass_context
async def search_patterns(ctx, query: str, framework: str, min_success_rate: float):
    """📈 Search for successful patterns in knowledge graph"""
    
    commander = ctx.obj['commander']
    if not commander.initialized:
        console.print("[red]❌ Please initialize with knowledge graphs first[/red]")
        return
    
    console.print(f"[blue]📈 Searching patterns for: {query}...[/blue]")
    
    if framework:
        patterns = await commander.graphiti_engine.query_successful_patterns(
            framework=framework,
            min_success_rate=min_success_rate
        )
    else:
        console.print("[yellow]⚠️  Please specify framework with --framework[/yellow]")
        return
    
    if patterns:
        table = Table(title=f"📈 Successful Patterns for '{query}'")
        table.add_column("Pattern Name", style="cyan")
        table.add_column("Success Rate", style="green")
        table.add_column("Usage Count", style="yellow")
        table.add_column("Framework", style="blue")
        
        for pattern in patterns[:10]:  # Top 10
            table.add_row(
                pattern.name,
                f"{pattern.success_rate:.1%}",
                str(pattern.usage_count),
                pattern.framework
            )
        
        console.print(table)
    else:
        console.print("[yellow]No patterns found matching criteria[/yellow]")


# Validation Commands
@validate.command('generate-code')
@click.option('--intent', '-i', required=True, help='Code generation intent')
@click.option('--framework', '-f', required=True, help='Target framework')
@click.option('--confidence-threshold', '-c', default=0.92, help='Confidence threshold')
@click.pass_context
async def validate_generate_code(ctx, intent: str, framework: str, confidence_threshold: float):
    """🎯 Validate code generation with multi-layer analysis"""
    
    commander = ctx.obj['commander']
    if not commander.initialized:
        console.print("[red]❌ Please initialize with knowledge graphs first[/red]")
        return
    
    console.print(f"[blue]🎯 Validating code generation for: {intent}...[/blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        validation_task = progress.add_task("Running multi-layer validation...", total=None)
        
        validation_result = await commander.validation_engine.validate_code_generation(
            intent, framework
        )
        
        progress.update(validation_task, description="✅ Multi-layer validation complete")
    
    # Display validation results
    consensus_score = validation_result.consensus_score
    
    if consensus_score >= confidence_threshold:
        console.print(f"[bold green]🎉 VALIDATION PASSED: {consensus_score:.1%} consensus[/bold green]")
    else:
        console.print(f"[bold red]⚠️  VALIDATION NEEDS IMPROVEMENT: {consensus_score:.1%} consensus[/bold red]")
    
    # Show layer breakdown
    table = Table(title="📊 Validation Layer Results")
    table.add_column("Layer", style="cyan")
    table.add_column("Confidence", style="green") 
    table.add_column("Issues", style="yellow")
    table.add_column("Status", style="blue")
    
    for layer_name, result in validation_result.layer_results.items():
        status = "✅ Pass" if result.confidence >= 0.8 else "⚠️  Review" if result.confidence >= 0.5 else "❌ Fail"
        table.add_row(
            layer_name.replace('_', ' ').title(),
            f"{result.confidence:.1%}",
            str(len(result.issues)),
            status
        )
    
    console.print(table)
    
    # Show recommendations
    if validation_result.recommendations:
        console.print("\n[bold yellow]💡 Recommendations:[/bold yellow]")
        for rec in validation_result.recommendations:
            console.print(f"  {rec}")
    
    # Show validated approach if available
    if validation_result.validated_approach:
        console.print("\n[bold green]✅ Validated Approach:[/bold green]")
        syntax = Syntax(validation_result.validated_approach, "python", theme="monokai", line_numbers=True)
        console.print(syntax)


@validate.command('code-file')
@click.argument('file_path')
@click.option('--frameworks', '-f', help='Comma-separated list of frameworks')
@click.option('--detect-mixing', is_flag=True, help='Detect framework mixing issues')
@click.pass_context
async def validate_code_file(ctx, file_path: str, frameworks: str, detect_mixing: bool):
    """📝 Validate existing code file against knowledge graphs"""
    
    commander = ctx.obj['commander']
    if not commander.initialized:
        console.print("[red]❌ Please initialize with knowledge graphs first[/red]")
        return
    
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        console.print(f"[red]❌ File not found: {file_path}[/red]")
        return
    
    console.print(f"[blue]📝 Validating code file: {file_path}...[/blue]")
    
    # Read code
    code_content = file_path_obj.read_text()
    
    # Determine frameworks
    framework_list = frameworks.split(',') if frameworks else ['PydanticAI']  # Default
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        validation_task = progress.add_task("Analyzing code structure...", total=None)
        
        validation_result = await commander.validation_engine.validate_code_generation(
            "code file validation",
            framework_list[0],
            code_content
        )
        
        progress.update(validation_task, description="✅ Code analysis complete")
    
    # Display results
    consensus_score = validation_result.consensus_score
    
    console.print(f"\n[bold]📊 Validation Results for {file_path}[/bold]")
    console.print(f"Consensus Score: {consensus_score:.1%}")
    
    if consensus_score >= 0.9:
        console.print("[bold green]✅ Excellent code quality[/bold green]")
    elif consensus_score >= 0.7:
        console.print("[bold yellow]⚠️  Good code with room for improvement[/bold yellow]")
    else:
        console.print("[bold red]❌ Code needs significant improvement[/bold red]")
    
    # Show issues if any
    if validation_result.overall_issues:
        console.print("\n[bold red]🚨 Issues Found:[/bold red]")
        for issue in validation_result.overall_issues[:10]:  # Top 10 issues
            severity_color = {
                "critical": "red",
                "high": "orange",
                "medium": "yellow",
                "low": "blue"
            }.get(issue.severity.value, "white")
            console.print(f"  [{severity_color}]• {issue.description}[/{severity_color}]")


# Hallucination Detection Commands
@detect.command('hallucinations')
@click.argument('file_path')
@click.option('--frameworks', '-f', default='PydanticAI', help='Comma-separated frameworks')
@click.option('--auto-correct', is_flag=True, help='Automatically generate corrections')
@click.pass_context
async def detect_hallucinations(ctx, file_path: str, frameworks: str, auto_correct: bool):
    """🚨 Detect AI hallucinations in generated code"""
    
    commander = ctx.obj['commander']
    if not commander.initialized:
        console.print("[red]❌ Please initialize with knowledge graphs first[/red]")
        return
    
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        console.print(f"[red]❌ File not found: {file_path}[/red]")
        return
    
    console.print(f"[blue]🚨 Detecting hallucinations in: {file_path}...[/blue]")
    
    # Read code
    code_content = file_path_obj.read_text()
    framework_list = frameworks.split(',')
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        detection_task = progress.add_task("Running hallucination detection...", total=None)
        
        hallucination_result = await commander.hallucination_detector.detect_hallucination(
            code_content, framework_list
        )
        
        progress.update(detection_task, description="✅ Hallucination detection complete")
    
    # Display results
    console.print(f"\n[bold]🧠 Hallucination Detection Results[/bold]")
    console.print(f"Confidence Score: {hallucination_result.confidence_score:.1%}")
    
    if hallucination_result.is_hallucination:
        console.print(f"[bold red]🚨 HALLUCINATIONS DETECTED: {len(hallucination_result.detected_hallucinations)} issues[/bold red]")
        
        # Show detected hallucinations
        table = Table(title="🚨 Detected Hallucinations")
        table.add_column("Type", style="red")
        table.add_column("Incorrect Usage", style="yellow")
        table.add_column("Correct Usage", style="green")
        table.add_column("Confidence", style="blue")
        
        for hallucination in hallucination_result.detected_hallucinations:
            table.add_row(
                hallucination.type.value.replace('_', ' ').title(),
                hallucination.incorrect_usage,
                hallucination.correct_usage or "See suggestions",
                f"{hallucination.confidence:.1%}"
            )
        
        console.print(table)
        
        # Show corrected code if auto-correct enabled
        if auto_correct and hallucination_result.corrected_code:
            console.print("\n[bold green]✅ Auto-Corrected Code:[/bold green]")
            syntax = Syntax(hallucination_result.corrected_code, "python", theme="monokai", line_numbers=True)
            console.print(syntax)
            
            # Offer to save corrected code
            if click.confirm("Save corrected code to file?"):
                corrected_path = file_path_obj.with_suffix('.corrected.py')
                corrected_path.write_text(hallucination_result.corrected_code)
                console.print(f"[green]✅ Corrected code saved to: {corrected_path}[/green]")
    else:
        console.print("[bold green]✅ No hallucinations detected - code looks good![/bold green]")


# Memory Commands
@memory.command('cross-project-learnings')
@click.option('--framework', '-f', required=True, help='Framework name')
@click.option('--decision-type', '-t', help='Filter by decision type')
@click.pass_context
async def cross_project_learnings(ctx, framework: str, decision_type: str):
    """🔗 Get learnings from across all projects"""
    
    commander = ctx.obj['commander']
    if not commander.initialized or not commander.graph_memory_bank:
        console.print("[red]❌ Please initialize with project path and knowledge graphs[/red]")
        return
    
    console.print(f"[blue]🔗 Getting cross-project learnings for {framework}...[/blue]")
    
    learnings = await commander.graph_memory_bank.get_cross_project_learnings(
        framework, decision_type
    )
    
    # Display learnings
    console.print(f"\n[bold]📊 Cross-Project Analysis for {framework}[/bold]")
    
    if learnings["overall_stats"]:
        stats = learnings["overall_stats"]
        console.print(f"🎯 Overall Success Rate: {stats['avg_success_rate']:.1%} (across {stats['total_decisions']} decisions)")
    
    if learnings["decision_types"]:
        table = Table(title="📈 Decision Type Analysis")
        table.add_column("Decision Type", style="cyan")
        table.add_column("Decisions", style="yellow")
        table.add_column("Success Rate", style="green")
        table.add_column("Projects", style="blue")
        
        for dt in learnings["decision_types"]:
            table.add_row(
                dt["decision_type"] or "General",
                str(dt["total_decisions"]),
                f"{dt['avg_success']:.1%}",
                str(dt["project_count"])
            )
        
        console.print(table)
    else:
        console.print("[yellow]No cross-project data available yet[/yellow]")


@memory.command('recommend')
@click.option('--query', '-q', required=True, help='Decision query')
@click.option('--framework', '-f', required=True, help='Framework name')
@click.option('--include-cross-project', is_flag=True, help='Include cross-project insights')
@click.pass_context
async def memory_recommend(ctx, query: str, framework: str, include_cross_project: bool):
    """💡 Get memory-enhanced recommendations"""
    
    commander = ctx.obj['commander']
    if not commander.initialized or not commander.graph_memory_bank:
        console.print("[red]❌ Please initialize with project path and knowledge graphs[/red]")
        return
    
    console.print(f"[blue]💡 Getting recommendations for: {query}...[/blue]")
    
    optimization = await commander.graph_memory_bank.optimize_decision_with_graph(
        query, framework
    )
    
    # Display recommendations
    console.print(f"\n[bold]💡 Memory-Enhanced Recommendations[/bold]")
    console.print(f"Success Probability: {optimization['success_probability']:.1%}")
    console.print(f"Confidence: {optimization['confidence']:.1%}")
    
    console.print("\n[bold yellow]📋 Recommendations:[/bold yellow]")
    for rec in optimization["recommendations"]:
        console.print(f"  {rec}")
    
    if optimization["temporal_patterns"]:
        console.print("\n[bold blue]📈 Proven Patterns:[/bold blue]")
        for pattern in optimization["temporal_patterns"]:
            console.print(f"  • {pattern}")
    
    if optimization["cross_framework_insights"]:
        console.print("\n[bold green]🔄 Cross-Framework Insights:[/bold green]")
        for insight in optimization["cross_framework_insights"]:
            console.print(f"  • {insight}")


# Performance and Stats Commands
@cli.command('stats')
@click.pass_context
async def stats(ctx):
    """📊 Show performance statistics for all components"""
    
    commander = ctx.obj['commander']
    if not commander.initialized:
        console.print("[red]❌ Please initialize first[/red]")
        return
    
    console.print("[blue]📊 Gathering performance statistics...[/blue]")
    
    # Gather stats from all components
    stats_data = {}
    
    if commander.graphiti_engine:
        stats_data["Graphiti Engine"] = await commander.graphiti_engine.get_performance_stats()
    
    if commander.rag_system:
        stats_data["RAG System"] = await commander.rag_system.get_performance_stats()
    
    if commander.validation_engine:
        stats_data["Validation Engine"] = await commander.validation_engine.get_performance_stats()
    
    if commander.hallucination_detector:
        stats_data["Hallucination Detector"] = await commander.hallucination_detector.get_performance_stats()
    
    if commander.graph_memory_bank:
        stats_data["Memory Bank"] = await commander.graph_memory_bank.get_performance_stats()
    
    # Display stats
    for component, stats in stats_data.items():
        table = Table(title=f"📊 {component} Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in stats.items():
            if isinstance(value, float):
                if 'time' in key.lower():
                    table.add_row(key.replace('_', ' ').title(), f"{value:.3f}s")
                elif 'rate' in key.lower() or 'threshold' in key.lower():
                    table.add_row(key.replace('_', ' ').title(), f"{value:.1%}")
                else:
                    table.add_row(key.replace('_', ' ').title(), f"{value:.2f}")
            else:
                table.add_row(key.replace('_', ' ').title(), str(value))
        
        console.print(table)
        console.print()


def main():
    """Main CLI entry point"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add async support to click
    def async_command(f):
        def wrapper(*args, **kwargs):
            return asyncio.run(f(*args, **kwargs))
        return wrapper
    
    # Apply async wrapper to all async commands
    for command in [init, add_framework, query_api, search_patterns, 
                   validate_generate_code, validate_code_file, detect_hallucinations,
                   cross_project_learnings, memory_recommend, stats]:
        command.callback = async_command(command.callback)
    
    cli()


if __name__ == "__main__":
    main()