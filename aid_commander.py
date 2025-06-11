#!/usr/bin/env python3
"""
AID Commander - Terminal-based tool for AI-Facilitated Iterative Development

Core commands:
- aid-commander init
- aid-commander start --project-name <name>
- aid-commander task add <task>
- aid-commander review
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from template_engine import TemplateEngine
from ai_service import AIService, OperationMode, should_use_ai, format_ai_suggestion
from logger import get_logger, get_error_handler, handle_errors

class AIDCommander:
    def __init__(self):
        self.config_dir = Path.home() / ".aid_commander"
        self.config_file = self.config_dir / "config.json"
        self.current_project = None
        self.project_dir = None
        self.template_engine = TemplateEngine()
        self.ai_service = AIService()
        self.logger = get_logger()
        self.error_handler = get_error_handler()
        
    @handle_errors("initialization")
    def init(self):
        """Initialize AID Commander"""
        self.logger.project_activity("Initializing AID Commander...")
        
        try:
            # Create config directory
            self.config_dir.mkdir(exist_ok=True)
            self.logger.debug(f"Created config directory: {self.config_dir}")
            
            # Create default config
            config = {
                "version": "2.0",
                "created": datetime.now().isoformat(),
                "projects": {},
                "settings": {
                    "confidence_threshold": 95,
                    "default_approach": "single_prd",
                    "operation_mode": "manual"
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            self.logger.success("AID Commander initialized successfully!")
            print(f"   Config saved to: {self.config_file}")
            print("\n📖 Next steps:")
            print("   1. Run: aid-commander start --project-name YourProject")
            print("   2. Follow the interactive setup process")
            
        except Exception as e:
            error_msg = self.error_handler.handle_config_error("initialization", e)
            print(error_msg)
            return False
        
    def start_project(self, project_name: str):
        """Start a new AID project"""
        self.logger.project_activity(f"Starting new AID project: {project_name}")
        
        try:
            # Create project directory
            project_dir = Path.cwd() / project_name
            project_dir.mkdir(exist_ok=True)
            
            # Project complexity assessment
            print("\n📊 Project Complexity Assessment")
            print("Answer these questions to choose the right approach:")
            
            questions = [
                "Will your project have more than 5-7 major features?",
                "Do you need multiple developers working simultaneously?", 
                "Are there distinct modules for independent development?",
                "Will different parts use different technologies?",
                "Complex integration with multiple external systems?"
            ]
            
            yes_count = 0
            for i, question in enumerate(questions, 1):
                answer = input(f"{i}. {question} (y/n): ").lower().strip()
                if answer.startswith('y'):
                    yes_count += 1
                    
            # Determine approach
            if yes_count >= 3:
                approach = "multi_component"
                print(f"\n📈 Recommendation: Multi-Component Approach ({yes_count}/5 complex indicators)")
            else:
                approach = "single_prd"  
                print(f"\n📉 Recommendation: Single PRD Approach ({yes_count}/5 complex indicators)")
                
            # Create project structure
            self._create_project_structure(project_dir, approach, project_name)
            
            # Update config
            self._update_project_config(project_name, project_dir, approach)
        
            print(f"\n🎉 Project {project_name} created successfully!")
            print(f"📁 Location: {project_dir}")
            print(f"🛠️ Approach: {approach}")
            print(f"\n📖 Next steps:")
            if approach == "single_prd":
                print(f"   1. Edit {project_name}_PRD.md with your requirements")
                print("   2. Run: aid-commander task generate")
            else:
                print(f"   1. Edit {project_name}_MPD.md to coordinate components") 
                print("   2. Create component PRDs for each module")
                print("   3. Run: aid-commander task generate")
                
        except Exception as e:
            error_msg = self.error_handler.handle_file_error("project creation", Path.cwd() / project_name, e)
            print(error_msg)
            
    def _create_project_structure(self, project_dir: Path, approach: str, project_name: str):
        """Create project files and directories using template engine"""
        
        # Collect user information for templates
        user_input = self._collect_user_info()
        
        if approach == "single_prd":
            # Single PRD approach using real template
            print("📝 Creating PRD from template...")
            prd_file = self.template_engine.create_prd(project_name, project_dir, user_input)
            print(f"✅ Created: {prd_file}")
            
            # Create tasks file
            tasks_file = self._create_tasks_file(project_dir, project_name)
            print(f"✅ Created: {tasks_file}")
            
        else:
            # Multi-component approach using real templates
            print("📝 Creating MPD from template...")
            mpd_file = self.template_engine.create_mpd(project_name, project_dir, user_input)
            print(f"✅ Created: {mpd_file}")
            
            print("📝 Creating Integration Strategy from template...")
            integration_file = self.template_engine.create_integration_strategy(project_name, project_dir, user_input)
            print(f"✅ Created: {integration_file}")
            
            # Create tasks file for multi-component
            tasks_file = self._create_tasks_file(project_dir, project_name)
            print(f"✅ Created: {tasks_file}")
            
        # Create enhanced project structure
        self._create_enhanced_directories(project_dir, approach)
        
    def _collect_user_info(self) -> Dict[str, str]:
        """Collect user information for template personalization"""
        print("\n📋 Template Personalization (optional - press Enter to skip)")
        
        user_input = {}
        
        # Optional fields with defaults
        optional_fields = [
            ("product_owner", "Product Owner name"),
            ("design_facilitator", "Design Facilitator name"), 
            ("author", "Author name"),
            ("program_owner", "Program Owner name (for MPD)")
        ]
        
        try:
            for field, description in optional_fields:
                value = input(f"  {description}: ").strip()
                if value:
                    user_input[field] = value
        except (EOFError, KeyboardInterrupt):
            print("\n📝 Using default template values")
                
        return user_input
        
    def _create_tasks_file(self, project_dir: Path, project_name: str) -> Path:
        """Create enhanced tasks file"""
        tasks_file = project_dir / f"{project_name}_Tasks.md"
        
        tasks_content = f"""# {project_name} - Task Tracking

