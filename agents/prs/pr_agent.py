from typing import Dict, List, Any
from ..base_agent import BaseAgent
import json

class PRReviewAgent(BaseAgent):
    async def analyze_pr(self, pr_number: int) -> Dict[str, Any]:
        """Analyze a pull request and provide review suggestions."""
        pr = self.repo.pull_request(pr_number)
        prompt = f"""Review this GitHub pull request and provide detailed review suggestions.

Pull Request Information:
Title: {pr.title}
Description:
{pr.body}

Please analyze the pull request and provide detailed suggestions for improvements in the following categories:

1. Code Changes:
- Review code quality
- Suggest improvements
- Identify potential issues

2. Testing:
- Review test coverage
- Suggest additional tests
- Verify test quality

3. Documentation:
- Review documentation changes
- Suggest documentation improvements
- Verify documentation completeness

4. Performance:
- Review performance implications
- Suggest optimizations
- Verify benchmarking

Please format your response as a JSON object with the following structure:
{{
    "code_changes": ["description", ...],
    "testing": ["description", ...],
    "documentation": ["description", ...],
    "performance": ["description", ...]
}}
"""
        return await self.analyze(prompt)
    
    async def create_review(self, pr_number: int) -> Dict[str, Any]:
        """Create a review based on analysis results."""
        analysis = await self.analyze_pr(pr_number)
        pr = self.repo.pull_request(pr_number)
        
        review_body = """
# Pull Request Review

## Code Changes
{code_changes}

## Testing
{testing}

## Documentation
{documentation}

## Performance
{performance}
""".format(
    code_changes="\n".join(analysis["code_changes"]),
    testing="\n".join(analysis["testing"]),
    documentation="\n".join(analysis["documentation"]),
    performance="\n".join(analysis["performance"])
)
        
        review = pr.create_review(body=review_body)
        return {
            "review_id": review.id,
            "review_url": review.html_url,
            "review_body": review_body
        }
