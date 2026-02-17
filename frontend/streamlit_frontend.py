"""
streamlit_frontend.py
Streamlit frontend for multi-agent research system
"""

import streamlit as st
import httpx
import time
import os
from shared.shared_models import AGENT_INFO

# Configuration - auto-detect local vs Kubernetes
default_url = "http://coordinator-service:8006"  # Kubernetes default
if os.path.exists("venv") or os.path.exists(".env.local"):
    # Likely running locally
    default_url = "http://localhost:8006"

COORDINATOR_URL = os.getenv("COORDINATOR_URL", default_url)

st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Multi-Agent Research System")
st.markdown("**Distributed AI agents running as microservices on Kubernetes**")

# Show connection status
try:
    with httpx.Client(timeout=5.0) as client:
        health_response = client.get(f"{COORDINATOR_URL}/health")
        if health_response.status_code == 200:
            st.success(f"✅ Connected to coordinator at {COORDINATOR_URL}")
        else:
            st.warning(f"⚠️ Coordinator returned status {health_response.status_code}")
except Exception as e:
    st.error(f"❌ Cannot reach coordinator at {COORDINATOR_URL}")
    st.info(f"""
    **Connection Issue Detected**
    
    The frontend cannot connect to the coordinator service.
    
    **Quick Fix:**
```bash
    # Check if coordinator is running
    kubectl get pods | grep coordinator
    
    # Check coordinator logs
    kubectl logs -f deployment/coordinator
    
    # Verify services
    kubectl get services
    
    # If using port-forward, ensure coordinator is accessible:
    kubectl port-forward service/coordinator-service 8006:8006
```
    
    Current COORDINATOR_URL: `{COORDINATOR_URL}`
    """)
    st.stop()

