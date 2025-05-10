from typing import Dict, List, Any
from ..base_agent import BaseAgent
import json

class IssueReportingAgent(BaseAgent):
    async def analyze_issues(self) -> Dict[str, Any]:
        """Analyze the repository for potential issues to report."""
        prompt = f"""Analyze this GitHub repository and identify potential issues to report.

Repository Information:
{self._format_repo_info()}

Please analyze the repository and provide detailed suggestions for improvements in the following categories:

1. Code Quality:
- Identify code style issues
- Suggest improvements
- Recommend best practices

2. Documentation:
- Identify missing documentation
- Suggest documentation improvements
- Recommend documentation structure

3. Testing:
- Identify missing tests
- Suggest test improvements
- Recommend testing best practices

4. Performance:
- Identify performance bottlenecks
- Suggest optimization strategies
- Recommend benchmarking approaches

Please format your response as a JSON object with the following structure:
{{
    "code_quality": ["description", ...],
    "documentation": ["description", ...],
    "testing": ["description", ...],
    "performance": ["description", ...]
}}
"""
        return await self.analyze(prompt)
    
    async def create_issues(self) -> List[Dict[str, Any]]:
        """Create issues based on analysis results."""
        analysis = await self.analyze_issues()
        created_issues = []
        
        for category, suggestions in analysis.items():
            for suggestion in suggestions:
                title = f"[{category.replace('_', ' ').title()}] {suggestion[:50]}"
                body = f"""## Description
{suggestion}

## Category
{category.replace('_', ' ').title()}

## Analysis
{analysis[category]}
"""
                result = await self.create_issue(title, body)
                if result['status'] == 'success':
                    created_issues.append(result)
        
        return created_issues
    
    def _format_repo_info(self) -> str:
        """Format repository information for the prompt."""
        info = []
        for key, value in self.repo_info.items():
            if key == 'recent_commits':
                commits = '\n'.join([
                    f"- {commit.message} ({commit.author.name if commit.author else 'Unknown'})"
                    for commit in value
                ])
                info.append(f"Recent Commits:\n{commits}")
            else:
                info.append(f"- {key.replace('_', ' ').title()}: {value}")
        return '\n'.join(info)
