#!/usr/bin/env python3
"""
VEDYA Simple Planning Agent (Fallback)
Works without LLM for testing the flow
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass

class ConversationStage(Enum):
    """Conversation stages."""
    INITIAL = "initial"
    GATHERING = "gathering"
    COMPLETE = "complete"

@dataclass
class PlanningSession:
    """Planning conversation session."""
    session_id: str
    stage: ConversationStage
    user_data: Dict[str, Any] = None
    conversation_history: List[Dict[str, str]] = None
    learning_plan: Optional[Dict[str, Any]] = None
    questions_asked: int = 0
    
    def __post_init__(self):
        if self.user_data is None:
            self.user_data = {}
        if self.conversation_history is None:
            self.conversation_history = []

class SimplePlanningAgent:
    """Simple planning agent for testing the flow."""
    
    def __init__(self):
        self.sessions: Dict[str, PlanningSession] = {}
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> PlanningSession:
        """Get existing session or create new one."""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        
        new_session_id = session_id or str(uuid.uuid4())
        session = PlanningSession(
            session_id=new_session_id,
            stage=ConversationStage.INITIAL
        )
        self.sessions[new_session_id] = session
        return session
    
    async def process_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process user message with simple logic."""
        session = self.get_or_create_session(session_id)
        
        # Add user message to history
        session.conversation_history.append({
            "sender": "user",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        message_lower = message.lower()
        
        # Extract subject from first message
        if session.stage == ConversationStage.INITIAL:
            if "generative ai" in message_lower or "gen ai" in message_lower:
                session.user_data["subject"] = "Generative AI"
                session.stage = ConversationStage.GATHERING
                response = "Excellent! Generative AI is a fascinating field. What's your current experience level with AI or programming?"
            elif "programming" in message_lower or "coding" in message_lower:
                session.user_data["subject"] = "Programming"
                session.stage = ConversationStage.GATHERING
                response = "Great choice! Programming opens up many opportunities. What's your current experience level?"
            elif "data science" in message_lower:
                session.user_data["subject"] = "Data Science"
                session.stage = ConversationStage.GATHERING
                response = "Data Science is an exciting field! What's your background with data and programming?"
            else:
                response = "Hello! Welcome to VEDYA. I'm here to help you create a personalized learning plan. What subject would you like to learn?"
        
        # Gather requirements
        elif session.stage == ConversationStage.GATHERING:
            session.questions_asked += 1
            
            # Extract experience level
            if "beginner" in message_lower or "new" in message_lower or "no experience" in message_lower:
                session.user_data["experience"] = "beginner"
            elif "intermediate" in message_lower or "some experience" in message_lower:
                session.user_data["experience"] = "intermediate"
            elif "advanced" in message_lower or "experienced" in message_lower:
                session.user_data["experience"] = "advanced"
            
            # Extract learning style
            if "hands-on" in message_lower or "project" in message_lower or "build" in message_lower:
                session.user_data["learning_style"] = "hands-on"
            elif "visual" in message_lower or "video" in message_lower:
                session.user_data["learning_style"] = "visual"
            elif "reading" in message_lower or "text" in message_lower:
                session.user_data["learning_style"] = "reading"
            
            # Extract timeline
            if "month" in message_lower or "weeks" in message_lower:
                session.user_data["timeline"] = "3 months"
            
            # Extract time commitment
            if "10 hours" in message_lower or "hour" in message_lower:
                session.user_data["time_commitment"] = "10 hours per week"
            
            # Check if we have enough info
            required_fields = ["subject", "experience", "learning_style"]
            has_required = all(field in session.user_data for field in required_fields)
            
            if has_required or session.questions_asked >= 4:
                # Generate learning plan
                session.learning_plan = self._generate_simple_plan(session.user_data)
                session.stage = ConversationStage.COMPLETE
                
                subject = session.user_data.get("subject", "your chosen topic")
                response = f"""Perfect! I've created your personalized {subject} learning plan.

Your plan includes:
• {len(session.learning_plan['modules'])} comprehensive modules
• Hands-on projects and exercises
• Structured learning path
• Progress tracking

The plan is now ready for you to review and start learning!"""
            else:
                # Ask for more info
                if "experience" not in session.user_data:
                    response = "What's your current experience level? Are you a complete beginner, have some experience, or consider yourself advanced?"
                elif "learning_style" not in session.user_data:
                    response = "How do you prefer to learn? Through hands-on projects, visual content like videos, or reading materials?"
                else:
                    response = "What timeline works for you? A few weeks for intensive learning or a few months for steady progress?"
        
        else:
            response = "Your learning plan is ready! You can now start your learning journey."
        
        # Add AI response to history
        session.conversation_history.append({
            "sender": "ai",
            "message": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": response,
            "session_id": session.session_id,
            "stage": session.stage.value,
            "metadata": {"questions_asked": session.questions_asked},
            "plan_ready": session.stage == ConversationStage.COMPLETE and session.learning_plan is not None
        }
    
    def _generate_simple_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a simple learning plan."""
        subject = user_data.get("subject", "Learning")
        experience = user_data.get("experience", "beginner")
        
        if "Generative AI" in subject:
            modules = [
                {
                    "id": "mod_1",
                    "title": "AI Fundamentals",
                    "description": "Understanding AI, machine learning, and how generative models work",
                    "duration": "2-3 weeks",
                    "concepts": ["What is AI", "Machine Learning Basics", "Neural Networks", "Generative Models"],
                    "objectives": ["Understand AI fundamentals", "Learn about neural networks", "Grasp generative model concepts"]
                },
                {
                    "id": "mod_2",
                    "title": "Working with AI Tools",
                    "description": "Hands-on experience with ChatGPT, Claude, and AI APIs",
                    "duration": "3-4 weeks",
                    "concepts": ["Prompt Engineering", "OpenAI API", "Claude API", "AI Integration"],
                    "objectives": ["Master prompt writing", "Use AI APIs", "Build simple AI applications"]
                },
                {
                    "id": "mod_3",
                    "title": "Building AI Applications",
                    "description": "Create real AI-powered applications and solutions",
                    "duration": "4-6 weeks",
                    "concepts": ["App Development", "RAG Systems", "Fine-tuning", "Deployment"],
                    "objectives": ["Build portfolio projects", "Deploy AI solutions", "Master advanced techniques"]
                }
            ]
        else:
            modules = [
                {
                    "id": "mod_1",
                    "title": f"{subject} Fundamentals",
                    "description": f"Core concepts and basics of {subject}",
                    "duration": "2-3 weeks",
                    "concepts": ["Basic concepts", "Core principles", "Essential tools"],
                    "objectives": ["Understand fundamentals", "Learn basic concepts", "Get familiar with tools"]
                },
                {
                    "id": "mod_2",
                    "title": f"Intermediate {subject}",
                    "description": f"Building on the basics with practical applications",
                    "duration": "3-4 weeks",
                    "concepts": ["Advanced concepts", "Practical applications", "Real projects"],
                    "objectives": ["Apply knowledge", "Build projects", "Solve real problems"]
                },
                {
                    "id": "mod_3",
                    "title": f"Advanced {subject}",
                    "description": f"Master-level concepts and professional applications",
                    "duration": "4-6 weeks",
                    "concepts": ["Expert techniques", "Industry practices", "Professional skills"],
                    "objectives": ["Master advanced techniques", "Professional-level skills", "Industry readiness"]
                }
            ]
        
        return {
            "title": f"Personalized {subject} Learning Journey",
            "description": f"A comprehensive {experience}-level learning plan for {subject}",
            "total_duration": "9-13 weeks",
            "modules": modules,
            "kanban_board": {
                "todo": [
                    {"id": "task_1", "title": "Complete Module 1: Fundamentals", "module": "mod_1"},
                    {"id": "task_2", "title": "Complete Module 2: Intermediate", "module": "mod_2"},
                    {"id": "task_3", "title": "Complete Module 3: Advanced", "module": "mod_3"}
                ],
                "in_progress": [],
                "completed": []
            }
        }
    
    def get_learning_plan(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the generated learning plan for a session."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if session.learning_plan:
                return {
                    "plan": session.learning_plan,
                    "user_profile": session.user_data,
                    "session_id": session_id
                }
        return None

# Global instance
simple_planning_agent = SimplePlanningAgent()
