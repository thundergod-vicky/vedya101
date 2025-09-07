#!/usr/bin/env python3
"""
User Service - Clerk Integration with Database and Email Notifications
This service handles user registration, profile management, and email notifications.
"""

import os
import asyncio
import asyncpg
import logging
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from email_service import VedyaEmailService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserService:
    """Service for managing users, Clerk integration, and email notifications."""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.email_service = VedyaEmailService()
        
        if not self.database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
    
    async def get_db_connection(self):
        """Get database connection with Supabase-compatible settings."""
        return await asyncpg.connect(self.database_url, statement_cache_size=0)
    
    async def create_user_from_clerk(self, clerk_user_id: str, email: str, name: str = None) -> Dict[str, Any]:
        """
        Create a new user from Clerk authentication data.
        This should be called when a user signs up via Clerk.
        """
        try:
            conn = await self.get_db_connection()
            
            # Check if user already exists
            existing_user = await conn.fetchrow(
                "SELECT * FROM users WHERE clerk_user_id = $1 OR email = $2",
                clerk_user_id, email
            )
            
            if existing_user:
                logger.info(f"User already exists: {email}")
                await conn.close()
                return {
                    "success": True,
                    "user_id": str(existing_user["id"]),
                    "message": "User already exists"
                }
            
            # Create new user
            user_id = await conn.fetchval("""
                INSERT INTO users (clerk_user_id, email, name, preferences)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, clerk_user_id, email, name, json.dumps({}))
            
            await conn.close()
            
            # Send welcome email
            try:
                await self.email_service.send_welcome_email(email, name or "Learner")
                logger.info(f"Welcome email sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send welcome email to {email}: {str(e)}")
            
            logger.info(f"New user created: {email} (ID: {user_id})")
            
            return {
                "success": True,
                "user_id": str(user_id),
                "message": "User created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create user from Clerk: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_by_clerk_id(self, clerk_user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Clerk user ID."""
        try:
            conn = await self.get_db_connection()
            
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE clerk_user_id = $1",
                clerk_user_id
            )
            
            await conn.close()
            
            if user:
                return dict(user)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by Clerk ID: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address."""
        try:
            conn = await self.get_db_connection()
            
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1",
                email
            )
            
            await conn.close()
            
            if user:
                return dict(user)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by email: {str(e)}")
            return None
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences."""
        try:
            conn = await self.get_db_connection()
            
            await conn.execute("""
                UPDATE users 
                SET preferences = $1, updated_at = NOW()
                WHERE id = $2
            """, json.dumps(preferences), user_id)
            
            await conn.close()
            
            logger.info(f"Updated preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user preferences: {str(e)}")
            return False
    
    async def send_learning_plan_notification(self, user_id: str, plan_details: Dict[str, Any]) -> bool:
        """Send learning plan ready notification to user."""
        try:
            # Get user info
            conn = await self.get_db_connection()
            user = await conn.fetchrow("SELECT email, name FROM users WHERE id = $1", user_id)
            await conn.close()
            
            if not user:
                logger.error(f"User not found: {user_id}")
                return False
            
            # Send email notification
            await self.email_service.send_learning_plan_ready(
                user["email"], 
                user["name"] or "Learner",
                plan_details.get("title", "Your Learning Plan"),
                plan_details.get("summary", "Your personalized learning plan is ready!")
            )
            
            logger.info(f"Learning plan notification sent to {user['email']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send learning plan notification: {str(e)}")
            return False
    
    async def send_progress_milestone_notification(self, user_id: str, milestone_data: Dict[str, Any]) -> bool:
        """Send progress milestone notification to user."""
        try:
            # Get user info
            conn = await self.get_db_connection()
            user = await conn.fetchrow("SELECT email, name FROM users WHERE id = $1", user_id)
            await conn.close()
            
            if not user:
                logger.error(f"User not found: {user_id}")
                return False
            
            # Send email notification
            await self.email_service.send_progress_milestone(
                user["email"],
                user["name"] or "Learner", 
                milestone_data.get("milestone", "Milestone Completed"),
                milestone_data.get("progress", 0)
            )
            
            logger.info(f"Milestone notification sent to {user['email']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send milestone notification: {str(e)}")
            return False
    
    async def send_daily_summary_notification(self, user_id: str, summary_data: Dict[str, Any]) -> bool:
        """Send daily summary notification to user."""
        try:
            # Get user info
            conn = await self.get_db_connection()
            user = await conn.fetchrow("SELECT email, name FROM users WHERE id = $1", user_id)
            await conn.close()
            
            if not user:
                logger.error(f"User not found: {user_id}")
                return False
            
            # Send email notification
            await self.email_service.send_daily_summary(
                user["email"],
                user["name"] or "Learner",
                summary_data
            )
            
            logger.info(f"Daily summary sent to {user['email']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send daily summary: {str(e)}")
            return False
    
    async def send_weekly_report_notification(self, user_id: str, report_data: Dict[str, Any]) -> bool:
        """Send weekly report notification to user."""
        try:
            # Get user info
            conn = await self.get_db_connection()
            user = await conn.fetchrow("SELECT email, name FROM users WHERE id = $1", user_id)
            await conn.close()
            
            if not user:
                logger.error(f"User not found: {user_id}")
                return False
            
            # Send email notification
            await self.email_service.send_weekly_report(
                user["email"],
                user["name"] or "Learner",
                report_data
            )
            
            logger.info(f"Weekly report sent to {user['email']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send weekly report: {str(e)}")
            return False
    
    async def get_all_users_for_notifications(self) -> list:
        """Get all users for batch notifications (daily/weekly reports)."""
        try:
            conn = await self.get_db_connection()
            
            users = await conn.fetch("""
                SELECT id, email, name, preferences 
                FROM users 
                WHERE email IS NOT NULL
                ORDER BY created_at
            """)
            
            await conn.close()
            
            return [dict(user) for user in users]
            
        except Exception as e:
            logger.error(f"Failed to get users for notifications: {str(e)}")
            return []

