from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from ai_agent import GitHubAIAssistant, GitHubConfig, AIConfig
from dotenv import load_dotenv
import os

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    suggestions: Dict[str, List[str]]
    issues_created: int

class Issue(BaseModel):
    title: str
    body: str
    number: int
    state: str

@app.get("/api/analyze")
async def analyze_repository():
    """Analyze the repository and return suggestions"""
    try:
        analysis = assistant.analyze_repository()
        return AnalysisResponse(
            status="success",
            suggestions=analysis,
            issues_created=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create_issues")
async def create_issues():
    """Create issues based on analysis"""
    try:
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
            issues_created=issues_created
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/issues")
async def get_issues():
    """Get all issues in the repository"""
    try:
        issues = []
        for issue in assistant.repo.issues(state='all'):
            issues.append({
                'title': issue.title,
                'body': issue.body,
                'number': issue.number,
                'state': issue.state
            })
        return issues
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
