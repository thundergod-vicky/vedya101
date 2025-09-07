#!/usr/bin/env python3
"""
VEDYA Professional Conversational Planning Agent
Clean, professional conversation flow for learning plan creation
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
from dotenv import load_dotenv

load_dotenv()

class PlanningStage(Enum):
    """Stages in the planning conversation."""
    INITIAL = "initial"
    GATHERING = "gathering"
    COMPLETE = "complete"

@dataclass
class UserProfile:
    """User learning profile."""
    subject: Optional[str] = None
    experience_level: Optional[str] = None
    learning_style: Optional[str] = None
    timeline: Optional[str] = None
    time_commitment: Optional[str] = None
    specific_goals: List[str] = None
    
    def __post_init__(self):
        if self.specific_goals is None:
            self.specific_goals = []

@dataclass
class LearningModule:
    """Learning module structure."""
    id: str
    title: str
    description: str
    duration: str
    concepts: List[str]
    objectives: List[str]
    prerequisites: List[str] = None
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []

@dataclass
class LearningPlan:
    """Complete learning plan."""
    plan_id: str
    title: str
    description: str
    subject: str
    total_duration: str
    difficulty_level: str
    modules: List[LearningModule]
    kanban_tasks: List[Dict[str, Any]]
    created_at: datetime

@dataclass
class PlanningSession:
    """Planning conversation session."""
    session_id: str
    stage: PlanningStage
    profile: UserProfile
    learning_plan: Optional[LearningPlan] = None
    conversation_history: List[Dict[str, str]] = None
    questions_asked: int = 0
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []

class ProfessionalPlanningAgent:
    """Professional planning agent for VEDYA."""
    
    def __init__(self):
        try:
            max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 4000))
        except:
            max_tokens = 4000
            
        self.llm = ChatOpenAI(
            model="o4-mini",
            temperature=1.0,  # o4-mini only supports default temperature
            api_key=os.getenv("OPENAI_API_KEY"),
            max_tokens=max_tokens
        )
        
        self.sessions: Dict[str, PlanningSession] = {}
    
    def get_session(self, session_id: Optional[str] = None) -> PlanningSession:
        """Get or create planning session."""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        
        new_session_id = session_id or str(uuid.uuid4())
        session = PlanningSession(
            session_id=new_session_id,
            stage=PlanningStage.INITIAL,
            profile=UserProfile()
        )
        self.sessions[new_session_id] = session
        return session
    
    async def process_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process planning conversation message."""
        session = self.get_session(session_id)
        
        # Add to conversation history
        session.conversation_history.append({
            "sender": "user",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        if session.stage == PlanningStage.INITIAL:
            response = await self._handle_initial(session, message)
        elif session.stage == PlanningStage.GATHERING:
            response = await self._handle_gathering(session, message)
        else:
            response = await self._handle_complete(session, message)
        
        # Add AI response to history
        session.conversation_history.append({
            "sender": "ai",
            "message": response["message"],
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": response["message"],
            "session_id": session.session_id,
            "stage": session.stage.value,
            "metadata": response.get("metadata", {}),
            "plan_ready": session.stage == PlanningStage.COMPLETE
        }
    
    async def _handle_initial(self, session: PlanningSession, message: str) -> Dict[str, Any]:
        """Handle initial conversation using LLM."""
        system_prompt = """You are VEDYA, a professional AI learning assistant. Your role is to have a natural conversation with the user to understand what they want to learn.

Guidelines:
- Be conversational and professional (minimal emojis)
- Extract the subject they want to learn from their message
- If they mention a subject, acknowledge it and ask about their experience level
- If they don't mention a subject clearly, ask them what they'd like to learn
- Keep responses concise and natural

Respond as JSON:
{
    "message": "Your natural response to the user",
    "extracted_subject": "subject if clearly mentioned, null otherwise",
    "next_stage": "gathering" or "initial"
}"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"User message: {message}")
            ])
            
            result = json.loads(response.content)
            
            if result.get("extracted_subject"):
                session.profile.subject = result["extracted_subject"]
                session.stage = PlanningStage.GATHERING
                session.questions_asked = 1
            
            return {
                "message": result["message"],
                "metadata": {"subject_extracted": bool(result.get("extracted_subject"))}
            }
            
        except Exception as e:
            # Fallback response
            return {
                "message": "Hello! Welcome to VEDYA. I'm here to help you create a personalized learning plan. What subject or skill would you like to learn?",
                "metadata": {"llm_error": True}
            }
    
    async def _handle_gathering(self, session: PlanningSession, message: str) -> Dict[str, Any]:
        """Handle requirements gathering conversation."""
        # Use LLM to extract information from user response
        await self._extract_info_from_message(session, message)
        
        # Check if we have enough information
        if self._has_sufficient_info(session):
            # Generate complete learning plan
            learning_plan = await self._generate_learning_plan(session)
            session.learning_plan = learning_plan
            session.stage = PlanningStage.COMPLETE
            
            return {
                "message": "Perfect! I have all the information I need. Let me create your personalized learning plan...",
                "metadata": {"plan_generation_started": True}
            }
        else:
            # Ask next question
            return await self._ask_next_question(session)
    
    async def _extract_info_from_message(self, session: PlanningSession, message: str):
        """Extract learning requirements from user message."""
        message_lower = message.lower()
        
        # Experience level detection
        if not session.profile.experience_level:
            if any(word in message_lower for word in ["beginner", "new", "never", "starting", "basic"]):
                session.profile.experience_level = "beginner"
            elif any(word in message_lower for word in ["intermediate", "some", "familiar", "bit of"]):
                session.profile.experience_level = "intermediate"
            elif any(word in message_lower for word in ["advanced", "experienced", "expert", "professional"]):
                session.profile.experience_level = "advanced"
        
        # Learning style detection
        if not session.profile.learning_style:
            if any(word in message_lower for word in ["hands-on", "project", "build", "practice", "doing"]):
                session.profile.learning_style = "hands-on"
            elif any(word in message_lower for word in ["visual", "video", "watch", "see", "demo"]):
                session.profile.learning_style = "visual"
            elif any(word in message_lower for word in ["reading", "text", "book", "article", "theory"]):
                session.profile.learning_style = "reading"
        
        # Timeline detection
        if not session.profile.timeline:
            if any(word in message_lower for word in ["week", "weeks", "quickly", "fast", "asap"]):
                session.profile.timeline = "intensive"
            elif any(word in message_lower for word in ["month", "months", "steady"]):
                session.profile.timeline = "regular"
            elif any(word in message_lower for word in ["slow", "casual", "spare time", "whenever"]):
                session.profile.timeline = "flexible"
        
        # Time commitment detection
        if not session.profile.time_commitment:
            import re
            time_patterns = re.findall(r'(\d+)\s*hour', message_lower)
            if time_patterns:
                hours = int(time_patterns[0])
                if hours <= 5:
                    session.profile.time_commitment = f"{hours} hours per week"
                else:
                    session.profile.time_commitment = f"{hours} hours per week"
    
    def _has_sufficient_info(self, session: PlanningSession) -> bool:
        """Check if we have enough information to create a plan."""
        profile = session.profile
        return (
            profile.subject and
            profile.experience_level and
            (profile.learning_style or session.questions_asked >= 3) and
            session.questions_asked >= 2
        )
    
    async def _ask_next_question(self, session: PlanningSession) -> Dict[str, Any]:
        """Ask the next logical question."""
        profile = session.profile
        session.questions_asked += 1
        
        if not profile.experience_level:
            response = f"Great choice with {profile.subject}! What's your current experience level?\n\nAre you a complete beginner, have some experience, or would you consider yourself advanced?"
        elif not profile.learning_style and session.questions_asked <= 3:
            response = "How do you prefer to learn?\n\nDo you learn best through hands-on projects, visual content like videos, or reading and theory?"
        elif not profile.timeline and session.questions_asked <= 4:
            response = "What timeline works best for you?\n\nAre you looking for intensive learning over a few weeks, steady progress over months, or flexible learning at your own pace?"
        else:
            # We have enough, generate plan
            learning_plan = await self._generate_learning_plan(session)
            session.learning_plan = learning_plan
            session.stage = PlanningStage.COMPLETE
            
            return {
                "message": "Perfect! I have all the information I need. Let me create your personalized learning plan...",
                "metadata": {"plan_generation_started": True}
            }
        
        return {"message": response, "metadata": {"gathering_info": True}}
    
    async def _generate_learning_plan(self, session: PlanningSession) -> LearningPlan:
        """Generate complete learning plan with modules and Kanban board."""
        profile = session.profile
        
        # Generate modules based on subject
        modules = []
        kanban_tasks = []
        
        if "generative ai" in profile.subject.lower():
            modules = [
                LearningModule(
                    id="mod_1",
                    title="AI Fundamentals & Understanding",
                    description="Learn the core concepts of AI and how generative models work",
                    duration="1-2 weeks",
                    concepts=["What is AI", "Machine Learning basics", "Neural Networks", "Generative Models"],
                    objectives=["Understand AI fundamentals", "Grasp how LLMs work", "Learn about different AI types"]
                ),
                LearningModule(
                    id="mod_2", 
                    title="Working with AI Tools & APIs",
                    description="Hands-on experience with ChatGPT, Claude, and AI APIs",
                    duration="2-3 weeks",
                    concepts=["Prompt Engineering", "OpenAI API", "Claude API", "AI Integration"],
                    objectives=["Master prompt writing", "Build AI applications", "Integrate multiple AI models"]
                ),
                LearningModule(
                    id="mod_3",
                    title="Building AI Applications",
                    description="Create real-world AI-powered applications and solutions",
                    duration="3-4 weeks", 
                    concepts=["App Development", "RAG Systems", "Fine-tuning", "Deployment"],
                    objectives=["Build portfolio projects", "Deploy AI solutions", "Master advanced techniques"]
                )
            ]
            
            kanban_tasks = [
                {"id": "task_1", "title": "Complete AI Fundamentals", "status": "todo", "module": "mod_1"},
                {"id": "task_2", "title": "Practice Prompt Engineering", "status": "todo", "module": "mod_2"},
                {"id": "task_3", "title": "Build First AI App", "status": "todo", "module": "mod_2"},
                {"id": "task_4", "title": "Create Portfolio Project", "status": "todo", "module": "mod_3"},
                {"id": "task_5", "title": "Deploy AI Solution", "status": "todo", "module": "mod_3"}
            ]
        
        else:
            # Generic modules for other subjects
            modules = [
                LearningModule(
                    id="mod_1",
                    title=f"{profile.subject.title()} Fundamentals",
                    description=f"Core concepts and foundations of {profile.subject}",
                    duration="2-3 weeks",
                    concepts=["Basic concepts", "Terminology", "Core principles"],
                    objectives=[f"Understand {profile.subject} basics", "Learn key terminology", "Grasp core principles"]
                ),
                LearningModule(
                    id="mod_2",
                    title=f"Practical {profile.subject.title()}",
                    description=f"Hands-on application of {profile.subject} concepts",
                    duration="3-4 weeks",
                    concepts=["Practical applications", "Real-world examples", "Hands-on practice"],
                    objectives=["Apply knowledge practically", "Build real projects", "Gain experience"]
                ),
                LearningModule(
                    id="mod_3",
                    title=f"Advanced {profile.subject.title()}",
                    description=f"Advanced concepts and professional applications",
                    duration="4-5 weeks",
                    concepts=["Advanced techniques", "Professional practices", "Industry standards"],
                    objectives=["Master advanced concepts", "Learn industry practices", "Build expertise"]
                )
            ]
            
            kanban_tasks = [
                {"id": "task_1", "title": f"Learn {profile.subject} Basics", "status": "todo", "module": "mod_1"},
                {"id": "task_2", "title": "Practice Core Concepts", "status": "todo", "module": "mod_1"},
                {"id": "task_3", "title": "Build First Project", "status": "todo", "module": "mod_2"},
                {"id": "task_4", "title": "Apply Advanced Techniques", "status": "todo", "module": "mod_3"},
                {"id": "task_5", "title": "Complete Capstone Project", "status": "todo", "module": "mod_3"}
            ]
        
        return LearningPlan(
            plan_id=f"plan_{session.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=f"Personalized {profile.subject.title()} Learning Journey",
            description=f"A comprehensive {profile.experience_level or 'beginner'} level course in {profile.subject}",
            subject=profile.subject,
            total_duration="6-9 weeks",
            difficulty_level=profile.experience_level or "beginner",
            modules=modules,
            kanban_tasks=kanban_tasks,
            created_at=datetime.now()
        )
    
    async def _handle_complete(self, session: PlanningSession, message: str) -> Dict[str, Any]:
        """Handle conversation after plan is complete."""
        return {
            "message": "Your learning plan is ready! Redirecting you to the plan overview...",
            "metadata": {"redirect_to_plan": True}
        }
    
    def get_learning_plan(self, session_id: str) -> Optional[LearningPlan]:
        """Get the generated learning plan."""
        session = self.sessions.get(session_id)
        return session.learning_plan if session else None

# Global instance
planning_agent = ProfessionalPlanningAgent()
