"""
coordinator_a2a.py
Coordinator Service - A2A Protocol Implementation (FIXED)
Orchestrates the multi-agent workflow using A2A messages
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Literal
import httpx
import uuid
import json
import redis
import os
import asyncio
from datetime import datetime
from shared.a2a_models import (
    A2AMessage, MessageStatus, create_action_request,
    AGENT_URIS, AGENT_SERVICES, A2AActionResponse, A2AError
)


class A2ACoordinator:
    """Coordinator that orchestrates multi-agent workflow using A2A protocol"""
    
    def __init__(self):
        self.agent_id = AGENT_URIS["coordinator"]
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis-service"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        
    async def send_message(self, agent_uri: str, message: A2AMessage) -> A2AMessage:
        """
        Send A2A message to an agent
        Uses HTTP POST to /message endpoint
        """
        agent_url = AGENT_SERVICES.get(agent_uri)
        if not agent_url:
            raise ValueError(f"Unknown agent URI: {agent_uri}")
        
        url = f"{agent_url}/message"
        
        try:
            print(f"[Coordinator] Sending message to {agent_uri}")
            async with httpx.AsyncClient(timeout=120.0) as client:
                # WORKAROUND: Manually serialize content to fix Pydantic Union serialization bug
                # The issue: Pydantic only serializes the @type discriminator for Union fields
                # The fix: Manually serialize the content object and construct the message dict
                message_dict = {
                    "@type": message.type,
                    "id": message.id,
                    "to": message.to,
                    "from": message.from_agent,
                    "content": json.loads(message.content.model_dump_json(by_alias=True, exclude_none=True)),
                    "timestamp": message.timestamp,
                    "metadata": message.metadata
                }
                if message.reply_to:
                    message_dict["reply_to"] = message.reply_to
                
                print(f"[Coordinator] Message payload: {json.dumps(message_dict, indent=2)}")
                
                response = await client.post(url, json=message_dict)
                response.raise_for_status()
                response_data = response.json()
                
                print(f"[Coordinator] Received response: {json.dumps(response_data, indent=2)}")
                
                # Parse the response back into A2AMessage
                return A2AMessage(**response_data)
                
        except httpx.ConnectError as e:
            print(f"[Coordinator] Connection error to {agent_uri}: {e}")
            raise Exception(f"Cannot connect to agent {agent_uri}")
        except Exception as e:
            print(f"[Coordinator] Error communicating with {agent_uri}: {e}")
            raise
    
    async def call_agent_action(
        self, 
        agent_uri: str, 
        action: str, 
        parameters: dict,
        context: dict = None
    ) -> dict:
        """
        Call an agent action using A2A protocol
        Returns the result from the action response
        """
        # Create action request message
        message = create_action_request(
            message_id=str(uuid.uuid4()),
            to=agent_uri,
            from_agent=self.agent_id,
            action=action,
            parameters=parameters,
            context=context or {}
        )
        
        # Send message and get response
        response = await self.send_message(agent_uri, message)
        
        # Debug: Print response structure
        print(f"[Coordinator] Response type: {type(response)}")
        print(f"[Coordinator] Response content type: {type(response.content)}")
        print(f"[Coordinator] Response content: {response.content}")
        
        # Check if response content is an A2AActionResponse
        if isinstance(response.content, A2AActionResponse):
            if response.content.status == MessageStatus.COMPLETED:
                return response.content.result
            else:
                error = response.content.error or "Action failed"
                raise Exception(f"Action {action} failed: {error}")
        
        # Check if it's an error response
        elif isinstance(response.content, A2AError):
            raise Exception(f"Agent error: {response.content.message}")
        
        # Try to access as dict (fallback)
        elif hasattr(response.content, '__dict__'):
            content_dict = response.content.__dict__
            if 'status' in content_dict:
                if content_dict['status'] == MessageStatus.COMPLETED:
                    return content_dict.get('result', {})
                else:
                    error = content_dict.get('error', 'Action failed')
                    raise Exception(f"Action {action} failed: {error}")
        
        # Last resort: check for status attribute
        elif hasattr(response.content, 'status'):
            if response.content.status == MessageStatus.COMPLETED:
                return response.content.result if hasattr(response.content, 'result') else {}
            else:
                error = response.content.error if hasattr(response.content, 'error') else "Action failed"
                raise Exception(f"Action {action} failed: {error}")
        
        # If none of the above worked, raise an error
        raise Exception(
            f"Unexpected response type from {agent_uri}. "
            f"Content type: {type(response.content)}, "
            f"Content: {response.content}"
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
        """Execute the complete A2A workflow"""
        try:
            state = self.get_state(task_id)
            print(f"[Coordinator] Starting A2A workflow for task {task_id}")
            
            # Step 1: Topic Refiner
            print("[Coordinator] Step 1: Refining topic")
            self.update_state(task_id, {
                "status": "refining_topic",
                "current_agent": "Dr. Topic Refiner"
            })
            
            result = await self.call_agent_action(
                agent_uri=AGENT_URIS["topic_refiner"],
                action="refine_topic",
                parameters={"task_id": task_id}
            )
            print(f"[Coordinator] Topic refined: {result.get('refined_topic', '')[:50]}...")
            
            # Main research loop
            iteration = 0
            max_iterations = state.get("max_iterations", 2)
            
            while iteration < max_iterations:
                print(f"[Coordinator] Iteration {iteration + 1}/{max_iterations}")
                
                # Step 2: Question Architect
                print("[Coordinator] Step 2: Generating questions")
                self.update_state(task_id, {
                    "status": "generating_questions",
                    "current_agent": "Prof. Question Architect"
                })
                
                result = await self.call_agent_action(
                    agent_uri=AGENT_URIS["question_architect"],
                    action="generate_questions",
                    parameters={"task_id": task_id}
                )
                print(f"[Coordinator] Generated {result.get('count', 0)} questions")
                
                # Step 3: Search Strategist
                print("[Coordinator] Step 3: Executing searches")
                self.update_state(task_id, {
                    "status": "searching",
                    "current_agent": "Agent Search Strategist"
                })
                
                result = await self.call_agent_action(
                    agent_uri=AGENT_URIS["search_strategist"],
                    action="execute_search",
                    parameters={"task_id": task_id, "max_results": 2}
                )
                print(f"[Coordinator] Found {result.get('results_count', 0)} results")
                
                # Step 4: Data Analyst
                print("[Coordinator] Step 4: Analyzing data")
                self.update_state(task_id, {
                    "status": "analyzing",
                    "current_agent": "Dr. Data Analyst"
                })
                
                result = await self.call_agent_action(
                    agent_uri=AGENT_URIS["data_analyst"],
                    action="analyze_results",
                    parameters={"task_id": task_id}
                )
                print(f"[Coordinator] Extracted {result.get('findings_count', 0)} findings")
                print(f"[Coordinator] Quality score: {result.get('quality_score', 0):.2f}")
                
                # Check if should continue
                decision = await self.should_continue(task_id)
                if decision == "finalize":
                    print("[Coordinator] Quality threshold met, finalizing...")
                    break
                
                iteration += 1
            
            # Step 5: Report Writer
            print("[Coordinator] Step 5: Generating report")
            self.update_state(task_id, {
                "status": "generating_report",
                "current_agent": "Dr. Report Writer"
            })
            
            result = await self.call_agent_action(
                agent_uri=AGENT_URIS["report_writer"],
                action="generate_report",
                parameters={"task_id": task_id}
            )
            print(f"[Coordinator] Report generated ({result.get('report_length', 0)} chars)")
            
            # Mark as complete
            self.update_state(task_id, {"status": "completed"})
            print(f"[Coordinator] Workflow completed for task {task_id}")
            
            return {"success": True, "task_id": task_id}
            
        except Exception as e:
            error_msg = f"Workflow error: {str(e)}"
            print(f"[Coordinator] {error_msg}")
            import traceback
            traceback.print_exc()
            self.update_state(task_id, {"status": "failed", "error": error_msg})
            return {"success": False, "error": error_msg}


# Create FastAPI app
coordinator = A2ACoordinator()
app = FastAPI(
    title="A2A Coordinator Service",
    description="Orchestrates multi-agent research using A2A protocol"
)


@app.get("/")
async def root():
    return {
        "service": "A2A Coordinator",
        "protocol": "A2A v1.0",
        "status": "online"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "coordinator",
        "protocol": "A2A"
    }


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
        "error": None,
        "protocol": "A2A v1.0"
    }
    
    coordinator.update_state(task_id, initial_state)
    
    # Start workflow in background
    asyncio.create_task(coordinator.run_workflow(task_id))
    
    return {
        "task_id": task_id,
        "status": "started",
        "protocol": "A2A",
        "message": "Research task started. Use /task/{task_id} to check progress."
    }


@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and results"""
    state = coordinator.get_state(task_id)
    if not state:
        raise HTTPException(status_code=404, detail="Task not found")
    return state


@app.get("/agents")
async def list_agents():
    """List all available agents and their URIs"""
    return {
        "protocol": "A2A v1.0",
        "agents": [
            {"name": "Topic Refiner", "uri": AGENT_URIS["topic_refiner"]},
            {"name": "Question Architect", "uri": AGENT_URIS["question_architect"]},
            {"name": "Search Strategist", "uri": AGENT_URIS["search_strategist"]},
            {"name": "Data Analyst", "uri": AGENT_URIS["data_analyst"]},
            {"name": "Report Writer", "uri": AGENT_URIS["report_writer"]}
        ]
    }


if __name__ == "__main__":
    print("Starting A2A Coordinator Service")
    print(f"Coordinator ID: {coordinator.agent_id}")
    uvicorn.run(app, host="0.0.0.0", port=8006)