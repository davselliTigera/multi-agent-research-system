# 🔄 Reusing Agents in Other Applications

The agents in this system are designed as independent microservices that can be reused in other applications. This guide shows you how.

## 📋 Table of Contents

- [Standalone Agent Usage](#standalone-agent-usage)
- [Python Library Integration](#python-library-integration)
- [API Integration](#api-integration)
- [Custom Workflows](#custom-workflows)
- [Agent Combinations](#agent-combinations)
- [Best Practices](#best-practices)

---

## 🎯 Standalone Agent Usage

### Using Agents as Python Classes

Each agent can be imported and used directly in Python applications:

```python
from agents.topic_refiner_service import TopicRefinerAgent

# Create agent instance
refiner = TopicRefinerAgent()

# Use directly
refined_topic = refiner.refine_topic("machine learning in healthcare")
print(refined_topic)
# Output: "Applications of machine learning algorithms in clinical diagnosis and patient outcome prediction"
```

### Example: Building a Custom Research Tool

```python
from agents.topic_refiner_service import TopicRefinerAgent
from agents.question_architect_service import QuestionArchitectAgent

# Initialize agents
refiner = TopicRefinerAgent()
architect = QuestionArchitectAgent()

# Custom workflow
def quick_research_outline(topic: str) -> dict:
    """Generate research outline without full workflow"""
    # Refine topic
    refined = refiner.refine_topic(topic)
    
    # Generate questions
    questions = architect.generate_questions(refined, iteration=0)
    
    return {
        "original_topic": topic,
        "refined_topic": refined,
        "research_questions": questions
    }

# Use it
outline = quick_research_outline("quantum computing")
print(outline)
```

---

## 📚 Python Library Integration

### Creating a Standalone Library

Structure for reusable library:

```
my-research-lib/
├── setup.py
├── research_agents/
│   ├── __init__.py
│   ├── base.py          # Copy base_agent.py
│   ├── refiner.py       # Copy topic_refiner_service.py
│   ├── architect.py     # Copy question_architect_service.py
│   └── analyst.py       # Copy data_analyst_service.py
└── examples/
    └── simple_usage.py
```

### Installation as Package

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="research-agents",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "langchain-google-genai>=1.0.10",
        "pydantic>=2.5.3",
    ],
    description="Reusable AI research agents",
)
```

Install locally:
```bash
pip install -e .
```

Use in any project:
```python
from research_agents import TopicRefinerAgent, QuestionArchitectAgent

refiner = TopicRefinerAgent()
result = refiner.refine_topic("AI ethics")
```

---

## 🌐 API Integration

### Using Agents as REST APIs

The agents are already exposed as REST APIs when deployed:

```bash
# Start a single agent
docker run -p 8001:8001 \
  -e GOOGLE_API_KEY="your-key" \
  multi-agent-research/topic-refiner:latest
```

### API Examples

#### Topic Refiner API

```bash
# Refine a topic
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "my-task-123",
    "agent_from": "my-app",
    "agent_to": "topic_refiner",
    "action": "refine_topic",
    "payload": {}
  }'
```

```python
# Python client
import requests

def refine_topic_api(topic: str, task_id: str):
    # First, store the topic in state (Redis or your DB)
    # Then call the agent
    response = requests.post(
        "http://localhost:8001/process",
        json={
            "task_id": task_id,
            "agent_from": "my-app",
            "agent_to": "topic_refiner",
            "action": "refine_topic",
            "payload": {}
        }
    )
    return response.json()
```

#### Question Architect API

```javascript
// JavaScript/Node.js client
const axios = require('axios');

async function generateQuestions(taskId, topic, iteration) {
  const response = await axios.post('http://localhost:8002/process', {
    task_id: taskId,
    agent_from: 'my-app',
    agent_to: 'question_architect',
    action: 'generate_questions',
    payload: {}
  });
  
  return response.data;
}
```

---

## 🔧 Custom Workflows

### Example 1: Quick FAQ Generator

Use agents to generate FAQs for any topic:

```python
from agents.question_architect_service import QuestionArchitectAgent
from agents.search_strategist_service import SearchStrategistAgent
from agents.data_analyst_service import DataAnalystAgent

class FAQGenerator:
    def __init__(self):
        self.architect = QuestionArchitectAgent()
        self.searcher = SearchStrategistAgent()
        self.analyst = DataAnalystAgent()
    
    def generate_faq(self, topic: str, num_questions: int = 5):
        """Generate FAQ from topic"""
        # Generate questions
        questions = self.architect.generate_questions(topic, 0)
        
        faqs = []
        for question in questions[:num_questions]:
            # Search for answer
            results = self.searcher.execute_search(question, max_results=3)
            
            # Analyze to get concise answer
            search_text = [f"{r['title']}: {r['body']}" for r in results]
            findings, _ = self.analyst.analyze_results(topic, search_text)
            
            faqs.append({
                "question": question,
                "answer": findings[0] if findings else "No information found"
            })
        
        return faqs

# Usage
generator = FAQGenerator()
faqs = generator.generate_faq("GraphQL")
for faq in faqs:
    print(f"Q: {faq['question']}")
    print(f"A: {faq['answer']}\n")
```

### Example 2: Automated Content Writer

```python
from agents.topic_refiner_service import TopicRefinerAgent
from agents.question_architect_service import QuestionArchitectAgent
from agents.report_writer_service import ReportWriterAgent

class ContentWriter:
    def __init__(self):
        self.refiner = TopicRefinerAgent()
        self.architect = QuestionArchitectAgent()
        self.writer = ReportWriterAgent()
    
    def write_article(self, rough_topic: str):
        """Generate article from rough topic"""
        # Refine topic
        refined = self.refiner.refine_topic(rough_topic)
        
        # Generate sections (questions)
        sections = self.architect.generate_questions(refined, 0)
        
        # Create article structure
        state = {
            "topic": refined,
            "research_questions": sections,
            "key_findings": [
                f"Key point about {section}" for section in sections
            ],
            "search_results": [],
            "iteration": 1,
            "quality_score": 0.8
        }
        
        # Generate article
        article = self.writer.generate_report(state)
        return article

# Usage
writer = ContentWriter()
article = writer.write_article("benefits of typescript")
print(article)
```

### Example 3: Smart Search Assistant

```python
from agents.search_strategist_service import SearchStrategistAgent
from agents.data_analyst_service import DataAnalystAgent

class SearchAssistant:
    def __init__(self):
        self.searcher = SearchStrategistAgent()
        self.analyst = DataAnalystAgent()
    
    def smart_search(self, query: str, num_results: int = 5):
        """Enhanced search with AI analysis"""
        # Execute search
        results = self.searcher.execute_search(query, max_results=num_results)
        
        # Prepare results for analysis
        result_texts = [
            f"{r.get('title', '')}: {r.get('body', '')}" 
            for r in results
        ]
        
        # Analyze and summarize
        insights, quality = self.analyst.analyze_results(query, result_texts)
        
        return {
            "query": query,
            "raw_results": results,
            "key_insights": insights,
            "quality_score": quality,
            "summary": insights[0] if insights else "No summary available"
        }

# Usage
assistant = SearchAssistant()
result = assistant.smart_search("best practices for REST APIs")
print(f"Summary: {result['summary']}")
print(f"Quality: {result['quality_score']}")
```

---

## 🧩 Agent Combinations

### Mix and Match Agents

You don't need all agents - use only what you need:

#### Minimal Setup: Topic + Questions
```python
from agents.topic_refiner_service import TopicRefinerAgent
from agents.question_architect_service import QuestionArchitectAgent

# Just topic refinement and question generation
refiner = TopicRefinerAgent()
architect = QuestionArchitectAgent()

topic = refiner.refine_topic("cloud computing")
questions = architect.generate_questions(topic, 0)
```

#### Search + Analysis Only
```python
from agents.search_strategist_service import SearchStrategistAgent
from agents.data_analyst_service import DataAnalystAgent

# Just search and analysis
searcher = SearchStrategistAgent()
analyst = DataAnalystAgent()

results = searcher.execute_search("kubernetes benefits")
findings, score = analyst.analyze_results("kubernetes", 
    [f"{r['title']}: {r['body']}" for r in results])
```

#### Report Generation Only
```python
from agents.report_writer_service import ReportWriterAgent

# Just report writing from existing data
writer = ReportWriterAgent()

state = {
    "topic": "Microservices Architecture",
    "research_questions": ["What are microservices?", "Benefits?"],
    "key_findings": ["Independent deployment", "Scalability"],
    "search_results": ["Result 1", "Result 2"],
    "iteration": 1,
    "quality_score": 0.9
}

report = writer.generate_report(state)
```

---

## 🎨 Integration Patterns

### Pattern 1: Webhook Integration

Use agents in event-driven architectures:

```python
from flask import Flask, request
from agents.topic_refiner_service import TopicRefinerAgent

app = Flask(__name__)
refiner = TopicRefinerAgent()

@app.route('/webhook/refine', methods=['POST'])
def refine_webhook():
    data = request.json
    topic = data.get('topic')
    
    refined = refiner.refine_topic(topic)
    
    # Send to your callback URL
    # requests.post(data['callback_url'], json={'refined': refined})
    
    return {'refined_topic': refined}

if __name__ == '__main__':
    app.run(port=5000)
```

### Pattern 2: Message Queue Integration

Use with RabbitMQ, Kafka, etc.:

```python
import pika
from agents.data_analyst_service import DataAnalystAgent

analyst = DataAnalystAgent()

def callback(ch, method, properties, body):
    data = json.loads(body)
    
    # Process with agent
    findings, score = analyst.analyze_results(
        data['topic'], 
        data['search_results']
    )
    
    # Publish results
    ch.basic_publish(
        exchange='',
        routing_key='analysis_results',
        body=json.dumps({'findings': findings, 'score': score})
    )

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='search_results')
channel.basic_consume(queue='search_results', on_message_callback=callback)
channel.start_consuming()
```

### Pattern 3: Serverless Functions

Deploy agents as AWS Lambda, Google Cloud Functions:

```python
# lambda_function.py
from agents.question_architect_service import QuestionArchitectAgent

architect = QuestionArchitectAgent()

def lambda_handler(event, context):
    topic = event.get('topic')
    iteration = event.get('iteration', 0)
    
    questions = architect.generate_questions(topic, iteration)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'questions': questions
        })
    }
