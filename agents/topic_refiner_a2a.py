"""
topic_refiner_a2a.py
Topic Refiner Agent - A2A Protocol Implementation
"""

import uvicorn
from typing import Dict, Any, List
from agents.a2a_base_agent import A2ABaseAgent
from shared.a2a_models import A2ACapability, AGENT_URIS


class TopicRefinerAgent(A2ABaseAgent):
    """A2A-compliant agent specialized in refining research topics"""
    
    def __init__(self):
        super().__init__(
            agent_id=AGENT_URIS["topic_refiner"],
            name="Dr. Topic Refiner",
            role="Research Topic Specialist",
            expertise="Clarifying research objectives and scoping studies",
            temperature=0.5
        )
    
    def get_capabilities(self) -> List[A2ACapability]:
        """Return agent capabilities"""
        return [
            A2ACapability(
                name="refine_topic",
                description="Refine and clarify a research topic",
                parameters={
                    "task_id": {
                        "type": "string",
                        "description": "Unique task identifier",
                        "required": True
                    }
                },
                returns={
                    "refined_topic": {
                        "type": "string",
                        "description": "Refined and focused research topic"
                    }
                }
            )
        ]
    
    async def handle_action(
        self, 
        action: str, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle action requests"""
        
        if action == "refine_topic":
            return await self._refine_topic(parameters, context)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _refine_topic(
        self, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Refine a research topic"""
        
        task_id = parameters.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        # Get current state
        state = self.get_state(task_id)
        if not state:
            raise ValueError(f"Task not found: {task_id}")
        
        topic = state.get("topic", "")
        
        # Refine the topic using LLM
        prompt = f"""Analyze this research topic: '{topic}'

Your task:
1. Identify the core research question
2. Suggest a more specific, searchable focus
3. Ensure the topic is neither too broad nor too narrow

Return ONLY the refined topic as a single clear sentence."""
        
        refined_topic = self.invoke_llm(prompt).strip()
        
        # Update state
        self.update_state(task_id, {
            "topic": refined_topic,
            "status": "topic_refined",
            "current_agent": self.name
        })
        
        # Add log
        self.add_log(task_id, "refined_topic", {
            "input": topic,
            "output": refined_topic
        })
        
        return {
            "refined_topic": refined_topic,
            "original_topic": topic
        }


# Create and run service
if __name__ == "__main__":
    agent = TopicRefinerAgent()
    app = agent.create_app()
    
    print(f"Starting {agent.name} with A2A protocol")
    print(f"Agent ID: {agent.agent_id}")
    print(f"Capabilities: {[cap.name for cap in agent.get_capabilities()]}")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
