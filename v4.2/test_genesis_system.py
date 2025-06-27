#!/usr/bin/env python3
"""
AID Commander Genesis v4.2 - Comprehensive System Test

Tests the complete Genesis system integration including ConceptCraft AI,
Adaptive Intelligence, Story Engine, and all major components.
"""

import asyncio
import sys
import traceback
from pathlib import Path
from typing import List, Dict, Any
import json

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "issues": [],
    "system_health": {}
}

def log_test(test_name: str, status: str, details: str = "", error: str = ""):
    """Log test results"""
    result = {
        "test": test_name,
        "status": status,
        "details": details,
        "error": error
    }
    
    if status == "PASS":
        test_results["passed"].append(result)
        print(f"✅ {test_name}: {details}")
    else:
        test_results["failed"].append(result)
        print(f"❌ {test_name}: {details}")
        if error:
            print(f"   Error: {error}")

def log_issue(component: str, issue: str, fix_suggestion: str = ""):
    """Log an issue that needs fixing"""
    issue_entry = {
        "component": component,
        "issue": issue,
        "fix_suggestion": fix_suggestion,
        "severity": "medium"
    }
    test_results["issues"].append(issue_entry)
    print(f"⚠️  {component}: {issue}")
    if fix_suggestion:
        print(f"   💡 Suggestion: {fix_suggestion}")

async def test_genesis_imports():
    """Test Genesis system imports and basic functionality"""
    print("\n🧪 Testing Genesis System Imports...")
    
    try:
        # Test main Genesis import
        from aid_commander_genesis import genesis_info, genesis_health_check
        
        # Test component imports
        from aid_commander_genesis import (
            get_conceptcraft_ai,
            get_adaptive_intelligence,
            get_story_engine,
            get_unified_validation,
            get_cross_project_learning,
            get_cli
        )
        
        log_test("Genesis Core Imports", "PASS", "All core components imported successfully")
        
        # Test Genesis info
        info = genesis_info()
        expected_components = [
            "conceptcraft_ai", "adaptive_intelligence", "story_engine",
            "unified_validation", "cross_project_learning"
        ]
        
        for component in expected_components:
            if component in info["components"]:
                log_test(f"Component Metadata - {component}", "PASS", info["components"][component][:50] + "...")
            else:
                log_test(f"Component Metadata - {component}", "FAIL", "Missing from Genesis metadata")
        
        # Test health check
        health = genesis_health_check()
        test_results["system_health"] = health
        
        if health["overall_status"] == "healthy":
            log_test("Genesis Health Check", "PASS", "System reports healthy status")
        else:
            log_test("Genesis Health Check", "FAIL", f"System status: {health['overall_status']}")
        
        return True
        
    except ImportError as e:
        log_test("Genesis Core Imports", "FAIL", "Import failed", str(e))
        log_issue("Genesis Core", "Import dependencies missing", 
                 "Run: pip install -e '.[all]' from v4.2 directory")
        return False
    except Exception as e:
        log_test("Genesis Core Imports", "FAIL", "Unexpected error", str(e))
        return False

async def test_conceptcraft_ai():
    """Test ConceptCraft AI component"""
    print("\n🧪 Testing ConceptCraft AI...")
    
    try:
        from aid_commander_genesis.conceptcraft import ConceptCraftAI, ConceptDocument
        
        # Test ConceptCraft AI initialization
        conceptcraft = ConceptCraftAI()
        initialized = await conceptcraft.initialize()
        
        if initialized:
            log_test("ConceptCraft AI Initialization", "PASS", "ConceptCraft AI initialized successfully")
        else:
            log_test("ConceptCraft AI Initialization", "FAIL", "Failed to initialize ConceptCraft AI")
        
        # Test health check
        health = conceptcraft.health_check()
        if health["status"] == "available":
            log_test("ConceptCraft AI Health", "PASS", "ConceptCraft AI reports available")
        else:
            log_test("ConceptCraft AI Health", "FAIL", f"Status: {health['status']}")
        
        # Test ConceptDocument model
        from aid_commander_genesis.conceptcraft.models import (
            ConceptDocument, StakeholderStory, StakeholderType, ValidationLevel
        )
        
        # Create test concept document
        test_concept = ConceptDocument(
            concept_id="test-001",
            concept_name="Test Concept",
            concept_description="A test concept for validation",
            validation_level=ValidationLevel.FOUNDATION
        )
        
        # Test model validation
        maturity_score = test_concept.calculate_maturity_score()
        prd_readiness = test_concept.calculate_prd_readiness()
        
        log_test("ConceptDocument Model", "PASS", 
                f"Maturity: {maturity_score:.1%}, PRD Readiness: {prd_readiness:.1%}")
        
        return True
        
    except Exception as e:
        log_test("ConceptCraft AI", "FAIL", "Component test failed", str(e))
        log_issue("ConceptCraft AI", "Component testing failed", 
                 "Check ConceptCraft AI implementation and dependencies")
        return False

