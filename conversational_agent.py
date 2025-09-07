#!/usr/bin/env python3
"""
VEDYA Interactive Chat Agent
A conversational agent that properly gathers user requirements before creating learning plans.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import openai
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Load environment variables
load_dotenv()

class VEDYAConversationalAgent:
    """Interactive conversational agent for VEDYA that gathers user requirements."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="o4-mini",
            temperature=1.0,  # o4-mini only supports default temperature
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.conversation_history = []
        self.user_profile = {}
        self.conversation_stage = "initial"  # initial, gathering_info, creating_plan, plan_ready
        
    def get_system_prompt(self) -> str:
        """Get the system prompt for the conversational agent."""
        return """You are VEDYA, an AI learning assistant that creates personalized learning experiences.

Your goal is to gather detailed information about the user's learning needs before creating a plan.

CONVERSATION STAGES:
1. INITIAL: Greet and ask what they want to learn
2. GATHERING_INFO: Ask follow-up questions to understand their needs
3. CREATING_PLAN: Confirm details and create the plan
4. PLAN_READY: Present the completed plan

QUESTIONS TO ASK (don't ask all at once, be conversational):
- What specific topic/subject do they want to learn?
- What's their current knowledge level (complete beginner, some experience, intermediate, advanced)?
- How much time can they dedicate per day/week?
- How long do they want the learning plan to be (weeks/months)?
- What's their preferred learning style (videos, reading, hands-on practice, interactive)?
- What's their main goal (career change, hobby, skill improvement, academic)?
- Do they have any specific deadlines or timelines?
- Any particular areas they want to focus on?

IMPORTANT RULES:
- Be conversational and friendly, not robotic
- Ask 1-2 questions at a time, not a long list
- Build on their previous answers
- Only create a plan when you have enough information
- If they're vague, ask for clarification
- Adapt your questions based on their responses
- Be encouraging and supportive

Current conversation stage: {stage}
User profile so far: {profile}
"""
    
    async def process_message(self, user_message: str, session_id: str = None) -> Dict[str, Any]:
        """Process a user message and return an appropriate response."""
        
        # Add user message to history
        self.conversation_history.append(HumanMessage(content=user_message))
        
        # Determine conversation stage and user profile
        self._analyze_conversation()
        
        # Create system message with current context
        system_prompt = self.get_system_prompt().format(
            stage=self.conversation_stage,
            profile=json.dumps(self.user_profile, indent=2)
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            *self.conversation_history
        ]
        
        # Get AI response
        try:
            response = await self.llm.ainvoke(messages)
            ai_message = response.content
            
            # Add AI response to history
            self.conversation_history.append(AIMessage(content=ai_message))
            
            # Check if we should create a plan
            should_create_plan = self._should_create_plan()
            
            return {
                "response": ai_message,
                "conversation_stage": self.conversation_stage,
                "user_profile": self.user_profile,
                "ready_for_plan": should_create_plan,
                "session_id": session_id or "default"
            }
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an error: {str(e)}. Could you please try again?"
            return {
                "response": error_response,
                "conversation_stage": "error",
                "user_profile": self.user_profile,
                "ready_for_plan": False,
                "session_id": session_id or "default"
            }
    
    def _analyze_conversation(self):
        """Analyze conversation to update user profile and stage."""
        if not self.conversation_history:
            return
            
        latest_message = self.conversation_history[-1].content.lower()
        
        # Extract information from the conversation
        self._extract_subject(latest_message)
        self._extract_level(latest_message)
        self._extract_time_commitment(latest_message)
        self._extract_timeline(latest_message)
        self._extract_learning_style(latest_message)
        self._extract_goals(latest_message)
        
        # Update conversation stage
        self._update_conversation_stage()
    
    def _extract_subject(self, message: str):
        """Extract learning subject from user message."""
        subjects = {
            "python": "Python Programming",
            "javascript": "JavaScript Programming", 
            "js": "JavaScript Programming",
            "web development": "Web Development",
            "web dev": "Web Development",
            "ai": "Artificial Intelligence",
            "artificial intelligence": "Artificial Intelligence", 
            "machine learning": "Machine Learning",
            "ml": "Machine Learning",
            "data science": "Data Science",
            "programming": "Programming",
            "coding": "Programming",
            "mathematics": "Mathematics",
            "math": "Mathematics",
            "physics": "Physics",
            "chemistry": "Chemistry",
            "biology": "Biology",
            "react": "React Development",
            "node": "Node.js Development",
            "java": "Java Programming",
            "c++": "C++ Programming",
            "cybersecurity": "Cybersecurity",
            "blockchain": "Blockchain Technology",
            "game development": "Game Development",
            "mobile development": "Mobile App Development"
        }
        
        for keyword, subject in subjects.items():
            if keyword in message:
                self.user_profile["subject"] = subject
                break
    
    def _extract_level(self, message: str):
        """Extract knowledge level from user message."""
        if any(word in message for word in ["beginner", "new", "start", "never", "first time", "no experience"]):
            self.user_profile["level"] = "beginner"
        elif any(word in message for word in ["intermediate", "some experience", "basic knowledge"]):
            self.user_profile["level"] = "intermediate"  
        elif any(word in message for word in ["advanced", "experienced", "expert", "professional"]):
            self.user_profile["level"] = "advanced"
    
    def _extract_time_commitment(self, message: str):
        """Extract time commitment from user message."""
        time_patterns = {
            "hour": ["1 hour", "one hour", "hour a day", "hour per day"],
            "2-3 hours": ["2 hours", "3 hours", "couple hours", "few hours"],
            "30 minutes": ["30 min", "half hour", "30 minutes"],
            "flexible": ["flexible", "varies", "depends"]
        }
        
        for time_value, patterns in time_patterns.items():
            if any(pattern in message for pattern in patterns):
                self.user_profile["time_per_day"] = time_value
                break
    
    def _extract_timeline(self, message: str):
        """Extract timeline from user message."""
        if any(word in message for word in ["week", "weeks"]):
            # Try to extract number of weeks
            words = message.split()
            for i, word in enumerate(words):
                if word.isdigit() and i + 1 < len(words) and "week" in words[i + 1]:
                    self.user_profile["timeline_weeks"] = int(word)
                    break
        elif any(word in message for word in ["month", "months"]):
            words = message.split()
            for i, word in enumerate(words):
                if word.isdigit() and i + 1 < len(words) and "month" in words[i + 1]:
                    self.user_profile["timeline_weeks"] = int(word) * 4
                    break
    
    def _extract_learning_style(self, message: str):
        """Extract learning style preferences."""
        styles = []
        if any(word in message for word in ["video", "videos", "watch", "visual"]):
            styles.append("video")
        if any(word in message for word in ["hands-on", "practice", "build", "projects"]):
            styles.append("hands-on")
        if any(word in message for word in ["reading", "books", "text", "articles"]):
            styles.append("reading")
        if any(word in message for word in ["interactive", "quizzes", "exercises"]):
            styles.append("interactive")
            
        if styles:
            self.user_profile["learning_style"] = styles
    
    def _extract_goals(self, message: str):
        """Extract learning goals."""
        goals = []
        if any(word in message for word in ["job", "career", "work", "employment"]):
            goals.append("career")
        if any(word in message for word in ["hobby", "interest", "fun", "personal"]):
            goals.append("personal")
        if any(word in message for word in ["project", "build", "create"]):
            goals.append("project-based")
        if any(word in message for word in ["exam", "test", "certification", "degree"]):
            goals.append("academic")
            
        if goals:
            self.user_profile["goals"] = goals
    
    def _update_conversation_stage(self):
        """Update conversation stage based on gathered information."""
        required_info = ["subject"]
        nice_to_have = ["level", "time_per_day", "timeline_weeks", "learning_style", "goals"]
        
        has_required = all(key in self.user_profile for key in required_info)
        has_most_info = sum(1 for key in nice_to_have if key in self.user_profile) >= 3
        
        if not has_required:
            self.conversation_stage = "gathering_basic"
        elif has_required and not has_most_info:
            self.conversation_stage = "gathering_details"
        elif has_required and has_most_info:
            self.conversation_stage = "ready_to_plan"
    
    def _should_create_plan(self) -> bool:
        """Determine if we have enough information to create a learning plan."""
        return (self.conversation_stage == "ready_to_plan" and 
                "subject" in self.user_profile and
                len(self.user_profile) >= 3)
    
    def get_plan_summary(self) -> Dict[str, Any]:
        """Generate a plan summary based on gathered information."""
        if not self._should_create_plan():
            return {"error": "Not enough information to create plan"}
        
        # Set defaults for missing information
        defaults = {
            "level": "beginner",
            "time_per_day": "1 hour", 
            "timeline_weeks": 8,
            "learning_style": ["mixed"],
            "goals": ["personal"]
        }
        
        for key, default_value in defaults.items():
            if key not in self.user_profile:
                self.user_profile[key] = default_value
        
        return {
            "subject": self.user_profile["subject"],
            "level": self.user_profile["level"],
            "duration_weeks": self.user_profile["timeline_weeks"],
            "time_commitment": self.user_profile["time_per_day"],
            "learning_style": self.user_profile["learning_style"],
            "goals": self.user_profile["goals"],
            "personalized": True,
            "user_driven": True
        }

# Test function
async def test_conversational_agent():
    """Test the conversational agent."""
    agent = VEDYAConversationalAgent()
    
    print("🎓 VEDYA Conversational Agent Test")
    print("=" * 50)
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['quit', 'exit']:
            break
            
        result = await agent.process_message(user_input)
        
        print(f"\n🤖 VEDYA: {result['response']}")
        print(f"\n📊 Stage: {result['conversation_stage']}")
        print(f"👤 Profile: {json.dumps(result['user_profile'], indent=2)}")
        
        if result['ready_for_plan']:
            print("\n✅ Ready to create learning plan!")
            plan = agent.get_plan_summary()
            print(f"📋 Plan: {json.dumps(plan, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_conversational_agent())
