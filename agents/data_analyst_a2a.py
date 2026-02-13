"""
data_analyst_a2a.py
Data Analyst Agent - A2A Protocol Implementation
"""

import uvicorn
from typing import Dict, Any, List
from agents.a2a_base_agent import A2ABaseAgent
from shared.a2a_models import A2ACapability, AGENT_URIS


class DataAnalystAgent(A2ABaseAgent):
    """A2A-compliant agent specialized in analyzing and synthesizing information"""
    
    def __init__(self):
        super().__init__(
            agent_id=AGENT_URIS["data_analyst"],
            name="Dr. Data Analyst",
            role="Research Data Analyst",
            expertise="Extracting insights and identifying patterns in research data",
            temperature=0.4
        )
    
    def get_capabilities(self) -> List[A2ACapability]:
        """Return agent capabilities"""
        return [
            A2ACapability(
                name="analyze_results",
                description="Analyze search results and extract key findings",
                parameters={
                    "task_id": {
                        "type": "string",
                        "description": "Unique task identifier",
                        "required": True
                    }
                },
                returns={
                    "findings": {
                        "type": "array",
                        "description": "Extracted key findings",
                        "items": {"type": "string"}
                    },
                    "quality_score": {
                        "type": "number",
                        "description": "Quality score of the research (0-1)"
                    },
                    "findings_count": {
                        "type": "integer",
                        "description": "Number of findings extracted"
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
        
        if action == "analyze_results":
            return await self._analyze_results(parameters, context)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _analyze_results(
        self, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze search results and extract key findings"""
        
        task_id = parameters.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        # Get current state
        state = self.get_state(task_id)
        if not state:
            raise ValueError(f"Task not found: {task_id}")
        
        topic = state.get("topic", "")
        search_results = state.get("search_results", [])
        
        if not search_results:
            findings = ["No data available for analysis"]
            quality_score = 0.0
        else:
            # Analyze results using LLM
            results_text = "\n\n".join(search_results[:15])
            
            prompt = f"""Topic: {topic}

Analyze these search results and extract key findings:

{results_text}

Your analysis should:
1. Identify the 5 most important facts or insights
2. Ensure findings are specific and well-supported
3. Avoid redundancy
4. Focus on actionable information

Return ONLY the findings, numbered 1-5, one per line."""
            
            response = self.invoke_llm(prompt)
            findings = response.strip().split('\n')
            findings = [f.strip().lstrip('0123456789. ') for f in findings if f.strip()][:5]
            
            # Calculate quality score
            quality_score = min(len(findings) * 0.15 + len(search_results) * 0.02, 1.0)
        
        # Update state
        all_findings = state.get("key_findings", []) + findings
        self.update_state(task_id, {
            "key_findings": all_findings,
            "quality_score": quality_score,
            "status": "analysis_completed",
            "current_agent": self.name
        })
        
        # Add log
        self.add_log(task_id, "analyzed_data", {
            "findings_extracted": len(findings),
            "quality_score": quality_score
        })
        
        return {
            "findings": findings,
            "quality_score": quality_score,
            "findings_count": len(findings),
            "total_findings": len(all_findings)
        }


# Create and run service
if __name__ == "__main__":
    agent = DataAnalystAgent()
    app = agent.create_app()
    
    print(f"Starting {agent.name} with A2A protocol")
    print(f"Agent ID: {agent.agent_id}")
    print(f"Capabilities: {[cap.name for cap in agent.get_capabilities()]}")
    
    uvicorn.run(app, host="0.0.0.0", port=8004)
