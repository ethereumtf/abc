from typing import Dict, List, Any
from ..base_agent import BaseAgent
import json

class CodeAnalysisAgent(BaseAgent):
    async def analyze_code(self) -> Dict[str, Any]:
        """Analyze the repository's codebase."""
        prompt = f"""Analyze this GitHub repository's codebase and provide detailed analysis.

Repository Information:
{self._format_repo_info()}

Please analyze the codebase and provide detailed insights in the following categories:

1. Code Quality:
- Identify code style issues
- Suggest improvements
- Recommend best practices

2. Architecture:
- Analyze code structure
- Identify architectural patterns
- Suggest architectural improvements

3. Security:
- Identify security vulnerabilities
- Suggest security improvements
- Recommend security best practices

4. Performance:
- Analyze performance characteristics
- Identify bottlenecks
- Suggest optimization strategies

Please format your response as a JSON object with the following structure:
{{
    "code_quality": ["description", ...],
    "architecture": ["description", ...],
    "security": ["description", ...],
    "performance": ["description", ...]
}}
"""
        return await self.analyze(prompt)
    
    async def suggest_improvements(self) -> Dict[str, Any]:
        """Suggest specific code improvements based on analysis."""
        analysis = await self.analyze_code()
        
        prompt = f"""Based on the previous analysis, suggest specific code improvements.

Analysis Results:
{json.dumps(analysis, indent=2)}

For each category, provide specific code changes that would improve the repository.
Please format your response as a JSON object with the following structure:
{{
    "code_quality": ["description", ...],
    "architecture": ["description", ...],
    "security": ["description", ...],
    "performance": ["description", ...]
}}
"""
        return await self.analyze(prompt)
