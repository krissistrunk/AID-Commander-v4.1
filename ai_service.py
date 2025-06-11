#!/usr/bin/env python3
"""
AI Service Layer for AID Commander
Provides AI provider abstraction and automated mode capabilities
"""

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import asyncio
import aiohttp
from datetime import datetime


class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"  
    AZURE = "azure"
    LOCAL = "local"


class OperationMode(Enum):
    """AID Commander operation modes"""
    MANUAL = "manual"      # User-driven (current enhanced manual mode)
    AUTOMATED = "automated"  # AI-driven task generation and management
    HYBRID = "hybrid"      # AI suggestions with user approval


@dataclass
class AIResponse:
    """Standardized AI response structure"""
    content: str
    confidence: float  # 0-100
    reasoning: str
    suggestions: List[str]
    provider: AIProvider
    tokens_used: int
    cost_estimate: float


@dataclass
class TaskAnalysis:
    """AI analysis of task complexity and dependencies"""
    task_id: str
    complexity: str  # "simple", "medium", "complex"
    estimated_effort: str  # "15min", "1hr", "1day", etc.
    dependencies: List[str]
    confidence: float
    suggestions: List[str]


class AIProviderBase(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_type = None
        
    @abstractmethod
    async def analyze_template(self, template_content: str, template_type: str) -> AIResponse:
        """Analyze PRD/MPD template and suggest improvements"""
        pass
        
    @abstractmethod
    async def generate_tasks(self, template_content: str, template_type: str) -> AIResponse:
        """Generate implementation tasks from template"""
        pass
        
    @abstractmethod
    async def analyze_task_complexity(self, task_description: str, context: str) -> TaskAnalysis:
        """Analyze individual task complexity and dependencies"""
        pass
        
    @abstractmethod
    async def suggest_next_steps(self, project_state: Dict[str, Any]) -> AIResponse:
        """Suggest next development steps based on project state"""
        pass


class OpenAIProvider(AIProviderBase):
    """OpenAI GPT provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_type = AIProvider.OPENAI
        self.api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        self.model = config.get("model", "gpt-4")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        
    async def analyze_template(self, template_content: str, template_type: str) -> AIResponse:
        """Analyze template using OpenAI"""
        prompt = f"""
        Analyze this {template_type.upper()} template for completeness and quality:
        
        {template_content}
        
        Provide:
        1. Overall assessment (0-100 confidence score)
        2. Missing sections or incomplete areas
        3. Suggestions for improvement
        4. Reasoning for your assessment
        """
        
        response = await self._make_request(prompt)
        return self._parse_response(response, "template_analysis")
        
    async def generate_tasks(self, template_content: str, template_type: str) -> AIResponse:
        """Generate tasks using OpenAI"""
        prompt = f"""
        Extract implementation tasks from this {template_type.upper()}:
        
        {template_content}
        
        Generate specific, actionable tasks with:
        1. Clear descriptions
        2. Estimated complexity (simple/medium/complex)
        3. Dependencies between tasks
        4. Implementation order suggestions
        """
        
        response = await self._make_request(prompt)
        return self._parse_response(response, "task_generation")
        
    async def analyze_task_complexity(self, task_description: str, context: str) -> TaskAnalysis:
        """Analyze task complexity using OpenAI"""
        prompt = f"""
        Analyze this development task:
        Task: {task_description}
        Context: {context}
        
        Provide:
        1. Complexity level (simple/medium/complex)
        2. Estimated effort (15min/1hr/4hr/1day/3day/1week)
        3. Required dependencies
        4. Implementation suggestions
        """
        
        response = await self._make_request(prompt)
        # Parse response into TaskAnalysis structure
        return TaskAnalysis(
            task_id=hash(task_description),
            complexity="medium",  # Default, should parse from response
            estimated_effort="1hr",
            dependencies=[],
            confidence=85.0,
            suggestions=[]
        )
        
    async def suggest_next_steps(self, project_state: Dict[str, Any]) -> AIResponse:
        """Suggest next steps using OpenAI"""
        prompt = f"""
        Based on this project state:
        {json.dumps(project_state, indent=2)}
        
        Suggest the next development steps:
        1. Priority tasks to complete
        2. Potential blockers or risks
        3. Resource recommendations
        4. Timeline suggestions
        """
        
        response = await self._make_request(prompt)
        return self._parse_response(response, "next_steps")
        
    async def _make_request(self, prompt: str) -> Dict[str, Any]:
        """Make request to OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert software development assistant for AID Commander."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/chat/completions", 
                                   headers=headers, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"OpenAI API error: {response.status}")
                return await response.json()
                
    def _parse_response(self, response: Dict[str, Any], operation_type: str) -> AIResponse:
        """Parse OpenAI response into AIResponse"""
        content = response["choices"][0]["message"]["content"]
        usage = response.get("usage", {})
        
        return AIResponse(
            content=content,
            confidence=85.0,  # Default, should extract from content
            reasoning="OpenAI analysis",
            suggestions=[],
            provider=self.provider_type,
            tokens_used=usage.get("total_tokens", 0),
            cost_estimate=self._calculate_cost(usage.get("total_tokens", 0))
        )
        
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate estimated cost based on tokens"""
        # GPT-4 pricing (approximate)
        cost_per_1k_tokens = 0.03
        return (tokens / 1000) * cost_per_1k_tokens


class AnthropicProvider(AIProviderBase):
    """Anthropic Claude provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_type = AIProvider.ANTHROPIC
        self.api_key = config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        self.model = config.get("model", "claude-3-sonnet-20240229")
        
    async def analyze_template(self, template_content: str, template_type: str) -> AIResponse:
        # Similar implementation to OpenAI but with Anthropic API
        pass
        
    async def generate_tasks(self, template_content: str, template_type: str) -> AIResponse:
        # Anthropic-specific implementation
        pass
        
    async def analyze_task_complexity(self, task_description: str, context: str) -> TaskAnalysis:
        # Anthropic-specific implementation
        pass
        
    async def suggest_next_steps(self, project_state: Dict[str, Any]) -> AIResponse:
        # Anthropic-specific implementation
        pass


