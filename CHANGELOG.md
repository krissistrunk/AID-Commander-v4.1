# Changelog

All notable changes to AID Commander will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-06-11

### Added
- **Dual-Mode Architecture**: Manual, Automated, and Hybrid operation modes
- **AI Service Layer**: Provider abstraction supporting OpenAI, Anthropic, Azure, and Local models
- **AI Setup Wizard**: Interactive wizard for configuring AI providers (`aid-commander setup`)
- **Enhanced Error Handling**: Robust error handling with detailed logging
- **Comprehensive Logging**: Structured logging with user-friendly console output and detailed file logs
- **Mode Management**: Switch between operation modes (`aid-commander mode [manual|automated|hybrid]`)
- **Status Monitoring**: System status command (`aid-commander status`)
- **AI-Enhanced Tasks**: Task complexity analysis and effort estimation in hybrid/automated modes
- **Graceful Fallbacks**: Automatic fallback to manual mode when AI is unavailable
- **User Documentation**: Complete user guide and setup instructions
- **Test Suite**: Comprehensive testing framework
- **Packaging**: pip-installable package with proper setup.py and pyproject.toml

### Enhanced
- **Template Engine**: Improved template validation and task extraction
- **Task Management**: Better task status tracking and filtering
- **Project Structure**: Enhanced directory organization for both single and multi-component projects
- **Configuration Management**: More robust config handling with validation

### Changed
- **Version Bump**: Updated to v2.0 to reflect major architectural changes
- **CLI Interface**: Added new commands while maintaining backward compatibility
- **Config Format**: Enhanced configuration with AI settings and operation modes

### Fixed
- **Template Validation**: More accurate template completeness checking
- **File Operations**: Better error handling for file read/write operations
- **Project Detection**: Improved current project detection logic

## [1.0.0] - 2025-06-10

### Added
- **Enhanced Manual Mode Foundation**: Complete manual mode implementation
- **Template Integration**: Real AID template integration (PRD/MPD creation)
- **Advanced Task Management**: Generate, list, filter, and update tasks
- **Template Validation**: Comprehensive template checking
- **Project Structure Support**: Both single PRD and multi-component approaches
- **Interactive Setup**: Guided project creation with complexity assessment
- **Task Status System**: Multiple status levels with visual indicators
- **Configuration System**: User configuration and project management

### Core Features
- `aid-commander init` - Initialize system
- `aid-commander start --project-name <name>` - Create projects
- `aid-commander task generate` - Extract tasks from templates
- `aid-commander task list [--status filter]` - List and filter tasks
- `aid-commander task add "description"` - Add manual tasks
- `aid-commander task status <id> <status>` - Update task status
- `aid-commander template validate` - Validate templates
- `aid-commander review` - Review project progress
- `aid-commander list` - List all projects

## [0.1.0] - Initial Development

### Added
- Basic project structure
- Initial CLI framework
- Template system foundation