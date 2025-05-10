import os
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from github3 import login
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

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

class GitHubAIAssistant:
    def __init__(self, config: GitHubConfig, ai_config: AIConfig):
        self.config = config
        self.ai_config = ai_config
        
        # Initialize Google Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel(ai_config.model_name)
        
        # Initialize GitHub client
        print("Initializing GitHub client...")
        self.gh = login(token=config.token)
        print(f"Accessing repository {config.repo_owner}/{config.repo_name}...")
        self.repo = self.gh.repository(config.repo_owner, config.repo_name)
        print(f"Repository access successful. Description: {self.repo.description}")

    def analyze_repository(self) -> Dict[str, List[str]]:
        """Analyze the repository and identify potential issues and improvements"""
        try:
            # Get repository information
            repo_info = {
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

            # Create a more detailed analysis prompt
            recent_commits = []
            for commit in repo_info['recent_commits']:
                recent_commits.append(f"- {commit.message} ({commit.author.name if commit.author else 'Unknown'})")
            
            open_issues = []
            for issue in repo_info['open_issues']:
                open_issues.append(f"- #{issue.number}: {issue.title} ({issue.state})")

            repo_info_str = f"""Repository Information:
            - Description: {repo_info['description']}
            - Languages: {', '.join(repo_info['languages'])}
            - Stars: {repo_info['stars']}
            - Forks: {repo_info['forks']}
            - Watchers: {repo_info['watchers']}
            - Open Issues: {repo_info['open_issues_count']}
            - Default Branch: {repo_info['default_branch']}"""

            commits_str = "\n".join(recent_commits)
            issues_str = "\n".join(open_issues)

            prompt = f"""Analyze this GitHub repository and provide detailed suggestions.

            {repo_info_str}

            Recent Commits:
            {commits_str}

            Open Issues:
            {issues_str}

            Please analyze the repository and provide detailed suggestions in the following categories:

            1. Code Improvements:
            - Identify potential code quality issues
            - Suggest architectural improvements
            - Recommend best practices

            2. Documentation:
            - Identify missing documentation
            - Suggest documentation improvements
            - Recommend documentation structure

            3. Testing:
            - Identify missing tests
            - Suggest test improvements
            - Recommend testing strategies

            4. Performance:
            - Identify potential performance bottlenecks
            - Suggest optimizations
            - Recommend monitoring strategies

            For each suggestion, please:
            - Provide a clear description of the issue
            - Explain the potential impact
            - Suggest specific steps to improve
            - Rate the priority (High, Medium, Low)

            Format the response as a JSON object with these categories and suggestions.
            """

            print("Sending analysis request to Gemini...")
            print("Prompt:", prompt)
            
            response = self.model.generate_content(prompt)
            analysis = response.text
            print("Received analysis:", analysis)
            
            return self._parse_analysis(analysis)
            
        except Exception as e:
            print(f"Error analyzing repository: {e}")
            return {}

    def _get_languages(self) -> List[str]:
        """Get the list of languages used in the repository"""
        try:
            # Get the languages dictionary from GitHub
            languages = self.repo.languages()
            
            # If languages is None or empty, return an empty list
            if not languages:
                return []
                
            # Convert the dictionary to a list of language names
            return list(languages.keys())
            
        except Exception as e:
            print(f"Error getting languages: {e}")
            return []

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
        suggestions = {}
        
        print("Parsing analysis...")
        print("Raw analysis:", analysis)
        
        try:
            # Try to parse as JSON first
            import json
            try:
                data = json.loads(analysis)
                if 'code_improvements' in data:
                    suggestions['code_improvements'] = [s['suggestion'] for s in data['code_improvements']]
                if 'documentation_gaps' in data:
                    suggestions['documentation'] = [s['suggestion'] for s in data['documentation_gaps']]
                if 'testing_needs' in data:
                    suggestions['testing'] = [s['suggestion'] for s in data['testing_needs']]
                if 'performance_optimizations' in data:
                    suggestions['performance'] = [s['suggestion'] for s in data['performance_optimizations']]
                
                print("Successfully parsed as JSON")
                return suggestions
            except json.JSONDecodeError:
                print("Failed to parse as JSON, trying numbered list format")

            # If JSON parsing fails, try numbered list format
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
            
            print("Parsed suggestions:", suggestions)
            return suggestions
        
        except Exception as e:
            print(f"Error parsing analysis: {e}")
            return {}

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
        repo_owner=os.getenv('REPO_OWNER'),
        repo_name=os.getenv('REPO_NAME')
    )
    
    ai_config = AIConfig()
    
    # Initialize and run the AI assistant
    assistant = GitHubAIAssistant(config, ai_config)
    assistant.run_analysis_cycle()