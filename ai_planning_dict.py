#!/usr/bin/env python3
"""
VEDYA AI-Powered Conversational Planning Agent
Fully AI-driven conversation and learning plan generation using Python dictionaries
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from strict_env import get_required


# Pydantic models for structured LLM outputs
class ConversationResponse(BaseModel):
    """Structure for conversation responses."""
    message: str = Field(..., description="Natural conversational response to the user")
    subject_identified: Optional[str] = Field(None, description="Subject clearly mentioned by user")
    ready_for_gathering: bool = Field(False, description="Whether to proceed to detailed gathering")
    extracted_info: Dict[str, Any] = Field(default_factory=dict, description="Any additional information extracted")

class RequirementsResponse(BaseModel):
    """Structure for requirements gathering responses."""
    message: str = Field(..., description="Response asking for more requirements")
    requirements_gathered: Dict[str, Any] = Field(default_factory=dict, description="Requirements extracted from user message")
    ready_for_planning: bool = Field(False, description="Whether enough information is gathered to create plan")
    missing_requirements: List[str] = Field(default_factory=list, description="List of missing requirement categories")

class LearningModule(BaseModel):
    """Structure for a learning module."""
    title: str = Field(..., description="Module title")
    description: str = Field(..., description="Module description")
    duration_weeks: int = Field(..., description="Duration in weeks")
    key_concepts: List[str] = Field(..., description="Key concepts to be learned")
    activities: List[str] = Field(..., description="Learning activities")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites for this module")

class KanbanTask(BaseModel):
    """Structure for Kanban board tasks."""
    task_id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    status: str = Field(default="todo", description="Task status: todo, in_progress, completed")
    assigned_to: str = Field(..., description="Agent or system responsible")
    priority: str = Field(default="medium", description="Priority: low, medium, high")
    estimated_hours: int = Field(..., description="Estimated hours to complete")

class LearningPlan(BaseModel):
    """Structure for complete learning plan."""
    plan_id: str = Field(..., description="Unique plan identifier")
    title: str = Field(..., description="Plan title")
    description: str = Field(..., description="Plan description")
    subject: str = Field(..., description="Main subject")
    difficulty_level: str = Field(..., description="Difficulty level")
    learning_style: str = Field(..., description="Preferred learning style")
    total_duration_weeks: int = Field(..., description="Total duration in weeks")
    modules: List[LearningModule] = Field(..., description="Learning modules")
    kanban_tasks: List[KanbanTask] = Field(..., description="Kanban board tasks")
    prerequisites: List[str] = Field(default_factory=list, description="Overall prerequisites")
    learning_outcomes: List[str] = Field(..., description="Expected learning outcomes")

class ConversationStage(Enum):
    """Conversation stages."""
    INITIAL = "initial"
    GATHERING = "gathering"
    PLANNING = "planning"
    COMPLETE = "complete"

@dataclass
class UserProfile:
    """User learning profile built dynamically."""
    raw_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.raw_data is None:
            self.raw_data = {}

@dataclass
class PlanningSession:
    """Planning conversation session."""
    session_id: str
    stage: ConversationStage
    profile: UserProfile
    conversation_history: List[Dict[str, str]] = None
    learning_plan: Optional[LearningPlan] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class AIPoweredPlanningAgent:
    """AI-powered conversational planning agent using structured outputs."""
    
    def __init__(self):
        # Initialize LLM with available model
        try:
            max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 4000))
        except:
            max_tokens = 4000
            
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY", "demo-key"),
            max_tokens=max_tokens
        )
        
        # Initialize parsers for structured outputs
        self.conversation_parser = PydanticOutputParser(pydantic_object=ConversationResponse)
        self.requirements_parser = PydanticOutputParser(pydantic_object=RequirementsResponse)
        self.plan_parser = PydanticOutputParser(pydantic_object=LearningPlan)
        
        # In-memory session storage
        self.sessions: Dict[str, PlanningSession] = {}
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> PlanningSession:
        """Get existing session or create new one."""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        
        new_session_id = session_id or str(uuid.uuid4())
        session = PlanningSession(
            session_id=new_session_id,
            stage=ConversationStage.INITIAL,
            profile=UserProfile()
        )
        self.sessions[new_session_id] = session
        return session
    
    async def process_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process user message and return structured response as dictionary."""
        session = self.get_or_create_session(session_id)
        session.updated_at = datetime.now()
        
        # Add user message to history
        session.conversation_history.append({
            "sender": "user",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Route to appropriate handler based on conversation stage
        if session.stage == ConversationStage.INITIAL:
            response_dict = await self._handle_initial_conversation(session, message)
        elif session.stage == ConversationStage.GATHERING:
            response_dict = await self._handle_requirements_gathering(session, message)
        elif session.stage == ConversationStage.PLANNING:
            response_dict = await self._handle_plan_creation(session, message)
        else:
            response_dict = await self._handle_plan_complete(session, message)
        
        # Add AI response to history
        session.conversation_history.append({
            "sender": "ai",
            "message": response_dict["message"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Return structured dictionary (not JSON string)
        return {
            "response": response_dict["message"],
            "session_id": session.session_id,
            "stage": session.stage.value,
            "metadata": response_dict.get("metadata", {}),
            "learning_plan": session.learning_plan.dict() if session.learning_plan else None
        }
    
    async def _handle_initial_conversation(self, session: PlanningSession, message: str) -> Dict[str, Any]:
        """Handle initial conversation using structured output."""
        system_prompt = f"""You are VEDYA, a professional AI learning assistant. 

Your job is to have a natural conversation with the user to identify what they want to learn. Be conversational, encouraging, and professional. No excessive emojis or special characters.

Analyze the user's message and:
1. Respond naturally to what they said
2. Identify if they mentioned a specific subject they want to learn
3. If subject is clear, acknowledge it and ask about their background/experience level
4. If subject is unclear, ask them to clarify what they'd like to learn

{self.conversation_parser.get_format_instructions()}"""

        try:
            context = self._build_conversation_context(session)
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Conversation context: {context}\n\nUser's latest message: {message}")
            ])
            
            # Parse structured response
            parsed_response = self.conversation_parser.parse(response.content)
            
            # Update session based on parsed response
            if parsed_response.subject_identified:
                session.profile.raw_data["subject"] = parsed_response.subject_identified
            
            if parsed_response.extracted_info:
                session.profile.raw_data.update(parsed_response.extracted_info)
            
            if parsed_response.ready_for_gathering:
                session.stage = ConversationStage.GATHERING
            
            return {
                "message": parsed_response.message,
                "metadata": {
                    "subject_identified": parsed_response.subject_identified,
                    "stage_advanced": parsed_response.ready_for_gathering
                }
            }
            
        except Exception as e:
            print(f"LLM error in initial conversation: {e}")
            # Fallback response
            if any(word in message.lower() for word in ["learn", "study", "teach"]):
                session.stage = ConversationStage.GATHERING
                return {
                    "message": "I understand you want to learn something. Could you tell me more about the specific subject or skill you're interested in?",
                    "metadata": {"fallback_response": True, "stage_advanced": True}
                }
            else:
                return {
                    "message": "Hello! I'm VEDYA, your learning assistant. What would you like to learn today?",
                    "metadata": {"fallback_response": True}
                }
    
    async def _handle_requirements_gathering(self, session: PlanningSession, message: str) -> Dict[str, Any]:
        """Handle requirements gathering using structured output."""
        current_data = session.profile.raw_data
        
        system_prompt = f"""You are VEDYA, gathering detailed learning requirements from the user.

Current information gathered:
{json.dumps(current_data, indent=2)}

Based on the user's latest message, extract any new requirements and determine what's still missing.

Required information categories:
- subject: What they want to learn
- experience_level: beginner, intermediate, advanced
- learning_style: visual, hands-on, reading, mixed
- time_availability: hours per week they can dedicate
- timeline: how long they want to take (weeks/months)
- specific_goals: what they want to achieve
- preferred_format: videos, projects, reading, etc.

Be conversational and ask for missing information naturally. When you have enough information (subject + at least 3-4 other categories), indicate ready_for_planning=true.

{self.requirements_parser.get_format_instructions()}"""

        try:
            context = self._build_conversation_context(session)
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Conversation context: {context}\n\nUser's latest message: {message}")
            ])
            
            # Parse structured response
            parsed_response = self.requirements_parser.parse(response.content)
            
            # Update session with gathered requirements
            if parsed_response.requirements_gathered:
                session.profile.raw_data.update(parsed_response.requirements_gathered)
            
            if parsed_response.ready_for_planning:
                session.stage = ConversationStage.PLANNING
                # Generate the learning plan
                plan_dict = await self._generate_learning_plan(session)
                return {
                    "message": f"{parsed_response.message}\n\nGreat! I have enough information to create your personalized learning plan. Let me prepare that for you...",
                    "metadata": {
                        "requirements_complete": True,
                        "plan_generated": True,
                        "redirect_to_plan": True
                    }
                }
            
            return {
                "message": parsed_response.message,
                "metadata": {
                    "gathering_in_progress": True,
                    "missing_requirements": parsed_response.missing_requirements
                }
            }
            
        except Exception as e:
            print(f"LLM error in requirements gathering: {e}")
            # Fallback logic
            self._extract_requirements_fallback(session, message)
            
            missing = []
            required_fields = ["subject", "experience_level", "learning_style", "time_availability"]
            for field in required_fields:
                if field not in session.profile.raw_data:
                    missing.append(field)
            
            if len(missing) <= 1:
                session.stage = ConversationStage.PLANNING
                await self._generate_learning_plan(session)
                return {
                    "message": "Perfect! I have enough information to create your learning plan. Let me prepare a detailed plan for you.",
                    "metadata": {"requirements_complete": True, "plan_generated": True, "redirect_to_plan": True}
                }
            else:
                next_question = self._get_next_question(missing[0])
                return {
                    "message": next_question,
                    "metadata": {"gathering_in_progress": True, "missing_requirements": missing}
                }
    
    async def _generate_learning_plan(self, session: PlanningSession) -> Dict[str, Any]:
        """Generate complete learning plan using structured output."""
        user_requirements = session.profile.raw_data
        
        system_prompt = f"""You are VEDYA's learning plan generator. Create a comprehensive, personalized learning plan.

User Requirements:
{json.dumps(user_requirements, indent=2)}

Generate a complete learning plan with:
1. 3-4 learning modules, each with clear progression
2. Realistic timeline based on user's availability
3. Mix of learning activities matching their style
4. Kanban tasks for project management
5. Clear learning outcomes

Make it practical and actionable. Focus on real-world application.

{self.plan_parser.get_format_instructions()}"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content="Generate the complete learning plan based on the user requirements.")
            ])
            
            # Parse structured response
            parsed_plan = self.plan_parser.parse(response.content)
            session.learning_plan = parsed_plan
            session.stage = ConversationStage.COMPLETE
            
            return parsed_plan.dict()
            
        except Exception as e:
            print(f"LLM error in plan generation: {e}")
            # Fallback plan generation
            plan = self._generate_fallback_plan(user_requirements)
            session.learning_plan = LearningPlan(**plan)
            session.stage = ConversationStage.COMPLETE
            return plan
    
    def _generate_fallback_plan(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fallback plan when LLM fails."""
        subject = requirements.get("subject", "the topic")
        
        return {
            "plan_id": f"plan_{uuid.uuid4().hex[:8]}",
            "title": f"Personalized {subject.title()} Learning Journey",
            "description": f"A comprehensive learning plan tailored to your {subject} goals",
            "subject": subject,
            "difficulty_level": requirements.get("experience_level", "beginner"),
            "learning_style": requirements.get("learning_style", "mixed"),
            "total_duration_weeks": 12,
            "modules": [
                {
                    "title": f"{subject.title()} Fundamentals",
                    "description": f"Core concepts and basics of {subject}",
                    "duration_weeks": 3,
                    "key_concepts": ["Basic terminology", "Core principles", "Essential tools"],
                    "activities": ["Reading materials", "Practice exercises", "Simple projects"],
                    "prerequisites": []
                },
                {
                    "title": f"Intermediate {subject.title()}",
                    "description": f"Building practical skills in {subject}",
                    "duration_weeks": 4,
                    "key_concepts": ["Advanced concepts", "Practical applications", "Real-world examples"],
                    "activities": ["Hands-on projects", "Case studies", "Peer collaboration"],
                    "prerequisites": [f"{subject.title()} Fundamentals"]
                },
                {
                    "title": f"Advanced {subject.title()} & Projects",
                    "description": f"Master-level concepts and portfolio development",
                    "duration_weeks": 5,
                    "key_concepts": ["Expert techniques", "Industry best practices", "Portfolio development"],
                    "activities": ["Capstone project", "Industry simulation", "Knowledge sharing"],
                    "prerequisites": [f"Intermediate {subject.title()}"]
                }
            ],
            "kanban_tasks": [
                {
                    "task_id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Complete Module 1",
                    "description": f"Master the fundamentals of {subject}",
                    "status": "todo",
                    "assigned_to": "Learner",
                    "priority": "high",
                    "estimated_hours": 20
                },
                {
                    "task_id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Complete Module 2",
                    "description": f"Build intermediate skills in {subject}",
                    "status": "todo",
                    "assigned_to": "Learner",
                    "priority": "medium",
                    "estimated_hours": 30
                }
            ],
            "prerequisites": [],
            "learning_outcomes": [
                f"Understand core concepts of {subject}",
                f"Apply {subject} knowledge to real projects",
                f"Build a portfolio demonstrating {subject} skills"
            ]
        }
    
    def _extract_requirements_fallback(self, session: PlanningSession, message: str):
        """Fallback method to extract requirements when LLM fails."""
        message_lower = message.lower()
        
        # Extract experience level
        if not session.profile.raw_data.get("experience_level"):
            if any(word in message_lower for word in ["beginner", "new", "start", "never"]):
                session.profile.raw_data["experience_level"] = "beginner"
            elif any(word in message_lower for word in ["intermediate", "some", "little"]):
                session.profile.raw_data["experience_level"] = "intermediate"
            elif any(word in message_lower for word in ["advanced", "experienced", "expert"]):
                session.profile.raw_data["experience_level"] = "advanced"
        
        # Extract learning style
        if not session.profile.raw_data.get("learning_style"):
            if any(word in message_lower for word in ["visual", "videos", "watch"]):
                session.profile.raw_data["learning_style"] = "visual"
            elif any(word in message_lower for word in ["hands-on", "practice", "projects", "build"]):
                session.profile.raw_data["learning_style"] = "hands-on"
            elif any(word in message_lower for word in ["reading", "books", "text"]):
                session.profile.raw_data["learning_style"] = "reading"
            else:
                session.profile.raw_data["learning_style"] = "mixed"
        
        # Extract time availability
        if not session.profile.raw_data.get("time_availability"):
            import re
            hours_match = re.search(r'(\d+)\s*hours?', message_lower)
            if hours_match:
                session.profile.raw_data["time_availability"] = f"{hours_match.group(1)} hours per week"
    
    def _get_next_question(self, missing_field: str) -> str:
        """Get next question for missing field."""
        questions = {
            "experience_level": "What's your current experience level with this subject? Are you a complete beginner, have some experience, or would you consider yourself advanced?",
            "learning_style": "How do you prefer to learn? Through videos and visual materials, hands-on projects and practice, reading materials, or a mix of all styles?",
            "time_availability": "How much time can you dedicate to learning each week? For example, 5-10 hours per week?",
            "timeline": "What's your ideal timeline for completing this learning journey? A few weeks, a couple of months, or do you prefer to take it slowly?",
            "specific_goals": "What specific goals do you hope to achieve? Are you learning for personal interest, career advancement, or a particular project?"
        }
        return questions.get(missing_field, "Could you tell me more about your learning preferences?")
    
    def _build_conversation_context(self, session: PlanningSession) -> str:
        """Build conversation context for LLM."""
        if not session.conversation_history:
            return "This is the start of the conversation."
        
        recent_messages = session.conversation_history[-3:]  # Last 3 messages for context
        context = []
        for msg in recent_messages:
            sender = msg["sender"].title()
            content = msg["message"][:100] + "..." if len(msg["message"]) > 100 else msg["message"]
            context.append(f"{sender}: {content}")
        
        return "\n".join(context)
    
    async def _handle_plan_creation(self, session: PlanningSession, message: str) -> Dict[str, Any]:
        """Handle plan creation stage."""
        return {
            "message": "Your learning plan is being prepared. Please wait while I finalize the details.",
            "metadata": {"plan_in_progress": True}
        }
    
    async def _handle_plan_complete(self, session: PlanningSession, message: str) -> Dict[str, Any]:
        """Handle post-plan completion messages."""
        return {
            "message": "Your learning plan is ready! You can view it on the plan page and start learning when you're ready.",
            "metadata": {"plan_ready": True}
        }
    
    def get_learning_plan(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the learning plan for a session as a dictionary."""
        session = self.sessions.get(session_id)
        if session and session.learning_plan:
            return session.learning_plan.dict()
        return None

# Global instance
ai_planning_agent = AIPoweredPlanningAgent()
