#!/usr/bin/env python3
"""
test_a2a_local.py
Test A2A communication locally to debug the issue
"""

import sys
import httpx
import json
import uuid
import redis
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
TOPIC_REFINER_URL = "http://localhost:8001"
COORDINATOR_AGENT_ID = "agent://coordinator"

# Connect to Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)


def create_test_task():
    """Create a test task in Redis"""
    task_id = "test-task-" + str(uuid.uuid4())
    
    state = {
        "task_id": task_id,
        "original_topic": "Top 3 cars built in 2025",
        "topic": "Top 3 cars built in 2025",
        "research_questions": [],
        "search_queries": [],
        "search_results": [],
        "key_findings": [],
        "iteration": 0,
        "max_iterations": 1,
        "quality_score": 0.0,
        "final_report": "",
        "status": "initialized",
        "current_agent": "",
        "agent_logs": [],
        "error": None,
        "protocol": "A2A v1.0"
    }
    
    redis_client.set(f"task:{task_id}", json.dumps(state))
    print(f"✅ Created test task: {task_id}")
    return task_id


def test_direct_endpoint(task_id):
    """Test the direct /refine_topic endpoint (if it exists)"""
    print("\n" + "="*80)
    print("TEST 1: Direct endpoint (old REST style)")
    print("="*80)
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{TOPIC_REFINER_URL}/refine_topic",
                json={"task_id": task_id}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Direct endpoint works!")
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_a2a_message(task_id):
    """Test A2A message format"""
    print("\n" + "="*80)
    print("TEST 2: A2A Protocol Message")
    print("="*80)
    
    # Create A2A message
    message = {
        "@type": "Message",
        "id": str(uuid.uuid4()),
        "to": "agent://topic-refiner",
        "from": COORDINATOR_AGENT_ID,
        "content": {
            "@type": "ActionRequest",
            "action": "refine_topic",
            "parameters": {
                "task_id": task_id
            },
            "context": {}
        },
        "timestamp": "2024-02-16T10:00:00Z"
    }
    
    print("\n📤 Sending message:")
    print(json.dumps(message, indent=2))
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{TOPIC_REFINER_URL}/message",
                json=message
            )
            
            print(f"\n📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print("\n📥 Response Data:")
                print(json.dumps(response_data, indent=2))
                
                # Detailed analysis
                print("\n🔍 Analysis:")
                print(f"  Response type: {response_data.get('@type')}")
                print(f"  Has 'content' field: {'content' in response_data}")
                
                if 'content' in response_data:
                    content = response_data['content']
                    print(f"  Content type (Python): {type(content)}")
                    
                    if isinstance(content, dict):
                        print(f"  Content @type: {content.get('@type')}")
                        print(f"  Content keys: {list(content.keys())}")
                        
                        # Check for required fields
                        has_status = 'status' in content
                        has_result = 'result' in content
                        has_action = 'action' in content
                        
                        print(f"  Has 'status': {has_status}")
                        print(f"  Has 'result': {has_result}")
                        print(f"  Has 'action': {has_action}")
                        
                        if has_status:
                            print(f"  Status value: {content['status']}")
                        if has_result:
                            print(f"  Result: {json.dumps(content['result'], indent=4)}")
                        
                        # This is what the coordinator expects
                        if has_status and has_result and content['status'] == 'completed':
                            print("\n✅ Response format is CORRECT!")
                        else:
                            print("\n❌ Response format is INCORRECT!")
                            print("   Expected: content.status = 'completed' and content.result = {...}")
                    else:
                        print(f"  ❌ Content is not a dict: {content}")
                
                # Check if we can retrieve the updated state
                print("\n📊 Checking Redis state:")
                state_json = redis_client.get(f"task:{task_id}")
                if state_json:
                    state = json.loads(state_json)
                    print(f"  Topic: {state.get('topic')}")
                    print(f"  Status: {state.get('status')}")
                    print(f"  Current agent: {state.get('current_agent')}")
                else:
                    print("  ❌ State not found in Redis")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
    
    except httpx.ConnectError as e:
        print(f"❌ Connection Error: {e}")
        print("\nMake sure topic-refiner is running:")
        print("  python agents/topic_refiner_a2a.py")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_capabilities():
    """Test capabilities endpoint"""
    print("\n" + "="*80)
    print("TEST 3: Capabilities Endpoint")
    print("="*80)
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{TOPIC_REFINER_URL}/capabilities")
            
            if response.status_code == 200:
                print("✅ Capabilities retrieved:")
                capabilities = response.json()
                print(json.dumps(capabilities, indent=2))
            else:
                print(f"❌ Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    print("🧪 A2A Communication Test Suite")
    print("="*80)
    
    # Check Redis connection
    try:
        redis_client.ping()
        print("✅ Redis connection: OK")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("\nStart Redis with:")
        print("  redis-server")
        return
    
    # Check if topic-refiner is running
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{TOPIC_REFINER_URL}/health")
            if response.status_code == 200:
                print("✅ Topic Refiner: Running")
            else:
                print(f"⚠️  Topic Refiner returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Topic Refiner not running: {e}")
        print("\nStart it with:")
        print("  python agents/topic_refiner_a2a.py")
        return
    
    # Create test task
    task_id = create_test_task()
    
    # Run tests
    test_capabilities()
    test_direct_endpoint(task_id)
    test_a2a_message(task_id)
    
    print("\n" + "="*80)
    print("✅ Testing complete!")
    print("="*80)


if __name__ == "__main__":
    main()