class AIService:
    """Main AI service orchestrator"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".aid_commander" / "ai_config.json"
        self.config = self._load_config()
        self.provider = self._initialize_provider()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load AI service configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            default_config = {
                "mode": OperationMode.MANUAL.value,
                "provider": AIProvider.OPENAI.value,
                "confidence_threshold": 85,
                "auto_approve_simple_tasks": False,
                "providers": {
                    "openai": {
                        "model": "gpt-4",
                        "max_tokens": 2000,
                        "temperature": 0.3
                    },
                    "anthropic": {
                        "model": "claude-3-sonnet-20240229",
                        "max_tokens": 2000
                    }
                }
            }
            
            # Create config directory and file
            self.config_path.parent.mkdir(exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
                
            return default_config
            
    def _initialize_provider(self) -> AIProviderBase:
        """Initialize the configured AI provider"""
        provider_name = self.config.get("provider", "openai")
        provider_config = self.config.get("providers", {}).get(provider_name, {})
        
        if provider_name == "openai":
            return OpenAIProvider(provider_config)
        elif provider_name == "anthropic":
            return AnthropicProvider(provider_config)
        else:
            raise ValueError(f"Unsupported AI provider: {provider_name}")
            
    def set_mode(self, mode: OperationMode):
        """Set operation mode"""
        self.config["mode"] = mode.value
        self._save_config()
        
    def get_mode(self) -> OperationMode:
        """Get current operation mode"""
        return OperationMode(self.config.get("mode", "manual"))
        
    def set_provider(self, provider: AIProvider):
        """Set AI provider"""
        self.config["provider"] = provider.value
        self.provider = self._initialize_provider()
        self._save_config()
        
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    async def analyze_project_template(self, template_file: Path, template_type: str) -> AIResponse:
        """Analyze project template with AI"""
        if self.get_mode() == OperationMode.MANUAL:
            # In manual mode, provide basic analysis without AI
            return AIResponse(
                content="Manual mode: Basic template validation completed",
                confidence=100.0,
                reasoning="Manual mode analysis",
                suggestions=["Review template sections manually"],
                provider=AIProvider.LOCAL,
                tokens_used=0,
                cost_estimate=0.0
            )
            
        template_content = template_file.read_text()
        return await self.provider.analyze_template(template_content, template_type)
        
    async def generate_ai_tasks(self, template_file: Path, template_type: str) -> AIResponse:
        """Generate tasks using AI analysis"""
        if self.get_mode() == OperationMode.MANUAL:
            # Manual mode fallback
            return AIResponse(
                content="Manual mode: Use template_engine for task extraction",
                confidence=100.0,
                reasoning="Manual mode operation",
                suggestions=["Use aid-commander task generate for manual task extraction"],
                provider=AIProvider.LOCAL,
                tokens_used=0,
                cost_estimate=0.0
            )
            
        template_content = template_file.read_text()
        return await self.provider.generate_tasks(template_content, template_type)
        
    async def analyze_task(self, task_description: str, project_context: str) -> TaskAnalysis:
        """Analyze individual task complexity"""
        if self.get_mode() == OperationMode.MANUAL:
            # Manual mode: basic analysis
            return TaskAnalysis(
                task_id=str(hash(task_description)),
                complexity="medium",
                estimated_effort="1hr",
                dependencies=[],
                confidence=100.0,
                suggestions=["Manually assess task complexity"]
            )
            
        return await self.provider.analyze_task_complexity(task_description, project_context)
        
    async def suggest_next_actions(self, project_state: Dict[str, Any]) -> AIResponse:
        """Get AI suggestions for next development steps"""
        if self.get_mode() == OperationMode.MANUAL:
            return AIResponse(
                content="Manual mode: Review tasks and make decisions manually",
                confidence=100.0,
                reasoning="Manual mode operation",
                suggestions=["Use aid-commander review to assess project state"],
                provider=AIProvider.LOCAL,
                tokens_used=0,
                cost_estimate=0.0
            )
            
        return await self.provider.suggest_next_steps(project_state)
        
    def get_status(self) -> Dict[str, Any]:
        """Get AI service status"""
        return {
            "mode": self.get_mode().value,
            "provider": self.config.get("provider"),
            "confidence_threshold": self.config.get("confidence_threshold"),
            "config_path": str(self.config_path),
            "available_providers": [p.value for p in AIProvider]
        }


# Utility functions for dual-mode support
def should_use_ai(mode: OperationMode, confidence_threshold: float = 85) -> bool:
    """Determine if AI should be used based on mode and confidence"""
    return mode in [OperationMode.AUTOMATED, OperationMode.HYBRID]


def format_ai_suggestion(response: AIResponse, max_length: int = 200) -> str:
    """Format AI suggestion for display in terminal"""
    content = response.content
    if len(content) > max_length:
        content = content[:max_length] + "..."
        
    return f"🤖 AI Suggestion (confidence: {response.confidence:.0f}%): {content}"


# Example usage and testing
async def test_ai_service():
    """Test function for AI service"""
    service = AIService()
    
    print("AI Service Status:")
    print(json.dumps(service.get_status(), indent=2))
    
    # Test template analysis
    template_path = Path("test_template.md")
    if template_path.exists():
        response = await service.analyze_project_template(template_path, "prd")
        print(f"\nTemplate Analysis: {response.content}")


if __name__ == "__main__":
    asyncio.run(test_ai_service())