## Task Status Legend
- `[ ]` Ready to start (dependencies met)
- `[!]` Waiting for clarification (need more info)
- `[>]` Currently working on
- `[R]` Needs revision (review failed)
- `[x]` Complete and approved

## Implementation Tasks

### Generated from Templates
*Use 'aid-commander task generate' to extract tasks from your PRD/MPD*

### Manual Tasks
*Use 'aid-commander task add "description"' to add manual tasks*

---
*Generated by AID Commander v2.0*
"""
        tasks_file.write_text(tasks_content)
        return tasks_file
        
    def _create_enhanced_directories(self, project_dir: Path, approach: str):
        """Create enhanced project directory structure"""
        
        # Standard directories
        directories = [
            "src",
            "tests", 
            "docs",
            "config",
            ".aid_commander"  # Project-specific AID data
        ]
        
        # Approach-specific directories
        if approach == "multi_component":
            directories.extend([
                "components",
                "shared",
                "integration"
            ])
            
        for dir_name in directories:
            dir_path = project_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            
            # Create .gitkeep for empty directories
            if dir_name not in ["src", "tests"]:
                (dir_path / ".gitkeep").touch()
                
        print(f"✅ Created {len(directories)} project directories")
        
    def _update_project_config(self, project_name: str, project_dir: Path, approach: str):
        """Update configuration with new project"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {"projects": {}}
            
        config["projects"][project_name] = {
            "path": str(project_dir),
            "approach": approach,
            "created": datetime.now().isoformat(),
            "status": "active"
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
    def add_task(self, task_description: str):
        """Add a new task to current project"""
        try:
            current_project = self._get_current_project()
            if not current_project:
                self.logger.warning("No active project found")
                print("❌ No active project. Run 'aid-commander start --project-name <name>' first")
                return
                
            self.logger.task_activity(f"Adding task: {task_description}")
            
            # Check AI mode for task analysis
            current_mode = self.ai_service.get_mode()
            
            if should_use_ai(current_mode):
                try:
                    import asyncio
                    # Get AI analysis of the task
                    analysis = asyncio.run(self.ai_service.analyze_task(task_description, ""))
                    status = "[ ]"  # Ready (AI analyzed)
                    print(f"🤖 AI Analysis: {analysis.complexity} complexity, ~{analysis.estimated_effort}")
                    if analysis.suggestions:
                        print(f"💡 Suggestions: {', '.join(analysis.suggestions[:2])}")
                except Exception as e:
                    status = "[ ]"  # Ready (fallback)
                    print(f"✅ Task ready for implementation (AI analysis unavailable: {e})")
            else:
                # Manual mode - always ready (user manages complexity)
                status = "[ ]"  # Ready
                print(f"✅ Task ready for implementation (Manual Mode)")
            
            # Add to tasks file with enhanced format
            project_name = current_project["name"]
            tasks_file = Path(current_project["path"]) / f"{project_name}_Tasks.md"
            
            if tasks_file.exists():
                content = tasks_file.read_text()
                
                # Find the "Manual Tasks" section
                if "### Manual Tasks" in content:
                    # Insert after the manual tasks header
                    lines = content.split('\n')
                    insert_index = None
                    for i, line in enumerate(lines):
                        if line.strip() == "### Manual Tasks":
                            # Skip any existing description lines
                            j = i + 1
                            while j < len(lines) and (lines[j].startswith('*') or lines[j].strip() == ''):
                                j += 1
                            insert_index = j
                            break
                            
                    if insert_index is not None:
                        new_task = f"{status} {task_description} (Added: {datetime.now().strftime('%Y-%m-%d %H:%M')})"
                        lines.insert(insert_index, new_task)
                        content = '\n'.join(lines)
                    else:
                        # Fallback: append to end
                        new_task = f"\n{status} {task_description} (Added: {datetime.now().strftime('%Y-%m-%d %H:%M')})"
                        content += new_task
                else:
                    # No "Manual Tasks" section found, append to end
                    new_task = f"\n{status} {task_description} (Added: {datetime.now().strftime('%Y-%m-%d %H:%M')})"
                    content += new_task
            else:
                # Create basic content structure if file doesn't exist
                content = f"# {project_name} Tasks\n\n### Manual Tasks\n\n{status} {task_description} (Added: {datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
                
            tasks_file.write_text(content)
            self.logger.success(f"Task added to {tasks_file}")
            
        except Exception as e:
            error_msg = self.error_handler.handle_unexpected_error("add task", e)
            print(error_msg)
            
    def generate_tasks(self):
        """Generate tasks from PRD/MPD templates"""
        current_project = self._get_current_project()
        if not current_project:
            print("❌ No active project found")
            return
            
        print("🔄 Generating tasks from templates...")
        
        project_name = current_project["name"]
        project_path = Path(current_project["path"])
        approach = current_project.get("approach", "single_prd")
        
        # Find template files
        if approach == "single_prd":
            template_file = project_path / f"{project_name}_PRD.md"
            template_type = "prd"
        else:
            template_file = project_path / f"{project_name}_MPD.md"
            template_type = "mpd"
            
        if not template_file.exists():
            print(f"❌ Template file not found: {template_file}")
            print(f"   Please create your {template_type.upper()} first")
            return
            
        # Validate template completeness
        is_complete, issues = self.template_engine.validate_template_completeness(template_file, template_type)
        
        if not is_complete:
            print("⚠️  Template validation issues found:")
            for issue in issues[:5]:  # Show first 5 issues
                print(f"   - {issue}")
            if len(issues) > 5:
                print(f"   ... and {len(issues) - 5} more issues")
                
            try:
                proceed = input("\nProceed with task generation anyway? (y/n): ").lower().strip()
                if not proceed.startswith('y'):
                    print("❌ Task generation cancelled")
                    return
            except (EOFError, KeyboardInterrupt):
                print("\n📝 Proceeding with task generation")
                pass
                
        # Extract tasks from template (with AI enhancement if available)
        current_mode = self.ai_service.get_mode()
        
        if should_use_ai(current_mode):
            try:
                import asyncio
                print("🤖 Generating AI-enhanced tasks...")
                ai_response = asyncio.run(self.ai_service.generate_ai_tasks(template_file, template_type))
                
                if ai_response.confidence >= 70:  # Use AI tasks if confident
                    print(f"✨ AI generated tasks (confidence: {ai_response.confidence:.0f}%)")
                    # Parse AI response into task format
                    tasks = self._parse_ai_tasks(ai_response.content)
                else:
                    print(f"⚠️  AI confidence low ({ai_response.confidence:.0f}%), using template extraction")
                    tasks = self.template_engine.extract_tasks_from_prd(template_file)
                    
            except Exception as e:
                print(f"⚠️  AI task generation failed: {e}")
                print("📝 Falling back to template extraction")
                tasks = self.template_engine.extract_tasks_from_prd(template_file)
        else:
            # Manual mode - use template engine
            tasks = self.template_engine.extract_tasks_from_prd(template_file)
        
        if not tasks:
            print("❌ No tasks found in template")
            print("   Try adding implementation sections with numbered items or bullet points")
            return
            
        print(f"✅ Found {len(tasks)} tasks in {template_type.upper()}")
        
        # Add tasks to tasks file
        tasks_file = project_path / f"{project_name}_Tasks.md"
        if tasks_file.exists():
            content = tasks_file.read_text()
            
            # Find the "Generated from Templates" section
            generated_section = "### Generated from Templates"
            if generated_section in content:
                lines = content.split('\n')
                insert_index = None
                for i, line in enumerate(lines):
                    if line.strip() == generated_section:
                        # Skip description lines
                        j = i + 1
                        while j < len(lines) and (lines[j].startswith('*') or lines[j].strip() == ''):
                            j += 1
                        insert_index = j
                        break
                        
                if insert_index is not None:
                    # Clear existing generated tasks
                    new_lines = []
                    for i, line in enumerate(lines):
                        if i < insert_index:
                            new_lines.append(line)
                        elif i >= insert_index and line.startswith('###'):
                            # Reached next section, add remaining lines
                            new_lines.extend(lines[i:])
                            break
                            
                    # Add new tasks
                    for task in tasks:
                        task_line = f"{task['status']} {task['description']} (from {task['section']})"
                        new_lines.insert(insert_index, task_line)
                        insert_index += 1
                        
                    content = '\n'.join(new_lines)
                    tasks_file.write_text(content)
                    print(f"✅ Added {len(tasks)} generated tasks to {tasks_file}")
                else:
                    print("❌ Could not find insertion point in tasks file")
            else:
                print("❌ Tasks file format not recognized")
        else:
            print(f"❌ Tasks file not found: {tasks_file}")
            
    def validate_templates(self):
        """Validate current project templates"""
        current_project = self._get_current_project()
        if not current_project:
            print("❌ No active project found")
            return
            
        print("🔍 Validating project templates...")
        
        project_name = current_project["name"]
        project_path = Path(current_project["path"])
        approach = current_project.get("approach", "single_prd")
        
        templates_to_check = []
        
        if approach == "single_prd":
            prd_file = project_path / f"{project_name}_PRD.md"
            if prd_file.exists():
                templates_to_check.append((prd_file, "prd"))
        else:
            mpd_file = project_path / f"{project_name}_MPD.md"
            integration_file = project_path / f"{project_name}_Integration.md"
            
            if mpd_file.exists():
                templates_to_check.append((mpd_file, "mpd"))
            if integration_file.exists():
                templates_to_check.append((integration_file, "integration"))
                
        if not templates_to_check:
            print("❌ No templates found to validate")
            return
            
        all_valid = True
        
        for template_file, template_type in templates_to_check:
            print(f"\n📋 Validating {template_file.name}...")
            
            is_complete, issues = self.template_engine.validate_template_completeness(template_file, template_type)
            
            if is_complete:
                print(f"✅ {template_file.name} is complete and ready")
            else:
                print(f"⚠️  {template_file.name} has {len(issues)} issues:")
                for issue in issues:
                    print(f"   - {issue}")
                all_valid = False
                
        if all_valid:
            print("\n🎉 All templates are valid and ready for task generation!")
        else:
            print("\n⚠️  Please address template issues before proceeding")
            
    def update_task_status(self, task_id: str, new_status: str):
        """Update the status of a specific task"""
        current_project = self._get_current_project()
        if not current_project:
            print("❌ No active project found")
            return
            
        valid_statuses = ["[ ]", "[!]", "[>]", "[R]", "[x]"]
        status_names = {
            "pending": "[ ]",
            "clarification": "[!]", 
            "working": "[>]",
            "revision": "[R]",
            "complete": "[x]"
        }
        
        # Convert status name to symbol
        if new_status in status_names:
            new_status = status_names[new_status]
        elif new_status not in valid_statuses:
            print(f"❌ Invalid status: {new_status}")
            print(f"   Valid options: {', '.join(status_names.keys())} or {', '.join(valid_statuses)}")
            return
            
        project_name = current_project["name"]
        tasks_file = Path(current_project["path"]) / f"{project_name}_Tasks.md"
        
        if not tasks_file.exists():
            print(f"❌ Tasks file not found: {tasks_file}")
            return
            
        content = tasks_file.read_text()
        lines = content.split('\n')
        
        # Find and update the task
        task_found = False
        for i, line in enumerate(lines):
            if line.strip().startswith(('[', '[')):  # Task line
                # Extract task number or match by partial description
                if task_id.isdigit():
                    # Match by line number (1-based)
                    task_lines = [j for j, l in enumerate(lines) if l.strip().startswith(('[', '['))]
                    try:
                        target_line = task_lines[int(task_id) - 1]
                        if i == target_line:
                            # Update status
                            old_status = line.strip()[:3]
                            lines[i] = line.replace(old_status, new_status, 1)
                            task_found = True
                            print(f"✅ Updated task {task_id}: {old_status} → {new_status}")
                            break
                    except (IndexError, ValueError):
                        continue
                else:
                    # Match by description substring
                    if task_id.lower() in line.lower():
                        old_status = line.strip()[:3]
                        lines[i] = line.replace(old_status, new_status, 1)
                        task_found = True
                        print(f"✅ Updated task: {old_status} → {new_status}")
                        print(f"   {line.strip()}")
                        break
                        
        if not task_found:
            print(f"❌ Task not found: {task_id}")
            print("   Use 'aid-commander review' to see all tasks")
            return
            
        # Save updated content
        tasks_file.write_text('\n'.join(lines))
        print(f"✅ Tasks file updated: {tasks_file}")
        
    def list_tasks(self, status_filter: str = None):
        """List tasks with optional status filter"""
        current_project = self._get_current_project()
        if not current_project:
            print("❌ No active project found")
            return
            
        project_name = current_project["name"]
        tasks_file = Path(current_project["path"]) / f"{project_name}_Tasks.md"
        
        if not tasks_file.exists():
            print(f"❌ Tasks file not found: {tasks_file}")
            return
            
        content = tasks_file.read_text()
        lines = content.split('\n')
        
        # Extract tasks
        tasks = []
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped.startswith(('[', '[')):
                status = line_stripped[:3]
                description = line_stripped[3:].strip()
                tasks.append({
                    'number': len(tasks) + 1,
                    'status': status,
                    'description': description,
                    'line': i + 1
                })
                
        if not tasks:
            print("📋 No tasks found")
            return
            
        # Filter by status if specified
        if status_filter:
            status_map = {
                "pending": "[ ]",
                "clarification": "[!]",
                "working": "[>]", 
                "revision": "[R]",
                "complete": "[x]"
            }
            filter_status = status_map.get(status_filter, status_filter)
            tasks = [t for t in tasks if t['status'] == filter_status]
            
        if not tasks:
            print(f"📋 No tasks found with status: {status_filter}")
            return
            
        # Display tasks
        print(f"📋 Tasks in {project_name}:")
        if status_filter:
            print(f"   Filter: {status_filter}")
        print("-" * 50)
        
        for task in tasks:
            print(f"{task['number']:2d}. {task['status']} {task['description']}")
            
        print(f"\n📊 Total: {len(tasks)} tasks")
        
    def review_tasks(self):
        """Review completed tasks"""
        current_project = self._get_current_project()
        if not current_project:
            print("❌ No active project found")
            return
            
        print("🔍 Reviewing project tasks...")
        
        project_name = current_project["name"]
        tasks_file = Path(current_project["path"]) / f"{project_name}_Tasks.md"
        
        if tasks_file.exists():
            content = tasks_file.read_text()
            print(f"\n📋 Current tasks in {project_name}:")
            print("=" * 50)
            print(content)
        else:
            print(f"❌ No tasks file found: {tasks_file}")
            
    def _get_current_project(self):
        """Get current active project"""
        if not self.config_file.exists():
            return None
            
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            
        # Find active project in current directory
        current_dir = Path.cwd()
        for name, project in config.get("projects", {}).items():
            project_path = Path(project["path"])
            if current_dir == project_path or current_dir.is_relative_to(project_path):
                return {"name": name, **project}
                
        return None
        
    def list_projects(self):
        """List all projects"""
        if not self.config_file.exists():
            print("❌ No projects found. Run 'aid-commander init' first")
            return
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print("❌ Configuration file corrupted. Run 'aid-commander init' to reset")
            return
        except Exception as e:
            error_msg = self.error_handler.handle_file_error("list projects", self.config_file, e)
            print(error_msg)
            return
            
        projects = config.get("projects", {})
        if not projects:
            print("📂 No projects found")
            return
            
        print("📂 AID Commander Projects:")
        print("=" * 40)
        for name, project in projects.items():
            status = "🟢" if project.get("status") == "active" else "🔴"
            print(f"{status} {name}")
            print(f"   Path: {project['path']}")
            print(f"   Approach: {project['approach']}")
            print(f"   Created: {project['created'][:10]}")
            print()
            
    def set_mode(self, mode: str):
        """Set operation mode (manual/automated/hybrid)"""
        valid_modes = ["manual", "automated", "hybrid"]
        if mode not in valid_modes:
            print(f"❌ Invalid mode: {mode}")
            print(f"   Valid modes: {', '.join(valid_modes)}")
            return
            
        # Update AI service mode
        try:
            ai_mode = OperationMode(mode)
            self.ai_service.set_mode(ai_mode)
            
            # Update main config
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {"settings": {}}
                
            config.setdefault("settings", {})["operation_mode"] = mode
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            print(f"✅ Operation mode set to: {mode}")
            
            if mode == "automated":
                print("🤖 Automated mode: AI will generate and manage tasks")
            elif mode == "hybrid":
                print("🤝 Hybrid mode: AI suggestions with user approval")
            else:
                print("👤 Manual mode: User-driven task management")
                
        except Exception as e:
            print(f"❌ Error setting mode: {e}")
            
    def get_status(self):
        """Get AID Commander and AI service status"""
        print("📊 AID Commander Status")
        print("=" * 40)
        
        # Main config status
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            print(f"Version: {config.get('version', 'Unknown')}")
            print(f"Operation Mode: {config.get('settings', {}).get('operation_mode', 'manual')}")
        else:
            print("Status: Not initialized")
            
        # Current project
        current_project = self._get_current_project()
        if current_project:
            print(f"Current Project: {current_project['name']}")
            print(f"Project Path: {current_project['path']}")
        else:
            print("Current Project: None")
            
        # AI Service status
        ai_status = self.ai_service.get_status()
        print(f"\n🤖 AI Service Status")
        print(f"AI Mode: {ai_status['mode']}")
        print(f"AI Provider: {ai_status['provider']}")
        print(f"Confidence Threshold: {ai_status['confidence_threshold']}%")
        
    def _parse_ai_tasks(self, ai_content: str) -> List[Dict[str, str]]:
        """Parse AI-generated task content into task format"""
        tasks = []
        lines = ai_content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for numbered items, bullet points, or task-like patterns
            if (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or
                line.startswith(('- ', '* ', '• ')) or
                line.startswith('Task:')):
                
                # Clean up the line
                description = line
                for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '- ', '* ', '• ', 'Task:']:
                    if description.startswith(prefix):
                        description = description[len(prefix):].strip()
                        break
                        
                if description and len(description) > 5:  # Filter out too short descriptions
                    tasks.append({
                        'description': description,
                        'status': '[ ]',  # Ready
                        'section': 'AI Generated'
                    })
                    
        return tasks

