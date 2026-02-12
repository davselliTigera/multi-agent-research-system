"""
question_architect_service.py
Question Architect Agent Microservice
"""

import uvicorn
from typing import List
from base_agent import BaseAgent
from shared_models import AgentMessage, AgentResponse

class QuestionArchitectAgent(BaseAgent):
    """Agent specialized in crafting research questions"""
    
    def __init__(self):
        super().__init__(
            name="Prof. Question Architect",
            role="Research Question Designer",
            expertise="Formulating precise, investigable research questions",
            temperature=0.7
        )
    
    def generate_questions(self, topic: str, iteration: int) -> List[str]:
        """Generate research questions"""
        prompt = f"""Research Topic: {topic}
Iteration: {iteration}

Generate 3 specific, actionable research questions that:
1. Are directly answerable through web searches
2. Cover different aspects of the topic
3. Build upon previous iterations (if any)
4. Are concrete and factual

Return ONLY the questions, numbered 1-3, one per line."""
        
        response = self.invoke(prompt)
        questions = response.strip().split('\n')
        questions = [q.strip().lstrip('0123456789. ') for q in questions if q.strip()]
        return questions[:3]
    
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
            
            # Generate questions
            topic = state.get("topic", "")
            iteration = state.get("iteration", 0)
            questions = self.generate_questions(topic, iteration)
            
            # Update state
            all_questions = state.get("research_questions", []) + questions
            self.update_state(message.task_id, {
                "research_questions": all_questions,
                "status": "questions_generated",
                "current_agent": self.name
            })
            
            # Add log
            self.add_log(message.task_id, "generated_questions", {
                "count": len(questions),
                "questions": questions
            })
            
            return AgentResponse(
                task_id=message.task_id,
                agent_name=self.name,
                success=True,
                data={"questions": questions}
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
    agent = QuestionArchitectAgent()
    app = agent.create_app()
    uvicorn.run(app, host="0.0.0.0", port=8002)
