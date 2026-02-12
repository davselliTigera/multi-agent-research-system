"""
report_writer_service.py
Report Writer Agent Microservice
"""

import uvicorn
from datetime import datetime
from agents.base_agent import BaseAgent
from shared.shared_models import AgentMessage, AgentResponse

class ReportWriterAgent(BaseAgent):
    """Agent specialized in writing comprehensive research reports"""
    
    def __init__(self):
        super().__init__(
            name="Dr. Report Writer",
            role="Research Report Specialist",
            expertise="Synthesizing findings into clear, structured reports",
            temperature=0.6
        )
    
    def generate_report(self, state: dict) -> str:
        """Generate comprehensive research report"""
        prompt = f"""Create a professional research report.

Topic: {state['topic']}

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
        
        report = self.invoke(prompt)
        
        # Add metadata footer
        report += f"\n\n---\n## 📊 Research Metadata\n\n"
        report += f"**Research Coordinator:** Multi-Agent System (Microservices)\n\n"
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
        
        return report
    
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
            
            # Generate report
            report = self.generate_report(state)
            
            # Update state
            self.update_state(message.task_id, {
                "final_report": report,
                "status": "report_completed",
                "current_agent": self.name
            })
            
            # Add log
            self.add_log(message.task_id, "generated_report", {
                "report_length": len(report)
            })
            
            return AgentResponse(
                task_id=message.task_id,
                agent_name=self.name,
                success=True,
                data={"report": report}
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
    agent = ReportWriterAgent()
    app = agent.create_app()
    uvicorn.run(app, host="0.0.0.0", port=8005)