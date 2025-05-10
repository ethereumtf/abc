from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.base_agent import BaseAgent
from typing import Dict, Any
import os

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Tensorus API",
    description="API for Tensorus repository analysis and management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent with default values
agent = BaseAgent(
    repo_owner=os.getenv('REPO_OWNER', 'tensorus'),
    repo_name=os.getenv('REPO_NAME', 'tensorus')
)

class IssueRequest(BaseModel):
    title: str
    body: str

class AnalysisRequest(BaseModel):
    prompt: str

class CodeRequest(BaseModel):
    code: str
    language: str

@app.post("/api/create_issues", response_model=Dict[str, Any])
async def create_issue(request: IssueRequest):
    try:
        result = await agent.create_issue(request.title, request.body)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/issues")
async def analyze_issues():
    try:
        prompt = "Analyze the repository issues and suggest improvements"
        result = await agent.analyze(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/docs")
async def analyze_docs():
    try:
        prompt = "Analyze the repository documentation and suggest improvements"
        result = await agent.analyze(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/tests")
async def analyze_tests():
    try:
        prompt = "Analyze the repository test coverage and suggest improvements"
        result = await agent.analyze(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/code")
async def analyze_code(request: CodeRequest):
    try:
        prompt = f"Analyze this {request.language} code and suggest improvements:\n{request.code}"
        result = await agent.analyze(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/issues")
async def get_issues():
    try:
        print("Fetching issues...")
        issues = await agent.get_issues()
        print(f"Found {len(issues)} issues")
        return issues
    except Exception as e:
        print(f"Error in get_issues endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "ok", "message": "Tensorus API is running"}