# Display agent team
with st.expander("👥 Meet the Agent Team", expanded=False):
    cols = st.columns(3)
    
    for idx, agent in enumerate(AGENT_INFO):
        with cols[idx % 3]:
            st.markdown(f"### {agent['emoji']} {agent['name']}")
            st.caption(f"**{agent['role']}**")
            st.write(f"*{agent['expertise']}*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    max_iterations = st.slider(
        "Max Iterations",
        min_value=1,
        max_value=5,
        value=2,
        help="Maximum research cycles"
    )
    
    st.divider()
    
    st.subheader("📚 Example Topics")
    example_topics = [
        "Benefits of multi-agent AI systems",
        "Kubernetes-native AI architectures",
        "Microservices vs monolithic AI systems",
        "State management in distributed systems",
        "Inter-service communication patterns"
    ]
    
    selected_example = st.selectbox("Choose example:", [""] + example_topics)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔬 Research Topic")
    
    with st.form("research_form"):
        topic = st.text_input(
            "Enter research topic:",
            value=selected_example,
            placeholder="e.g., Benefits of multi-agent AI systems"
        )
        
        submitted = st.form_submit_button("🚀 Deploy Agents", type="primary")
    
    if submitted and topic:
        # Start research
        st.subheader("🔄 Agent Activity")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Agent status display
        agent_cols = st.columns(5)
        agent_status = {}
        
        agent_display = [
            ("topic_refiner", "🎯 Refiner"),
            ("question_architect", "❓ Architect"),
            ("search_strategist", "🔍 Strategist"),
            ("data_analyst", "📊 Analyst"),
            ("report_writer", "📝 Writer")
        ]
        
        for i, (key, label) in enumerate(agent_display):
            with agent_cols[i]:
                agent_status[key] = st.empty()
                agent_status[key].metric(label, "⏳ Standby")
        
        with st.status("Coordinating agents...", expanded=True) as status:
            try:
                # Call coordinator to start research
                status.write(f"Connecting to coordinator at {COORDINATOR_URL}...")
                
                with httpx.Client(timeout=30.0) as client:
                    try:
                        response = client.post(
                            f"{COORDINATOR_URL}/start_research",
                            params={"topic": topic, "max_iterations": max_iterations}
                        )
                        response.raise_for_status()
                        result = response.json()
                    except httpx.ConnectError as e:
                        st.error(f"❌ Cannot connect to coordinator service at {COORDINATOR_URL}")
                        st.error(f"Error: {str(e)}")
                        st.info("""
                        **Troubleshooting:**
                        1. Check coordinator pod is running: `kubectl get pods | grep coordinator`
                        2. Check coordinator logs: `kubectl logs -f deployment/coordinator`
                        3. Verify service exists: `kubectl get service coordinator-service`
                        4. Port forward to coordinator: `kubectl port-forward service/coordinator-service 8006:8006`
                        """)
                        status.update(label="Connection failed", state="error")
                        st.stop()
                    except httpx.TimeoutException:
                        st.error("❌ Request timed out - coordinator may be overloaded")
                        status.update(label="Request timed out", state="error")
                        st.stop()
                    except Exception as e:
                        st.error(f"❌ HTTP Error: {str(e)}")
                        status.update(label="Request failed", state="error")
                        st.stop()
                
                if result.get("status") == "failed":
                    status.update(label="Research failed", state="error")
                    st.error(f"Error: {result.get('error')}")
                else:
                    task_id = result["task_id"]
                    status.write(f"Research task started: {task_id}")
                    
                    # Poll for status
                    completed = False
                    current_agent = None
                    poll_count = 0
                    max_polls = 120  # 4 minutes max (2 second intervals)
                    
                    while not completed and poll_count < max_polls:
                        with httpx.Client(timeout=10.0) as client:
                            try:
                                response = client.get(f"{COORDINATOR_URL}/task/{task_id}")
                                response.raise_for_status()
                                state = response.json()
                            except Exception as e:
                                st.warning(f"Error polling status: {e}")
                                time.sleep(2)
                                poll_count += 1
                                continue
                        
                        task_status = state.get("status", "")
                        new_agent = state.get("current_agent", "")
                        
                        # Update UI based on agent
                        if new_agent != current_agent and new_agent:
                            current_agent = new_agent
                            
                            # Map agent names to keys
                            agent_key_map = {info["name"]: info["key"] for info in AGENT_INFO}
                            agent_key = agent_key_map.get(new_agent)
                            
                            if agent_key and agent_key in agent_status:
                                status.write(f"Agent active: {new_agent}")
                                agent_status[agent_key].metric(
                                    next(label for k, label in agent_display if k == agent_key),
                                    "🔄 Working",
                                    delta="Active"
                                )
                        
                        # Update progress bar
                        progress = min(len(state.get("agent_logs", [])) / 10, 1.0)
                        progress_bar.progress(progress)
                        status_text.text(f"Status: {task_status} | Logs: {len(state.get('agent_logs', []))}")
                        
                        # Check if completed
                        if task_status in ["completed", "failed"]:
                            completed = True
                            
                            # Mark all as complete
                            for key, label in agent_display:
                                if key in agent_status:
                                    agent_status[key].metric(label, "✅ Done", delta="Complete")
                            
                            if task_status == "completed":
                                status.update(label="Research complete!", state="complete")
                            else:
                                status.update(label="Research failed", state="error")
                                st.error(f"Error: {state.get('error')}")
                        else:
                            time.sleep(2)
                            poll_count += 1
                    
                    if not completed:
                        st.warning("⚠️ Research timed out after 4 minutes. Check coordinator logs.")
                        status.update(label="Timed out", state="error")
                        st.stop()
                        
                        progress_bar.progress(min(len(state.get("agent_logs", [])) / 10, 1.0))
                    
                    if task_status == "completed":
                        # Display results
                        st.divider()
                        st.subheader("📊 Research Output")
                        
                        tabs = st.tabs(["📄 Report", "🗣️ Agent Logs", "❓ Questions", "💡 Findings", "📈 Analytics"])
                        
                        with tabs[0]:
                            st.markdown(state.get("final_report", ""))
                            
                            st.download_button(
                                label="📥 Download Report",
                                data=state.get("final_report", ""),
                                file_name=f"research_{topic.replace(' ', '_')}.md",
                                mime="text/markdown"
                            )
                        
                        with tabs[1]:
                            st.subheader("Agent Activity Log")
                            for idx, log in enumerate(state.get("agent_logs", [])):
                                st.markdown(f"**🤖 {log.get('agent', 'Unknown')} - {log.get('action', 'Unknown')}**")
                                st.json(log)
                                if idx < len(state.get("agent_logs", [])) - 1:
                                    st.divider()
                        
                        with tabs[2]:
                            st.subheader("Research Questions")
                            for i, q in enumerate(state.get("research_questions", []), 1):
                                st.write(f"{i}. {q}")
                        
                        with tabs[3]:
                            st.subheader("Key Findings")
                            for i, f in enumerate(state.get("key_findings", []), 1):
                                st.info(f"**Finding {i}:** {f}")
                        
                        with tabs[4]:
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Agents Deployed", 5)
                                st.metric("Iterations", state.get("iteration", 0))
                            
                            with col2:
                                st.metric("Questions", len(state.get("research_questions", [])))
                                st.metric("Sources", len(state.get("search_results", [])))
                            
                            with col3:
                                st.metric("Findings", len(state.get("key_findings", [])))
                                st.metric("Quality", f"{state.get('quality_score', 0):.2f}")
                
            except Exception as e:
                status.update(label="System error", state="error")
                st.error(f"Error: {e}")
                import traceback
                st.code(traceback.format_exc())

with col2:
    st.subheader("🗺️ Microservice Architecture")
    
    st.markdown("""
```mermaid
    graph TD
        UI[Streamlit UI] --> CO[Coordinator Service]
        CO --> TR[Topic Refiner Pod]
        CO --> QA[Question Architect Pod]
        CO --> SS[Search Strategist Pod]
        CO --> DA[Data Analyst Pod]
        CO --> RW[Report Writer Pod]
        
        TR --> Redis[(Redis State Store)]
        QA --> Redis
        SS --> Redis
        DA --> Redis
        RW --> Redis
        CO --> Redis
        
        style UI fill:#e8f5e9
        style CO fill:#fff3e0
        style Redis fill:#fce4ec
```
    """)
    
    st.markdown("---")
    
    st.markdown("### ℹ️ Architecture Overview")
    st.markdown("""
    **Kubernetes-Native Multi-Agent System:**
    
    - Each agent runs as an independent pod
    - Redis for shared state management
    - RESTful inter-service communication
    - Coordinator orchestrates workflow
    - Horizontal scaling per agent type
    - Service mesh ready
    """)
    
    st.markdown("---")
    
    st.markdown("### 🎯 Service Endpoints")
    st.markdown("""
    - **Coordinator**: :8006
    - **Topic Refiner**: :8001
    - **Question Architect**: :8002
    - **Search Strategist**: :8003
    - **Data Analyst**: :8004
    - **Report Writer**: :8005
    - **Redis**: :6379
    """)

if __name__ == "__main__":
    pass