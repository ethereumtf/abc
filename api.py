from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Any
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

# Import specialized agents
from agents.issues.issue_agent import IssueReportingAgent
from agents.code.code_agent import CodeAnalysisAgent
from agents.tests.test_agent import TestAgent
from agents.prs.pr_agent import PRReviewAgent

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
issue_agent = IssueReportingAgent(
    os.getenv('REPO_OWNER', 'tensorus'),
    os.getenv('REPO_NAME', 'tensorus')
)
code_agent = CodeAnalysisAgent(
    os.getenv('REPO_OWNER', 'tensorus'),
    os.getenv('REPO_NAME', 'tensorus')
)
test_agent = TestAgent(
    os.getenv('REPO_OWNER', 'tensorus'),
    os.getenv('REPO_NAME', 'tensorus')
)
pr_agent = PRReviewAgent(
    os.getenv('REPO_OWNER', 'tensorus'),
    os.getenv('REPO_NAME', 'tensorus')
)

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
        issue_agent.repo = issue_agent.gh.repository(owner, repo)

        # Analyze repository
        analysis = await issue_agent.analyze_issues()
        
        # Create issues based on analysis
        issues_created = 0
        for category, suggestions in analysis.items():
            for suggestion in suggestions:
                issue = issue_agent.create_issue(
                    title=f"{category.title()} - {suggestion[:50]}...",
                    body=suggestion
                )
                issues_created += 1

        return AnalysisResponse(
            status="success",
            suggestions=analysis,
            issues_created=issues_created,
            repository_info={
                "owner": owner,
                "repo": repo,
                "issues_created": issues_created
            }
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
        code_agent.repo = code_agent.gh.repository(owner, repo)

        # Analyze repository
        analysis = await code_agent.analyze_code()
        
        return AnalysisResponse(
            status="success",
            suggestions=analysis,
            issues_created=0,
            repository_info={
                "owner": owner,
                "repo": repo
            }
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
        test_agent.repo = test_agent.gh.repository(owner, repo)

        # Analyze repository
        analysis = await test_agent.analyze_tests()
        
        return AnalysisResponse(
            status="success",
            suggestions=analysis,
            issues_created=0,
            repository_info={
                "owner": owner,
                "repo": repo
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create/issue")
async def create_issue(request: Request):
    """Create a specific issue based on analysis"""
    try:
        # Get repository settings from request
        repo_data = await request.json()
        owner = repo_data.get('owner')
        repo = repo_data.get('repo')
        title = repo_data.get('title')
        body = repo_data.get('body')

        if not owner or not repo or not title or not body:
            raise HTTPException(status_code=400, detail="Repository owner, name, title, and body are required")

        # Update repository configuration
        issue_agent.repo = issue_agent.gh.repository(owner, repo)

        # Create issue
        issue = issue_agent.create_issue(title, body)

        return Issue(
            title=issue.title,
            body=issue.body,
            number=issue.number,
            state=issue.state,
            created_at=issue.created_at,
            updated_at=issue.updated_at,
            comments=issue.comments
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review/pr")
async def review_pr(request: Request):
    """Review a pull request"""
    try:
        # Get repository settings from request
        repo_data = await request.json()
        owner = repo_data.get('owner')
        repo = repo_data.get('repo')
        pr_number = repo_data.get('pr_number')

        if not owner or not repo or not pr_number:
            raise HTTPException(status_code=400, detail="Repository owner, name, and PR number are required")

        # Update repository configuration
        pr_agent.repo = pr_agent.gh.repository(owner, repo)

        # Review PR
        review = await pr_agent.analyze_pr(pr_number)
        
        return AnalysisResponse(
            status="success",
            suggestions=review,
            issues_created=0,
            repository_info={
                "owner": owner,
                "repo": repo,
                "pr_number": pr_number
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create/review")
async def create_review(request: Request):
    """Create a review for a pull request"""
    try:
        # Get repository settings from request
        repo_data = await request.json()
        owner = repo_data.get('owner')
        repo = repo_data.get('repo')
        pr_number = repo_data.get('pr_number')

        if not owner or not repo or not pr_number:
            raise HTTPException(status_code=400, detail="Repository owner, name, and PR number are required")

        # Update repository configuration
        pr_agent.repo = pr_agent.gh.repository(owner, repo)

        # Create review
        review = await pr_agent.create_review(pr_number)

        return {
            "review_id": review["review_id"],
            "review_url": review["review_url"],
            "review_body": review["review_body"]
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
