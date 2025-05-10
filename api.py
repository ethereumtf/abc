from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn
from ai_agent import GitHubConfig, AIConfig
from specialized_agents import (
    IssueReportingAgent,
    DocumentationImprovementAgent,
    CodeContributionAgent,
    CodeReviewAgent,
    TestAutomationAgent
)
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

# Initialize specialized agents
config = GitHubConfig(
    token=os.getenv('GITHUB_TOKEN'),
    repo_owner=os.getenv('REPO_OWNER', 'tensorus'),
    repo_name=os.getenv('REPO_NAME', 'tensorus')
)

ai_config = AIConfig()

# Initialize specialized agents
issue_agent = IssueReportingAgent(config, ai_config)
docs_agent = DocumentationImprovementAgent(config, ai_config)
code_agent = CodeContributionAgent(config, ai_config)
review_agent = CodeReviewAgent(config, ai_config)
test_agent = TestAutomationAgent(config, ai_config)

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

@app.post("/api/analyze/issues")
async def analyze_issues(request: Request):
    """Analyze the repository for potential issues to report"""
    try:
        # Get repository settings from request
        repo_data = await request.json()
        owner = repo_data.get('owner')
        repo = repo_data.get('repo')

        if not owner or not repo:
            raise HTTPException(status_code=400, detail="Repository owner and name are required")

        # Update repository configuration
        issue_agent.config.repo_owner = owner
        issue_agent.config.repo_name = repo
        issue_agent.repo = issue_agent.gh.repository(owner, repo)

        # Get analysis
        analysis = issue_agent.analyze_issues()
        
        return AnalysisResponse(
            status="success",
            suggestions=analysis,
            issues_created=0,
            repository_info={}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/docs")
async def analyze_docs(request: Request):
    """Analyze the repository for documentation improvements"""
    try:
        # Get repository settings from request
        repo_data = await request.json()
        owner = repo_data.get('owner')
        repo = repo_data.get('repo')

        if not owner or not repo:
            raise HTTPException(status_code=400, detail="Repository owner and name are required")

        # Update repository configuration
        docs_agent.config.repo_owner = owner
        docs_agent.config.repo_name = repo
        docs_agent.repo = docs_agent.gh.repository(owner, repo)

        # Get analysis
        analysis = docs_agent.analyze_documentation()
        
        return AnalysisResponse(
            status="success",
            suggestions=analysis,
            issues_created=0,
            repository_info={}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/code")
async def analyze_code(request: Request):
    """Analyze the repository for code contributions"""
    try:
        # Get repository settings from request
        repo_data = await request.json()
        owner = repo_data.get('owner')
        repo = repo_data.get('repo')

        if not owner or not repo:
            raise HTTPException(status_code=400, detail="Repository owner and name are required")

        # Update repository configuration
        code_agent.config.repo_owner = owner
        code_agent.config.repo_name = repo
        code_agent.repo = code_agent.gh.repository(owner, repo)

        # Get analysis
        analysis = code_agent.analyze_codebase()
        
        return AnalysisResponse(
            status="success",
            suggestions=analysis,
            issues_created=0,
            repository_info={}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/tests")
async def analyze_tests(request: Request):
    """Analyze the repository for testing and automation improvements"""
    try:
        # Get repository settings from request
        repo_data = await request.json()
        owner = repo_data.get('owner')
        repo = repo_data.get('repo')

        if not owner or not repo:
            raise HTTPException(status_code=400, detail="Repository owner and name are required")

        # Update repository configuration
        test_agent.config.repo_owner = owner
        test_agent.config.repo_name = repo
        test_agent.repo = test_agent.gh.repository(owner, repo)

        # Get analysis
        analysis = test_agent.analyze_tests()
        
        return AnalysisResponse(
            status="success",
            suggestions=analysis,
            issues_created=0,
            repository_info={}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create_issue")
async def create_issue(request: Request):
    """Create a specific issue based on analysis"""
    try:
        # Get repository settings from request
        repo_data = await request.json()
        owner = repo_data.get('owner')
        repo = repo_data.get('repo')
        category = repo_data.get('category')
        suggestion = repo_data.get('suggestion')

        if not owner or not repo or not category or not suggestion:
            raise HTTPException(status_code=400, detail="Repository owner, name, category, and suggestion are required")

        # Update repository configuration
        issue_agent.config.repo_owner = owner
        issue_agent.config.repo_name = repo
        issue_agent.repo = issue_agent.gh.repository(owner, repo)

        # Create issue
        title = f"[{category.replace('_', ' ')}] {suggestion[:50]}..."
        body = f"""{suggestion}

Category: {category}
Priority: Medium
"""
        issue = issue_agent.create_issue(title, body)

        return {
            'status': 'success',
            'issue': issue
        }
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
