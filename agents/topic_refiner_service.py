"""
topic_refiner_service.py
Topic Refiner Agent Microservice
"""

import uvicorn
from base_agent import BaseAgent
from shared_models import AgentMessage, AgentResponse

class TopicRefinerAgent(BaseAgent):
    """Agent specialized in refining research topics"""
    
    def __init__(self):
        super().__init__(
            name="Dr. Topic Refiner",
            role="Research Topic Specialist",
            expertise="Clarifying research objectives and scoping studies",
            temperature=0.5
        )
    
    def refine_topic(self, topic: str) -> str:
        """Refine a research topic"""
        prompt = f"""Analyze this research topic: '{topic}'

Your task:
1. Identify the core research question
2. Suggest a more specific, searchable focus
3. Ensure the topic is neither too broad nor too narrow

Return ONLY the refined topic as a single clear sentence."""
        
        return self.invoke(prompt).strip()
    
    def process(self, message: AgentMessage) -> AgentResponse:
        """Process incoming message"""
        try:
            # Get current state
            state = self.get_state(message.task_id)
            if not state:
                return AgentResponse(
                    task_id=message.task_id,
                    agent_name=self.name,
                    success=False,
                    data={},
                    error="State not found"
                )
            
            # Refine topic
            topic = state.get("topic", "")
            refined_topic = self.refine_topic(topic)
            
            # Update state
            self.update_state(message.task_id, {
                "topic": refined_topic,
                "status": "topic_refined",
                "current_agent": self.name
            })
            
            # Add log
            self.add_log(message.task_id, "refined_topic", {
                "input": topic,
                "output": refined_topic
            })
            
            return AgentResponse(
                task_id=message.task_id,
                agent_name=self.name,
                success=True,
                data={"refined_topic": refined_topic}
            )
            
        except Exception as e:
            return AgentResponse(
                task_id=message.task_id,
                agent_name=self.name,
                success=False,
                data={},
                error=str(e)
            )

# Create and run service
if __name__ == "__main__":
    agent = TopicRefinerAgent()
    app = agent.create_app()
    uvicorn.run(app, host="0.0.0.0", port=8001)
