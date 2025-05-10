import os
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from github3 import login
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

load_dotenv()

class GitHubConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    token: str
    repo_owner: str
    repo_name: str

class AIConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    model_name: str = "gemini-2.0-flash"
    temperature: float = 0.7
    max_output_tokens: int = 2048

class BaseAIAssistant:
    def __init__(self, config: GitHubConfig, ai_config: AIConfig):
        self.config = config
        self.ai_config = ai_config
        
        # Initialize Google Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel(ai_config.model_name)
        
        # Initialize GitHub client
        self.gh = login(token=config.token)
        self.repo = self.gh.repository(config.repo_owner, config.repo_name)

    def _get_repository_info(self) -> Dict[str, Any]:
        return {
            'description': self.repo.description or "No description",
            'languages': self._get_languages(),
            'open_issues': list(self.repo.issues(state='open'))[:10],
            'recent_commits': list(self.repo.commits())[:10],
            'stars': self.repo.stargazers_count,
            'forks': self.repo.forks_count,
            'watchers': self.repo.watchers_count,
            'open_issues_count': self.repo.open_issues_count,
            'default_branch': self.repo.default_branch
        }

    def _get_languages(self) -> List[str]:
        return list(self.repo.languages().keys())

class IssueReportingAgent(BaseAIAssistant):
    def analyze_issues(self) -> Dict[str, List[str]]:
        repo_info = self._get_repository_info()
        
        prompt = """Analyze this GitHub repository and identify potential issues to report.

        Repository Information:
        - Description: {description}
        - Languages: {languages}
        - Stars: {stars}
        - Forks: {forks}
        - Watchers: {watchers}
        - Open Issues: {open_issues_count}
        - Default Branch: {default_branch}

        Recent Commits:
        {commits}

        Please analyze the repository and provide detailed suggestions for new issues to report in the following categories:

        1. Bug Reports:
        - Identify potential bugs in the code
        - Suggest test cases that would catch these bugs
        - Recommend steps to reproduce

        2. Feature Requests:
        - Identify missing features
        - Suggest new features that would enhance the project
        - Provide use cases for each feature

        3. Performance Issues:
        - Identify potential performance bottlenecks
        - Suggest optimization opportunities
        - Recommend benchmarks to measure improvements

        4. Security Concerns:
        - Identify potential security vulnerabilities
        - Suggest security improvements
        - Recommend security best practices

        Please format your response as a JSON object with the following structure:
        {
            "bug_reports": ["description", ...],
            "feature_requests": ["description", ...],
            "performance_issues": ["description", ...],
            "security_concerns": ["description", ...]
        }
        """.format(
            description=repo_info['description'],
            languages=', '.join(repo_info['languages']),
            stars=repo_info['stars'],
            forks=repo_info['forks'],
            watchers=repo_info['watchers'],
            open_issues_count=repo_info['open_issues_count'],
            default_branch=repo_info['default_branch'],
            commits='\n'.join(["- {} ({})".format(commit.message, commit.author.name if commit.author else 'Unknown') for commit in repo_info['recent_commits']])
        )
        
        response = self.model.generate_content(prompt)
        return self._parse_response(response)

    def create_issue(self, title: str, body: str) -> Dict[str, Any]:
        issue = self.repo.create_issue(title=title, body=body)
        return {
            'number': issue.number,
            'title': issue.title,
            'url': issue.html_url
        }

class DocumentationImprovementAgent(BaseAIAssistant):
    def analyze_documentation(self) -> Dict[str, List[str]]:
        repo_info = self._get_repository_info()
        
        prompt = f"""Analyze this GitHub repository's documentation and identify areas for improvement.

        Repository Information:
        - Description: {repo_info['description']}
        - Languages: {', '.join(repo_info['languages'])}
        - Stars: {repo_info['stars']}
        - Forks: {repo_info['forks']}
        - Watchers: {repo_info['watchers']}
        - Open Issues: {repo_info['open_issues_count']}
        - Default Branch: {repo_info['default_branch']}

        Please analyze the repository and provide detailed suggestions for documentation improvements in the following categories:

        1. API Documentation:
        - Identify missing API documentation
        - Suggest improvements to existing API docs
        - Recommend documentation structure

        2. User Guides:
        - Identify missing user guides
        - Suggest improvements to existing guides
        - Recommend additional guides

        3. Examples:
        - Identify missing code examples
        - Suggest improvements to existing examples
        - Recommend new example scenarios

        4. Best Practices:
        - Identify missing best practices documentation
        - Suggest improvements to existing best practices
        - Recommend new best practices

        Please format your response as a JSON object with the following structure:
        {{
            "api_docs": ["description", ...],
            "user_guides": ["description", ...],
            "examples": ["description", ...],
            "best_practices": ["description", ...]
        }}
        """
        
        response = self.model.generate_content(prompt)
        return self._parse_response(response)

