import os
from typing import Optional, List, Dict
import google.generativeai as genai
from github3 import login
from dotenv import load_dotenv
from pydantic import BaseModel

class GitHubConfig(BaseModel):
    token: str
    repo_owner: str
    repo_name: str

class AIConfig(BaseModel):
    model_name: str = "gemini-pro"
    temperature: float = 0.7
    max_output_tokens: int = 2048

class GitHubAIAssistant:
    def __init__(self, config: GitHubConfig, ai_config: AIConfig):
        self.config = config
        self.ai_config = ai_config
        
        # Initialize Google Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel(ai_config.model_name)
        
        # Initialize GitHub client
        self.gh = login(token=config.token)
        self.repo = self.gh.repository(config.repo_owner, config.repo_name)

    def analyze_repository(self) -> Dict[str, List[str]]:
        """Analyze the repository and identify potential issues and improvements"""
        # Get repository information
        repo_info = {
            'description': self.repo.description,
            'languages': list(self.repo.languages().keys()),
            'open_issues': self.repo.issues(state='open'),
            'recent_commits': self.repo.commits()[:10]
        }

        # Use Gemini to analyze repository
        prompt = f"""
        Analyze this GitHub repository and identify potential improvements:
        Repository Description: {repo_info['description']}
        Languages: {', '.join(repo_info['languages'])}
        
        Identify:
        1. Code improvements needed
        2. Documentation gaps
        3. Testing needs
        4. Performance optimizations

        Return a structured JSON with categories and specific suggestions.
        """

        response = self.model.generate_content(prompt)
        analysis = response.text
        return self._parse_analysis(analysis)

    def create_issue(self, title: str, body: str) -> bool:
        """Create a new issue in the repository"""
        try:
            self.repo.create_issue(title=title, body=body)
            return True
        except Exception as e:
            print(f"Error creating issue: {e}")
            return False

    def propose_changes(self, issue_id: int, changes: str) -> bool:
        """Propose code changes for an existing issue"""
        try:
            issue = self.repo.issue(issue_id)
            issue.create_comment(f"Proposed changes:\n\n{changes}")
            return True
        except Exception as e:
            print(f"Error proposing changes: {e}")
            return False

    def _parse_analysis(self, analysis: str) -> Dict[str, List[str]]:
        """Parse the analysis response from Gemini"""
        # This is a simplified parser - in production, use a more robust JSON parsing
        suggestions = {}
        current_category = None
        
        for line in analysis.split('\n'):
            line = line.strip()
            if line.startswith('1.'):
                current_category = 'code_improvements'
            elif line.startswith('2.'):
                current_category = 'documentation'
            elif line.startswith('3.'):
                current_category = 'testing'
            elif line.startswith('4.'):
                current_category = 'performance'
            elif current_category and line:
                if current_category not in suggestions:
                    suggestions[current_category] = []
                suggestions[current_category].append(line)
        
        return suggestions

    def run_analysis_cycle(self):
        """Run a complete analysis and contribution cycle"""
        print("Starting analysis cycle...")
        
        # Analyze repository
        analysis = self.analyze_repository()
        print("Analysis complete. Identified improvements:")
        print(analysis)
        
        # Create issues for identified improvements
        for category, suggestions in analysis.items():
            for suggestion in suggestions:
                title = f"[AI Suggestion] {category.replace('_', ' ').title()}: {suggestion[:50]}"
                body = f"""
                AI Analysis: {suggestion}
                
                Category: {category.replace('_', ' ').title()}
                Status: Awaiting Review
                """
                self.create_issue(title, body)

        print("Analysis cycle completed.")

if __name__ == "__main__":
    # Load configuration
    load_dotenv()
    
    # Example configuration
    config = GitHubConfig(
        token=os.getenv('GITHUB_TOKEN'),
        repo_owner='ethereumtf',
        repo_name='abc'
    )
    
    ai_config = AIConfig()
    
    # Initialize and run the AI assistant
    assistant = GitHubAIAssistant(config, ai_config)
    assistant.run_analysis_cycle()
