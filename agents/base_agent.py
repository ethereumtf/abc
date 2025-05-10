from typing import Dict, List, Any
import google.generativeai as genai
from github3 import login
from dotenv import load_dotenv
import json
import os

load_dotenv()

class BaseAgent:
    def __init__(self, repo_owner: str, repo_name: str):
        # Initialize Google Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Initialize GitHub client
        self.gh = login(token=os.getenv('GITHUB_TOKEN'))
        self.repo = self.gh.repository(repo_owner, repo_name)
        
        # Store repository information
        self.repo_info = self._get_repository_info()
        
    def _get_repository_info(self) -> Dict[str, Any]:
        return {
            'description': self.repo.description or "No description",
            'languages': self.repo.languages(),
            'stars': self.repo.stargazers_count,
            'forks': self.repo.forks_count,
            'watchers': self.repo.watchers_count,
            'open_issues_count': self.repo.open_issues_count,
            'default_branch': self.repo.default_branch,
            'recent_commits': list(self.repo.commits())[:10]
        }
    
    async def analyze(self, prompt: str) -> Dict[str, Any]:
        """Analyze the repository using Gemini AI."""
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            print(f"Error in analysis: {e}")
            return {}
    
    async def create_issue(self, title: str, body: str) -> Dict[str, Any]:
        """Create a new issue in the repository."""
        try:
            issue = self.repo.create_issue(
                title=title,
                body=body
            )
            return {
                'status': 'success',
                'issue': {
                    'number': issue.number,
                    'url': issue.html_url
                }
            }
        except Exception as e:
            print(f"Error creating issue: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def create_pull_request(self, title: str, body: str, branch: str) -> Dict[str, Any]:
        """Create a new pull request."""
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=branch,
                base=self.repo.default_branch
            )
            return {
                'status': 'success',
                'pr': {
                    'number': pr.number,
                    'url': pr.html_url
                }
            }
        except Exception as e:
            print(f"Error creating PR: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def create_branch(self, branch_name: str) -> bool:
        """Create a new branch from the default branch."""
        try:
            default_branch = self.repo.branch(self.repo.default_branch)
            self.repo.create_ref(f"refs/heads/{branch_name}", default_branch.commit.sha)
            return True
        except Exception as e:
            print(f"Error creating branch: {e}")
            return False
