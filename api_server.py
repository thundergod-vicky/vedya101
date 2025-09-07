#!/usr/bin/env python3
"""
VEDYA API Server
FastAPI server to serve the LangGraph agent system to the frontend
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import os
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

# Import our agent system
from vedya_agents import create_vedya_langgraph_system
from email_service import email_service
from user_service import UserService
from ai_planning_agent import ai_planning_agent

# Helper function to ensure correct temperature for models
def get_safe_temperature(model_name, default_temp=0.7):
    """Returns a safe temperature value for the given model.
    Some models like o4-mini only support temperature=1.0"""
    if model_name == "o4-mini":
        return 1.0
    return default_temp

app = FastAPI(
    title="VEDYA API",
    description="AI-Powered Education Platform API",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent system instance
agent_system = None
user_service = None
user_sessions = {}  # Simple in-memory session storage

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str

@app.on_event("startup")
async def startup_event():
    """Initialize the agent system on startup."""
    global agent_system, user_service
    print("🚀 Starting VEDYA Agent System...")
    try:
        agent_system = create_vedya_langgraph_system()
        user_service = UserService()
        print("✅ VEDYA Agent System initialized successfully!")
        print("✅ User Service initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        raise

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "VEDYA API is running",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "agent_system": "initialized" if agent_system else "not initialized",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Main chat endpoint for professional planning conversation."""
    try:
        # Use the AI-powered planning agent
        result = await ai_planning_agent.process_message(
            message=chat_message.message,
            session_id=chat_message.session_id
        )
        
        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        # Fallback response
        session_id = chat_message.session_id or str(uuid.uuid4())
        return ChatResponse(
            response="I'm here to help you create a personalized learning plan. What would you like to learn?",
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )

@app.post("/chat/stream")
async def chat_stream_endpoint(chat_message: ChatMessage):
    """Streaming chat endpoint for real-time responses."""
    from streaming_utils import stream_text_chunks
    
    async def generate_response():
        try:
            # Use the AI planning agent system
            result = await ai_planning_agent.process_message(
                message=chat_message.message,
                session_id=chat_message.session_id
            )
            
            response_text = result["response"]
            session_id = result["session_id"]
            metadata = result.get("metadata", {})
            
            # Send initial metadata
            yield f"data: {json.dumps({'type': 'metadata', 'session_id': session_id, 'timestamp': datetime.now().isoformat()})}\n\n"
            
            # Stream the response character by character for a more natural feel
            accumulated = ""
            async for char in stream_text_chunks(response_text, character_by_character=True):
                accumulated += char
                yield f"data: {json.dumps({'type': 'content', 'content': char, 'accumulated': accumulated})}\n\n"
            
            # Send final metadata with action buttons
            if metadata:
                yield f"data: {json.dumps({'type': 'final_metadata', 'metadata': metadata})}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            print(f"Error in streaming chat endpoint: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': 'Something went wrong. Please try again.'})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/learning-plan")
async def create_learning_plan(chat_message: ChatMessage):
    """Create a personalized learning plan."""
    try:
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # Process with AI planning agent
        result = await ai_planning_agent.process_message(
            message=chat_message.message,
            session_id=session_id
        )
        
        return {
            "success": True,
            "response": result["response"],
            "session_id": result["session_id"],
            "plan_ready": result.get("plan_ready", False)
        }
        
    except Exception as e:
        print(f"Error creating learning plan: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": "I'm having trouble creating your learning plan. Please try again."
        }

