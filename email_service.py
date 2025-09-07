#!/usr/bin/env python3
"""
VEDYA Email Notification Service
AWS SES integration for sending learning progress notifications
"""

import os
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class VedyaEmailService:
    """AWS SES email service for VEDYA notifications."""
    
    def __init__(self):
        self.smtp_username = os.getenv("SES_SMTP_USERNAME")
        self.smtp_password = os.getenv("SES_SMTP_PASSWORD")
        self.smtp_host = os.getenv("SES_SMTP_HOST", "email-smtp.ap-south-1.amazonaws.com")
        self.smtp_port = int(os.getenv("SES_SMTP_PORT", "587"))
        self.from_email = os.getenv("SES_FROM_EMAIL", "support@vayuinnovations.com")
        self.from_name = os.getenv("SES_FROM_NAME", "VEDYA - AI Learning Platform")
        self.reply_to = os.getenv("SES_REPLY_TO", "noreply@vayuinnovations.com")
        
        # Notification settings
        self.notifications_enabled = os.getenv("NOTIFICATIONS_ENABLED", "false").lower() == "true"
        self.daily_summary_enabled = os.getenv("DAILY_SUMMARY_ENABLED", "false").lower() == "true"
        self.progress_alerts_enabled = os.getenv("PROGRESS_ALERTS_ENABLED", "false").lower() == "true"
        self.weekly_report_enabled = os.getenv("WEEKLY_REPORT_ENABLED", "false").lower() == "true"
        
        if not all([self.smtp_username, self.smtp_password]):
            logger.warning("SES credentials not found. Email notifications will be disabled.")
            self.notifications_enabled = False
    
    def _create_smtp_connection(self):
        """Create and return an SMTP connection."""
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            return server
        except Exception as e:
            logger.error(f"Failed to connect to SES SMTP: {e}")
            raise
    
    def _create_message(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> MIMEMultipart:
        """Create an email message."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.from_name} <{self.from_email}>"
        msg['To'] = to_email
        msg['Reply-To'] = self.reply_to
        
        # Add text version if provided
        if text_content:
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
        
        # Add HTML version
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        return msg
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send an email using AWS SES SMTP."""
        if not self.notifications_enabled:
            logger.info("Email notifications disabled. Skipping email send.")
            return False
        
        try:
            # Create message
            msg = self._create_message(to_email, subject, html_content, text_content)
            
            # Send email
            with self._create_smtp_connection() as server:
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new users."""
        subject = "Welcome to VEDYA - Your AI Learning Journey Begins! 🚀"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Welcome to VEDYA</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
                .content {{ padding: 40px 20px; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b; }}
                .button {{ display: inline-block; background-color: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .feature {{ margin: 20px 0; padding: 15px; border-left: 4px solid #667eea; background-color: #f8fafc; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to VEDYA! 🎓</h1>
                    <p>Your AI-Powered Learning Journey Starts Now</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name}! 👋</h2>
                    <p>We're thrilled to have you join VEDYA, where artificial intelligence meets personalized education. Get ready for a learning experience like no other!</p>
                    
                    <div class="feature">
                        <h3>🤖 AI-Powered Personalization</h3>
                        <p>Our intelligent agents create custom learning paths just for you</p>
                    </div>
                    
                    <div class="feature">
                        <h3>📊 Real-Time Progress Tracking</h3>
                        <p>Watch your knowledge grow with detailed analytics and insights</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🎯 Adaptive Learning</h3>
                        <p>Content that adjusts to your pace and learning style</p>
                    </div>
                    
                    <p>Ready to start learning? Click below to access your personalized dashboard:</p>
                    <a href="https://vedya.vercel.app" class="button">Start Learning Now 🚀</a>
                    
                    <p>Need help? Our AI assistant is always ready to guide you through your learning journey.</p>
                </div>
                <div class="footer">
                    <p>Powered by VAYU Innovations | AI-Driven Education Technology</p>
                    <p>This email was sent to {user_email}. If you didn't sign up for VEDYA, please ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to VEDYA, {user_name}!
        
        Your AI-Powered Learning Journey Starts Now
        
        We're thrilled to have you join VEDYA, where artificial intelligence meets personalized education.
        
        What you can expect:
        - AI-Powered Personalization: Custom learning paths just for you
        - Real-Time Progress Tracking: Detailed analytics and insights
        - Adaptive Learning: Content that adjusts to your pace
        
        Start learning now: https://vedya.vercel.app
        
        Powered by VAYU Innovations
        """
        
        return await self.send_email(user_email, subject, html_content, text_content)
    
    async def send_daily_summary(self, user_email: str, user_name: str, summary_data: Dict[str, Any]) -> bool:
        """Send daily learning summary."""
        if not self.daily_summary_enabled:
            return False
        
        subject = f"Your Daily Learning Summary - {datetime.now().strftime('%B %d, %Y')} 📚"
        
        # Extract summary data
        time_spent = summary_data.get('time_spent_minutes', 0)
        lessons_completed = summary_data.get('lessons_completed', 0)
        quiz_score = summary_data.get('avg_quiz_score', 0)
        ai_interactions = summary_data.get('ai_interactions', 0)
        streak_days = summary_data.get('streak_days', 0)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Daily Learning Summary</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; }}
                .stat {{ display: inline-block; margin: 10px; padding: 20px; background-color: #f0f9ff; border-radius: 8px; text-align: center; width: 120px; }}
                .stat-number {{ font-size: 24px; font-weight: bold; color: #0369a1; }}
                .stat-label {{ font-size: 12px; color: #64748b; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Daily Learning Summary 📚</h1>
                    <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
                </div>
                <div class="content">
                    <h2>Great job today, {user_name}! 🎉</h2>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <div class="stat">
                            <div class="stat-number">{time_spent}</div>
                            <div class="stat-label">Minutes Learned</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">{lessons_completed}</div>
                            <div class="stat-label">Lessons Completed</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">{quiz_score}%</div>
                            <div class="stat-label">Avg Quiz Score</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">{ai_interactions}</div>
                            <div class="stat-label">AI Chats</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">{streak_days}</div>
                            <div class="stat-label">Day Streak</div>
                        </div>
                    </div>
                    
                    <h3>🎯 Tomorrow's Goals</h3>
                    <ul>
                        <li>Continue your learning streak</li>
                        <li>Try to beat today's quiz score</li>
                        <li>Explore new topics with our AI assistant</li>
                    </ul>
                    
                    <p>Keep up the excellent work! Your dedication to learning is inspiring.</p>
                </div>
                <div class="footer">
                    <p>Powered by VAYU Innovations | AI-Driven Education Technology</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_content)
    
    async def send_learning_plan_ready(self, user_email: str, user_name: str, plan_title: str, plan_summary: str) -> bool:
        """Send notification when learning plan is ready."""
        subject = f"Your Learning Plan is Ready: {plan_title} 🎯"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Learning Plan Ready</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; }}
                .plan-box {{ background-color: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b; }}
                .button {{ display: inline-block; background-color: #f59e0b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your Learning Plan is Ready! 🎯</h1>
                    <p>AI-Curated Just for You</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name}! 👋</h2>
                    <p>Great news! Our AI agents have crafted a personalized learning plan based on your goals and preferences.</p>
                    
                    <div class="plan-box">
                        <h3>📘 {plan_title}</h3>
                        <p>{plan_summary}</p>
                    </div>
                    
                    <p>Your plan includes:</p>
                    <ul>
                        <li>🎯 Customized learning objectives</li>
                        <li>📚 Curated content and resources</li>
                        <li>🔄 Progress tracking and milestones</li>
                        <li>🤖 AI-powered assistance throughout</li>
                    </ul>
                    
                    <a href="https://vedya.vercel.app" class="button">Start Your Learning Journey 🚀</a>
                    
                    <p>Your AI learning assistant is ready to guide you every step of the way!</p>
                </div>
                <div class="footer">
                    <p>Powered by VAYU Innovations | AI-Driven Education Technology</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_content)
    
    async def send_progress_milestone(self, user_email: str, user_name: str, milestone: str, completion_percentage: float) -> bool:
        """Send notification for progress milestones."""
        if not self.progress_alerts_enabled:
            return False
        
        subject = f"Milestone Achieved: {milestone} 🏆"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Milestone Achieved</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; }}
                .progress-bar {{ background-color: #e5e7eb; height: 20px; border-radius: 10px; margin: 20px 0; }}
                .progress-fill {{ background-color: #8b5cf6; height: 100%; border-radius: 10px; width: {completion_percentage}%; }}
                .celebration {{ text-align: center; font-size: 48px; margin: 20px 0; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Milestone Achieved! 🏆</h1>
                    <p>Celebrating Your Progress</p>
                </div>
                <div class="content">
                    <div class="celebration">🎉</div>
                    <h2>Congratulations, {user_name}!</h2>
                    <p>You've reached an important milestone in your learning journey:</p>
                    
                    <h3 style="color: #8b5cf6;">🎯 {milestone}</h3>
                    
                    <p>Your overall progress:</p>
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                    <p style="text-align: center; font-weight: bold;">{completion_percentage:.1f}% Complete</p>
                    
                    <p>Keep up the excellent work! Every step forward is a victory worth celebrating.</p>
                    
                    <h3>🚀 What's Next?</h3>
                    <ul>
                        <li>Continue with your current learning plan</li>
                        <li>Explore advanced topics in your area of interest</li>
                        <li>Challenge yourself with more complex exercises</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>Powered by VAYU Innovations | AI-Driven Education Technology</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_content)
    
    async def send_weekly_report(self, user_email: str, user_name: str, weekly_data: Dict[str, Any]) -> bool:
        """Send weekly learning report."""
        if not self.weekly_report_enabled:
            return False
        
        subject = f"Your Weekly Learning Report - Week of {datetime.now().strftime('%B %d, %Y')} 📊"
        
        # Extract weekly data
        total_time = weekly_data.get('total_time_minutes', 0)
        lessons_completed = weekly_data.get('lessons_completed', 0)
        avg_score = weekly_data.get('avg_quiz_score', 0)
        topics_covered = weekly_data.get('topics_covered', [])
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Weekly Learning Report</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; }}
                .metric {{ margin: 15px 0; padding: 15px; background-color: #f0f9ff; border-radius: 8px; }}
                .metric-value {{ font-size: 20px; font-weight: bold; color: #0369a1; }}
                .topic {{ background-color: #dbeafe; padding: 8px 12px; border-radius: 16px; display: inline-block; margin: 4px; font-size: 14px; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Weekly Learning Report 📊</h1>
                    <p>Week of {datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name}! 👋</h2>
                    <p>Here's a summary of your learning achievements this week:</p>
                    
                    <div class="metric">
                        <strong>⏱️ Total Learning Time</strong>
                        <div class="metric-value">{total_time} minutes</div>
                    </div>
                    
                    <div class="metric">
                        <strong>📚 Lessons Completed</strong>
                        <div class="metric-value">{lessons_completed} lessons</div>
                    </div>
                    
                    <div class="metric">
                        <strong>🎯 Average Quiz Score</strong>
                        <div class="metric-value">{avg_score}%</div>
                    </div>
                    
                    <h3>📖 Topics Covered This Week</h3>
                    <div style="margin: 20px 0;">
                        {' '.join([f'<span class="topic">{topic}</span>' for topic in topics_covered[:10]])}
                    </div>
                    
                    <h3>🚀 Next Week's Goals</h3>
                    <ul>
                        <li>Maintain your learning momentum</li>
                        <li>Explore new challenging topics</li>
                        <li>Improve your quiz scores</li>
                        <li>Engage more with AI assistant</li>
                    </ul>
                    
                    <p>Your dedication to continuous learning is inspiring. Keep up the great work!</p>
                </div>
                <div class="footer">
                    <p>Powered by VAYU Innovations | AI-Driven Education Technology</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_content)

# Global email service instance
email_service = VedyaEmailService()

async def main():
    """Test the email service."""
    # Test welcome email
    success = await email_service.send_welcome_email(
        "test@example.com",
        "Test User"
    )
    print(f"Welcome email sent: {success}")

if __name__ == "__main__":
    asyncio.run(main())