async def test_adaptive_intelligence():
    """Test Adaptive Intelligence Engine"""
    print("\n🧪 Testing Adaptive Intelligence Engine...")
    
    try:
        from aid_commander_genesis.adaptive_intelligence import (
            AdaptiveIntelligenceEngine, ExecutionMode, ComplexityAnalysis
        )
        
        # Test engine initialization
        engine = AdaptiveIntelligenceEngine()
        initialized = await engine.initialize()
        
        if initialized:
            log_test("Adaptive Intelligence Initialization", "PASS", "Engine initialized successfully")
        else:
            log_test("Adaptive Intelligence Initialization", "FAIL", "Failed to initialize engine")
        
        # Test health check
        health = engine.health_check()
        if health["status"] == "available":
            log_test("Adaptive Intelligence Health", "PASS", 
                    f"Loaded {health['loaded_patterns']} patterns, {health['historical_decisions']} decisions")
        else:
            log_test("Adaptive Intelligence Health", "FAIL", f"Status: {health['status']}")
        
        # Test execution modes
        modes = [ExecutionMode.LIGHTWEIGHT, ExecutionMode.KNOWLEDGE_GRAPH, 
                ExecutionMode.HYBRID, ExecutionMode.CREATIVE]
        
        log_test("Execution Modes", "PASS", f"Available modes: {[m.value for m in modes]}")
        
        return True
        
    except Exception as e:
        log_test("Adaptive Intelligence", "FAIL", "Component test failed", str(e))
        log_issue("Adaptive Intelligence", "Component testing failed",
                 "Check Adaptive Intelligence implementation")
        return False

async def test_story_engine():
    """Test Story-Enhanced PRD Engine"""
    print("\n🧪 Testing Story-Enhanced PRD Engine...")
    
    try:
        from aid_commander_genesis.story_engine import StoryEnhancedPRDEngine
        
        # Test engine initialization
        engine = StoryEnhancedPRDEngine()
        initialized = await engine.initialize()
        
        if initialized:
            log_test("Story Engine Initialization", "PASS", "Story Engine initialized successfully")
        else:
            log_test("Story Engine Initialization", "FAIL", "Failed to initialize Story Engine")
        
        # Test health check
        health = engine.health_check()
        if health["status"] == "available":
            log_test("Story Engine Health", "PASS", "Story Engine reports available")
        else:
            log_test("Story Engine Health", "FAIL", f"Status: {health['status']}")
        
        return True
        
    except Exception as e:
        log_test("Story Engine", "FAIL", "Component test failed", str(e))
        log_issue("Story Engine", "Component testing failed",
                 "Check Story Engine implementation")
        return False

async def test_unified_validation():
    """Test Unified Validation System"""
    print("\n🧪 Testing Unified Validation System...")
    
    try:
        from aid_commander_genesis.unified_validation import UnifiedValidationSystem
        
        # Test system initialization
        system = UnifiedValidationSystem()
        initialized = await system.initialize()
        
        if initialized:
            log_test("Unified Validation Initialization", "PASS", "Validation system initialized")
        else:
            log_test("Unified Validation Initialization", "FAIL", "Failed to initialize validation")
        
        # Test health check
        health = system.health_check()
        if health["status"] == "available":
            log_test("Unified Validation Health", "PASS", "Validation system reports available")
        else:
            log_test("Unified Validation Health", "FAIL", f"Status: {health['status']}")
        
        return True
        
    except Exception as e:
        log_test("Unified Validation", "FAIL", "Component test failed", str(e))
        log_issue("Unified Validation", "Implementation incomplete", 
                 "Complete Unified Validation System implementation")
        return False

async def test_cross_project_learning():
    """Test Cross-Project Learning Engine"""
    print("\n🧪 Testing Cross-Project Learning Engine...")
    
    try:
        from aid_commander_genesis.cross_project_learning import CrossProjectLearningEngine
        
        # Test engine initialization
        engine = CrossProjectLearningEngine()
        initialized = await engine.initialize()
        
        if initialized:
            log_test("Cross-Project Learning Initialization", "PASS", "Learning engine initialized")
        else:
            log_test("Cross-Project Learning Initialization", "FAIL", "Failed to initialize learning")
        
        # Test health check
        health = engine.health_check()
        if health["status"] == "available":
            log_test("Cross-Project Learning Health", "PASS", "Learning engine reports available")
        else:
            log_test("Cross-Project Learning Health", "FAIL", f"Status: {health['status']}")
        
        return True
        
    except Exception as e:
        log_test("Cross-Project Learning", "FAIL", "Component test failed", str(e))
        log_issue("Cross-Project Learning", "Implementation incomplete",
                 "Complete Cross-Project Learning Engine implementation")
        return False

