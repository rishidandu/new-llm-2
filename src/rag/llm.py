import logging
from typing import Dict, Any
from openai import OpenAI
from config.settings import Config

class LLMGenerator:
    """Handles OpenAI LLM interactions"""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)
    
    def generate_answer(self, query: str, context: str) -> str:
        """Generate detailed answer using OpenAI GPT-4"""
        try:
            system_message = """You are an expert assistant for Arizona State University (ASU) with comprehensive knowledge about academics and student experiences.

IMPORTANT DATA COVERAGE:
The system contains extensive information about:
- Course grades, difficulty, and professor ratings (119,000+ records)
- Academic programs and requirements  
- General university policies and procedures
- Student discussions about coursework and majors

The system has LIMITED information about:
- Campus facilities, study locations, and building details
- Current student services and resource hours
- Campus life, events, and extracurricular activities

Your responses should be:
- Concise and mobile-friendly (aim for 100-150 words max) when context is available
- Well-structured with clear sections when appropriate
- Honest about data limitations - if asking about facilities/services, acknowledge the limitation and suggest contacting ASU directly or checking asu.edu/my.asu.edu
- Include relevant examples, statistics, or specific details from the available context
- Professional yet conversational in tone
- Include practical next steps or recommendations when relevant

Always cite specific information from the provided context and clearly acknowledge when information might be limited."""

            user_prompt = f"""Based on the following context about ASU, provide a detailed and comprehensive answer to the user's question.

Context:
{context}

Question: {query}

Please provide a thorough response that includes:
1. Direct answer to the question
2. Relevant details and examples from the context
3. Practical implications or next steps (when applicable)
4. Any important caveats or limitations

Answer:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            self.logger.error(f"Error generating answer: {e}")
            return f"Error generating answer: {e}" 