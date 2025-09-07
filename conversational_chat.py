#!/usr/bin/env python3
"""
VEDYA Conversational Chat System
Handles step-by-step conversational learning flow
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Literal
from enum import Enum
from dataclasses import dataclass, asdict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from strict_env import get_required  # strict loader

# Already loaded strictly via strict_env

class ConversationStage(Enum):
    """Different stages of the conversation flow."""
    GREETING = "greeting"
    REQUIREMENTS_GATHERING = "requirements_gathering"
    PLAN_PRESENTATION = "plan_presentation"
    PLAN_APPROVAL = "plan_approval"
    TEACHING = "teaching"
    ASSESSMENT = "assessment"
    COMPLETED = "completed"

@dataclass
class UserRequirements:
    """User learning requirements collected during conversation."""
    subject: Optional[str] = None
    learning_style: Optional[str] = None
    difficulty_level: Optional[str] = None
    timeline: Optional[str] = None
    specific_goals: List[str] = None
    experience_level: Optional[str] = None
    time_commitment: Optional[str] = None
    preferred_format: Optional[str] = None
    
    def __post_init__(self):
        if self.specific_goals is None:
            self.specific_goals = []

@dataclass
class LearningModule:
    """Individual learning module structure."""
    title: str
    description: str
    duration: str
    key_concepts: List[str]
    activities: List[str]
    completed: bool = False

@dataclass
class LearningPlan:
    """Complete learning plan structure."""
    plan_id: str
    title: str
    description: str
    modules: List[LearningModule]
    total_duration: str
    difficulty: str
    learning_style: str
    approved: bool = False

@dataclass
class ConversationSession:
    """Conversation session state."""
    session_id: str
    stage: ConversationStage
    requirements: UserRequirements
    learning_plan: Optional[LearningPlan] = None
    current_module_index: int = 0
    current_lesson_step: int = 0
    conversation_history: List[Dict[str, str]] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class ConversationalChatSystem:
    """Main conversational chat system for VEDYA."""
    
    def __init__(self):
        # Initialize LLM with max_tokens from env
        try:
            max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 4000))
        except:
            max_tokens = 4000
            
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise RuntimeError("OPENAI_API_KEY missing. Set it in .env before starting the server.")
        self.llm = ChatOpenAI(
            model="o4-mini",
            temperature=1.0,  # o4-mini only supports default temperature
            api_key=openai_key,
            max_tokens=max_tokens
        )
        
        # In-memory session storage (replace with database in production)
        self.sessions: Dict[str, ConversationSession] = {}
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> ConversationSession:
        """Get existing session or create new one."""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        
        # Create new session
        new_session_id = session_id or str(uuid.uuid4())
        session = ConversationSession(
            session_id=new_session_id,
            stage=ConversationStage.GREETING,
            requirements=UserRequirements()
        )
        self.sessions[new_session_id] = session
        return session
    
    async def process_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process user message and return appropriate response."""
        session = self.get_or_create_session(session_id)
        session.updated_at = datetime.now()
        
        # Add user message to history
        session.conversation_history.append({
            "sender": "user",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Route to appropriate handler based on conversation stage
        if session.stage == ConversationStage.GREETING:
            response = await self._handle_greeting(session, message)
        elif session.stage == ConversationStage.REQUIREMENTS_GATHERING:
            response = await self._handle_requirements_gathering(session, message)
        elif session.stage == ConversationStage.PLAN_PRESENTATION:
            response = await self._handle_plan_presentation(session, message)
        elif session.stage == ConversationStage.PLAN_APPROVAL:
            response = await self._handle_plan_approval(session, message)
        elif session.stage == ConversationStage.TEACHING:
            response = await self._handle_teaching(session, message)
        elif session.stage == ConversationStage.ASSESSMENT:
            response = await self._handle_assessment(session, message)
        else:
            response = await self._handle_completed(session, message)
        
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
            "metadata": response.get("metadata", {})
        }
    
    async def _handle_greeting(self, session: ConversationSession, message: str) -> Dict[str, Any]:
        """Handle initial greeting and start requirements gathering."""
        # Extract learning topic from the very first message if provided
        message_lower = message.lower()
        
        # Check if user already mentioned what they want to learn
        learning_topics = {
            "generative ai": ["generative ai", "gen ai", "generative artificial intelligence"],
            "data science": ["data science", "data analysis", "machine learning", "ml"],
            "programming": ["programming", "coding", "code", "python", "javascript", "java"],
            "web development": ["web dev", "web development", "html", "css", "react", "frontend"],
            "artificial intelligence": ["ai", "artificial intelligence", "machine learning"]
        }
        
        detected_subject = None
        for subject, keywords in learning_topics.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_subject = subject
                break
        
        if detected_subject:
            # User already told us what they want to learn!
            session.requirements.subject = detected_subject
            session.stage = ConversationStage.REQUIREMENTS_GATHERING
            
            response = f"Excellent choice! **{detected_subject.title()}** is such an exciting field! 🚀\n\n"
            
            if "generative ai" in detected_subject.lower():
                response += """I'll help you master the world of Generative AI - from understanding how ChatGPT works to building your own AI applications!

🤔 Quick question: What's your current experience with AI or programming?
• **Complete beginner** - Never touched AI/programming before
• **Some experience** - Know basics of programming or have used AI tools
• **Experienced** - Have programming background, want to dive into AI"""
            else:
                response += f"""Let me create the perfect learning path for you!

🤔 What's your current experience level with {detected_subject}?
• **Beginner** - Just starting out
• **Intermediate** - Have some knowledge
• **Advanced** - Want to deepen expertise"""
            
            return {"message": response, "metadata": {"subject_detected": detected_subject}}
        
        # If no subject detected, ask for it
        session.stage = ConversationStage.REQUIREMENTS_GATHERING
        response = """Hello! 👋 Welcome to VEDYA, your AI learning companion! 

What would you like to learn today? Just tell me your interest:
• **Generative AI** - Build AI apps, understand LLMs
• **Programming** - Python, JavaScript, etc.
• **Data Science** - Analytics, machine learning
• **Web Development** - Build websites and apps
• **Or anything else** - Just tell me! ✨"""
        
        return {"message": response, "metadata": {"next_expected": "subject_interest"}}
    
    async def _handle_requirements_gathering(self, session: ConversationSession, message: str) -> Dict[str, Any]:
        """Handle requirements gathering conversation."""
        message_lower = message.lower()
        
        # Extract information from user's message
        self._extract_requirements_from_message(session, message)
        
        # Check if we have enough info to create a plan
        req = session.requirements
        if req.subject and req.difficulty_level and (req.learning_style or req.experience_level):
            # We have enough information! Create the plan
            session.stage = ConversationStage.PLAN_PRESENTATION
            return await self._create_learning_plan(session)
        
        # Ask for missing information in a smart, conversational way
        if not req.difficulty_level and not req.experience_level:
            if "generative ai" in (req.subject or "").lower():
                response = """Perfect! Generative AI is the future! 🤖

What's your background?
• **"I'm new to this"** - Never coded or used AI tools professionally
• **"I've used ChatGPT/AI tools"** - Familiar with AI but want to build things
• **"I can code"** - Have programming experience, want to learn AI
• **"I'm already in tech"** - Want to add AI skills to existing knowledge"""
            else:
                response = f"""Great choice! What's your experience level with {req.subject or 'this topic'}?
• **Beginner** - Starting from scratch
• **Intermediate** - Have some knowledge
• **Advanced** - Want to master it"""
        
        elif not req.learning_style:
            response = """How do you like to learn best?
• **"Hands-on projects"** - Build things while learning
• **"Step-by-step tutorials"** - Structured lessons and practice
• **"Theory first"** - Understand concepts deeply first
• **"Mixed approach"** - Combination of everything"""
        
        else:
            # Fallback - create plan with what we have
            session.stage = ConversationStage.PLAN_PRESENTATION
            return await self._create_learning_plan(session)
        
        return {"message": response, "metadata": {"gathering_requirements": True}}
    
    def _extract_requirements_from_message(self, session: ConversationSession, message: str):
        """Extract learning requirements from user message."""
        message_lower = message.lower()
        req = session.requirements
        
        # Extract experience level
        if not req.difficulty_level and not req.experience_level:
            if any(phrase in message_lower for phrase in ["new to this", "beginner", "never", "starting", "complete beginner"]):
                req.difficulty_level = "beginner"
                req.experience_level = "none"
            elif any(phrase in message_lower for phrase in ["used chatgpt", "used ai", "familiar with ai", "some experience"]):
                req.difficulty_level = "beginner"
                req.experience_level = "some"
            elif any(phrase in message_lower for phrase in ["can code", "programming", "developer", "experienced"]):
                req.difficulty_level = "intermediate"
                req.experience_level = "experienced"
            elif any(phrase in message_lower for phrase in ["already in tech", "advanced", "expert"]):
                req.difficulty_level = "advanced"
                req.experience_level = "experienced"
        
        # Extract learning style
        if not req.learning_style:
            if any(phrase in message_lower for phrase in ["hands-on", "projects", "build", "practical"]):
                req.learning_style = "hands-on"
            elif any(phrase in message_lower for phrase in ["step-by-step", "tutorials", "structured", "guided"]):
                req.learning_style = "visual"
            elif any(phrase in message_lower for phrase in ["theory", "concepts", "understand deeply", "reading"]):
                req.learning_style = "reading"
            elif any(phrase in message_lower for phrase in ["mixed", "combination", "everything"]):
                req.learning_style = "mixed"
        
        # Extract timeline
        if not req.timeline:
            if any(phrase in message_lower for phrase in ["quick", "fast", "weeks", "month"]):
                req.timeline = "4-6 weeks"
            elif any(phrase in message_lower for phrase in ["slowly", "months", "long term"]):
                req.timeline = "3-6 months"
    
    async def _fallback_requirements_gathering(self, session: ConversationSession, message: str) -> Dict[str, Any]:
        """Fallback requirements gathering if LLM parsing fails."""
        message_lower = message.lower()
        
        # Extract subject
        if not session.requirements.subject:
            subjects = {
                "programming": ["programming", "coding", "code", "python", "javascript", "java", "c++"],
                "data science": ["data science", "data", "ai", "machine learning", "artificial intelligence"],
                "web development": ["web dev", "web development", "html", "css", "react", "frontend", "backend"],
                "mathematics": ["math", "mathematics", "calculus", "algebra", "statistics"],
                "languages": ["language", "spanish", "french", "english", "german", "chinese"]
            }
            
            for subject, keywords in subjects.items():
                if any(keyword in message_lower for keyword in keywords):
                    session.requirements.subject = subject
                    break
        
        # Extract difficulty level
        if not session.requirements.difficulty_level:
            if any(word in message_lower for word in ["beginner", "new", "start", "basic"]):
                session.requirements.difficulty_level = "beginner"
            elif any(word in message_lower for word in ["intermediate", "some experience"]):
                session.requirements.difficulty_level = "intermediate"
            elif any(word in message_lower for word in ["advanced", "expert", "experienced"]):
                session.requirements.difficulty_level = "advanced"
        
        # Extract learning style
        if not session.requirements.learning_style:
            if any(word in message_lower for word in ["visual", "videos", "watch"]):
                session.requirements.learning_style = "visual"
            elif any(word in message_lower for word in ["hands-on", "practice", "projects"]):
                session.requirements.learning_style = "hands-on"
            elif any(word in message_lower for word in ["reading", "books", "text"]):
                session.requirements.learning_style = "reading"
        
        # Determine what to ask next
        if not session.requirements.subject:
            response = "That sounds interesting! Could you be more specific about the subject? For example, are you interested in programming, data science, web development, mathematics, languages, or something else? 🤔"
        elif not session.requirements.difficulty_level:
            response = f"Great choice on {session.requirements.subject}! 🎯 What's your current experience level? Are you a complete beginner, have some experience, or would you consider yourself advanced?"
        elif not session.requirements.learning_style:
            response = "Perfect! How do you prefer to learn? 📚\n\n• **Visual** (videos, diagrams, demonstrations)\n• **Hands-on** (projects, exercises, building things)\n• **Reading** (articles, books, documentation)\n• **Mixed** (combination of all styles)"
        elif not session.requirements.timeline:
            response = "Excellent! One more question - what's your ideal timeline? Are you looking to learn this over a few weeks, a couple of months, or take it more slowly over several months? ⏰"
        else:
            # Enough information gathered, create plan
            session.stage = ConversationStage.PLAN_PRESENTATION
            return await self._create_learning_plan(session)
        
        return {"message": response, "metadata": {"gathering_requirements": True}}
    
    async def _create_learning_plan(self, session: ConversationSession) -> Dict[str, Any]:
        """Create a learning plan based on gathered requirements."""
        req = session.requirements
        
        # Create learning modules based on subject
        modules = []
        if req.subject and "generative ai" in req.subject.lower():
            if req.experience_level == "none":
                modules = [
                    LearningModule(
                        title="AI Fundamentals & Tools",
                        description="Understand how AI works and master essential tools",
                        duration="1-2 weeks",
                        key_concepts=["What is AI & Machine Learning", "ChatGPT & Claude Deep Dive", "Prompt Engineering Basics", "AI Ethics & Limitations"],
                        activities=["Hands-on prompt experiments", "AI tool comparison", "Build your first AI workflow"]
                    ),
                    LearningModule(
                        title="Building with AI APIs",
                        description="Create real applications using AI APIs",
                        duration="2-3 weeks",
                        key_concepts=["OpenAI API Setup", "Building Chat Applications", "Image Generation with DALL-E", "Text Analysis & Summarization"],
                        activities=["Build a personal AI assistant", "Create an AI image generator", "Text summarization tool"]
                    ),
                    LearningModule(
                        title="Advanced AI Applications",
                        description="Master advanced techniques and build portfolio projects",
                        duration="2-4 weeks",
                        key_concepts=["Fine-tuning Models", "RAG (Retrieval Augmented Generation)", "AI Agents & Workflows", "Deployment & Scaling"],
                        activities=["Build a knowledge base chatbot", "Create an AI research assistant", "Deploy your AI app"]
                    )
                ]
            else:
                modules = [
                    LearningModule(
                        title="AI Architecture & APIs",
                        description="Deep dive into LLMs and practical implementation",
                        duration="1-2 weeks",
                        key_concepts=["Transformer Architecture", "OpenAI vs Anthropic vs Open Source", "API Integration Patterns", "Cost Optimization"],
                        activities=["API comparison project", "Cost analysis tool", "Multi-model application"]
                    ),
                    LearningModule(
                        title="Advanced AI Techniques",
                        description="Master cutting-edge AI development practices",
                        duration="2-3 weeks",
                        key_concepts=["RAG Implementation", "Vector Databases", "AI Agents & Tool Use", "Fine-tuning Strategies"],
                        activities=["Build enterprise RAG system", "Create multi-agent workflow", "Custom model fine-tuning"]
                    ),
                    LearningModule(
                        title="Production AI Systems",
                        description="Scale and deploy AI applications professionally",
                        duration="2-3 weeks",
                        key_concepts=["MLOps for LLMs", "Monitoring & Evaluation", "Security & Privacy", "Enterprise Integration"],
                        activities=["Production deployment", "Monitoring dashboard", "Security audit"]
                    )
                ]
        else:
            # Generic modules for other subjects
            subject_name = req.subject or "Your Topic"
            modules = [
                LearningModule(
                    title=f"{subject_name} Foundations",
                    description=f"Master the core concepts of {subject_name.lower()}",
                    duration="2-3 weeks",
                    key_concepts=["Fundamentals", "Key Principles", "Essential Tools", "Best Practices"],
                    activities=["Guided tutorials", "Practice exercises", "Real-world examples"]
                ),
                LearningModule(
                    title=f"Practical {subject_name}",
                    description=f"Apply {subject_name.lower()} skills to real projects",
                    duration="3-4 weeks",
                    key_concepts=["Advanced Concepts", "Project Work", "Problem Solving", "Industry Applications"],
                    activities=["Hands-on projects", "Case studies", "Portfolio building"]
                ),
                LearningModule(
                    title=f"Mastering {subject_name}",
                    description=f"Become an expert in {subject_name.lower()}",
                    duration="2-4 weeks",
                    key_concepts=["Expert Techniques", "Optimization", "Advanced Applications", "Career Development"],
                    activities=["Capstone project", "Community engagement", "Professional development"]
                )
            ]
        
        # Create the learning plan
        plan = LearningPlan(
            plan_id=f"plan_{session.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=f"Master {req.subject or 'Your Chosen Topic'}",
            description=f"A comprehensive {req.difficulty_level or 'personalized'} learning journey",
            modules=modules,
            total_duration=req.timeline or "5-10 weeks",
            difficulty=req.difficulty_level or "beginner",
            learning_style=req.learning_style or "hands-on"
        )
        
        session.learning_plan = plan
        session.stage = ConversationStage.PLAN_APPROVAL
        
        # Format the plan presentation
        response = f"""� **Your Personalized {req.subject or 'Learning'} Plan**

Perfect! I've created a learning path that matches your background and goals:

"""
        
        for i, module in enumerate(modules, 1):
            response += f"**Week {i}: {module.title}** ⏱️ {module.duration}\n"
            response += f"└─ {module.description}\n"
            response += f"└─ 🎯 Key Skills: {', '.join(module.key_concepts[:2])}...\n\n"
        
        if "generative ai" in (req.subject or "").lower():
            response += """🚀 **By the end, you'll be able to:**
• Build AI-powered applications from scratch
• Integrate multiple AI models and APIs
• Create intelligent chatbots and assistants
• Deploy AI solutions to production

"""
        
        response += """💡 **Ready to start?** Type **"start learning"** to begin Module 1!

Or ask me to **"modify"** anything about this plan. ✨"""
        
        return {"message": response, "metadata": {"plan_created": True, "awaiting_approval": True}}
    
    async def _handle_plan_presentation(self, session: ConversationSession, message: str) -> Dict[str, Any]:
        """Handle plan presentation stage."""
        # This stage immediately transitions to approval, so redirect
        return await self._handle_plan_approval(session, message)
    
    async def _handle_plan_approval(self, session: ConversationSession, message: str) -> Dict[str, Any]:
        """Handle plan approval or modification requests."""
        message_lower = message.lower()
        
        # Check for approval
        if any(word in message_lower for word in ["approve", "start", "begin", "yes", "looks good", "perfect"]):
            session.learning_plan.approved = True
            session.stage = ConversationStage.TEACHING
            session.current_module_index = 0
            session.current_lesson_step = 0
            
            first_module = session.learning_plan.modules[0]
            response = f"""🎉 **Excellent! Let's Start Learning!**

Welcome to **Module 1: {first_module.title}**

{first_module.description}

**🎯 What we'll cover in this module:**
"""
            for concept in first_module.key_concepts:
                response += f"• {concept}\n"
            
            response += f"""
**⏱️ Estimated time**: {first_module.duration}

**🚀 Let's begin with the first concept: {first_module.key_concepts[0]}**

{self._get_first_lesson_content(session)}

Ready to dive in? Ask me any questions or type **"continue"** when you're ready for the next part! 💪"""
            
            return {"message": response, "metadata": {"teaching_started": True, "current_module": 0}}
        
        # Check for modification requests
        elif any(word in message_lower for word in ["change", "modify", "different", "adjust"]):
            response = """🔄 **I'd be happy to modify your learning plan!**

What would you like to change? For example:
• Make it **faster** or **slower** paced?
• Focus more on **hands-on projects** or **theory**?
• **Add** or **remove** specific topics?
• Change the **difficulty level**?
• Adjust the **learning style** approach?

Just let me know what you'd prefer, and I'll update your plan accordingly! ✨"""
            
            return {"message": response, "metadata": {"modification_requested": True}}
        
        # Default response if unclear
        else:
            response = """I want to make sure this learning plan is perfect for you! 

You can:
• Say **"approve"** or **"start"** to begin learning with this plan
• Request **"changes"** and tell me what you'd like modified
• Ask any **questions** about the modules or content

What would you like to do? 🤔"""
            
            return {"message": response, "metadata": {"awaiting_clear_decision": True}}
    
    def _get_first_lesson_content(self, session: ConversationSession) -> str:
        """Get the first lesson content for the current module."""
        if not session.learning_plan or not session.learning_plan.modules:
            return "Let's start with the basics!"
        
        current_module = session.learning_plan.modules[session.current_module_index]
        first_concept = current_module.key_concepts[0] if current_module.key_concepts else "the fundamentals"
        
        # Generate lesson content based on subject and concept
        subject = session.requirements.subject or "this topic"
        
        if "programming" in subject.lower():
            return f"""**Understanding {first_concept}**

In programming, {first_concept.lower()} are the building blocks of every program. Think of them as labeled boxes that store information your program needs to remember.

**🔍 Simple Example:**
```
name = "Alice"
age = 25
is_student = True
```

Here we have three {first_concept.lower()}:
• `name` stores text (a string)
• `age` stores a number (an integer)  
• `is_student` stores true/false (a boolean)

**💡 Key Point**: Choose meaningful names that describe what the {first_concept.lower()} represents!"""
        
        else:
            return f"""**Understanding {first_concept}**

{first_concept} form the foundation of {subject}. Let's start by understanding what {first_concept.lower()} really means and why it's important.

**🔍 Key Concept:**
{first_concept} help us organize and understand the core ideas we need to master.

**💡 Remember**: Every expert started with these basics, so take your time to really understand each concept!"""
    
    async def _handle_teaching(self, session: ConversationSession, message: str) -> Dict[str, Any]:
        """Handle the teaching conversation - step by step instruction."""
        message_lower = message.lower()
        
        if not session.learning_plan or not session.learning_plan.modules:
            return {"message": "Something went wrong with your learning plan. Let's restart!", "metadata": {"error": True}}
        
        current_module = session.learning_plan.modules[session.current_module_index]
        
        # Handle continue/next requests
        if any(word in message_lower for word in ["continue", "next", "proceed", "move on"]):
            return await self._advance_lesson(session)
        
        # Handle questions about current content
        elif any(word in message_lower for word in ["what", "how", "why", "explain", "help", "?"]):
            return await self._answer_teaching_question(session, message)
        
        # Handle completion/understanding confirmation
        elif any(word in message_lower for word in ["got it", "understand", "clear", "makes sense", "ready"]):
            response = f"""Great! 🎉 I'm glad that makes sense.

Let's practice what we just learned about {current_module.key_concepts[session.current_lesson_step] if session.current_lesson_step < len(current_module.key_concepts) else 'this concept'}.

**🎯 Quick Practice:**
{self._get_practice_exercise(session)}

Try this out and let me know how it goes, or type **"continue"** when you're ready for the next concept!"""
            
            return {"message": response, "metadata": {"practice_provided": True}}
        
        # Default encouraging response
        else:
            response = f"""I'm here to help you master **{current_module.title}**! 

You can:
• Ask **questions** about anything that's unclear
• Say **"continue"** when you're ready for the next part
• Say **"got it"** if you understand and want to practice
• Type **"help"** for more guidance

What would you like to do next? 🤓"""
            
            return {"message": response, "metadata": {"teaching_guidance": True}}
    
    async def _advance_lesson(self, session: ConversationSession) -> Dict[str, Any]:
        """Advance to the next lesson step."""
        current_module = session.learning_plan.modules[session.current_module_index]
        
        # Move to next concept in current module
        session.current_lesson_step += 1
        
        # Check if module is completed
        if session.current_lesson_step >= len(current_module.key_concepts):
            # Module completed
            current_module.completed = True
            
            # Check if all modules are completed
            if session.current_module_index >= len(session.learning_plan.modules) - 1:
                # All modules completed
                session.stage = ConversationStage.COMPLETED
                return await self._handle_course_completion(session)
            else:
                # Move to next module
                session.current_module_index += 1
                session.current_lesson_step = 0
                next_module = session.learning_plan.modules[session.current_module_index]
                
                response = f"""🎉 **Module {session.current_module_index} Complete!**

Congratulations! You've mastered **{current_module.title}**. 

**🚀 Ready for Module {session.current_module_index + 1}: {next_module.title}**

{next_module.description}

**🎯 In this module we'll cover:**
"""
                for concept in next_module.key_concepts:
                    response += f"• {concept}\n"
                
                response += f"""
**⏱️ Estimated time**: {next_module.duration}

Let's start with **{next_module.key_concepts[0]}**:

{self._get_lesson_content(session, next_module.key_concepts[0])}

Ready to continue? Ask questions or type **"continue"** for the next part! 💪"""
                
                return {"message": response, "metadata": {"module_completed": True, "new_module_started": True}}
        
        # Continue with next concept in current module
        next_concept = current_module.key_concepts[session.current_lesson_step]
        
        response = f"""✨ **Moving on to: {next_concept}**

{self._get_lesson_content(session, next_concept)}

Any questions about {next_concept}, or shall we **"continue"** to practice this concept? 🤔"""
        
        return {"message": response, "metadata": {"concept_advanced": True}}
    
    def _get_lesson_content(self, session: ConversationSession, concept: str) -> str:
        """Generate lesson content for a specific concept."""
        subject = session.requirements.subject or "this topic"
        
        # Simple content generation based on concept and subject
        if "programming" in subject.lower():
            content_map = {
                "Variables": "Variables are like labeled containers that store data. You can put information in them and retrieve it later.",
                "Data Types": "Data types define what kind of information you can store: numbers, text, true/false values, lists, etc.",
                "Control Flow": "Control flow determines the order in which your program executes. Think of it as giving directions to your computer.",
                "Functions": "Functions are reusable blocks of code that perform specific tasks. They help organize your code and avoid repetition.",
                "Arrays": "Arrays are ordered lists that can store multiple items of the same type. Like a shopping list or a row of mailboxes.",
                "Lists": "Lists are flexible containers that can hold multiple items, which can be of different types.",
                "Dictionaries": "Dictionaries store information in key-value pairs, like a real dictionary where words (keys) have definitions (values).",
                "Basic Algorithms": "Algorithms are step-by-step instructions for solving problems, like a recipe for cooking."
            }
        else:
            content_map = {
                concept: f"{concept} are fundamental building blocks in {subject}. Understanding {concept.lower()} will help you grasp more advanced topics later."
            }
        
        return content_map.get(concept, f"Let's explore {concept} in the context of {subject}. This concept will help you understand how everything connects together.")
    
    def _get_practice_exercise(self, session: ConversationSession) -> str:
        """Generate a practice exercise for the current concept."""
        if not session.learning_plan:
            return "Try applying what you just learned in a simple example!"
        
        current_module = session.learning_plan.modules[session.current_module_index]
        current_concept = current_module.key_concepts[session.current_lesson_step] if session.current_lesson_step < len(current_module.key_concepts) else "this concept"
        subject = session.requirements.subject or "this topic"
        
        if "programming" in subject.lower():
            exercises = {
                "Variables": "Create three variables: one for your name, one for your age, and one for your favorite color.",
                "Data Types": "Identify the data type for these values: 42, 'Hello', True, [1,2,3]",
                "Control Flow": "Write a simple if-statement that checks if a number is positive or negative.",
                "Functions": "Create a function that takes your name as input and returns a greeting message."
            }
            return exercises.get(current_concept, f"Try creating a simple example using {current_concept.lower()}.")
        
        return f"Think of a real-world example where {current_concept.lower()} would be useful in {subject}."
    
    async def _answer_teaching_question(self, session: ConversationSession, question: str) -> Dict[str, Any]:
        """Answer a question during teaching using LLM."""
        if not session.learning_plan:
            return {"message": "I'm here to help! What would you like to know?", "metadata": {"generic_help": True}}
        
        current_module = session.learning_plan.modules[session.current_module_index]
        current_concept = current_module.key_concepts[session.current_lesson_step] if session.current_lesson_step < len(current_module.key_concepts) else "current topic"
        
        system_prompt = f"""You are VEDYA, a patient and encouraging AI tutor. 

Current context:
- Student is learning: {session.requirements.subject}
- Current module: {current_module.title}
- Current concept: {current_concept}
- Learning style: {session.requirements.learning_style}
- Level: {session.requirements.difficulty_level}

Answer the student's question in a helpful, encouraging way. Keep explanations clear and appropriate for their level. Include examples when helpful.

Respond naturally as a teacher would."""
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=question)
            ])
            
            ai_response = response.content + "\n\nDoes that help clarify things? Feel free to ask more questions or say **\"continue\"** when you're ready to move on! 😊"
            
            return {"message": ai_response, "metadata": {"question_answered": True}}
            
        except Exception as e:
            # Fallback response if LLM fails
            return {
                "message": f"That's a great question about {current_concept}! Let me help explain that in simpler terms. The key thing to remember is that {current_concept.lower()} are designed to make things easier for you. Would you like me to show you a specific example?",
                "metadata": {"fallback_answer": True}
            }
    
    async def _handle_assessment(self, session: ConversationSession, message: str) -> Dict[str, Any]:
        """Handle assessment stage."""
        # For now, redirect to completion
        return await self._handle_course_completion(session)
    
    async def _handle_course_completion(self, session: ConversationSession) -> Dict[str, Any]:
        """Handle course completion."""
        session.stage = ConversationStage.COMPLETED
        
        response = f"""🎓 **Congratulations! You've Completed Your Learning Journey!**

You've successfully mastered **{session.requirements.subject}** through:
"""
        
        for i, module in enumerate(session.learning_plan.modules, 1):
            status = "✅" if module.completed else "📝"
            response += f"{status} **Module {i}**: {module.title}\n"
        
        response += f"""
**🏆 Your Achievements:**
• Completed {len([m for m in session.learning_plan.modules if m.completed])} modules
• Mastered {session.requirements.difficulty_level} level {session.requirements.subject}
• Applied {session.requirements.learning_style} learning style effectively

**🚀 What's Next?**
• Start a new learning journey in a different subject
• Deep dive into advanced topics
• Apply your knowledge to real projects
• Share your learning experience with others

Ready to learn something new? Just tell me what interests you next! ✨

Thank you for learning with VEDYA! 🎉"""
        
        return {"message": response, "metadata": {"course_completed": True}}
    
    async def _handle_completed(self, session: ConversationSession, message: str) -> Dict[str, Any]:
        """Handle messages after course completion."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["new", "start", "another", "different", "learn"]):
            # Start a new learning journey
            new_session = ConversationSession(
                session_id=str(uuid.uuid4()),
                stage=ConversationStage.GREETING,
                requirements=UserRequirements()
            )
            self.sessions[new_session.session_id] = new_session
            
            return {
                "response": "Excellent! I'm excited to help you learn something new! 🎉\n\nWhat subject or skill would you like to explore this time?",
                "session_id": new_session.session_id,
                "stage": new_session.stage.value,
                "metadata": {"new_journey_started": True}
            }
        
        return {"message": "I'm here whenever you're ready to start a new learning adventure! What would you like to explore next? 🌟", "metadata": {"awaiting_new_topic": True}}

# Global instance for use in API
conversational_chat = ConversationalChatSystem()
