"""
search_strategist_service.py
Search Strategist Agent Microservice
"""

import uvicorn
from typing import List
from base_agent import BaseAgent
from shared_models import AgentMessage, AgentResponse
from duckduckgo_search import DDGS

class SearchStrategistAgent(BaseAgent):
    """Agent specialized in search strategy and execution"""
    
    def __init__(self):
        super().__init__(
            name="Agent Search Strategist",
            role="Information Retrieval Specialist",
            expertise="Designing search strategies and executing queries",
            temperature=0.3
        )
    
    def optimize_query(self, question: str) -> str:
        """Optimize a question for search engines"""
        prompt = f"""Convert this research question into an optimal search query:
'{question}'

Return ONLY the search query (no explanation)."""
        
        return self.invoke(prompt).strip()
    
    def execute_search(self, question: str, max_results: int = 2) -> List[dict]:
        """Execute search"""
        try:
            optimized_query = self.optimize_query(question)
        except Exception:
            optimized_query = question
        
        try:
            ddgs = DDGS()
            results = ddgs.text(optimized_query, max_results=max_results)
            return list(results)
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
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
            
            # Execute searches
            search_results = state.get("search_results", [])
            search_queries = state.get("search_queries", [])
            new_results_count = 0
            
            for question in state.get("research_questions", []):
                if question not in search_queries:
                    results = self.execute_search(question, max_results=2)
                    
                    for result in results:
                        title = result.get('title', '')
                        body = result.get('body', '')
                        search_results.append(f"**{title}**\n{body}")
                        new_results_count += 1
                    
                    search_queries.append(question)
            
            # Update state
            self.update_state(message.task_id, {
                "search_results": search_results,
                "search_queries": search_queries,
                "iteration": state.get("iteration", 0) + 1,
                "status": "search_completed",
                "current_agent": self.name
            })
            
            # Add log
            self.add_log(message.task_id, "executed_searches", {
                "queries_processed": len(state.get("research_questions", [])),
                "new_results": new_results_count
            })
            
            return AgentResponse(
                task_id=message.task_id,
                agent_name=self.name,
                success=True,
                data={"new_results": new_results_count}
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
    agent = SearchStrategistAgent()
    app = agent.create_app()
    uvicorn.run(app, host="0.0.0.0", port=8003)
