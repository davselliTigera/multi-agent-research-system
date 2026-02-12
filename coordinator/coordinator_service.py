"""
coordinator_service.py
Coordinator Agent - Orchestrates the multi-agent workflow
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Literal
import httpx
import uuid
import json
import redis
import os
from datetime import datetime
from shared_models import AgentMessage, AgentResponse, ResearchState, AGENTS

class CoordinatorService:
    """Coordinator that orchestrates the multi-agent workflow"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis-service"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        self.agents = AGENTS
        
    async def call_agent(self, agent_key: str, message: AgentMessage) -> AgentResponse:
        """Call an agent service"""
        url = f"{self.agents[agent_key]}/process"
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                print(f"Calling agent {agent_key} at {url}")
                response = await client.post(url, json=message.model_dump())
                response.raise_for_status()
                result = AgentResponse(**response.json())
                print(f"Agent {agent_key} responded: success={result.success}")
                return result
        except httpx.ConnectError as e:
            print(f"Connection error calling {agent_key} at {url}: {e}")
            return AgentResponse(
                task_id=message.task_id,
                agent_name=agent_key,
                success=False,
                data={},
                error=f"Connection error: {str(e)}"
            )
        except Exception as e:
            print(f"Error calling {agent_key}: {e}")
            return AgentResponse(
                task_id=message.task_id,
                agent_name=agent_key,
                success=False,
                data={},
                error=str(e)
            )
    
    def get_state(self, task_id: str) -> dict:
        """Get current state"""
        state_json = self.redis_client.get(f"task:{task_id}")
        if state_json:
            return json.loads(state_json)
        return None
    
    def update_state(self, task_id: str, updates: dict):
        """Update state"""
        state = self.get_state(task_id) or {}
        state.update(updates)
        self.redis_client.set(f"task:{task_id}", json.dumps(state))
    
    async def should_continue(self, task_id: str) -> Literal["continue", "finalize"]:
        """Decide whether to continue research"""
        state = self.get_state(task_id)
        
        # Hard limits
        if state.get("iteration", 0) >= state.get("max_iterations", 2):
            return "finalize"
        
        if state.get("quality_score", 0) >= 0.8:
            return "finalize"
        
        if len(state.get("key_findings", [])) >= 10:
            return "finalize"
        
        return "continue"
    
    async def run_workflow(self, task_id: str):
        """Execute the complete workflow"""
        try:
            state = self.get_state(task_id)
            print(f"Starting workflow for task {task_id}")
            
            # Step 1: Topic Refiner
            print("Step 1: Topic Refiner")
            self.update_state(task_id, {"status": "refining_topic", "current_agent": "Dr. Topic Refiner"})
            message = AgentMessage(
                task_id=task_id,
                agent_from="coordinator",
                agent_to="topic_refiner",
                action="refine_topic",
                payload={}
            )
            result = await self.call_agent("topic_refiner", message)
            if not result.success:
                error_msg = f"Topic refiner failed: {result.error}"
                print(error_msg)
                self.update_state(task_id, {"status": "failed", "error": error_msg})
                return {"success": False, "error": error_msg}
            
            # Main research loop
            iteration = 0
            max_iterations = state.get("max_iterations", 2)
            
            while iteration < max_iterations:
                print(f"Iteration {iteration + 1}/{max_iterations}")
                
                # Step 2: Question Architect
                print("Step 2: Question Architect")
                self.update_state(task_id, {"status": "generating_questions", "current_agent": "Prof. Question Architect"})
                message = AgentMessage(
                    task_id=task_id,
                    agent_from="coordinator",
                    agent_to="question_architect",
                    action="generate_questions",
                    payload={}
                )
                result = await self.call_agent("question_architect", message)
                if not result.success:
                    error_msg = f"Question architect failed: {result.error}"
                    print(error_msg)
                    self.update_state(task_id, {"status": "failed", "error": error_msg})
                    return {"success": False, "error": error_msg}
                
                # Step 3: Search Strategist
                print("Step 3: Search Strategist")
                self.update_state(task_id, {"status": "searching", "current_agent": "Agent Search Strategist"})
                message = AgentMessage(
                    task_id=task_id,
                    agent_from="coordinator",
                    agent_to="search_strategist",
                    action="execute_search",
                    payload={}
                )
                result = await self.call_agent("search_strategist", message)
                if not result.success:
                    error_msg = f"Search strategist failed: {result.error}"
                    print(error_msg)
                    self.update_state(task_id, {"status": "failed", "error": error_msg})
                    return {"success": False, "error": error_msg}
                
                # Step 4: Data Analyst
                print("Step 4: Data Analyst")
                self.update_state(task_id, {"status": "analyzing", "current_agent": "Dr. Data Analyst"})
                message = AgentMessage(
                    task_id=task_id,
                    agent_from="coordinator",
                    agent_to="data_analyst",
                    action="analyze_results",
                    payload={}
                )
                result = await self.call_agent("data_analyst", message)
                if not result.success:
                    error_msg = f"Data analyst failed: {result.error}"
                    print(error_msg)
                    self.update_state(task_id, {"status": "failed", "error": error_msg})
                    return {"success": False, "error": error_msg}
                
                # Check if should continue
                decision = await self.should_continue(task_id)
                if decision == "finalize":
                    break
                
                iteration += 1
            
            # Step 5: Report Writer
            print("Step 5: Report Writer")
            self.update_state(task_id, {"status": "generating_report", "current_agent": "Dr. Report Writer"})
            message = AgentMessage(
                task_id=task_id,
                agent_from="coordinator",
                agent_to="report_writer",
                action="generate_report",
                payload={}
            )
            result = await self.call_agent("report_writer", message)
            if not result.success:
                error_msg = f"Report writer failed: {result.error}"
                print(error_msg)
                self.update_state(task_id, {"status": "failed", "error": error_msg})
                return {"success": False, "error": error_msg}
            
            # Mark as complete
            print(f"Workflow completed for task {task_id}")
            self.update_state(task_id, {"status": "completed"})
            
            return {"success": True, "task_id": task_id}
            
        except Exception as e:
            error_msg = f"Workflow error: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.update_state(task_id, {"status": "failed", "error": error_msg})
            return {"success": False, "error": error_msg}

# Create FastAPI app
coordinator = CoordinatorService()
app = FastAPI(title="Coordinator Service")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "coordinator"}

@app.post("/start_research")
async def start_research(topic: str, max_iterations: int = 2):
    """Start a new research task"""
    task_id = str(uuid.uuid4())
    
    # Initialize state
    initial_state = {
        "task_id": task_id,
        "original_topic": topic,
        "topic": topic,
        "research_questions": [],
        "search_queries": [],
        "search_results": [],
        "key_findings": [],
        "iteration": 0,
        "max_iterations": max_iterations,
        "quality_score": 0.0,
        "final_report": "",
        "status": "initialized",
        "current_agent": "",
        "agent_logs": [],
        "error": None
    }
    
    coordinator.update_state(task_id, initial_state)
    
    # Start workflow in background (don't await)
    import asyncio
    asyncio.create_task(coordinator.run_workflow(task_id))
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Research task started. Use /task/{task_id} to check progress."
    }

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and results"""
    state = coordinator.get_state(task_id)
    if not state:
        raise HTTPException(status_code=404, detail="Task not found")
    return state

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)
