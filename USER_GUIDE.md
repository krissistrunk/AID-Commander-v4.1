# AID Commander User Guide 🚀

**AI-Facilitated Iterative Development - Terminal Tool**

Version 2.0 | Enhanced Manual Mode + AI Integration

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Core Concepts](#core-concepts)
4. [Command Reference](#command-reference)
5. [Operation Modes](#operation-modes)
6. [AI Configuration](#ai-configuration)
7. [Project Workflows](#project-workflows)
8. [Troubleshooting](#troubleshooting)
9. [Examples](#examples)

---

## 🚀 Quick Start

### 1. Initialize AID Commander
```bash
python aid_commander.py init
```

### 2. Create Your First Project
```bash
python aid_commander.py start --project-name MyAwesomeApp
```

### 3. Generate Tasks from Template
```bash
cd MyAwesomeApp
python ../aid_commander.py task generate
```

### 4. Start Building!
```bash
python ../aid_commander.py task list
python ../aid_commander.py review
```

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- Internet connection (for AI features)

### Setup
1. **Clone/Download** the AID Commander files
2. **Install Dependencies** (optional for AI features):
   ```bash
   pip install aiohttp  # For AI providers
   ```
3. **Make Executable** (optional):
   ```bash
   chmod +x aid_commander.py
   ```

### Verify Installation
```bash
python aid_commander.py --help
```

---

## 🧠 Core Concepts

### Projects
- **Single PRD**: Simple projects with one Product Requirements Document
- **Multi-Component**: Complex projects with multiple modules (MPD + Integration Strategy)

### Templates
- **PRD Template**: Product Requirements Document with structured sections
- **MPD Template**: Multi-Product Document for coordinating components
- **Integration Strategy**: How components work together

### Tasks
- **Generated Tasks**: Extracted from your PRD/MPD templates
- **Manual Tasks**: Added by you directly
- **Status Tracking**: `[ ]` Ready, `[>]` Working, `[x]` Complete, etc.

### Operation Modes
- **Manual**: You control everything (default)
- **Hybrid**: AI suggestions with your approval
- **Automated**: AI drives task generation and management

---

## 📚 Command Reference

### Core Commands

#### `init`
Initialize AID Commander configuration
```bash
aid-commander init
```

#### `start --project-name <name>`
Create a new project with guided setup
```bash
aid-commander start --project-name WebStore
```

#### `status`
Show system and project status
```bash
aid-commander status
```

#### `list`
List all your projects
```bash
aid-commander list
```

### Task Management

#### `task add <description>`
Add a manual task to current project
```bash
aid-commander task add "Set up user authentication"
```

#### `task generate`
Generate tasks from PRD/MPD templates
```bash
aid-commander task generate
```

#### `task list [--status <filter>]`
List tasks with optional status filter
```bash
aid-commander task list
aid-commander task list --status working
aid-commander task list --status complete
```

#### `task status <id> <new_status>`
Update task status
```bash
aid-commander task status 1 working
aid-commander task status "auth" complete
```

**Status Options:**
- `pending` or `[ ]` - Ready to start
- `clarification` or `[!]` - Needs more info
- `working` or `[>]` - Currently working
- `revision` or `[R]` - Needs revision
- `complete` or `[x]` - Done

### Template Management

#### `template validate`
Validate current project templates
```bash
aid-commander template validate
```

#### `review`
Review all project tasks and progress
```bash
aid-commander review
```

### AI & Mode Management

#### `mode <operation_mode>`
Set operation mode
```bash
aid-commander mode manual     # User-driven (default)
aid-commander mode hybrid     # AI suggestions + approval
aid-commander mode automated  # AI-driven
```

---

## 🤖 Operation Modes

### Manual Mode (Default)
- **User Control**: You manage everything
- **Template Driven**: Uses AID templates for structure
- **No AI Required**: Works without API keys
- **Best For**: Learning AID, full control, no AI dependencies

### Hybrid Mode
- **AI Suggestions**: Get AI recommendations with confidence scores
- **User Approval**: You decide whether to accept AI suggestions
- **Smart Fallbacks**: Falls back to manual mode if AI unavailable
- **Best For**: Getting AI help while maintaining control

### Automated Mode
- **AI Driven**: AI generates and manages tasks automatically
- **High Confidence**: Only acts when AI is confident (>85%)
- **User Override**: You can still manually add/modify tasks
- **Best For**: Rapid prototyping, experienced users

### Switching Modes
```bash
# Start in manual mode (safe default)
aid-commander mode manual

# Get AI suggestions with approval
aid-commander mode hybrid

# Let AI drive (requires API setup)
aid-commander mode automated

# Check current mode
aid-commander status
```

---

## 🔧 AI Configuration

### Supported Providers
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude 3 models
- **Azure**: Azure OpenAI Service
- **Local**: Local AI models (future)

### API Key Setup

#### Option 1: Environment Variables (Recommended)
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

#### Option 2: Configuration File
Create `~/.aid_commander/ai_config.json`:
```json
{
  "provider": "openai",
  "providers": {
    "openai": {
      "api_key": "your-openai-key",
      "model": "gpt-4"
    },
    "anthropic": {
      "api_key": "your-anthropic-key", 
      "model": "claude-3-sonnet-20240229"
    }
  }
}
```

### Testing AI Setup
```bash
aid-commander mode hybrid
aid-commander task add "Test AI integration"
```

If you see AI analysis output, it's working! If not, check your API keys.

---

## 🔄 Project Workflows

### Workflow 1: Simple App (Single PRD)
```bash
# 1. Create project
aid-commander start --project-name SimpleApp

# 2. Edit the generated PRD
# Edit SimpleApp_PRD.md with your requirements

# 3. Generate tasks
aid-commander task generate

# 4. Start working
aid-commander task list
aid-commander task status 1 working

# 5. Track progress
aid-commander review
```

### Workflow 2: Complex System (Multi-Component)
```bash
# 1. Create project (answer "yes" to complexity questions)
aid-commander start --project-name ComplexSystem

# 2. Plan components
# Edit ComplexSystem_MPD.md to define components
# Edit ComplexSystem_Integration.md for integration strategy

# 3. Generate coordinated tasks
aid-commander task generate

# 4. Work systematically
aid-commander task list --status pending
aid-commander task status "database" working
```

### Workflow 3: AI-Assisted Development
```bash
# 1. Set up AI (see AI Configuration)
export OPENAI_API_KEY="your-key"

# 2. Switch to hybrid mode
aid-commander mode hybrid

# 3. Get AI-enhanced task analysis
aid-commander task add "Implement user authentication"
# See: 🤖 AI Analysis: medium complexity, ~2hr

# 4. Generate AI-enhanced tasks
aid-commander task generate
# See: ✨ AI generated tasks (confidence: 87%)
```

---

## 🛠 Troubleshooting

### Common Issues

#### "No active project found"
**Problem**: Running commands outside a project directory
**Solution**: 
```bash
cd YourProjectName
aid-commander task list  # Now works
```

#### "Template file not found"
**Problem**: Missing PRD/MPD file
**Solution**: Check if your template file exists and has content
```bash
ls -la  # Look for YourProject_PRD.md
```

#### "AI analysis unavailable"
**Problem**: API key not configured or invalid
**Solutions**:
```bash
# Check API key
echo $OPENAI_API_KEY

# Switch back to manual mode
aid-commander mode manual

# Verify status
aid-commander status
```

#### "Permission denied"
**Problem**: Cannot write to config directory
**Solution**: Check permissions
```bash
ls -la ~/.aid_commander/
chmod 755 ~/.aid_commander/
```

### Logs and Debugging

#### View logs
```bash
# Check today's log file
cat ~/.aid_commander/logs/aid_commander_$(date +%Y%m%d).log

# Watch logs in real-time
tail -f ~/.aid_commander/logs/aid_commander_$(date +%Y%m%d).log
```

#### Clean restart
```bash
# Backup your projects first!
mv ~/.aid_commander ~/.aid_commander.backup
aid-commander init
```

---

## 📝 Examples

### Example 1: E-commerce Website
```bash
# Create project
aid-commander start --project-name EcommerceStore

# The PRD template guides you to define:
# - User authentication
# - Product catalog
# - Shopping cart
# - Payment processing
# - Order management

# Generate implementation tasks
aid-commander task generate

# Result: 15-20 specific, actionable tasks
aid-commander task list
```

### Example 2: Mobile App Backend
```bash
# Create complex project
aid-commander start --project-name MobileAppBackend

# Use MPD approach for:
# - API Gateway component
# - User Service component  
# - Data Service component
# - Notification Service component

aid-commander task generate
# Result: Component-specific tasks + integration tasks
```

### Example 3: AI-Enhanced Workflow
```bash
# Set up AI
export OPENAI_API_KEY="your-key"
aid-commander mode hybrid

# Create project with AI suggestions
aid-commander start --project-name AIAssistedApp

# Get AI task analysis
aid-commander task add "Implement real-time chat"
# Output: 🤖 AI Analysis: complex complexity, ~1day
#         💡 Suggestions: Use WebSockets, Consider rate limiting

# Generate AI-enhanced tasks
aid-commander task generate
# Output: ✨ AI generated tasks (confidence: 89%)
#         - Set up WebSocket server
#         - Implement message queuing
#         - Add rate limiting middleware
#         - Create chat room management
```

---

## 🎯 Best Practices

### 1. Start Simple
- Begin with manual mode to learn the system
- Use single PRD approach for first projects
- Switch to AI modes once comfortable

### 2. Template Quality
- Fill out PRD/MPD templates completely
- Be specific about requirements
- Use the validation command before generating tasks

### 3. Task Management
- Update task status regularly
- Use descriptive task descriptions
- Review progress frequently

### 4. AI Usage
- Start with hybrid mode before automated
- Review AI suggestions before accepting
- Keep API keys secure

### 5. Project Organization
- Use clear, descriptive project names
- Keep related projects in dedicated directories
- Regular backups of project files

---

## 🔗 Quick Reference Card

```bash
# Essential Commands
aid-commander init                          # Setup
aid-commander start --project-name MyApp    # Create project
aid-commander task generate                 # Extract tasks
aid-commander task add "description"        # Add task
aid-commander task list                     # View tasks
aid-commander task status 1 working         # Update status
aid-commander review                        # Full review
aid-commander status                        # System status

# Mode Management
aid-commander mode manual                   # User control
aid-commander mode hybrid                   # AI + approval
aid-commander mode automated                # AI driven

# Troubleshooting
aid-commander template validate             # Check templates
aid-commander list                         # List projects
tail -f ~/.aid_commander/logs/*.log        # View logs
```

---

## 📞 Support

### Getting Help
1. **Check this guide** for common solutions
2. **Review logs** in `~/.aid_commander/logs/`
3. **Try manual mode** if AI features fail
4. **Recreate config** with `aid-commander init`

### Reporting Issues
Include this information:
- Command that failed
- Error message
- OS and Python version
- Log file contents
- Project structure

---

**Happy Building with AID Commander! 🚀**

*AI-Facilitated Iterative Development makes complex projects manageable through structured templates, intelligent task generation, and flexible AI integration.*