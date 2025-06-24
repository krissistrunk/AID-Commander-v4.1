#!/usr/bin/env python3
"""
AID Commander v4.1 - Comprehensive Step-by-Step Testing

This script tests every component systematically and documents issues.
"""

import sys
import asyncio
import traceback
from pathlib import Path
from typing import List, Dict, Any
import json

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "issues": [],
    "fixes_needed": []
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
        
        # Add to fixes needed
        test_results["fixes_needed"].append({
            "component": test_name,
            "issue": details,
            "error": error
        })

def log_issue(component: str, issue: str, fix_suggestion: str = ""):
    """Log an issue that needs fixing"""
    issue_entry = {
        "component": component,
        "issue": issue,
        "fix_suggestion": fix_suggestion
    }
    test_results["issues"].append(issue_entry)
    print(f"🔧 ISSUE - {component}: {issue}")
    if fix_suggestion:
        print(f"   Suggested fix: {fix_suggestion}")

async def test_step_1_project_structure():
    """Test 1: Verify project structure exists"""
    print("\n🧪 TEST 1: Project Structure")
    
    try:
        project_root = Path("/Users/krissistrunk/Desktop/alwaysAccess.nosync/Sistronics/LearnstarAIDTest/AID_Commander/v4.1")
        
        required_files = [
            "pyproject.toml",
            "README.md", 
            "aid_commander_v41/__init__.py",
            "aid_commander_v41/cli/main.py",
            "aid_commander_v41/knowledge_graph/graphiti/temporal_engine.py",
            "aid_commander_v41/knowledge_graph/rag/hybrid_search.py",
            "aid_commander_v41/frameworks/pydantic_ai/knowledge_builder.py",
            "aid_commander_v41/validation/multi_layer/validation_engine.py",
            "aid_commander_v41/validation/hallucination/detection_engine.py",
            "aid_commander_v41/memory_enhanced/graph_memory_bank.py",
            "infrastructure/docker/docker-compose.yml"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            log_test("Project Structure", "FAIL", 
                    f"Missing {len(missing_files)} required files", 
                    f"Missing: {', '.join(missing_files)}")
            for missing in missing_files:
                log_issue("Project Structure", f"Missing file: {missing}", 
                         "Create the missing file with proper implementation")
        else:
            log_test("Project Structure", "PASS", "All required files present")
            
    except Exception as e:
        log_test("Project Structure", "FAIL", "Exception during structure check", str(e))

async def test_step_2_basic_imports():
    """Test 2: Test basic Python imports"""
    print("\n🧪 TEST 2: Basic Python Imports")
    
    try:
        # Test basic Python imports
        sys.path.insert(0, str(Path("/Users/krissistrunk/Desktop/alwaysAccess.nosync/Sistronics/LearnstarAIDTest/AID_Commander/v4.1")))
        
        import_tests = [
            ("aid_commander_v41", "Main package import"),
            ("pydantic", "Pydantic dependency"),
            ("click", "CLI framework"),
            ("rich", "Rich terminal library"),
            ("structlog", "Structured logging"),
            ("asyncio", "Async support")
        ]
        
        for module, description in import_tests:
            try:
                __import__(module)
                log_test(f"Import {module}", "PASS", description)
            except ImportError as e:
                log_test(f"Import {module}", "FAIL", f"Failed to import {module}", str(e))
                log_issue("Dependencies", f"Missing dependency: {module}", 
                         f"Install with: pip install {module}")
                
    except Exception as e:
        log_test("Basic Imports", "FAIL", "Exception during import tests", str(e))

async def test_step_3_pyproject_toml():
    """Test 3: Validate pyproject.toml configuration"""
    print("\n🧪 TEST 3: PyProject Configuration")
    
    try:
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            import tomli as tomllib  # Fallback for older Python
        
        pyproject_path = Path("/Users/krissistrunk/Desktop/alwaysAccess.nosync/Sistronics/LearnstarAIDTest/AID_Commander/v4.1/pyproject.toml")
        
        if not pyproject_path.exists():
            log_test("PyProject TOML", "FAIL", "pyproject.toml not found")
            log_issue("Configuration", "Missing pyproject.toml", "Create pyproject.toml with proper dependencies")
            return
        
        with open(pyproject_path, "rb") as f:
            config = tomllib.load(f)
        
        # Check required sections
        required_sections = ["build-system", "project"]
        missing_sections = [section for section in required_sections if section not in config]
        
        if missing_sections:
            log_test("PyProject TOML", "FAIL", f"Missing sections: {missing_sections}")
            log_issue("Configuration", f"Missing pyproject.toml sections: {missing_sections}",
                     "Add missing sections to pyproject.toml")
        else:
            log_test("PyProject TOML", "PASS", "Configuration file is valid")
            
        # Check dependencies
        if "project" in config and "dependencies" in config["project"]:
            deps = config["project"]["dependencies"]
            log_test("Dependencies Listed", "PASS", f"Found {len(deps)} dependencies")
        else:
            log_test("Dependencies Listed", "FAIL", "No dependencies section found")
            log_issue("Configuration", "Missing dependencies in pyproject.toml",
                     "Add dependencies section with required packages")
            
    except ImportError:
        log_test("PyProject TOML", "FAIL", "tomllib not available (Python < 3.11)")
        log_issue("Python Version", "Need Python 3.11+ for tomllib", "Upgrade Python or use alternative TOML parser")
    except Exception as e:
        log_test("PyProject TOML", "FAIL", "Exception parsing pyproject.toml", str(e))

async def test_step_4_docker_infrastructure():
    """Test 4: Docker infrastructure availability"""
    print("\n🧪 TEST 4: Docker Infrastructure")
    
    try:
        import subprocess
        
        # Check if Docker is available
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                log_test("Docker Available", "PASS", f"Docker version: {result.stdout.strip()}")
            else:
                log_test("Docker Available", "FAIL", "Docker command failed")
                log_issue("Infrastructure", "Docker not available", "Install Docker Desktop or Docker Engine")
        except FileNotFoundError:
            log_test("Docker Available", "FAIL", "Docker command not found")
            log_issue("Infrastructure", "Docker not installed", "Install Docker Desktop")
        except subprocess.TimeoutExpired:
            log_test("Docker Available", "FAIL", "Docker command timed out")
            log_issue("Infrastructure", "Docker command timeout", "Check Docker installation and startup")
        
        # Check docker-compose file
        compose_path = Path("/Users/krissistrunk/Desktop/alwaysAccess.nosync/Sistronics/LearnstarAIDTest/AID_Commander/v4.1/infrastructure/docker/docker-compose.yml")
        if compose_path.exists():
            log_test("Docker Compose File", "PASS", "docker-compose.yml found")
        else:
            log_test("Docker Compose File", "FAIL", "docker-compose.yml not found")
            log_issue("Infrastructure", "Missing docker-compose.yml", "Create docker-compose file with required services")
        
    except Exception as e:
        log_test("Docker Infrastructure", "FAIL", "Exception during Docker tests", str(e))

async def test_step_5_cli_basic():
    """Test 5: Basic CLI functionality"""
    print("\n🧪 TEST 5: Basic CLI Functionality")
    
    try:
        # Import CLI components
        from aid_commander_v41.cli.main import AIDCommanderV41, cli
        log_test("CLI Import", "PASS", "Successfully imported CLI components")
        
        # Test CLI object creation
        commander = AIDCommanderV41()
        log_test("CLI Object Creation", "PASS", "AIDCommanderV41 object created")
        
        # Test configuration loading
        config = commander._load_config()
        if isinstance(config, dict) and len(config) > 0:
            log_test("CLI Configuration", "PASS", f"Loaded config with {len(config)} settings")
        else:
            log_test("CLI Configuration", "FAIL", "Config is empty or invalid")
            log_issue("CLI", "Invalid configuration", "Fix _load_config method to return proper config dict")
        
    except ImportError as e:
        log_test("CLI Import", "FAIL", "Failed to import CLI components", str(e))
        log_issue("CLI", "Import error in CLI", "Fix import paths and missing dependencies")
    except Exception as e:
        log_test("CLI Basic", "FAIL", "Exception during CLI tests", str(e))

async def test_step_6_knowledge_graph_imports():
    """Test 6: Knowledge Graph component imports"""
    print("\n🧪 TEST 6: Knowledge Graph Imports")
    
    try:
        # Test Graphiti engine import
        try:
            from aid_commander_v41.knowledge_graph.graphiti.temporal_engine import AIDGraphitiEngine
            log_test("Graphiti Import", "PASS", "AIDGraphitiEngine imported successfully")
        except ImportError as e:
            log_test("Graphiti Import", "FAIL", "Failed to import Graphiti engine", str(e))
            log_issue("Knowledge Graph", "Graphiti import failed", "Fix import paths and dependencies")
        
        # Test RAG system import
        try:
            from aid_commander_v41.knowledge_graph.rag.hybrid_search import HybridRAGSystem
            log_test("RAG Import", "PASS", "HybridRAGSystem imported successfully")
        except ImportError as e:
            log_test("RAG Import", "FAIL", "Failed to import RAG system", str(e))
            log_issue("Knowledge Graph", "RAG import failed", "Fix import paths and dependencies")
        
        # Test Pydantic AI builder import
        try:
            from aid_commander_v41.frameworks.pydantic_ai.knowledge_builder import PydanticAIKnowledgeBuilder
            log_test("Pydantic AI Builder Import", "PASS", "PydanticAIKnowledgeBuilder imported successfully")
        except ImportError as e:
            log_test("Pydantic AI Builder Import", "FAIL", "Failed to import Pydantic AI builder", str(e))
            log_issue("Frameworks", "Pydantic AI builder import failed", "Fix import paths and dependencies")
        
    except Exception as e:
        log_test("Knowledge Graph Imports", "FAIL", "Exception during import tests", str(e))

async def test_step_7_validation_imports():
    """Test 7: Validation system imports"""
    print("\n🧪 TEST 7: Validation System Imports")
    
    try:
        # Test multi-layer validation import
        try:
            from aid_commander_v41.validation.multi_layer.validation_engine import MultiLayerValidationEngine
            log_test("Multi-Layer Validation Import", "PASS", "MultiLayerValidationEngine imported")
        except ImportError as e:
            log_test("Multi-Layer Validation Import", "FAIL", "Failed to import validation engine", str(e))
            log_issue("Validation", "Multi-layer validation import failed", "Fix import paths and dependencies")
        
        # Test hallucination detection import
        try:
            from aid_commander_v41.validation.hallucination.detection_engine import HallucinationDetectionEngine
            log_test("Hallucination Detection Import", "PASS", "HallucinationDetectionEngine imported")
        except ImportError as e:
            log_test("Hallucination Detection Import", "FAIL", "Failed to import hallucination detector", str(e))
            log_issue("Validation", "Hallucination detection import failed", "Fix import paths and dependencies")
        
    except Exception as e:
        log_test("Validation Imports", "FAIL", "Exception during validation import tests", str(e))

async def test_step_8_memory_import():
    """Test 8: Enhanced memory system import"""
    print("\n🧪 TEST 8: Enhanced Memory System Import")
    
    try:
        # Test enhanced memory bank import
        try:
            from aid_commander_v41.memory_enhanced.graph_memory_bank import GraphEnhancedMemoryBank
            log_test("Enhanced Memory Import", "PASS", "GraphEnhancedMemoryBank imported")
        except ImportError as e:
            log_test("Enhanced Memory Import", "FAIL", "Failed to import enhanced memory bank", str(e))
            log_issue("Memory", "Enhanced memory import failed", "Fix import paths and dependencies")
        
        # Test v4.0 memory bank import
        try:
            # This should work since we're extending v4.0
            import sys
            sys.path.insert(0, str(Path("/Users/krissistrunk/Desktop/alwaysAccess.nosync/Sistronics/LearnstarAIDTest/AID_Commander/v4")))
            from memory_service import MemoryBank, MemoryContext
            log_test("V4.0 Memory Import", "PASS", "V4.0 MemoryBank imported")
        except ImportError as e:
            log_test("V4.0 Memory Import", "FAIL", "Failed to import v4.0 memory bank", str(e))
            log_issue("Memory", "V4.0 memory bank import failed", "Fix path to v4.0 memory_service")
        
    except Exception as e:
        log_test("Memory Import", "FAIL", "Exception during memory import tests", str(e))

async def test_step_9_dependency_check():
    """Test 9: Check external dependencies"""
    print("\n🧪 TEST 9: External Dependencies")
    
    external_deps = [
        ("neo4j", "Neo4j driver for graph database"),
        ("chromadb", "ChromaDB for vector storage"),
        ("sentence_transformers", "Sentence transformers for embeddings"),
        ("httpx", "HTTP client for API calls"),
        ("bs4", "BeautifulSoup for web scraping"),
        ("pytest", "Testing framework"),
        ("pytest_asyncio", "Async testing support")
    ]
    
    for dep, description in external_deps:
        try:
            __import__(dep)
            log_test(f"Dependency {dep}", "PASS", description)
        except ImportError:
            log_test(f"Dependency {dep}", "FAIL", f"Missing dependency: {dep}")
            log_issue("Dependencies", f"Missing external dependency: {dep}", 
                     f"Install with: pip install {dep}")

async def test_step_10_class_instantiation():
    """Test 10: Basic class instantiation"""
    print("\n🧪 TEST 10: Class Instantiation")
    
    try:
        # Mock config for testing
        mock_config = {
            "neo4j_uri": "bolt://localhost:7687",
            "neo4j_username": "neo4j",
            "neo4j_password": "test-password",
            "redis_url": "redis://localhost:6379",
            "chroma_persist_dir": "./test_chroma_db",
            "confidence_threshold": 0.92
        }
        
        # Test AIDGraphitiEngine instantiation
        try:
            from aid_commander_v41.knowledge_graph.graphiti.temporal_engine import AIDGraphitiEngine
            neo4j_config = {
                "uri": mock_config["neo4j_uri"],
                "username": mock_config["neo4j_username"],
                "password": mock_config["neo4j_password"]
            }
            engine = AIDGraphitiEngine(neo4j_config)
            log_test("Graphiti Engine Creation", "PASS", "AIDGraphitiEngine instantiated")
        except Exception as e:
            log_test("Graphiti Engine Creation", "FAIL", "Failed to create Graphiti engine", str(e))
            log_issue("Knowledge Graph", "Graphiti engine instantiation failed", "Fix constructor and dependencies")
        
        # Test HybridRAGSystem instantiation
        try:
            from aid_commander_v41.knowledge_graph.rag.hybrid_search import HybridRAGSystem
            chroma_config = {"persist_directory": mock_config["chroma_persist_dir"]}
            rag_system = HybridRAGSystem(chroma_config, neo4j_config)
            log_test("RAG System Creation", "PASS", "HybridRAGSystem instantiated")
        except Exception as e:
            log_test("RAG System Creation", "FAIL", "Failed to create RAG system", str(e))
            log_issue("Knowledge Graph", "RAG system instantiation failed", "Fix constructor and dependencies")
        
    except Exception as e:
        log_test("Class Instantiation", "FAIL", "Exception during instantiation tests", str(e))

async def test_step_11_file_structure_validation():
    """Test 11: Validate file structure and content"""
    print("\n🧪 TEST 11: File Structure Validation")
    
    try:
        project_root = Path("/Users/krissistrunk/Desktop/alwaysAccess.nosync/Sistronics/LearnstarAIDTest/AID_Commander/v4.1")
        
        # Check if main files have content
        main_files = [
            "aid_commander_v41/knowledge_graph/graphiti/temporal_engine.py",
            "aid_commander_v41/knowledge_graph/rag/hybrid_search.py", 
            "aid_commander_v41/validation/multi_layer/validation_engine.py",
            "aid_commander_v41/validation/hallucination/detection_engine.py",
            "aid_commander_v41/cli/main.py"
        ]
        
        for file_path in main_files:
            full_path = project_root / file_path
            if full_path.exists():
                content = full_path.read_text()
                if len(content) > 1000:  # Should have substantial content
                    log_test(f"File Content {file_path}", "PASS", f"File has {len(content)} characters")
                else:
                    log_test(f"File Content {file_path}", "FAIL", f"File too small: {len(content)} characters")
                    log_issue("File Content", f"File {file_path} has insufficient content", 
                             "Add proper implementation to the file")
            else:
                log_test(f"File Exists {file_path}", "FAIL", "File does not exist")
                log_issue("File Structure", f"Missing file: {file_path}", "Create the missing file")
                
    except Exception as e:
        log_test("File Structure Validation", "FAIL", "Exception during file validation", str(e))

def print_test_summary():
    """Print comprehensive test summary"""
    print("\n" + "="*80)
    print("🧪 AID COMMANDER v4.1 - COMPREHENSIVE TEST RESULTS")
    print("="*80)
    
    total_tests = len(test_results["passed"]) + len(test_results["failed"])
    pass_rate = len(test_results["passed"]) / total_tests * 100 if total_tests > 0 else 0
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {len(test_results['passed'])} ({pass_rate:.1f}%)")
    print(f"   Failed: {len(test_results['failed'])}")
    print(f"   Issues Found: {len(test_results['issues'])}")
    
    if test_results["failed"]:
        print(f"\n❌ FAILED TESTS:")
        for i, test in enumerate(test_results["failed"], 1):
            print(f"   {i}. {test['test']}: {test['details']}")
            if test['error']:
                print(f"      Error: {test['error']}")
    
    if test_results["issues"]:
        print(f"\n🔧 ISSUES TO FIX:")
        for i, issue in enumerate(test_results["issues"], 1):
            print(f"   {i}. {issue['component']}: {issue['issue']}")
            if issue['fix_suggestion']:
                print(f"      Fix: {issue['fix_suggestion']}")
    
    print(f"\n📋 FIXES NEEDED ({len(test_results['fixes_needed'])}):")
    fix_categories = {}
    for fix in test_results["fixes_needed"]:
        category = fix["component"].split()[0]  # Get first word as category
        if category not in fix_categories:
            fix_categories[category] = []
        fix_categories[category].append(fix)
    
    for category, fixes in fix_categories.items():
        print(f"\n   🔧 {category.upper()}:")
        for fix in fixes:
            print(f"      • {fix['issue']}")
    
    # Save results to file
    results_file = Path("/Users/krissistrunk/Desktop/alwaysAccess.nosync/Sistronics/LearnstarAIDTest/AID_Commander/v4.1/test_results.json")
    with open(results_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    if pass_rate >= 80:
        print(f"\n🎉 OVERALL: Good foundation - {pass_rate:.1f}% tests passing")
    elif pass_rate >= 60:
        print(f"\n⚠️  OVERALL: Needs work - {pass_rate:.1f}% tests passing")
    else:
        print(f"\n🚨 OVERALL: Significant issues - {pass_rate:.1f}% tests passing")

async def main():
    """Run comprehensive testing"""
    print("🚀 Starting AID Commander v4.1 Comprehensive Testing")
    print("="*60)
    
    # Run all test steps
    await test_step_1_project_structure()
    await test_step_2_basic_imports()
    await test_step_3_pyproject_toml()
    await test_step_4_docker_infrastructure()
    await test_step_5_cli_basic()
    await test_step_6_knowledge_graph_imports()
    await test_step_7_validation_imports()
    await test_step_8_memory_import()
    await test_step_9_dependency_check()
    await test_step_10_class_instantiation()
    await test_step_11_file_structure_validation()
    
    # Print comprehensive summary
    print_test_summary()

if __name__ == "__main__":
    asyncio.run(main())