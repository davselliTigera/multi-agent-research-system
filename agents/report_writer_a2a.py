"""
report_writer_a2a.py
Report Writer Agent - A2A Protocol Implementation
"""

import uvicorn
from datetime import datetime
from typing import Dict, Any, List
from agents.a2a_base_agent import A2ABaseAgent
from shared.a2a_models import A2ACapability, AGENT_URIS


class ReportWriterAgent(A2ABaseAgent):
    """A2A-compliant agent specialized in writing comprehensive research reports"""
    
    def __init__(self):
        super().__init__(
            agent_id=AGENT_URIS["report_writer"],
            name="Dr. Report Writer",
            role="Research Report Specialist",
            expertise="Synthesizing findings into clear, structured reports",
            temperature=0.6
        )
    
    def get_capabilities(self) -> List[A2ACapability]:
        """Return agent capabilities"""
        return [
            A2ACapability(
                name="generate_report",
                description="Generate comprehensive research report",
                parameters={
                    "task_id": {
                        "type": "string",
                        "description": "Unique task identifier",
                        "required": True
                    }
                },
                returns={
                    "report": {
                        "type": "string",
                        "description": "Formatted research report"
                    },
                    "report_length": {
                        "type": "integer",
                        "description": "Length of report in characters"
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
        
        if action == "generate_report":
            return await self._generate_report(parameters, context)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _generate_report(
        self, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive research report"""
        
        task_id = parameters.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        # Get current state
        state = self.get_state(task_id)
        if not state:
            raise ValueError(f"Task not found: {task_id}")
        
        # Generate report using LLM
        prompt = f"""Create a professional research report.

Topic: {state.get('topic', 'N/A')}

Research Questions Investigated:
{chr(10).join('• ' + q for q in state.get('research_questions', []))}

Key Findings from Analysis:
{chr(10).join('• ' + f for f in state.get('key_findings', []))}

Research Scope:
- {len(state.get('search_results', []))} sources consulted
- {state.get('iteration', 0)} research iterations completed
- Quality score: {state.get('quality_score', 0):.2f}

Generate a well-structured report with:

# Executive Summary
[2-3 sentence overview]

# Research Methodology
[Brief description of approach]

# Key Findings
[Detailed findings with context]

# Conclusions and Insights
[Synthesis and implications]

# Recommendations
[If applicable, suggest next steps]

Write in a professional, academic tone. Be comprehensive but concise."""
        
        report = self.invoke_llm(prompt)
        
        # Add metadata footer
        report += f"\n\n---\n## 📊 Research Metadata\n\n"
        report += f"**Research Protocol:** A2A Multi-Agent System\n\n"
        report += f"**Participating Agents:**\n"
        report += f"- Dr. Topic Refiner (Topic Analysis)\n"
        report += f"- Prof. Question Architect (Question Design)\n"
        report += f"- Agent Search Strategist (Information Retrieval)\n"
        report += f"- Dr. Data Analyst (Analysis & Synthesis)\n"
        report += f"- Dr. Report Writer (Report Generation)\n\n"
        report += f"**Research Statistics:**\n"
        report += f"- Original Topic: {state.get('original_topic', 'N/A')}\n"
        report += f"- Refined Topic: {state.get('topic', 'N/A')}\n"
        report += f"- Questions Generated: {len(state.get('research_questions', []))}\n"
        report += f"- Sources Consulted: {len(state.get('search_results', []))}\n"
        report += f"- Key Findings: {len(state.get('key_findings', []))}\n"
        report += f"- Research Iterations: {state.get('iteration', 0)}\n"
        report += f"- Quality Score: {state.get('quality_score', 0):.2f}/1.00\n"
        report += f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"- Protocol: A2A v1.0\n"
        
        # Update state
        self.update_state(task_id, {
            "final_report": report,
            "status": "report_completed",
            "current_agent": self.name
        })
        
        # Add log
        self.add_log(task_id, "generated_report", {
            "report_length": len(report)
        })
        
        return {
            "report": report,
            "report_length": len(report)
        }


# Create and run service
if __name__ == "__main__":
    agent = ReportWriterAgent()
    app = agent.create_app()
    
    print(f"Starting {agent.name} with A2A protocol")
    print(f"Agent ID: {agent.agent_id}")
    print(f"Capabilities: {[cap.name for cap in agent.get_capabilities()]}")
    
    uvicorn.run(app, host="0.0.0.0", port=8005)
