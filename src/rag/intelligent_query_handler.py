import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class ClarificationQuestion:
    """Represents a clarifying question to ask the user"""
    question: str
    options: List[str]
    context: str
    field_name: str

@dataclass
class EnhancedResponse:
    """Enhanced response with additional context and suggestions"""
    answer: str
    sources: List[Dict[str, Any]]
    follow_up_questions: List[str]
    related_topics: List[str]
    action_items: List[str]
    confidence_score: float
    needs_clarification: bool
    clarification_questions: List[ClarificationQuestion]

class IntelligentQueryHandler:
    """Handles intelligent query processing with clarification and enhancement"""
    
    def __init__(self, rag_system):
        self.rag_system = rag_system
        
        # Define common clarification patterns
        self.clarification_patterns = {
            'job_type': {
                'patterns': [r'job', r'work', r'employment', r'career'],
                'questions': [
                    "What type of job are you looking for?",
                    "Are you interested in on-campus or off-campus positions?",
                    "What's your field of study or major?"
                ],
                'options': [
                    "On-campus student worker",
                    "Off-campus part-time",
                    "Internship",
                    "Research position",
                    "Food service",
                    "Administrative/Office work"
                ]
            },
            'course_info': {
                'patterns': [r'course', r'class', r'grade', r'professor'],
                'questions': [
                    "What specific course or subject are you asking about?",
                    "Are you looking for grade information or professor ratings?",
                    "What semester are you interested in?"
                ],
                'options': [
                    "Course grades and difficulty",
                    "Professor ratings and reviews",
                    "Course recommendations",
                    "Grade distributions",
                    "Pass rates"
                ]
            },
            'campus_location': {
                'patterns': [r'campus', r'location', r'where', r'building'],
                'questions': [
                    "Which ASU campus are you referring to?",
                    "Are you looking for something specific on campus?"
                ],
                'options': [
                    "Tempe campus",
                    "Downtown Phoenix",
                    "Polytechnic campus",
                    "West campus",
                    "Online/ASU Online"
                ]
            }
        }
    
    def analyze_query(self, question: str) -> Dict[str, Any]:
        """Analyze the query to determine if clarification is needed"""
        analysis = {
            'needs_clarification': False,
            'clarification_questions': [],
            'detected_topics': [],
            'confidence_score': 0.8
        }
        
        question_lower = question.lower()
        
        # Check for vague terms that need clarification
        vague_terms = [
            'good', 'best', 'easy', 'hard', 'nice', 'bad', 'better',
            'some', 'any', 'things', 'stuff', 'etc', 'and so on'
        ]
        
        vague_count = sum(1 for term in vague_terms if term in question_lower)
        if vague_count > 2:
            analysis['needs_clarification'] = True
            analysis['confidence_score'] -= 0.3
        
        # Check for specific topics that might need clarification
        for topic, config in self.clarification_patterns.items():
            if any(re.search(pattern, question_lower) for pattern in config['patterns']):
                analysis['detected_topics'].append(topic)
                
                # Check if the query is specific enough
                if not self._is_specific_enough(question, topic):
                    analysis['needs_clarification'] = True
                    analysis['clarification_questions'].append(
                        ClarificationQuestion(
                            question=config['questions'][0],
                            options=config['options'],
                            context=f"To provide better information about {topic}",
                            field_name=topic
                        )
                    )
        
        return analysis
    
    def _is_specific_enough(self, question: str, topic: str) -> bool:
        """Check if the question is specific enough for the given topic"""
        # Add logic to determine if question is specific enough
        specific_indicators = {
            'job_type': ['campus', 'off-campus', 'internship', 'research', 'food service'],
            'course_info': ['mat', 'cs', 'eng', 'bus', 'specific course code'],
            'campus_location': ['tempe', 'downtown', 'polytechnic', 'west', 'online']
        }
        
        question_lower = question.lower()
        indicators = specific_indicators.get(topic, [])
        
        return any(indicator in question_lower for indicator in indicators)
    
    def generate_clarification_questions(self, question: str) -> List[ClarificationQuestion]:
        """Generate specific clarifying questions based on the query"""
        questions = []
        question_lower = question.lower()
        
        # Job-related clarifications
        if any(term in question_lower for term in ['job', 'work', 'employment']):
            if 'campus' not in question_lower and 'off-campus' not in question_lower:
                questions.append(ClarificationQuestion(
                    question="Are you looking for on-campus or off-campus job opportunities?",
                    options=["On-campus", "Off-campus", "Both", "Not sure"],
                    context="This will help me provide more relevant job listings and advice",
                    field_name="job_location"
                ))
            
            if not any(major in question_lower for major in ['cs', 'engineering', 'business', 'arts', 'science']):
                questions.append(ClarificationQuestion(
                    question="What's your major or field of study?",
                    options=["Computer Science", "Engineering", "Business", "Arts", "Sciences", "Other"],
                    context="This helps me suggest jobs relevant to your field",
                    field_name="major"
                ))
        
        # Course-related clarifications
        if any(term in question_lower for term in ['course', 'class', 'grade']):
            if not re.search(r'[A-Z]{2,4}\s*\d{3,4}', question_lower):  # No course code pattern
                questions.append(ClarificationQuestion(
                    question="What specific course or subject are you interested in?",
                    options=["Math courses", "Computer Science", "Engineering", "Business", "General Education", "Other"],
                    context="This helps me provide specific grade and professor information",
                    field_name="course_subject"
                ))
        
        return questions
    
    def enhance_response(self, base_result: Dict[str, Any], question: str) -> EnhancedResponse:
        """Enhance the base response with additional context and suggestions"""
        
        # Generate follow-up questions
        follow_up_questions = self._generate_follow_up_questions(question, base_result)
        
        # Extract related topics
        related_topics = self._extract_related_topics(question, base_result)
        
        # Generate action items
        action_items = self._generate_action_items(question, base_result)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(base_result)
        
        # Check if clarification is needed
        analysis = self.analyze_query(question)
        clarification_questions = self.generate_clarification_questions(question)
        
        return EnhancedResponse(
            answer=base_result.get('answer', ''),
            sources=base_result.get('sources', []),
            follow_up_questions=follow_up_questions,
            related_topics=related_topics,
            action_items=action_items,
            confidence_score=confidence_score,
            needs_clarification=analysis['needs_clarification'],
            clarification_questions=clarification_questions
        )
    
    def _generate_follow_up_questions(self, question: str, result: Dict[str, Any]) -> List[str]:
        """Generate relevant follow-up questions"""
        follow_ups = []
        question_lower = question.lower()
        
        if 'job' in question_lower or 'work' in question_lower:
            follow_ups.extend([
                "What's your major? This could help me suggest more relevant opportunities.",
                "Are you looking for on-campus or off-campus positions?",
                "What's your preferred work schedule (weekdays, weekends, evenings)?",
                "Do you have any specific skills or experience you'd like to highlight?"
            ])
        
        if 'course' in question_lower or 'grade' in question_lower:
            follow_ups.extend([
                "What semester are you planning to take this course?",
                "Are you more interested in professor ratings or grade distributions?",
                "Do you want to know about specific sections or professors?",
                "Are you looking for easy courses or challenging ones?"
            ])
        
        if 'professor' in question_lower:
            follow_ups.extend([
                "What specific courses does this professor teach?",
                "Are you looking for teaching style or grading information?",
                "What's your major? Some professors are better for certain fields."
            ])
        
        return follow_ups[:3]  # Limit to top 3
    
    def _extract_related_topics(self, question: str, result: Dict[str, Any]) -> List[str]:
        """Extract related topics for further exploration"""
        topics = []
        question_lower = question.lower()
        
        if 'job' in question_lower:
            topics.extend([
                "Career Services at ASU",
                "Student Employment Office",
                "Work+ Program",
                "Internship Opportunities",
                "Resume Building"
            ])
        
        if 'course' in question_lower or 'grade' in question_lower:
            topics.extend([
                "Course Registration Tips",
                "Professor Selection Strategies",
                "Grade Point Average (GPA) Information",
                "Academic Advising"
            ])
        
        if 'campus' in question_lower:
            topics.extend([
                "Campus Resources",
                "Student Life",
                "Campus Events",
                "Student Organizations"
            ])
        
        return topics[:5]  # Limit to top 5
    
    def _generate_action_items(self, question: str, result: Dict[str, Any]) -> List[str]:
        """Generate actionable next steps"""
        actions = []
        question_lower = question.lower()
        
        if 'job' in question_lower:
            actions.extend([
                "Check the Student Jobs board on My ASU daily",
                "Contact your department's administrative office",
                "Visit the Career Services office",
                "Update your resume and cover letter",
                "Network with professors and classmates"
            ])
        
        if 'course' in question_lower:
            actions.extend([
                "Check course registration dates",
                "Review professor ratings on RateMyProfessors",
                "Talk to academic advisors",
                "Join course-specific study groups",
                "Review course syllabi and requirements"
            ])
        
        return actions[:4]  # Limit to top 4
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score based on result quality"""
        confidence = 0.8  # Base confidence
        
        # Adjust based on number of sources
        sources = result.get('sources', [])
        if len(sources) >= 3:
            confidence += 0.1
        elif len(sources) == 0:
            confidence -= 0.3
        
        # Adjust based on answer length (more detailed = higher confidence)
        answer = result.get('answer', '')
        if len(answer) > 200:
            confidence += 0.1
        elif len(answer) < 50:
            confidence -= 0.2
        
        return min(1.0, max(0.0, confidence))
    
    def process_query(self, question: str, user_context: Dict[str, Any] = None) -> EnhancedResponse:
        """Main method to process a query with intelligent enhancement"""
        
        # Get base result from RAG system
        base_result = self.rag_system.query(question, top_k=5)
        
        # Enhance the response
        enhanced_response = self.enhance_response(base_result, question)
        
        # If user context is provided, personalize the response
        if user_context:
            enhanced_response = self._personalize_response(enhanced_response, user_context)
        
        return enhanced_response
    
    def _personalize_response(self, response: EnhancedResponse, user_context: Dict[str, Any]) -> EnhancedResponse:
        """Personalize response based on user context"""
        # Add personalization logic here
        # For example, if user has specified major, filter related topics
        if 'major' in user_context:
            major = user_context['major']
            response.related_topics = [topic for topic in response.related_topics 
                                     if major.lower() in topic.lower() or 'general' in topic.lower()]
        
        return response 