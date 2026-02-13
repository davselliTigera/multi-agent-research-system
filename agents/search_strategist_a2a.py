"""
search_strategist_a2a.py
Search Strategist Agent - A2A Protocol Implementation
"""

import uvicorn
from typing import Dict, Any, List
from agents.a2a_base_agent import A2ABaseAgent
from shared.a2a_models import A2ACapability, AGENT_URIS
from duckduckgo_search import DDGS


class SearchStrategistAgent(A2ABaseAgent):
    """A2A-compliant agent specialized in search strategy and execution"""
    
    def __init__(self):
        super().__init__(
            agent_id=AGENT_URIS["search_strategist"],
            name="Agent Search Strategist",
            role="Information Retrieval Specialist",
            expertise="Designing search strategies and executing queries",
            temperature=0.3
        )
    
    def get_capabilities(self) -> List[A2ACapability]:
        """Return agent capabilities"""
        return [
            A2ACapability(
                name="execute_search",
                description="Execute web searches for research questions",
                parameters={
                    "task_id": {
                        "type": "string",
                        "description": "Unique task identifier",
                        "required": True
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results per query",
                        "default": 2
                    }
                },
                returns={
                    "results_count": {
                        "type": "integer",
                        "description": "Total number of results found"
                    },
                    "queries_processed": {
                        "type": "integer",
                        "description": "Number of queries processed"
                    }
                }
            ),
            A2ACapability(
                name="optimize_query",
                description="Optimize a search query for better results",
                parameters={
                    "query": {
                        "type": "string",
                        "description": "Query to optimize",
                        "required": True
                    }
                },
                returns={
                    "optimized_query": {
                        "type": "string",
                        "description": "Optimized search query"
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
        
        if action == "execute_search":
            return await self._execute_search(parameters, context)
        elif action == "optimize_query":
            return await self._optimize_query(parameters, context)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _optimize_query(
        self, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize a search query"""
        
        query = parameters.get("query")
        if not query:
            raise ValueError("query is required")
        
        prompt = f"""Convert this research question into an optimal search query:
'{query}'

Return ONLY the search query (no explanation)."""
        
        optimized = self.invoke_llm(prompt).strip()
        
        return {
            "optimized_query": optimized,
            "original_query": query
        }
    
    async def _execute_search(
        self, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute searches for research questions"""
        
        task_id = parameters.get("task_id")
        max_results = parameters.get("max_results", 2)
        
        if not task_id:
            raise ValueError("task_id is required")
        
        # Get current state
        state = self.get_state(task_id)
        if not state:
            raise ValueError(f"Task not found: {task_id}")
        
        search_results = state.get("search_results", [])
        search_queries = state.get("search_queries", [])
        new_results_count = 0
        queries_processed = 0
        
        # Search for each unanswered question
        for question in state.get("research_questions", []):
            if question not in search_queries:
                try:
                    # Use question directly (skip optimization for speed)
                    ddgs = DDGS()
                    results = ddgs.text(question, max_results=max_results)
                    
                    for result in results:
                        title = result.get('title', '')
                        body = result.get('body', '')
                        search_results.append(f"**{title}**\n{body}")
                        new_results_count += 1
                    
                    search_queries.append(question)
                    queries_processed += 1
                    
                except Exception as e:
                    print(f"Search error for '{question}': {e}")
        
        # Update state
        self.update_state(task_id, {
            "search_results": search_results,
            "search_queries": search_queries,
            "iteration": state.get("iteration", 0) + 1,
            "status": "search_completed",
            "current_agent": self.name
        })
        
        # Add log
        self.add_log(task_id, "executed_searches", {
            "queries_processed": queries_processed,
            "new_results": new_results_count
        })
        
        return {
            "results_count": new_results_count,
            "queries_processed": queries_processed,
            "total_results": len(search_results)
        }


# Create and run service
if __name__ == "__main__":
    agent = SearchStrategistAgent()
    app = agent.create_app()
    
    print(f"Starting {agent.name} with A2A protocol")
    print(f"Agent ID: {agent.agent_id}")
    print(f"Capabilities: {[cap.name for cap in agent.get_capabilities()]}")
    
    uvicorn.run(app, host="0.0.0.0", port=8003)