```

---

## 🔐 Best Practices

### 1. Environment Configuration

```python
import os
from agents.base_agent import BaseAgent

# Set API key before using agents
os.environ['GOOGLE_API_KEY'] = 'your-key-here'

# Or pass directly
from shared.shared_models import GOOGLE_API_KEY
```

### 2. Error Handling

```python
from agents.search_strategist_service import SearchStrategistAgent

searcher = SearchStrategistAgent()

try:
    results = searcher.execute_search("query")
except Exception as e:
    print(f"Search failed: {e}")
    # Fallback logic
    results = []
```

### 3. Caching Results

```python
from functools import lru_cache
from agents.topic_refiner_service import TopicRefinerAgent

class CachedRefiner:
    def __init__(self):
        self.agent = TopicRefinerAgent()
    
    @lru_cache(maxsize=100)
    def refine_topic(self, topic: str) -> str:
        return self.agent.refine_topic(topic)
```

### 4. Rate Limiting

```python
import time
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=10, period=60)  # 10 calls per minute
def rate_limited_search(query):
    searcher = SearchStrategistAgent()
    return searcher.execute_search(query)
```

### 5. Async Usage

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def async_agent_call(agent, method, *args):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, method, *args)

# Usage
async def main():
    refiner = TopicRefinerAgent()
    result = await async_agent_call(refiner, refiner.refine_topic, "AI")
    print(result)

asyncio.run(main())
```