class CodeContributionAgent(BaseAIAssistant):
    def analyze_codebase(self) -> Dict[str, List[str]]:
        repo_info = self._get_repository_info()
        
        prompt = """Analyze this GitHub repository's codebase and identify areas for code contributions.

        Repository Information:
        - Description: {description}
        - Languages: {languages}
        - Stars: {stars}
        - Forks: {forks}
        - Watchers: {watchers}
        - Open Issues: {open_issues_count}
        - Default Branch: {default_branch}

        Recent Commits:
        {recent_commits}

        Please analyze the repository and provide detailed suggestions for code contributions in the following categories:

        1. Code Improvements:
        - Identify areas for code quality improvements
        - Suggest refactoring opportunities
        - Recommend code organization changes

        2. Missing Features:
        - Identify missing functionality
        - Suggest feature implementations
        - Recommend integration points

        3. Performance Optimizations:
        - Identify performance bottlenecks
        - Suggest optimization strategies
        - Recommend benchmarking approaches

        4. Error Handling:
        - Identify missing error handling
        - Suggest robust error handling
        - Recommend logging improvements

        Please format your response as a JSON object with the following structure:
        {{
            "code_improvements": ["description", ...],
            "missing_features": ["description", ...],
            "performance_optimizations": ["description", ...],
            "error_handling": ["description", ...]
        }}
        """.format(
            description=repo_info['description'],
            languages=', '.join(repo_info['languages']),
            stars=repo_info['stars'],
            forks=repo_info['forks'],
            watchers=repo_info['watchers'],
            open_issues_count=repo_info['open_issues_count'],
            default_branch=repo_info['default_branch'],
            recent_commits='\n'.join(["- {} ({})".format(commit.message, commit.author.name if commit.author else 'Unknown') for commit in repo_info['recent_commits']])
        )
        
        response = self.model.generate_content(prompt)
        return self._parse_response(response)

class CodeReviewAgent(BaseAIAssistant):
    def analyze_code_review(self, pull_request_number: int) -> Dict[str, List[str]]:
        pr = self.repo.pull_request(pull_request_number)
        
        prompt = """Review this GitHub pull request and provide detailed feedback.

        Pull Request Information:
        - Title: {title}
        - Author: {author}
        - Created: {created_at}
        - Changes: {changed_files} files changed

        Please review the changes and provide feedback in the following categories:

        1. Code Quality:
        - Identify code style issues
        - Suggest improvements
        - Recommend best practices

        2. Documentation:
        - Identify missing or unclear documentation
        - Suggest documentation improvements
        - Recommend documentation best practices

        3. Testing:
        - Identify missing tests
        - Suggest test improvements
        - Recommend testing best practices

        4. Performance:
        - Identify performance issues
        - Suggest performance improvements
        - Recommend performance best practices

        Please format your response as a JSON object with the following structure:
        {{
            "code_quality": ["feedback", ...],
            "documentation": ["feedback", ...],
            "testing": ["feedback", ...],
            "performance": ["feedback", ...]
        }}
        """.format(
            title=pr.title,
            author=pr.user.login,
            created_at=str(pr.created_at),
            changed_files=pr.changed_files
        )
        
        response = self.model.generate_content(prompt)
        return self._parse_response(response)

class TestAutomationAgent(BaseAIAssistant):
    def analyze_tests(self) -> Dict[str, List[str]]:
        repo_info = self._get_repository_info()
        
        prompt = """Analyze this GitHub repository's testing and automation setup and identify areas for improvement.

        Repository Information:
        - Description: {description}
        - Languages: {languages}
        - Stars: {stars}
        - Forks: {forks}
        - Watchers: {watchers}
        - Open Issues: {open_issues_count}
        - Default Branch: {default_branch}

        Please analyze the repository and provide detailed suggestions for testing and automation improvements in the following categories:

        1. Unit Tests:
        - Identify missing unit tests
        - Suggest test improvements
        - Recommend test organization

        2. Integration Tests:
        - Identify missing integration tests
        - Suggest test improvements
        - Recommend test scenarios

        3. CI/CD:
        - Identify missing CI/CD configurations
        - Suggest CI/CD improvements
        - Recommend best practices

        4. Test Automation:
        - Identify areas for automation
        - Suggest automation improvements
        - Recommend automation tools

        Please format your response as a JSON object with the following structure:
        {{
            "unit_tests": ["suggestion", ...],
            "integration_tests": ["suggestion", ...],
            "ci_cd": ["suggestion", ...],
            "test_automation": ["suggestion", ...]
        }}
        """.format(
            description=repo_info['description'],
            languages=', '.join(repo_info['languages']),
            stars=repo_info['stars'],
            forks=repo_info['forks'],
            watchers=repo_info['watchers'],
            open_issues_count=repo_info['open_issues_count'],
            default_branch=repo_info['default_branch']
        )
        
        response = self.model.generate_content(prompt)
        return self._parse_response(response)

    def _parse_response(self, response):
        try:
            content = response.text
            if content.startswith('{'):
                return json.loads(content)
            else:
                # If not JSON, try to parse as numbered list
                suggestions = {}
                current_category = None
                lines = content.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if line.endswith(':'):
                        current_category = line[:-1].lower().replace(' ', '_')
                        suggestions[current_category] = []
                    elif current_category and line:
                        body = """{}
Category: {}
Priority: Medium
""".format(line, current_category)
                        suggestions[current_category].append(body)
                return suggestions
        except Exception as e:
            print("Error parsing response: %s" % e)
            return {}
