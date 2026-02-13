"""
question_architect_a2a.py
Question Architect Agent - A2A Protocol Implementation
"""

import uvicorn
from typing import Dict, Any, List
from agents.a2a_base_agent import A2ABaseAgent
from shared.a2a_models import A2ACapability, AGENT_URIS


class QuestionArchitectAgent(A2ABaseAgent):
    """A2A-compliant agent specialized in crafting research questions"""
    
    def __init__(self):
        super().__init__(
            agent_id=AGENT_URIS["question_architect"],
            name="Prof. Question Architect",
            role="Research Question Designer",
            expertise="Formulating precise, investigable research questions",
            temperature=0.7
        )
    
    def get_capabilities(self) -> List[A2ACapability]:
        """Return agent capabilities"""
        return [
            A2ACapability(
                name="generate_questions",
                description="Generate specific research questions for a topic",
                parameters={
                    "task_id": {
                        "type": "string",
                        "description": "Unique task identifier",
                        "required": True
                    }
                },
                returns={
                    "questions": {
                        "type": "array",
                        "description": "List of research questions",
                        "items": {"type": "string"}
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of questions generated"
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
        
        if action == "generate_questions":
            return await self._generate_questions(parameters, context)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _generate_questions(
        self, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate research questions"""
        
        task_id = parameters.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        # Get current state
        state = self.get_state(task_id)
        if not state:
            raise ValueError(f"Task not found: {task_id}")
        
        topic = state.get("topic", "")
        iteration = state.get("iteration", 0)
        
        # Generate questions using LLM
        prompt = f"""Research Topic: {topic}
Iteration: {iteration}

Generate 3 specific, actionable research questions that:
1. Are directly answerable through web searches
2. Cover different aspects of the topic
3. Build upon previous iterations (if any)
4. Are concrete and factual

Return ONLY the questions, numbered 1-3, one per line."""
        
        response = self.invoke_llm(prompt)
        questions = response.strip().split('\n')
        questions = [q.strip().lstrip('0123456789. ') for q in questions if q.strip()][:3]
        
        # Update state
        all_questions = state.get("research_questions", []) + questions
        self.update_state(task_id, {
            "research_questions": all_questions,
            "status": "questions_generated",
            "current_agent": self.name
        })
        
        # Add log
        self.add_log(task_id, "generated_questions", {
            "count": len(questions),
            "questions": questions
        })
        
        return {
            "questions": questions,
            "count": len(questions),
            "total_questions": len(all_questions)
        }


# Create and run service
if __name__ == "__main__":
    agent = QuestionArchitectAgent()
    app = agent.create_app()
    
    print(f"Starting {agent.name} with A2A protocol")
    print(f"Agent ID: {agent.agent_id}")
    print(f"Capabilities: {[cap.name for cap in agent.get_capabilities()]}")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
