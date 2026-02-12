#!/usr/bin/env python3
"""
FastAPI Integration Example
Shows how to expose agents as REST APIs in your own service
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import sys
import os
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.topic_refiner_service import TopicRefinerAgent
from agents.question_architect_service import QuestionArchitectAgent
from agents.search_strategist_service import SearchStrategistAgent

# Initialize FastAPI
app = FastAPI(
    title="Research Agents API",
    description="Expose research agents as REST APIs",
    version="1.0.0"
)

# Initialize agents (singleton pattern)
refiner = TopicRefinerAgent()
architect = QuestionArchitectAgent()
searcher = SearchStrategistAgent()

# In-memory storage for demo (use Redis/DB in production)
tasks_storage = {}


# Request/Response models
class TopicRequest(BaseModel):
    topic: str

class TopicResponse(BaseModel):
    original: str
    refined: str

class QuestionsRequest(BaseModel):
    topic: str
    iteration: int = 0

class QuestionsResponse(BaseModel):
    topic: str
    questions: List[str]

class SearchRequest(BaseModel):
    query: str
    max_results: int = 5

class SearchResponse(BaseModel):
    query: str
    results: List[dict]
    count: int

class ResearchRequest(BaseModel):
    topic: str
    num_questions: int = 3

class ResearchResponse(BaseModel):
    task_id: str
    status: str
    message: str


# Endpoints
@app.get("/")
def root():
    """API information"""
    return {
        "name": "Research Agents API",
        "version": "1.0.0",
        "endpoints": {
            "refine": "POST /refine - Refine a research topic",
            "questions": "POST /questions - Generate research questions",
            "search": "POST /search - Execute web search",
            "research": "POST /research - Full research workflow (async)",
            "status": "GET /research/{task_id} - Check research status"
        }
    }


@app.post("/refine", response_model=TopicResponse)
def refine_topic(request: TopicRequest):
    """
    Refine a research topic
    
    Example:
    ```
    POST /refine
    {"topic": "machine learning"}
    ```
    """
    try:
        refined = refiner.refine_topic(request.topic)
        return TopicResponse(
            original=request.topic,
            refined=refined
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/questions", response_model=QuestionsResponse)
def generate_questions(request: QuestionsRequest):
    """
    Generate research questions for a topic
    
    Example:
    ```
    POST /questions
    {"topic": "quantum computing", "iteration": 0}
    ```
    """
    try:
        questions = architect.generate_questions(
            request.topic, 
            request.iteration
        )
        return QuestionsResponse(
            topic=request.topic,
            questions=questions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
def execute_search(request: SearchRequest):
    """
    Execute web search
    
    Example:
    ```
    POST /search
    {"query": "kubernetes benefits", "max_results": 5}
    ```
    """
    try:
        results = searcher.execute_search(
            request.query,
            max_results=request.max_results
        )
        return SearchResponse(
            query=request.query,
            results=results,
            count=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Start a full research workflow (async)
    
    Example:
    ```
    POST /research
    {"topic": "microservices", "num_questions": 5}
    ```
    
    Then check status with: GET /research/{task_id}
    """
    task_id = str(uuid4())
    
    # Initialize task
    tasks_storage[task_id] = {
        "status": "started",
        "topic": request.topic,
        "results": None
    }
    
    # Run research in background
    background_tasks.add_task(
        run_research_workflow,
        task_id,
        request.topic,
        request.num_questions
    )
    
    return ResearchResponse(
        task_id=task_id,
        status="started",
        message=f"Research started. Check status at /research/{task_id}"
    )


@app.get("/research/{task_id}")
def get_research_status(task_id: str):
    """
    Get research task status
    
    Example:
    ```
    GET /research/abc-123-def
    ```
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks_storage[task_id]


# Background task
def run_research_workflow(task_id: str, topic: str, num_questions: int):
    """Execute research workflow"""
    try:
        tasks_storage[task_id]["status"] = "processing"
        
        # Step 1: Refine topic
        refined = refiner.refine_topic(topic)
        
        # Step 2: Generate questions
        questions = architect.generate_questions(refined, 0)[:num_questions]
        
        # Step 3: Search for each question
        all_results = []
        for question in questions:
            results = searcher.execute_search(question, max_results=2)
            all_results.extend(results)
        
        # Update task with results
        tasks_storage[task_id] = {
            "status": "completed",
            "topic": topic,
            "refined_topic": refined,
            "questions": questions,
            "search_results": all_results,
            "total_results": len(all_results)
        }
        
    except Exception as e:
        tasks_storage[task_id] = {
            "status": "failed",
            "topic": topic,
            "error": str(e)
        }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agents": ["refiner", "architect", "searcher"]}


# Run with: uvicorn fastapi_example:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)