def main():
    parser = argparse.ArgumentParser(description="AID Commander - AI-Facilitated Iterative Development")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    subparsers.add_parser('init', help='Initialize AID Commander')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start a new project')
    start_parser.add_argument('--project-name', required=True, help='Name of the project')
    
    # Task commands
    task_parser = subparsers.add_parser('task', help='Task management')
    task_subparsers = task_parser.add_subparsers(dest='task_action')
    
    add_task_parser = task_subparsers.add_parser('add', help='Add a new task')
    add_task_parser.add_argument('description', help='Task description')
    
    task_subparsers.add_parser('generate', help='Generate tasks from PRD/MPD templates')
    
    list_task_parser = task_subparsers.add_parser('list', help='List all tasks')
    list_task_parser.add_argument('--status', help='Filter by status (pending, working, complete, etc.)')
    
    status_parser = task_subparsers.add_parser('status', help='Update task status')
    status_parser.add_argument('task_id', help='Task number or description substring')
    status_parser.add_argument('new_status', help='New status (pending, working, complete, etc.)')
    
    # Template commands
    template_parser = subparsers.add_parser('template', help='Template management')
    template_subparsers = template_parser.add_subparsers(dest='template_action')
    
    template_subparsers.add_parser('validate', help='Validate current project templates')
    
    # Review command
    subparsers.add_parser('review', help='Review project tasks')
    
    # List command
    subparsers.add_parser('list', help='List all projects')
    
    # Mode command
    mode_parser = subparsers.add_parser('mode', help='Set operation mode')
    mode_parser.add_argument('operation_mode', choices=['manual', 'automated', 'hybrid'], 
                           help='Operation mode to set')
    
    # Status command
    subparsers.add_parser('status', help='Show AID Commander status')
    
    # Setup command
    subparsers.add_parser('setup', help='Run AI setup wizard')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    commander = AIDCommander()
    
    if args.command == 'init':
        commander.init()
    elif args.command == 'start':
        commander.start_project(args.project_name)
    elif args.command == 'task':
        if args.task_action == 'add':
            commander.add_task(args.description)
        elif args.task_action == 'generate':
            commander.generate_tasks()
        elif args.task_action == 'list':
            commander.list_tasks(args.status)
        elif args.task_action == 'status':
            commander.update_task_status(args.task_id, args.new_status)
        else:
            print("❌ Unknown task action. Use 'add', 'generate', 'list', or 'status'")
    elif args.command == 'template':
        if args.template_action == 'validate':
            commander.validate_templates()
        else:
            print("❌ Unknown template action. Use 'validate'")
    elif args.command == 'review':
        commander.review_tasks()
    elif args.command == 'list':
        commander.list_projects()
    elif args.command == 'mode':
        commander.set_mode(args.operation_mode)
    elif args.command == 'status':
        commander.get_status()
    elif args.command == 'setup':
        from ai_setup_wizard import AISetupWizard
        wizard = AISetupWizard()
        wizard.run()
    else:
        print(f"❌ Unknown command: {args.command}")

if __name__ == "__main__":
    main()