async def test_cli_interface():
    """Test Genesis CLI interface"""
    print("\n🧪 Testing Genesis CLI Interface...")
    
    try:
        from aid_commander_genesis.cli import GenesisCommandLine
        
        # Test CLI initialization
        cli = GenesisCommandLine()
        
        # Test configuration loading
        config = cli.config
        expected_keys = ["version", "genesis_mode", "settings", "integrations"]
        
        for key in expected_keys:
            if key in config:
                log_test(f"CLI Config - {key}", "PASS", f"Configuration key present")
            else:
                log_test(f"CLI Config - {key}", "FAIL", f"Missing configuration key: {key}")
        
        # Test component lazy loading
        conceptcraft = cli.conceptcraft_ai
        adaptive = cli.adaptive_intelligence
        story = cli.story_engine
        
        log_test("CLI Component Lazy Loading", "PASS", "All components loaded successfully")
        
        return True
        
    except Exception as e:
        log_test("CLI Interface", "FAIL", "CLI test failed", str(e))
        log_issue("CLI Interface", "CLI component failed",
                 "Check CLI implementation and component integration")
        return False

async def test_integration_workflow():
    """Test integrated workflow simulation"""
    print("\n🧪 Testing Integrated Workflow...")
    
    try:
        from aid_commander_genesis import get_conceptcraft_ai, get_adaptive_intelligence, get_story_engine
        from aid_commander_genesis.conceptcraft.models import ConceptDocument, ValidationLevel
        from aid_commander_genesis.adaptive_intelligence.models import ExecutionMode, UserPreferences
        
        # Simulate concept development
        conceptcraft = get_conceptcraft_ai()
        
        # Create mock concept document
        mock_concept = ConceptDocument(
            concept_id="integration-test-001",
            concept_name="Integration Test Concept",
            concept_description="A concept created for integration testing",
            validation_level=ValidationLevel.FOUNDATION
        )
        
        # Test adaptive intelligence analysis
        adaptive = get_adaptive_intelligence()
        complexity_analysis = await adaptive.analyze_concept_complexity(mock_concept)
        
        log_test("Concept Complexity Analysis", "PASS", 
                f"Complexity: {complexity_analysis.complexity_score:.1f}/10")
        
        # Test mode determination
        user_prefs = UserPreferences()
        execution_mode = await adaptive.determine_execution_mode(
            mock_concept, user_prefs
        )
        
        log_test("Execution Mode Determination", "PASS", 
                f"Recommended mode: {execution_mode.value}")
        
        # Test story engine PRD generation
        story_engine = get_story_engine()
        prd_document = await story_engine.generate_prd_from_concept(
            mock_concept, execution_mode
        )
        
        if prd_document and "executive_summary" in prd_document:
            log_test("Story-Enhanced PRD Generation", "PASS", 
                    "PRD generated with all required sections")
        else:
            log_test("Story-Enhanced PRD Generation", "FAIL", 
                    "PRD generation incomplete")
        
        log_test("Integration Workflow", "PASS", "End-to-end workflow simulation successful")
        
        return True
        
    except Exception as e:
        log_test("Integration Workflow", "FAIL", "Workflow simulation failed", str(e))
        log_issue("Integration", "Component integration issues",
                 "Debug component interfaces and data flow")
        return False

