# AID Commander Setup Guide ⚡

**Get up and running in 5 minutes**

---

## 🚀 Quick Setup

### Step 1: Prerequisites
```bash
# Check Python version (need 3.8+)
python3 --version

# Install optional AI dependencies
pip install aiohttp
```

### Step 2: Download & Initialize
```bash
# Navigate to AID Commander directory
cd /path/to/aid_commander

# Initialize the system
python3 aid_commander.py init
```

### Step 3: Create Your First Project
```bash
# Create a simple project
python3 aid_commander.py start --project-name TestProject

# Answer the complexity questions:
# - Will your project have more than 5-7 major features? n
# - Do you need multiple developers working simultaneously? n  
# - Are there distinct modules for independent development? n
# - Will different parts use different technologies? n
# - Complex integration with multiple external systems? n

# Skip personalization (press Enter for each field)
```

### Step 4: Generate Tasks
```bash
# Navigate to your project
cd TestProject

# Edit the PRD with your requirements (optional for testing)
# nano TestProject_PRD.md

# Generate tasks from template
python3 ../aid_commander.py task generate
```

### Step 5: Start Working
```bash
# View all tasks
python3 ../aid_commander.py task list

# Add a custom task
python3 ../aid_commander.py task add "Set up development environment"

# Update task status
python3 ../aid_commander.py task status 1 working

# Review progress
python3 ../aid_commander.py review
```

---

## 🤖 Optional: AI Setup

### For OpenAI (GPT-4)
```bash
# Set environment variable
export OPENAI_API_KEY="your-openai-api-key"

# Switch to hybrid mode
python3 ../aid_commander.py mode hybrid

# Test AI features
python3 ../aid_commander.py task add "Implement user authentication"
# Should show: 🤖 AI Analysis: medium complexity, ~2hr
```

### For Anthropic (Claude)
```bash
# Set environment variable  
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Configure provider in ~/.aid_commander/ai_config.json:
{
  "provider": "anthropic",
  "providers": {
    "anthropic": {
      "model": "claude-3-sonnet-20240229"
    }
  }
}
```

---

## ✅ Verification Checklist

- [ ] `python3 aid_commander.py --help` shows command list
- [ ] `python3 aid_commander.py status` shows system info
- [ ] Project creation works without errors
- [ ] Task generation creates tasks in Tasks.md file
- [ ] Task status updates work
- [ ] AI mode switching works (if configured)

---

## 🔧 Common Setup Issues

### "Python command not found"
```bash
# Try different python commands
python --version
python3 --version
python3.8 --version

# Use the one that shows Python 3.8+
```

### "No module named 'aiohttp'"
```bash
# Install AI dependencies
pip install aiohttp
# or
pip3 install aiohttp
```

### "Permission denied" on config directory
```bash
# Check home directory permissions
ls -la ~/.aid_commander/
# Fix if needed
chmod 755 ~/.aid_commander/
```

### "Template file not found"
- Make sure you're in the project directory when running commands
- Check that YourProject_PRD.md exists
- Try `python3 aid_commander.py template validate`

---

## 🎯 Next Steps

1. **Read the [User Guide](USER_GUIDE.md)** for detailed instructions
2. **Try different project types** (single PRD vs multi-component)
3. **Experiment with AI modes** (manual → hybrid → automated)
4. **Customize templates** for your specific needs

---

**You're ready to start building with AID Commander! 🚀**

Run `python3 aid_commander.py start --project-name YourRealProject` to begin.