# Example usage and testing
async def test_user_service():
    """Test the user service functionality."""
    print("🧪 Testing User Service")
    
    user_service = UserService()
    
    # Test user creation
    test_user_data = {
        "clerk_user_id": "user_test123",
        "email": "support@vayuinnovations.com",  # Use verified email for testing
        "name": "Test User"
    }
    
    print(f"\n1️⃣ Creating user: {test_user_data['email']}")
    result = await user_service.create_user_from_clerk(**test_user_data)
    print(f"Result: {result}")
    
    if result["success"]:
        user_id = result["user_id"]
        
        # Test getting user by Clerk ID
        print(f"\n2️⃣ Getting user by Clerk ID")
        user = await user_service.get_user_by_clerk_id(test_user_data["clerk_user_id"])
        print(f"User found: {user is not None}")
        
        # Test learning plan notification
        print(f"\n3️⃣ Sending learning plan notification")
        plan_data = {
            "title": "AI Fundamentals Learning Path",
            "summary": "A comprehensive introduction to artificial intelligence",
            "duration": "4 weeks",
            "topics": ["Machine Learning", "Neural Networks", "Deep Learning"]
        }
        
        success = await user_service.send_learning_plan_notification(user_id, plan_data)
        print(f"Learning plan notification sent: {success}")
        
        # Test milestone notification
        print(f"\n4️⃣ Sending milestone notification")
        milestone_data = {
            "milestone": "Completed Module 1: Introduction to AI",
            "progress": 25,
            "next_steps": "Continue with Module 2: Machine Learning Basics"
        }
        
        success = await user_service.send_progress_milestone_notification(user_id, milestone_data)
        print(f"Milestone notification sent: {success}")

if __name__ == "__main__":
    # Run tests
    asyncio.run(test_user_service())
