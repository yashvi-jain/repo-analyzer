from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from analyzer import analyze_github_repository
from database import init_db

app = FastAPI(
    title="GitHub Repository Analyzer",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():

    init_db()

@app.get("/")
def root():

    return {
        "message": "GitHub Repository Analyzer API"
    }

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }

@app.post("/analyze")
def analyze(payload: dict):

    github_url = payload.get("github_url")

    if not github_url:
        raise HTTPException(
            status_code=400,
            detail="github_url is required",
        )

    return analyze_github_repository(
        github_url
    )

# Database endpoints
# (implemented after persistence)
@app.get("/repositories")
def repositories():

    return {
        "message":
        "Coming after database integration."
    }

@app.get("/repository/{repo_id}")
def repository(repo_id: int):

    return {
        "message":
        f"Repository {repo_id} endpoint coming soon."
    }

@app.delete("/repository/{repo_id}")
def delete_repository(repo_id: int):

    return {
        "message":
        f"Repository {repo_id} deleted."
    }