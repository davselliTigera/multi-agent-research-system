#!/usr/bin/env python3
"""
FAQ Generator using Research Agents
Demonstrates reusing agents to create a custom FAQ generation tool
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.question_architect_service import QuestionArchitectAgent
from agents.search_strategist_service import SearchStrategistAgent
from agents.data_analyst_service import DataAnalystAgent


class FAQGenerator:
    """Generate FAQs for any topic using AI agents"""
    
    def __init__(self):
        print("Initializing FAQ Generator...")
        self.architect = QuestionArchitectAgent()
        self.searcher = SearchStrategistAgent()
        self.analyst = DataAnalystAgent()
        print("✓ Agents ready\n")
    
    def generate_faq(self, topic: str, num_questions: int = 5) -> list:
        """
        Generate FAQ from topic
        
        Args:
            topic: The topic to generate FAQs for
            num_questions: Number of Q&A pairs to generate
            
        Returns:
            List of dict with 'question' and 'answer' keys
        """
        print(f"🎯 Generating FAQ for: {topic}")
        print(f"📝 Target questions: {num_questions}\n")
        
        # Step 1: Generate questions
        print("1️⃣  Generating questions...")
        questions = self.architect.generate_questions(topic, 0)
        print(f"   ✓ Generated {len(questions)} questions\n")
        
        faqs = []
        
        # Step 2: For each question, search and analyze
        for i, question in enumerate(questions[:num_questions], 1):
            print(f"2️⃣  Processing Q{i}: {question[:60]}...")
            
            # Search for information
            results = self.searcher.execute_search(question, max_results=3)
            print(f"   ✓ Found {len(results)} search results")
            
            if results:
                # Analyze to extract concise answer
                search_texts = [
                    f"{r.get('title', '')}: {r.get('body', '')}" 
                    for r in results
                ]
                
                findings, quality = self.analyst.analyze_results(topic, search_texts)
                print(f"   ✓ Extracted findings (quality: {quality:.2f})")
                
                answer = findings[0] if findings else "No information found"
            else:
                answer = "No information found"
            
            faqs.append({
                "question": question,
                "answer": answer
            })
            print()
        
        return faqs
    
    def format_faq(self, faqs: list) -> str:
        """Format FAQs as markdown"""
        output = "# Frequently Asked Questions\n\n"
        
        for i, faq in enumerate(faqs, 1):
            output += f"## {i}. {faq['question']}\n\n"
            output += f"{faq['answer']}\n\n"
            output += "---\n\n"
        
        return output


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python faq_generator.py <topic> [num_questions]")
        print("\nExample:")
        print("  python faq_generator.py 'GraphQL APIs' 5")
        sys.exit(1)
    
    topic = sys.argv[1]
    num_questions = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # Check for API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        print("Set it with: export GOOGLE_API_KEY='your-key'")
        sys.exit(1)
    
    # Generate FAQ
    generator = FAQGenerator()
    faqs = generator.generate_faq(topic, num_questions)
    
    # Format and display
    print("\n" + "="*60)
    print("GENERATED FAQ")
    print("="*60 + "\n")
    
    formatted = generator.format_faq(faqs)
    print(formatted)
    
    # Save to file
    filename = f"faq_{topic.replace(' ', '_').lower()}.md"
    with open(filename, 'w') as f:
        f.write(formatted)
    
    print(f"✅ FAQ saved to: {filename}")


if __name__ == '__main__':
    main()