@app.get("/learning-plan/{session_id}")
async def get_learning_plan(session_id: str):
    """Get the generated learning plan for a session."""
    try:
        plan_data = ai_planning_agent.get_learning_plan(session_id)
        
        if not plan_data:
            raise HTTPException(status_code=404, detail="Learning plan not found for this session")
        
        return {
            "success": True,
            "data": plan_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving learning plan: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Email Notification Models
class NotificationRequest(BaseModel):
    email: str
    name: str
    notification_type: str
    data: Optional[Dict[str, Any]] = None

class WelcomeEmailRequest(BaseModel):
    email: str
    name: str

class ProgressMilestoneRequest(BaseModel):
    email: str
    name: str
    milestone: str
    completion_percentage: float

class LearningPlanReadyRequest(BaseModel):
    email: str
    name: str
    plan_title: str
    plan_summary: str

# Email Notification Endpoints
@app.post("/notifications/welcome")
async def send_welcome_notification(request: WelcomeEmailRequest):
    """Send welcome email to new users."""
    try:
        success = await email_service.send_welcome_email(request.email, request.name)
        return {
            "success": success,
            "message": "Welcome email sent successfully" if success else "Failed to send welcome email",
            "email": request.email,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send welcome email: {str(e)}")

@app.post("/notifications/learning-plan-ready")
async def send_learning_plan_ready_notification(request: LearningPlanReadyRequest):
    """Send learning plan ready notification."""
    try:
        success = await email_service.send_learning_plan_ready(
            request.email, request.name, request.plan_title, request.plan_summary
        )
        return {
            "success": success,
            "message": "Learning plan notification sent successfully" if success else "Failed to send learning plan notification",
            "email": request.email,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error sending learning plan notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send learning plan notification: {str(e)}")

@app.post("/notifications/progress-milestone")
async def send_progress_milestone_notification(request: ProgressMilestoneRequest):
    """Send progress milestone notification."""
    try:
        success = await email_service.send_progress_milestone(
            request.email, request.name, request.milestone, request.completion_percentage
        )
        return {
            "success": success,
            "message": "Progress milestone notification sent successfully" if success else "Failed to send progress milestone notification",
            "email": request.email,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error sending progress milestone notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send progress milestone notification: {str(e)}")

@app.post("/notifications/daily-summary")
async def send_daily_summary_notification(request: NotificationRequest):
    """Send daily summary notification."""
    try:
        if request.notification_type != "daily_summary":
            raise HTTPException(status_code=400, detail="Invalid notification type")
        
        summary_data = request.data or {}
        success = await email_service.send_daily_summary(request.email, request.name, summary_data)
        return {
            "success": success,
            "message": "Daily summary sent successfully" if success else "Failed to send daily summary",
            "email": request.email,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error sending daily summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send daily summary: {str(e)}")

@app.post("/notifications/weekly-report")
async def send_weekly_report_notification(request: NotificationRequest):
    """Send weekly report notification."""
    try:
        if request.notification_type != "weekly_report":
            raise HTTPException(status_code=400, detail="Invalid notification type")
        
        weekly_data = request.data or {}
        success = await email_service.send_weekly_report(request.email, request.name, weekly_data)
        return {
            "success": success,
            "message": "Weekly report sent successfully" if success else "Failed to send weekly report",
            "email": request.email,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error sending weekly report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send weekly report: {str(e)}")

@app.get("/notifications/status")
async def get_notification_status():
    """Get current notification service status."""
    return {
        "notifications_enabled": email_service.notifications_enabled,
        "daily_summary_enabled": email_service.daily_summary_enabled,
        "progress_alerts_enabled": email_service.progress_alerts_enabled,
        "weekly_report_enabled": email_service.weekly_report_enabled,
        "smtp_configured": bool(email_service.smtp_username and email_service.smtp_password),
        "timestamp": datetime.now().isoformat()
    }

# === USER MANAGEMENT ENDPOINTS ===
# These endpoints handle Clerk integration and user database management

class UserRegistrationData(BaseModel):
    clerk_user_id: str
    email: str
    name: Optional[str] = None

class UserResponse(BaseModel):
    success: bool
    user_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

@app.post("/users/register", response_model=UserResponse)
async def register_user_from_clerk(user_data: UserRegistrationData):
    """
    Register a new user from Clerk authentication.
    This endpoint should be called from your frontend after Clerk signup.
    """
    if not user_service:
        raise HTTPException(status_code=500, detail="User service not initialized")
    
    try:
        result = await user_service.create_user_from_clerk(
            clerk_user_id=user_data.clerk_user_id,
            email=user_data.email,
            name=user_data.name
        )
        
        return UserResponse(**result)
        
    except Exception as e:
        print(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")

@app.get("/users/clerk/{clerk_user_id}")
async def get_user_by_clerk_id(clerk_user_id: str):
    """Get user information by Clerk user ID."""
    if not user_service:
        raise HTTPException(status_code=500, detail="User service not initialized")
    
    try:
        user = await user_service.get_user_by_clerk_id(clerk_user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove sensitive fields
        safe_user = {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "preferences": user["preferences"],
            "created_at": user["created_at"].isoformat() if user["created_at"] else None,
            "updated_at": user["updated_at"].isoformat() if user["updated_at"] else None
        }
        
        return {
            "success": True,
            "user": safe_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

@app.get("/users/email/{email}")
async def get_user_by_email(email: str):
    """Get user information by email address."""
    if not user_service:
        raise HTTPException(status_code=500, detail="User service not initialized")
    
    try:
        user = await user_service.get_user_by_email(email)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove sensitive fields
        safe_user = {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "preferences": user["preferences"],
            "created_at": user["created_at"].isoformat() if user["created_at"] else None,
            "updated_at": user["updated_at"].isoformat() if user["updated_at"] else None
        }
        
        return {
            "success": True,
            "user": safe_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

class UserPreferencesUpdate(BaseModel):
    preferences: Dict[str, Any]

@app.patch("/users/{user_id}/preferences")
async def update_user_preferences(user_id: str, update_data: UserPreferencesUpdate):
    """Update user preferences."""
    if not user_service:
        raise HTTPException(status_code=500, detail="User service not initialized")
    
    try:
        success = await user_service.update_user_preferences(user_id, update_data.preferences)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update preferences")
        
        return {
            "success": True,
            "message": "Preferences updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")

# === USER NOTIFICATION ENDPOINTS ===
# These endpoints send notifications to specific users by user ID

class UserNotificationData(BaseModel):
    user_id: str
    data: Dict[str, Any]

@app.post("/users/{user_id}/notifications/learning-plan")
async def send_user_learning_plan_notification(user_id: str, notification_data: Dict[str, Any]):
    """Send learning plan notification to a specific user."""
    if not user_service:
        raise HTTPException(status_code=500, detail="User service not initialized")
    
    try:
        success = await user_service.send_learning_plan_notification(user_id, notification_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to send notification")
        
        return {
            "success": True,
            "message": "Learning plan notification sent successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending learning plan notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

@app.post("/users/{user_id}/notifications/milestone")
async def send_user_milestone_notification(user_id: str, notification_data: Dict[str, Any]):
    """Send milestone notification to a specific user."""
    if not user_service:
        raise HTTPException(status_code=500, detail="User service not initialized")
    
    try:
        success = await user_service.send_progress_milestone_notification(user_id, notification_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to send notification")
        
        return {
            "success": True,
            "message": "Milestone notification sent successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending milestone notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

@app.post("/users/{user_id}/notifications/daily-summary")
async def send_user_daily_summary(user_id: str, notification_data: Dict[str, Any]):
    """Send daily summary to a specific user."""
    if not user_service:
        raise HTTPException(status_code=500, detail="User service not initialized")
    
    try:
        success = await user_service.send_daily_summary_notification(user_id, notification_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to send notification")
        
        return {
            "success": True,
            "message": "Daily summary sent successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending daily summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

@app.post("/users/{user_id}/notifications/weekly-report")
async def send_user_weekly_report(user_id: str, notification_data: Dict[str, Any]):
    """Send weekly report to a specific user."""
    if not user_service:
        raise HTTPException(status_code=500, detail="User service not initialized")
    
    try:
        success = await user_service.send_weekly_report_notification(user_id, notification_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to send notification")
        
        return {
            "success": True,
            "message": "Weekly report sent successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending weekly report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

# Learning Plans endpoints
@app.get("/learning-plans")
async def get_learning_plans(authorization: str = Header(None)):
    """Get all learning plans for a user."""
    try:
        # For now, return mock data with realistic new user progress
        mock_plans = [
            {
                "id": "plan_1",
                "title": "Introduction to Artificial Intelligence",
                "subject": "Computer Science",
                "description": "Comprehensive introduction to AI concepts, machine learning, and neural networks",
                "totalDuration": "6 weeks",
                "difficulty": "Intermediate",
                "learningStyle": "Visual + Hands-on",
                "overallProgress": 0,  # New user should start at 0%
                "createdAt": "2024-01-15",
                "modules": [
                    {
                        "id": "module_1",
                        "title": "AI Fundamentals",
                        "description": "Basic concepts and history of AI",
                        "duration": "1 week",
                        "status": "not_started",  # Should start as not_started
                        "progress": 0,
                        "tasks": [
                            {
                                "id": "task_1",
                                "title": "What is AI?",
                                "description": "Learn the definition and types of AI",
                                "status": "todo",  # All tasks should be todo initially
                                "module": "AI Fundamentals",
                                "priority": "high",
                                "estimatedTime": "30 mins"
                            },
                            {
                                "id": "task_2",
                                "title": "History of AI",
                                "description": "Timeline of AI development",
                                "status": "todo",
                                "module": "AI Fundamentals",
                                "priority": "medium",
                                "estimatedTime": "45 mins"
                            }
                        ]
                    },
                    {
                        "id": "module_2",
                        "title": "Machine Learning Basics",
                        "description": "Introduction to ML algorithms and concepts",
                        "duration": "2 weeks",
                        "status": "not_started",
                        "progress": 0,
                        "tasks": [
                            {
                                "id": "task_3",
                                "title": "Supervised Learning",
                                "description": "Learn about classification and regression",
                                "status": "todo",
                                "module": "Machine Learning Basics",
                                "priority": "high",
                                "estimatedTime": "1 hour"
                            },
                            {
                                "id": "task_4",
                                "title": "Unsupervised Learning",
                                "description": "Clustering and dimensionality reduction",
                                "status": "todo",
                                "module": "Machine Learning Basics",
                                "priority": "high",
                                "estimatedTime": "1.5 hours"
                            },
                            {
                                "id": "task_5",
                                "title": "Model Evaluation",
                                "description": "Metrics and validation techniques",
                                "status": "todo",
                                "module": "Machine Learning Basics",
                                "priority": "medium",
                                "estimatedTime": "45 mins"
                            }
                        ]
                    },
                    {
                        "id": "module_3",
                        "title": "Neural Networks",
                        "description": "Deep learning and neural network architectures",
                        "duration": "2 weeks",
                        "status": "not_started",
                        "progress": 0,
                        "tasks": [
                            {
                                "id": "task_6",
                                "title": "Perceptrons",
                                "description": "Single layer neural networks",
                                "status": "todo",
                                "module": "Neural Networks",
                                "priority": "high",
                                "estimatedTime": "1 hour"
                            },
                            {
                                "id": "task_7",
                                "title": "Backpropagation",
                                "description": "Learning algorithm for neural networks",
                                "status": "todo",
                                "module": "Neural Networks",
                                "priority": "high",
                                "estimatedTime": "2 hours"
                            }
                        ]
                    }
                ]
            }
        ]
        
        return {
            "success": True,
            "plans": mock_plans
        }

    except Exception as e:
        print(f"Error getting learning plans: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get learning plans: {str(e)}")

@app.post("/teaching/start")
async def start_teaching_session(request: dict):
    """Start a new teaching session for a specific plan/module."""
    try:
        plan_id = request.get('plan_id')
        module_id = request.get('module_id')
        
        # Get learning plan data (this would come from database in production)
        # For now, using the mock plan structure
        learning_plan = {
            "id": plan_id,
            "subject": "Artificial Intelligence",
            "learning_style": "Visual + Hands-on",
            "difficulty": "Intermediate",
            "description": "Comprehensive introduction to AI concepts, machine learning, and neural networks",
            "modules": [
                {
                    "id": "module_1",
                    "title": "AI Fundamentals",
                    "description": "Basic concepts and history of AI"
                }
            ]
        }
        
        # Use the TeachingAssistant agent from our agent system
        if agent_system and hasattr(agent_system, 'agents') and 'teaching_assistant' in agent_system.agents:
            teaching_assistant = agent_system.agents['teaching_assistant']
            result = await teaching_assistant.start_teaching_session(learning_plan, {"user_id": "test_user"})
            return result
        else:
            # Fallback if agent system not available
            return {
                "success": True,
                "initial_message": f"Welcome to your {learning_plan['subject']} learning session! I'm your AI instructor, and I'm excited to guide you through the fundamentals. Let's start by exploring what artificial intelligence really means and how it shapes our world today.",
                "current_concept": "ai_fundamentals",
                "plan_data": learning_plan,
                "session_context": {
                    "subject": learning_plan['subject'],
                    "module": "AI Fundamentals",
                    "learning_style": learning_plan['learning_style'],
                    "difficulty": learning_plan['difficulty']
                }
            }
        
    except Exception as e:
        print(f"Error starting teaching session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start teaching session: {str(e)}")

@app.post("/teaching/chat")
async def teaching_chat(request: dict):
    """Handle teaching chat messages with streaming support."""
    try:
        message = request.get('message', '')
        plan_id = request.get('plan_id')
        module_id = request.get('module_id')
        current_concept = request.get('current_concept', '')
        stream = request.get('stream', False)
        
        print(f"📝 Teaching chat request: '{message}' | Stream: {stream}")
        
        # Build session context
        session_context = {
            "subject": "Artificial Intelligence",
            "module": "AI Fundamentals", 
            "learning_style": "Visual + Hands-on",
            "difficulty": "Intermediate",
            "current_concept": current_concept
        }
        
        # Use the TeachingAssistant agent
        if agent_system and hasattr(agent_system, 'agents') and 'teaching_assistant' in agent_system.agents:
            teaching_assistant = agent_system.agents['teaching_assistant']
            
            if stream:
                # Return streaming response
                async def generate_stream():
                    async for chunk in teaching_assistant.stream_teaching_chat(message, session_context):
                        yield f"data: {json.dumps(chunk)}\n\n"
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
                return StreamingResponse(
                    generate_stream(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "*",
                    }
                )
            else:
                # For non-streaming response, process the message
                response = await teaching_assistant.handle_teaching_chat(message, session_context)
                
                # Check if visual generation is appropriate based on message content
                message_lower = message.lower()
                should_generate_visual = any(word in message_lower for word in 
                    ['visual', 'show', 'diagram', 'picture', 'graph', 'chart', 'illustration']) or \
                    any(word in response.lower() for word in 
                    ['diagram', 'visual', 'chart', 'graph', 'illustration', 'picture', 'shown', 'visualize'])
                
                print(f"✅ Teaching response generated | Visual needed: {should_generate_visual}")
                
                return {
                    "success": True,
                    "response": response,
                    "current_concept": current_concept,
                    "should_generate_visual": should_generate_visual,
                    "visual_concept": current_concept,
                    "visual_type": "concept_illustration"
                }
        else:
            print("❌ Teaching assistant agent not available")
            raise HTTPException(status_code=500, detail="Teaching assistant agent not available")
            
    except Exception as e:
        print(f"Error in teaching chat: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process teaching chat: {str(e)}")

@app.post("/teaching/generate-diagram")
async def generate_teaching_diagram(request: dict):
    """Generate supervised educational diagrams."""
    try:
        concept = request.get('concept', '')
        diagram_type = request.get('type', 'concept_illustration')
        subject = request.get('subject', 'General')
        supervised = request.get('supervised', True)
        
        print(f"📊 Diagram generation request: {concept} ({diagram_type}) - {subject}")
        
        # Use ImageGenerationAssistant with supervision if available
        if agent_system and hasattr(agent_system, 'agents') and 'image_generation' in agent_system.agents:
            image_agent = agent_system.agents['image_generation']
            
            # Create supervisor context for validation
            supervisor_context = {
                "teaching_session": True,
                "requesting_agent": "TeachingAssistant",
                "current_subject": subject,
                "session_id": f"session_{concept}",
                "student_context": {"subject": subject}
            }
            
            result = await image_agent.generate_educational_visual(
                concept=concept,
                subject=subject,
                visual_type=diagram_type,
                supervisor_context=supervisor_context
            )
            
            if result.get('success'):
                print(f"✅ Generated diagram URL: {result['visual_url']}")
                return {
                    "success": True,
                    "diagram_url": result['visual_url'],
                    "diagram_type": result['visual_type'],
                    "concept": result['concept'],
                    "educational_context": result.get('educational_context', ''),
                    "supervised": True
                }
            else:
                print(f"❌ Image generation failed: {result.get('error', 'Unknown error')}")
                # Fall through to placeholder generation
        else:
            print("⚠️ Image generation agent not available, using placeholder")
        
        # Fallback to enhanced placeholder generation
        concept_clean = concept.replace(' ', '+').replace('_', '+')
        subject_clean = subject.replace(' ', '+')
        
        # Subject-specific color schemes
        subject_colors = {
            'artificial intelligence': '4F46E5/FFFFFF',
            'computer science': '059669/FFFFFF', 
            'mathematics': 'DC2626/FFFFFF',
            'physics': '7C3AED/FFFFFF',
            'chemistry': 'EA580C/FFFFFF',
            'biology': '16A34A/FFFFFF'
        }
        
        color = subject_colors.get(subject.lower(), '6366F1/FFFFFF')
        
        # Enhanced diagram generation based on type
        if diagram_type == "concept_illustration":
            diagram_url = f"https://via.placeholder.com/800x600/{color}?text={concept_clean}%0A%0A{subject_clean}%0A%0AKey+Concepts+%26+Applications"
        elif diagram_type == "flowchart":
            diagram_url = f"https://via.placeholder.com/800x600/{color}?text={concept_clean}+Process%0A%0AStep+1+→+Step+2+→+Step+3%0A%0AWorkflow+Visualization"
        else:
            diagram_url = f"https://via.placeholder.com/800x600/{color}?text={concept_clean}%0A%0AEducational+Diagram%0A%0A{subject_clean}"
        
        print(f"🖼️ Using placeholder image: {diagram_url}")
        
        return {
            "success": True,
            "diagram_url": diagram_url,
            "diagram_type": diagram_type,
            "concept": concept,
            "supervised": supervised
        }
        
    except Exception as e:
        print(f"Error generating diagram: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate diagram: {str(e)}")

@app.post("/teaching/assessment/create")
async def create_assessment(request: dict):
    """Create an assessment for a specific concept."""
    try:
        concept = request.get("concept", "")
        subject = request.get("subject", "Artificial Intelligence")
        difficulty = request.get("difficulty", "Intermediate")
        learning_style = request.get("learning_style", "Visual + Hands-on")
        previous_responses = request.get("previous_responses", [])
        
        if not concept:
            raise HTTPException(status_code=400, detail="Concept is required")
        
        # Use the AssessmentAgent to create an assessment
        if agent_system and hasattr(agent_system, 'agents') and 'assessment' in agent_system.agents:
            assessment_agent = agent_system.agents['assessment']
            result = await assessment_agent.create_assessment_for_concept(
                concept=concept,
                subject=subject,
                difficulty=difficulty,
                learning_style=learning_style,
                previous_responses=previous_responses
            )
            return result
        else:
            # Fallback response
            return {
                "success": True,
                "assessment": {
                    "questions": [
                        {
                            "id": "q1",
                            "question": f"Which of the following best describes {concept}?",
                            "type": "multiple_choice",
                            "options": [
                                "A fundamental concept in AI",
                                "An advanced mathematical theory",
                                "A programming language",
                                "A hardware component"
                            ],
                            "correct_answer": "A fundamental concept in AI",
                            "explanation": f"{concept} is indeed a fundamental concept in AI."
                        },
                        {
                            "id": "q2",
                            "question": f"True or False: {concept} is important for understanding AI systems.",
                            "type": "true_false",
                            "options": ["True", "False"],
                            "correct_answer": "True",
                            "explanation": f"{concept} is a crucial component for understanding AI systems."
                        }
                    ],
                    "passing_score": 1,
                    "concept_assessed": concept,
                    "difficulty": difficulty,
                    "created_at": datetime.now().isoformat()
                }
            }
        
    except Exception as e:
        print(f"Error creating assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create assessment: {str(e)}")

@app.post("/teaching/assessment/grade")
async def grade_assessment(request: dict):
    """Grade a user's assessment answers."""
    try:
        user_answers = request.get("user_answers", [])
        assessment = request.get("assessment", {})
        
        if not user_answers or not assessment:
            raise HTTPException(status_code=400, detail="User answers and assessment are required")
        
        # Use the AssessmentAgent to grade the assessment
        if agent_system and hasattr(agent_system, 'agents') and 'assessment' in agent_system.agents:
            assessment_agent = agent_system.agents['assessment']
            result = await assessment_agent.grade_assessment(
                user_answers=user_answers,
                assessment=assessment
            )
            return result
        else:
            # Fallback response
            return {
                "success": True,
                "passed": True,
                "score": 1,
                "total": 2,
                "score_percentage": 50.0,
                "feedback": "Good job! You've shown a solid understanding of the concept.",
                "question_results": [
                    {
                        "id": user_answers[0].get("id", "q1"),
                        "question": "Question text",
                        "user_answer": user_answers[0].get("answer", ""),
                        "correct": True,
                        "correct_answer": "Correct answer",
                        "explanation": "Explanation of the correct answer."
                    }
                ],
                "concept": assessment.get("concept_assessed", "the concept"),
                "subject": "Artificial Intelligence",
                "completed_at": datetime.now().isoformat()
            }
        
    except Exception as e:
        print(f"Error grading assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to grade assessment: {str(e)}")

@app.post("/teaching/assessment/recommendations")
async def get_teaching_recommendations(request: dict):
    """Get teaching recommendations based on assessment results."""
    try:
        assessment_result = request.get("assessment_result", {})
        
        if not assessment_result:
            raise HTTPException(status_code=400, detail="Assessment result is required")
        
        # Use the AssessmentAgent to provide recommendations
        if agent_system and hasattr(agent_system, 'agents') and 'assessment' in agent_system.agents:
            assessment_agent = agent_system.agents['assessment']
            result = await assessment_agent.provide_teaching_recommendations(assessment_result)
            return result
        else:
            # Fallback response
            passed = assessment_result.get("passed", False)
            concept = assessment_result.get("concept", "the concept")
            
            if passed:
                return {
                    "success": True,
                    "should_continue": True,
                    "message": f"Great job! You've demonstrated understanding of {concept}. Let's continue with the next concept.",
                    "next_action": "continue_teaching"
                }
            else:
                return {
                    "success": True,
                    "should_continue": False,
                    "message": f"Let's review {concept} a bit more before moving on.",
                    "review_points": [
                        "Review the key definitions and examples",
                        "Try to apply the concept in different contexts",
                        "Focus on understanding the underlying principles"
                    ],
                    "next_action": "review_concept"
                }
        
    except Exception as e:
        print(f"Error getting teaching recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get teaching recommendations: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🔥 Starting VEDYA API Server...")
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
