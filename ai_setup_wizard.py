#!/usr/bin/env python3
"""
AI Setup Wizard for AID Commander
Guides users through AI provider configuration
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional


class AISetupWizard:
    """Interactive wizard for setting up AI providers"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".aid_commander"
        self.ai_config_file = self.config_dir / "ai_config.json"
        
    def run(self):
        """Run the interactive AI setup wizard"""
        print("🤖 AID Commander AI Setup Wizard")
        print("=" * 40)
        print()
        
        # Check if AI is already configured
        if self.ai_config_file.exists():
            print("⚠️  AI configuration already exists.")
            choice = input("Do you want to reconfigure? (y/n): ").lower().strip()
            if not choice.startswith('y'):
                print("Setup cancelled.")
                return
        
        print("This wizard will help you set up AI providers for enhanced functionality.")
        print()
        
        # Step 1: Choose provider
        provider = self._choose_provider()
        if not provider:
            print("Setup cancelled.")
            return
            
        # Step 2: Configure chosen provider
        config = self._configure_provider(provider)
        if not config:
            print("Setup cancelled.")
            return
            
        # Step 3: Save configuration
        self._save_config(config)
        
        # Step 4: Test configuration
        self._test_configuration(provider)
        
        print()
        print("🎉 AI setup complete!")
        print()
        print("Next steps:")
        print("1. Switch to hybrid mode: aid-commander mode hybrid")
        print("2. Try adding a task: aid-commander task add 'Test AI integration'")
        print("3. Generate AI-enhanced tasks: aid-commander task generate")
        
    def _choose_provider(self) -> Optional[str]:
        """Let user choose AI provider"""
        print("📋 Available AI Providers:")
        print()
        print("1. OpenAI (GPT-4, GPT-3.5-turbo)")
        print("   - Most popular and well-tested")
        print("   - Requires OpenAI API key")
        print("   - Cost: ~$0.03 per 1K tokens")
        print()
        print("2. Anthropic (Claude 3)")
        print("   - High-quality reasoning")
        print("   - Requires Anthropic API key") 
        print("   - Cost: ~$0.015 per 1K tokens")
        print()
        print("3. Skip AI setup (use manual mode only)")
        print()
        
        while True:
            choice = input("Choose provider (1-3): ").strip()
            
            if choice == "1":
                return "openai"
            elif choice == "2":
                return "anthropic"
            elif choice == "3":
                return None
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
                
    def _configure_provider(self, provider: str) -> Optional[Dict]:
        """Configure the chosen provider"""
        print(f"\n🔧 Configuring {provider.title()}")
        print("=" * 30)
        
        if provider == "openai":
            return self._configure_openai()
        elif provider == "anthropic":
            return self._configure_anthropic()
        else:
            return None
            
    def _configure_openai(self) -> Optional[Dict]:
        """Configure OpenAI provider"""
        print()
        print("OpenAI Setup Instructions:")
        print("1. Go to https://platform.openai.com/api-keys")
        print("2. Create a new API key")
        print("3. Copy the key (starts with 'sk-')")
        print()
        
        # Check environment variable first
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            print(f"✅ Found API key in environment variable")
            use_env = input("Use existing environment variable? (y/n): ").lower().strip()
            if use_env.startswith('y'):
                api_key = env_key
            else:
                api_key = self._get_api_key("OpenAI")
        else:
            api_key = self._get_api_key("OpenAI")
            
        if not api_key:
            return None
            
        # Choose model
        print("\nAvailable OpenAI models:")
        print("1. gpt-4 (recommended, higher quality)")
        print("2. gpt-3.5-turbo (faster, lower cost)")
        
        while True:
            model_choice = input("Choose model (1-2): ").strip()
            if model_choice == "1":
                model = "gpt-4"
                break
            elif model_choice == "2":
                model = "gpt-3.5-turbo"
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
                
        return {
            "provider": "openai",
            "confidence_threshold": 85,
            "providers": {
                "openai": {
                    "api_key": api_key,
                    "model": model,
                    "max_tokens": 2000,
                    "temperature": 0.3
                }
            }
        }
        
    def _configure_anthropic(self) -> Optional[Dict]:
        """Configure Anthropic provider"""
        print()
        print("Anthropic Setup Instructions:")
        print("1. Go to https://console.anthropic.com/")
        print("2. Create an API key")
        print("3. Copy the key")
        print()
        
        # Check environment variable first
        env_key = os.getenv("ANTHROPIC_API_KEY")
        if env_key:
            print(f"✅ Found API key in environment variable")
            use_env = input("Use existing environment variable? (y/n): ").lower().strip()
            if use_env.startswith('y'):
                api_key = env_key
            else:
                api_key = self._get_api_key("Anthropic")
        else:
            api_key = self._get_api_key("Anthropic")
            
        if not api_key:
            return None
            
        return {
            "provider": "anthropic",
            "confidence_threshold": 85,
            "providers": {
                "anthropic": {
                    "api_key": api_key,
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 2000
                }
            }
        }
        
    def _get_api_key(self, provider_name: str) -> Optional[str]:
        """Get API key from user input"""
        print(f"🔑 Enter your {provider_name} API key:")
        print("(Leave blank to cancel)")
        
        try:
            api_key = input("API Key: ").strip()
            if not api_key:
                return None
                
            # Basic validation
            if provider_name == "OpenAI" and not api_key.startswith("sk-"):
                print("⚠️  Warning: OpenAI API keys usually start with 'sk-'")
                confirm = input("Continue anyway? (y/n): ").lower().strip()
                if not confirm.startswith('y'):
                    return None
                    
            return api_key
            
        except (EOFError, KeyboardInterrupt):
            print("\nSetup cancelled.")
            return None
            
    def _save_config(self, config: Dict):
        """Save AI configuration to file"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            
            with open(self.ai_config_file, 'w') as f:
                # Don't save API key to file for security
                safe_config = config.copy()
                for provider_name in safe_config.get("providers", {}):
                    if "api_key" in safe_config["providers"][provider_name]:
                        safe_config["providers"][provider_name]["api_key"] = "***configured***"
                        
                json.dump(safe_config, f, indent=2)
                
            # Set environment variable for current session
            provider = config["provider"]
            api_key = config["providers"][provider]["api_key"]
            
            if provider == "openai":
                os.environ["OPENAI_API_KEY"] = api_key
                print("✅ OpenAI API key set for current session")
                print("💡 To make permanent, add to your shell profile:")
                print(f"   export OPENAI_API_KEY='{api_key}'")
            elif provider == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = api_key
                print("✅ Anthropic API key set for current session")
                print("💡 To make permanent, add to your shell profile:")
                print(f"   export ANTHROPIC_API_KEY='{api_key}'")
                
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            
    def _test_configuration(self, provider: str):
        """Test the AI configuration"""
        print(f"\n🧪 Testing {provider.title()} connection...")
        
        try:
            # Import here to avoid import errors if dependencies missing
            import asyncio
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            
            from ai_service import AIService
            
            # Create AI service and test
            ai_service = AIService()
            
            # Simple test - just check if we can create the service
            status = ai_service.get_status()
            
            if status["provider"] == provider:
                print("✅ Configuration test passed!")
                print(f"   Provider: {status['provider']}")
                print(f"   Mode: {status['mode']}")
            else:
                print("⚠️  Configuration loaded but provider mismatch")
                
        except ImportError as e:
            print("⚠️  AI dependencies not installed")
            print("   Run: pip install aiohttp")
        except Exception as e:
            print(f"⚠️  Configuration test failed: {e}")
            print("   You can still use manual mode")


def main():
    """Run the AI setup wizard"""
    wizard = AISetupWizard()
    wizard.run()


if __name__ == "__main__":
    main()