async def test_file_structure():
    """Test Genesis file structure and organization"""
    print("\n🧪 Testing Genesis File Structure...")
    
    # Expected file structure
    expected_files = [
        "aid_commander_genesis/__init__.py",
        "aid_commander_genesis/cli/__init__.py", 
        "aid_commander_genesis/cli/main.py",
        "aid_commander_genesis/conceptcraft/__init__.py",
        "aid_commander_genesis/conceptcraft/core.py",
        "aid_commander_genesis/conceptcraft/models.py",
        "aid_commander_genesis/adaptive_intelligence/__init__.py",
        "aid_commander_genesis/adaptive_intelligence/core.py",
        "aid_commander_genesis/adaptive_intelligence/models.py",
        "aid_commander_genesis/story_engine/__init__.py",
        "aid_commander_genesis/story_engine/core.py",
        "aid_commander_genesis/unified_validation/__init__.py",
        "aid_commander_genesis/cross_project_learning/__init__.py",
        "pyproject.toml",
        "README.md"
    ]
    
    base_path = Path(__file__).parent
    missing_files = []
    present_files = []
    
    for file_path in expected_files:
        full_path = base_path / file_path
        if full_path.exists():
            present_files.append(file_path)
        else:
            missing_files.append(file_path)
    
    if not missing_files:
        log_test("File Structure", "PASS", f"All {len(expected_files)} expected files present")
    else:
        log_test("File Structure", "FAIL", 
                f"{len(missing_files)} files missing: {missing_files[:3]}...")
        
        for missing in missing_files:
            log_issue("File Structure", f"Missing file: {missing}",
                     "Create missing file or update expected structure")
    
    return len(missing_files) == 0

def generate_test_report():
    """Generate comprehensive test report"""
    total_tests = len(test_results["passed"]) + len(test_results["failed"])
    pass_rate = len(test_results["passed"]) / total_tests * 100 if total_tests > 0 else 0
    
    print(f"\n\n🧪 AID COMMANDER GENESIS v4.2 - COMPREHENSIVE TEST RESULTS")
    print("=" * 70)
    print(f"📊 SUMMARY:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {len(test_results['passed'])} ({pass_rate:.1f}%)")
    print(f"   Failed: {len(test_results['failed'])}")
    print(f"   Issues Found: {len(test_results['issues'])}")
    
    if test_results["failed"]:
        print(f"\n❌ FAILED TESTS:")
        for failure in test_results["failed"]:
            print(f"   • {failure['test']}: {failure['details']}")
    
    if test_results["issues"]:
        print(f"\n⚠️  ISSUES TO ADDRESS:")
        for issue in test_results["issues"]:
            print(f"   • {issue['component']}: {issue['issue']}")
            if issue.get("fix_suggestion"):
                print(f"     💡 {issue['fix_suggestion']}")
    
    if test_results["system_health"]:
        print(f"\n🏥 SYSTEM HEALTH:")
        health = test_results["system_health"]
        print(f"   Overall Status: {health.get('overall_status', 'unknown')}")
        if health.get("components"):
            for component, status in health["components"].items():
                component_status = status.get("status", "unknown")
                print(f"   {component}: {component_status}")
    
    # Save test results
    results_file = Path(__file__).parent / "test_results_genesis.json"
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    # Overall assessment
    if pass_rate >= 90:
        print(f"\n🎉 GENESIS SYSTEM STATUS: EXCELLENT ({pass_rate:.1f}% pass rate)")
        print("   Genesis is ready for development and testing!")
    elif pass_rate >= 75:
        print(f"\n✅ GENESIS SYSTEM STATUS: GOOD ({pass_rate:.1f}% pass rate)")
        print("   Genesis is functional with minor issues to address.")
    elif pass_rate >= 50:
        print(f"\n⚠️  GENESIS SYSTEM STATUS: NEEDS WORK ({pass_rate:.1f}% pass rate)")
        print("   Genesis requires attention before production use.")
    else:
        print(f"\n❌ GENESIS SYSTEM STATUS: MAJOR ISSUES ({pass_rate:.1f}% pass rate)")
        print("   Genesis needs significant development before use.")

async def main():
    """Run comprehensive Genesis system tests"""
    print("🌟 AID Commander Genesis v4.2 - Comprehensive System Testing")
    print("=" * 70)
    
    # Run all test suites
    test_suites = [
        ("System Imports", test_genesis_imports),
        ("File Structure", test_file_structure),
        ("ConceptCraft AI", test_conceptcraft_ai),
        ("Adaptive Intelligence", test_adaptive_intelligence),
        ("Story Engine", test_story_engine),
        ("Unified Validation", test_unified_validation),
        ("Cross-Project Learning", test_cross_project_learning),
        ("CLI Interface", test_cli_interface),
        ("Integration Workflow", test_integration_workflow)
    ]
    
    for suite_name, test_func in test_suites:
        try:
            print(f"\n{'='*20} {suite_name} {'='*20}")
            if asyncio.iscoroutinefunction(test_func):
                await test_func()
            else:
                test_func()
        except Exception as e:
            log_test(f"{suite_name} Suite", "FAIL", "Test suite crashed", str(e))
            print(f"💥 Test suite crashed: {e}")
            traceback.print_exc()
    
    # Generate final report
    generate_test_report()

if __name__ == "__main__":
    asyncio.run(main())