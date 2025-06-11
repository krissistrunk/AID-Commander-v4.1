#!/usr/bin/env python3
"""
Template Engine for AID Commander
Parses and manages AID templates (PRD, MPD, Integration Strategy)
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class TemplateEngine:
    def __init__(self, templates_dir: Path = None):
        """Initialize template engine with templates directory"""
        if templates_dir is None:
            templates_dir = Path(__file__).parent
        self.templates_dir = templates_dir
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, str]:
        """Load all available templates"""
        templates = {}
        
        # Standard AID templates
        template_files = {
            'prd': 'AID_PRD_Template.md',
            'mpd': 'MPD_Template.md', 
            'integration': 'Integration_Strategy_Template.md'
        }
        
        for template_type, filename in template_files.items():
            template_path = self.templates_dir / filename
            if template_path.exists():
                templates[template_type] = template_path.read_text()
            else:
                print(f"⚠️  Template not found: {template_path}")
                
        return templates
        
    def create_prd(self, project_name: str, project_dir: Path, 
                  user_input: Dict[str, str] = None) -> Path:
        """Create a PRD from template with user input"""
        if 'prd' not in self.templates:
            raise FileNotFoundError("PRD template not found")
            
        template = self.templates['prd']
        user_input = user_input or {}
        
        # Default substitutions
        substitutions = {
            '[Project/Feature Name]': project_name,
            '[Date Created]': datetime.now().strftime('%Y-%m-%d'),
            '[Date]': datetime.now().strftime('%Y-%m-%d'),
            '[Product Owner Name(s)]': user_input.get('product_owner', 'Product Owner'),
            '[Design Facilitator Name]': user_input.get('design_facilitator', 'Design Facilitator'),
            '[Author]': user_input.get('author', 'AID Commander User'),
            '[Author(s)]': user_input.get('author', 'AID Commander User'),
            'Status: [Draft | In Review | Approved | Archived]': 'Status: Draft'
        }
        
        # Apply substitutions
        filled_template = template
        for placeholder, value in substitutions.items():
            filled_template = filled_template.replace(placeholder, value)
            
        # Write to project directory
        prd_file = project_dir / f"{project_name}_PRD.md"
        prd_file.write_text(filled_template)
        
        return prd_file
        
    def create_mpd(self, project_name: str, project_dir: Path,
                  user_input: Dict[str, str] = None) -> Path:
        """Create an MPD from template with user input"""
        if 'mpd' not in self.templates:
            raise FileNotFoundError("MPD template not found")
            
        template = self.templates['mpd']
        user_input = user_input or {}
        
        # Default substitutions
        substitutions = {
            '[Program Name]': project_name,
            '[Date Created]': datetime.now().strftime('%Y-%m-%d'),
            '[Date]': datetime.now().strftime('%Y-%m-%d'),
            '[Program Owner Name]': user_input.get('program_owner', 'Program Owner'),
            '[Program Owner]': user_input.get('program_owner', 'Program Owner'),
            '[Product Owner Name(s)]': user_input.get('program_owner', 'Program Owner'),
            '[Author]': user_input.get('author', 'AID Commander User'),
        }
        
        # Apply substitutions
        filled_template = template
        for placeholder, value in substitutions.items():
            filled_template = filled_template.replace(placeholder, value)
            
        # Write to project directory
        mpd_file = project_dir / f"{project_name}_MPD.md"
        mpd_file.write_text(filled_template)
        
        return mpd_file
        
    def create_integration_strategy(self, project_name: str, project_dir: Path,
                                  user_input: Dict[str, str] = None) -> Path:
        """Create Integration Strategy from template"""
        if 'integration' not in self.templates:
            raise FileNotFoundError("Integration Strategy template not found")
            
        template = self.templates['integration']
        user_input = user_input or {}
        
        # Default substitutions
        substitutions = {
            '[Program Name]': project_name,
            '[Date Created]': datetime.now().strftime('%Y-%m-%d'),
            '[Author]': user_input.get('author', 'AID Commander User'),
        }
        
        # Apply substitutions
        filled_template = template
        for placeholder, value in substitutions.items():
            filled_template = filled_template.replace(placeholder, value)
            
        # Write to project directory
        integration_file = project_dir / f"{project_name}_Integration.md"
        integration_file.write_text(filled_template)
        
        return integration_file
        
    def parse_prd_sections(self, prd_file: Path) -> Dict[str, str]:
        """Parse PRD file and extract sections"""
        if not prd_file.exists():
            return {}
            
        content = prd_file.read_text()
        sections = {}
        
        # Split by markdown headers
        header_pattern = r'^(#{1,6})\s+(.+)$'
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            header_match = re.match(header_pattern, line)
            if header_match:
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                    
                # Start new section
                header_level = len(header_match.group(1))
                section_title = header_match.group(2)
                current_section = section_title
                current_content = []
            else:
                current_content.append(line)
                
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
            
        return sections
        
    def validate_template_completeness(self, template_file: Path, 
                                     template_type: str) -> Tuple[bool, List[str]]:
        """Validate that template has all required sections filled out"""
        if not template_file.exists():
            return False, ["Template file does not exist"]
            
        content = template_file.read_text()
        issues = []
        
        # Check for unfilled placeholders
        placeholder_patterns = [
            r'\[.*?\]',  # [Placeholder text]
            r'TODO:',    # TODO items
            r'TBD',      # To be determined
        ]
        
        for pattern in placeholder_patterns:
            matches = re.findall(pattern, content)
            if matches:
                issues.extend([f"Unfilled placeholder: {match}" for match in matches])
                
        # Template-specific validations
        if template_type == 'prd':
            required_sections = [
                'Introduction & Product Vision',
                'Core User Workflows & Experience',
                'System Architecture & Technical Foundation',
                'Functional Requirements & Implementation Tasks'
            ]
        elif template_type == 'mpd':
            required_sections = [
                'Program Overview & Strategic Vision',
                'Component Architecture & Relationships',
                'Cross-Component Integration Strategy'
            ]
        else:
            required_sections = []
            
        # Check required sections exist and have content
        for required_section in required_sections:
            if required_section not in content:
                issues.append(f"Missing required section: {required_section}")
            else:
                # Check section has substantial content (not just header)
                section_pattern = rf'#{1,6}\s+.*{re.escape(required_section)}.*?\n(.*?)(?=\n#{1,6}|\Z)'
                section_match = re.search(section_pattern, content, re.DOTALL)
                if section_match:
                    section_content = section_match.group(1).strip()
                    if len(section_content) < 20:  # More lenient minimum content length
                        issues.append(f"Section '{required_section}' needs more content")
                        
        is_complete = len(issues) == 0
        return is_complete, issues
        
    def extract_tasks_from_prd(self, prd_file: Path) -> List[Dict[str, str]]:
        """Extract implementation tasks from PRD sections"""
        sections = self.parse_prd_sections(prd_file)
        tasks = []
        
        # Look for task-related sections
        task_patterns = [
            r'(\d+)\.\s+(.+)',           # Numbered lists like "1. Task description"
            r'(\d+\.\d+\.?\d*)\s+(.+)',  # Numbered items like "5.1.1 Task description"
            r'-\s*(.+)',                 # Bullet points
            r'\*\s*(.+)',                # Asterisk bullets
        ]
        
        for section_name, content in sections.items():
            if any(keyword in section_name.lower() for keyword in 
                   ['implementation', 'task', 'requirement', 'feature']):
                
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    for pattern in task_patterns:
                        match = re.match(pattern, line)
                        if match:
                            if len(match.groups()) == 2:
                                task_id, task_desc = match.groups()
                            else:
                                task_id = f"{section_name}_{len(tasks)+1}"
                                task_desc = match.group(1)
                                
                            tasks.append({
                                'id': task_id.strip(),
                                'description': task_desc.strip(),
                                'section': section_name,
                                'status': '[ ]',  # Default to pending
                                'dependencies': [],
                                'estimated_hours': 0
                            })
                            break
                            
        return tasks
        
    def get_available_templates(self) -> List[str]:
        """Get list of available template types"""
        return list(self.templates.keys())
        
    def get_template_info(self, template_type: str) -> Dict[str, str]:
        """Get information about a specific template"""
        if template_type not in self.templates:
            return {}
            
        template = self.templates[template_type]
        
        # Extract basic info from template
        info = {
            'type': template_type,
            'description': self._extract_template_description(template),
            'placeholders': self._extract_placeholders(template),
            'sections': self._extract_sections(template)
        }
        
        return info
        
    def _extract_template_description(self, template: str) -> str:
        """Extract description from template comments or content"""
        # Look for description in comments or first paragraph
        lines = template.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if line.strip().startswith('#') and 'template' in line.lower():
                return line.strip('# ').strip()
        return "AID Template"
        
    def _extract_placeholders(self, template: str) -> List[str]:
        """Extract placeholder patterns from template"""
        placeholders = re.findall(r'\[.*?\]', template)
        return list(set(placeholders))  # Remove duplicates
        
    def _extract_sections(self, template: str) -> List[str]:
        """Extract section headers from template"""
        headers = re.findall(r'^#{1,6}\s+(.+)$', template, re.MULTILINE)
        return headers