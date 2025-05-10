from typing import Dict, List, Any
from ..base_agent import BaseAgent
import json

class TestAgent(BaseAgent):
    async def analyze_tests(self) -> Dict[str, Any]:
        """Analyze the repository's test suite."""
        prompt = f"""Analyze this GitHub repository's test suite and provide detailed analysis.

Repository Information:
{self._format_repo_info()}

Please analyze the test suite and provide detailed insights in the following categories:

1. Test Coverage:
- Analyze code coverage
- Identify untested code paths
- Suggest additional tests

2. Test Quality:
- Analyze test quality
- Identify flaky tests
- Suggest test improvements

3. Test Organization:
- Analyze test organization
- Suggest better test structure
- Recommend test naming conventions

4. Performance:
- Analyze test performance
- Identify slow tests
- Suggest optimization strategies

Please format your response as a JSON object with the following structure:
{{
    "test_coverage": ["description", ...],
    "test_quality": ["description", ...],
    "test_organization": ["description", ...],
    "performance": ["description", ...]
}}
"""
        return await self.analyze(prompt)
    
    async def suggest_tests(self) -> Dict[str, Any]:
        """Suggest new tests based on analysis."""
        analysis = await self.analyze_tests()
        
        prompt = f"""Based on the previous analysis, suggest new tests to improve the test suite.

Analysis Results:
{json.dumps(analysis, indent=2)}

For each category, provide specific test cases that would improve the repository's test coverage.
Please format your response as a JSON object with the following structure:
{{
    "test_coverage": ["description", ...],
    "test_quality": ["description", ...],
    "test_organization": ["description", ...],
    "performance": ["description", ...]
}}
"""
        return await self.analyze(prompt)
