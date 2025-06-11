#!/usr/bin/env python3
"""
Comprehensive test suite for AID Commander
Tests core functionality, error handling, and edge cases
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import modules to test
from aid_commander import AIDCommander
from template_engine import TemplateEngine
from logger import AIDLogger, ErrorHandler
from ai_service import AIService, OperationMode, AIProvider


class TestAIDCommander(unittest.TestCase):
    """Test the main AID Commander functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.test_dir)
        
        # Mock the config directory to avoid affecting real config
        self.config_dir = self.test_dir / ".aid_commander"
        
        with patch.object(Path, 'home', return_value=self.test_dir):
            self.commander = AIDCommander()
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test AID Commander initialization"""
        self.commander.init()
        
        # Check config file was created
        self.assertTrue(self.commander.config_file.exists())
        
        # Check config content
        with open(self.commander.config_file, 'r') as f:
            config = json.load(f)
        
        self.assertEqual(config["version"], "2.0")
        self.assertIn("projects", config)
        self.assertIn("settings", config)
        self.assertEqual(config["settings"]["operation_mode"], "manual")
    
    def test_project_creation_single_prd(self):
        """Test creating a single PRD project"""
        # Initialize first
        self.commander.init()
        
        # Mock user input for single PRD approach (all 'n' answers)
        with patch('builtins.input', side_effect=['n'] * 9):  # 5 complexity questions + 4 personalization
            self.commander.start_project("TestProject")
        
        # Check project directory was created
        project_dir = self.test_dir / "TestProject"
        self.assertTrue(project_dir.exists())
        
        # Check essential files were created
        self.assertTrue((project_dir / "TestProject_PRD.md").exists())
        self.assertTrue((project_dir / "TestProject_Tasks.md").exists())
        
        # Check project structure
        self.assertTrue((project_dir / "src").exists())
        self.assertTrue((project_dir / "tests").exists())
        self.assertTrue((project_dir / "docs").exists())
    
    def test_project_creation_multi_component(self):
        """Test creating a multi-component project"""
        self.commander.init()
        
        # Mock user input for multi-component approach (all 'y' for complexity)
        with patch('builtins.input', side_effect=['y'] * 5 + [''] * 4):  # 5 'y' + 4 empty personalization
            self.commander.start_project("ComplexProject")
        
        project_dir = self.test_dir / "ComplexProject"
        
        # Check MPD files were created
        self.assertTrue((project_dir / "ComplexProject_MPD.md").exists())
        self.assertTrue((project_dir / "ComplexProject_Integration.md").exists())
        
        # Check multi-component directories
        self.assertTrue((project_dir / "components").exists())
        self.assertTrue((project_dir / "shared").exists())
        self.assertTrue((project_dir / "integration").exists())
    
    def test_task_operations(self):
        """Test task add, list, and status operations"""
        # Setup project
        self.commander.init()
        with patch('builtins.input', side_effect=['n'] * 9):
            self.commander.start_project("TaskTest")
        
        os.chdir(self.test_dir / "TaskTest")
        
        # Test adding a task
        self.commander.add_task("Test task description")
        
        # Check task was added to file
        tasks_file = Path("TaskTest_Tasks.md")
        content = tasks_file.read_text()
        self.assertIn("Test task description", content)
        self.assertIn("[ ]", content)  # Should have ready status
        
        # Test updating task status
        self.commander.update_task_status("1", "working")
        
        content = tasks_file.read_text()
        self.assertIn("[>]", content)  # Should have working status
    
    def test_template_validation(self):
        """Test template validation functionality"""
        self.commander.init()
        with patch('builtins.input', side_effect=['n'] * 9):
            self.commander.start_project("ValidateTest")
        
        os.chdir(self.test_dir / "ValidateTest")
        
        # Test validation - should pass for newly created template
        self.commander.validate_templates()
        
        # Test with incomplete template
        prd_file = Path("ValidateTest_PRD.md")
        prd_file.write_text("# Incomplete PRD\n\nThis is incomplete.")
        
        # Should detect issues
        self.commander.validate_templates()
    
    def test_mode_switching(self):
        """Test operation mode switching"""
        self.commander.init()
        
        # Test switching to different modes
        self.commander.set_mode("hybrid")
        self.assertEqual(self.commander.ai_service.get_mode(), OperationMode.HYBRID)
        
        self.commander.set_mode("automated")
        self.assertEqual(self.commander.ai_service.get_mode(), OperationMode.AUTOMATED)
        
        self.commander.set_mode("manual")
        self.assertEqual(self.commander.ai_service.get_mode(), OperationMode.MANUAL)
        
        # Test invalid mode
        self.commander.set_mode("invalid")
        # Should remain in manual mode
        self.assertEqual(self.commander.ai_service.get_mode(), OperationMode.MANUAL)
    
    def test_project_listing(self):
        """Test project listing functionality"""
        self.commander.init()
        
        # Create multiple projects
        with patch('builtins.input', side_effect=['n'] * 9):
            self.commander.start_project("Project1")
        with patch('builtins.input', side_effect=['y'] * 5 + [''] * 4):
            self.commander.start_project("Project2")
        
        # Test listing projects
        self.commander.list_projects()
        
        # Check config contains both projects
        with open(self.commander.config_file, 'r') as f:
            config = json.load(f)
        
        self.assertIn("Project1", config["projects"])
        self.assertIn("Project2", config["projects"])


class TestTemplateEngine(unittest.TestCase):
    """Test the template engine functionality"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.template_engine = TemplateEngine()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_prd_creation(self):
        """Test PRD template creation"""
        user_input = {
            "product_owner": "Test Owner",
            "author": "Test Author"
        }
        
        prd_file = self.template_engine.create_prd("TestApp", self.test_dir, user_input)
        
        self.assertTrue(prd_file.exists())
        
        content = prd_file.read_text()
        self.assertIn("TestApp", content)
        self.assertIn("Test Owner", content)
        self.assertIn("Test Author", content)
    
    def test_mpd_creation(self):
        """Test MPD template creation"""
        user_input = {
            "program_owner": "Test Program Owner"
        }
        
        mpd_file = self.template_engine.create_mpd("TestSystem", self.test_dir, user_input)
        
        self.assertTrue(mpd_file.exists())
        
        content = mpd_file.read_text()
        self.assertIn("TestSystem", content)
        self.assertIn("Test Program Owner", content)
    
    def test_task_extraction(self):
        """Test task extraction from templates"""
        # Create a test PRD with tasks
        test_prd = self.test_dir / "test.md"
        test_prd.write_text("""
# Test PRD

## Implementation Tasks

1. Set up the database
2. Create user authentication
3. Build the frontend

## Technical Implementation

- Database design and setup
- API endpoint creation
- Frontend component development
        """)
        
        tasks = self.template_engine.extract_tasks_from_prd(test_prd)
        
        self.assertGreater(len(tasks), 0)
        self.assertTrue(any("database" in task["description"].lower() for task in tasks))
        self.assertTrue(any("authentication" in task["description"].lower() for task in tasks))
    
    def test_template_validation(self):
        """Test template validation"""
        # Create incomplete PRD
        incomplete_prd = self.test_dir / "incomplete.md"
        incomplete_prd.write_text("# Incomplete PRD\n\nThis is missing sections.")
        
        is_complete, issues = self.template_engine.validate_template_completeness(incomplete_prd, "prd")
        
        self.assertFalse(is_complete)
        self.assertGreater(len(issues), 0)
        
        # Create complete PRD
        complete_prd = self.test_dir / "complete.md"
        complete_prd.write_text("""
# Complete PRD

## Project Overview
This is a complete project overview.

## Target Users
Target users are defined here.

## Core Features
1. Feature one
2. Feature two

## Technical Requirements
Technical requirements listed.

## Success Metrics
Success metrics defined.

## Implementation Plan
1. Step one
2. Step two
        """)
        
        is_complete, issues = self.template_engine.validate_template_completeness(complete_prd, "prd")
        
        self.assertTrue(is_complete)
        self.assertEqual(len(issues), 0)