---

## 📦 Publishing as NPM Package (for Node.js)

Create TypeScript/JavaScript wrappers:

```typescript
// research-agents.ts
import axios from 'axios';

export class TopicRefiner {
  private baseUrl: string;
  
  constructor(baseUrl: string = 'http://localhost:8001') {
    this.baseUrl = baseUrl;
  }
  
  async refine(topic: string, taskId: string): Promise<string> {
    const response = await axios.post(`${this.baseUrl}/process`, {
      task_id: taskId,
      agent_from: 'nodejs-client',
      agent_to: 'topic_refiner',
      action: 'refine_topic',
      payload: {}
    });
    
    return response.data.data.refined_topic;
  }
}

// Usage
const refiner = new TopicRefiner();
const refined = await refiner.refine('machine learning', 'task-123');
```

---

## 🚀 Quick Start Templates

### Template 1: Simple CLI Tool

```python
#!/usr/bin/env python3
import sys
from agents.topic_refiner_service import TopicRefinerAgent
from agents.question_architect_service import QuestionArchitectAgent

def main():
    if len(sys.argv) < 2:
        print("Usage: research-tool <topic>")
        sys.exit(1)
    
    topic = ' '.join(sys.argv[1:])
    
    refiner = TopicRefinerAgent()
    architect = QuestionArchitectAgent()
    
    print(f"Original: {topic}")
    refined = refiner.refine_topic(topic)
    print(f"Refined: {refined}")
    
    print("\nResearch Questions:")
    questions = architect.generate_questions(refined, 0)
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")

if __name__ == '__main__':
    main()
```

### Template 2: FastAPI Service

```python
from fastapi import FastAPI
from agents.topic_refiner_service import TopicRefinerAgent

app = FastAPI()
refiner = TopicRefinerAgent()

@app.post("/refine")
def refine_topic(topic: str):
    return {"refined": refiner.refine_topic(topic)}

@app.get("/health")
def health():
    return {"status": "healthy"}
```

---

## 📚 More Examples

Check the `examples/` directory for:
- Integration with popular frameworks (Django, Flask, FastAPI)
- Chatbot implementations
- Slack/Discord bots
- Jupyter notebook workflows
- CI/CD pipeline integrations

## 🤝 Contributing

If you create interesting integrations, please share them!

---

**Questions?** Open an issue or discussion on GitHub!