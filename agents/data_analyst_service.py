"""
data_analyst_service.py
Data Analyst Agent Microservice
"""

import uvicorn
from typing import List, Tuple
from agents.base_agent import BaseAgent
from shared.shared_models import AgentMessage, AgentResponse

class DataAnalystAgent(BaseAgent):
    """Agent specialized in analyzing and synthesizing information"""
    
    def __init__(self):
        super().__init__(
            name="Dr. Data Analyst",
            role="Research Data Analyst",
            expertise="Extracting insights and identifying patterns in research data",
            temperature=0.4
        )
    
    def analyze_results(self, topic: str, search_results: List[str]) -> Tuple[List[str], float]:
        """Analyze search results and extract key findings"""
        if not search_results:
            return ["No data available for analysis"], 0.0
        
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
        
        response = self.invoke(prompt)
        findings = response.strip().split('\n')
        findings = [f.strip().lstrip('0123456789. ') for f in findings if f.strip()][:5]
        
        # Calculate quality score
        quality = min(len(findings) * 0.15 + len(search_results) * 0.02, 1.0)
        
        return findings, quality
    
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
            
            # Analyze results
            topic = state.get("topic", "")
            search_results = state.get("search_results", [])
            findings, quality_score = self.analyze_results(topic, search_results)
            
            # Update state
            all_findings = state.get("key_findings", []) + findings
            self.update_state(message.task_id, {
                "key_findings": all_findings,
                "quality_score": quality_score,
                "status": "analysis_completed",
                "current_agent": self.name
            })
            
            # Add log
            self.add_log(message.task_id, "analyzed_data", {
                "findings_extracted": len(findings),
                "quality_score": quality_score
            })
            
            return AgentResponse(
                task_id=message.task_id,
                agent_name=self.name,
                success=True,
                data={
                    "findings": findings,
                    "quality_score": quality_score
                }
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
    agent = DataAnalystAgent()
    app = agent.create_app()
    uvicorn.run(app, host="0.0.0.0", port=8004)