class TestAIService(unittest.TestCase):
    """Test AI service functionality"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Mock config path
        with patch.object(Path, 'home', return_value=self.test_dir):
            self.ai_service = AIService()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_mode_management(self):
        """Test operation mode management"""
        # Test default mode
        self.assertEqual(self.ai_service.get_mode(), OperationMode.MANUAL)
        
        # Test mode switching
        self.ai_service.set_mode(OperationMode.HYBRID)
        self.assertEqual(self.ai_service.get_mode(), OperationMode.HYBRID)
        
        self.ai_service.set_mode(OperationMode.AUTOMATED)
        self.assertEqual(self.ai_service.get_mode(), OperationMode.AUTOMATED)
    
    def test_config_creation(self):
        """Test AI configuration file creation"""
        # Config should be created automatically
        self.assertTrue(self.ai_service.config_path.exists())
        
        # Check default configuration
        config = self.ai_service.config
        self.assertIn("mode", config)
        self.assertIn("provider", config)
        self.assertIn("providers", config)
    
    def test_status_reporting(self):
        """Test AI service status reporting"""
        status = self.ai_service.get_status()
        
        self.assertIn("mode", status)
        self.assertIn("provider", status)
        self.assertIn("confidence_threshold", status)
        self.assertIn("available_providers", status)


class TestLogger(unittest.TestCase):
    """Test logging functionality"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        
        with patch.object(Path, 'home', return_value=self.test_dir):
            self.logger = AIDLogger()
            self.error_handler = ErrorHandler(self.logger)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_logger_creation(self):
        """Test logger creation and setup"""
        # Log directory should be created (either in home or temp fallback)
        log_dir = self.test_dir / ".aid_commander" / "logs"
        import tempfile
        fallback_dir = Path(tempfile.gettempdir()) / "aid_commander_logs"
        self.assertTrue(log_dir.exists() or fallback_dir.exists())
    
    def test_error_handling(self):
        """Test error handling functionality"""
        # Test file error handling
        file_error = FileNotFoundError("Test file not found")
        message = self.error_handler.handle_file_error("test operation", Path("test.txt"), file_error)
        self.assertIn("File not found", message)
        
        # Test network error handling
        network_error = Exception("401 Unauthorized")
        message = self.error_handler.handle_network_error("test API call", network_error)
        self.assertIn("authentication failed", message.lower())


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.test_dir)
        
        with patch.object(Path, 'home', return_value=self.test_dir):
            self.commander = AIDCommander()
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_no_project_operations(self):
        """Test operations when no project is active"""
        self.commander.init()
        
        # These should handle gracefully with no project
        self.commander.add_task("Test task")
        self.commander.generate_tasks()
        self.commander.validate_templates()
        self.commander.review_tasks()
    
    def test_corrupted_config(self):
        """Test handling of corrupted configuration"""
        self.commander.init()
        
        # Corrupt the config file
        self.commander.config_file.write_text("invalid json content")
        
        # Operations should handle gracefully
        self.commander.list_projects()
    
    def test_missing_template_files(self):
        """Test operations with missing template files"""
        self.commander.init()
        with patch('builtins.input', side_effect=['n'] * 9):
            self.commander.start_project("MissingTemplateTest")
        
        os.chdir(self.test_dir / "MissingTemplateTest")
        
        # Remove the PRD file
        Path("MissingTemplateTest_PRD.md").unlink()
        
        # Generate tasks should handle missing template
        self.commander.generate_tasks()
    
    def test_permission_errors(self):
        """Test handling of permission errors"""
        self.commander.init()
        
        # Make config directory read-only
        os.chmod(self.commander.config_dir, 0o444)
        
        try:
            # This should handle permission error gracefully
            self.commander.init()
        finally:
            # Restore permissions for cleanup
            os.chmod(self.commander.config_dir, 0o755)


def run_all_tests():
    """Run all test suites"""
    print("🧪 Running AID Commander Test Suite")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestAIDCommander,
        TestTemplateEngine,
        TestAIService,
        TestLogger,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("🧪 Test Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if not result.failures and not result.errors:
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n⚠️  Some tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)