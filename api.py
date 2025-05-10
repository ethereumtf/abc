from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn
from ai_agent import GitHubAIAssistant, GitHubConfig, AIConfig
from dotenv import load_dotenv
import os
import json

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"]
)

# Load environment variables
load_dotenv()

# Initialize AI Assistant
config = GitHubConfig(
    token=os.getenv('GITHUB_TOKEN'),
    repo_owner=os.getenv('REPO_OWNER', 'ethereumtf'),
    repo_name=os.getenv('REPO_NAME', 'abc')
)

ai_config = AIConfig()
assistant = GitHubAIAssistant(config, ai_config)

class AnalysisResponse(BaseModel):
    status: str
    suggestions: Dict[str, List[str]] = {}
    issues_created: int = 0
    repository_info: Dict[str, Any] = {}

class Issue(BaseModel):
    title: str
    body: str
    number: int
    state: str
    created_at: str
    updated_at: str
    comments: int

@app.post("/api/analyze")
async def analyze_repository(request: Request):
    """Analyze the repository and return suggestions"""
    try:
        # Get repository settings from request
        repo_data = await request.json()
        owner = repo_data.get('owner')
        repo = repo_data.get('repo')

        if not owner or not repo:
            raise HTTPException(status_code=400, detail="Repository owner and name are required")

        # Update repository configuration
        assistant.config.repo_owner = owner
        assistant.config.repo_name = repo
        assistant.repo = assistant.gh.repository(owner, repo)

        # Get repository information
        repo_info = {
            'description': assistant.repo.description or "No description",
            'languages': assistant._get_languages(),
            'stars': assistant.repo.stargazers_count,
            'forks': assistant.repo.forks_count,
            'watchers': assistant.repo.watchers_count,
            'created_at': str(assistant.repo.created_at),
            'updated_at': str(assistant.repo.updated_at)
        }

        # Get analysis
        analysis = assistant.analyze_repository()
        
        try:
            return AnalysisResponse(
                status="success",
                suggestions=analysis,
                issues_created=0,
                repository_info=repo_info
            )
        except Exception as e:
            print(f"Error creating response: {e}")
            return AnalysisResponse(
                status="error",
                suggestions={},
                issues_created=0,
                repository_info={}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create_issues")
async def create_issues(request: Request):
    """Create issues based on analysis"""
    try:
        # Get repository settings from request
        repo_data = await request.json()
        owner = repo_data.get('owner')
        repo = repo_data.get('repo')

        if not owner or not repo:
            raise HTTPException(status_code=400, detail="Repository owner and name are required")

        # Update repository configuration
        assistant.config.repo_owner = owner
        assistant.config.repo_name = repo
        assistant.repo = assistant.gh.repository(owner, repo)

        analysis = assistant.analyze_repository()
        issues_created = 0
        
        for category, suggestions in analysis.items():
            for suggestion in suggestions:
                title = f"[AI Suggestion] {category.replace('_', ' ').title()}: {suggestion[:50]}"
                body = f"""
                AI Analysis: {suggestion}
                
                Category: {category.replace('_', ' ').title()}
                Status: Awaiting Review
                """
                if assistant.create_issue(title, body):
                    issues_created += 1
        
        return AnalysisResponse(
            status="success",
            suggestions=analysis,
            issues_created=issues_created,
            repository_info={
                'description': assistant.repo.description or "No description",
                'languages': assistant._get_languages(),
                'stars': assistant.repo.stargazers_count,
                'forks': assistant.repo.forks_count,
                'watchers': assistant.repo.watchers_count,
                'created_at': str(assistant.repo.created_at),
                'updated_at': str(assistant.repo.updated_at)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/issues")
async def get_issues(request: Request):
    """Get all issues in the repository"""
    try:
        # Get repository settings from request
        repo_data = await request.json()
        owner = repo_data.get('owner')
        repo = repo_data.get('repo')

        if not owner or not repo:
            raise HTTPException(status_code=400, detail="Repository owner and name are required")

        # Update repository configuration
        assistant.config.repo_owner = owner
        assistant.config.repo_name = repo
        assistant.repo = assistant.gh.repository(owner, repo)

        issues = []
        for issue in assistant.repo.issues(state='all'):
            issues.append({
                'title': issue.title,
                'body': issue.body,
                'number': issue.number,
                'state': issue.state,
                'created_at': str(issue.created_at),
                'updated_at': str(issue.updated_at),
                'comments': issue.comments_count
            })
        return issues
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/repository")
async def get_repository_info():
    """Get repository information"""
    try:
        repo_info = {
            'description': assistant.repo.description or "No description",
            'languages': assistant._get_languages(),
            'stars': assistant.repo.stargazers_count,
            'forks': assistant.repo.forks_count,
            'watchers': assistant.repo.watchers_count,
            'created_at': str(assistant.repo.created_at),
            'updated_at': str(assistant.repo.updated_at),
            'open_issues': assistant.repo.open_issues_count,
            'default_branch': assistant.repo.default_branch
        }
        return repo_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/your-code.js")
async def serve_js():
    return FileResponse("your-code.js")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
