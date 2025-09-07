# Clerk Integration Guide - VEDYA Platform

This guide shows how to integrate Clerk authentication with the VEDYA backend to automatically create user profiles and send email notifications.

## 🔄 User Flow Overview

```
1. User signs up via Clerk (Frontend) 
   ↓
2. Frontend calls /users/register (Backend)
   ↓  
3. Backend creates user in database
   ↓
4. Backend sends welcome email via SES
   ↓
5. User receives personalized notifications
```

## 🎯 Frontend Integration (Next.js)

### 1. Install Required Dependencies

```bash
cd frontend
npm install @clerk/nextjs
```

### 2. Update Frontend Environment Variables

Add to `frontend/.env.local`:

```env
# Clerk Configuration
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Create User Registration Hook

Create `frontend/src/hooks/useUserRegistration.ts`:

```typescript
import { useUser } from '@clerk/nextjs';
import { useEffect, useState } from 'react';

interface UserRegistrationResult {
  isRegistered: boolean;
  isLoading: boolean;
  error: string | null;
}

export function useUserRegistration(): UserRegistrationResult {
  const { user, isLoaded } = useUser();
  const [isRegistered, setIsRegistered] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function registerUser() {
      if (!isLoaded || !user) return;

      setIsLoading(true);
      setError(null);

      try {
        // Check if user already exists
        const checkResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/users/clerk/${user.id}`
        );

        if (checkResponse.ok) {
          // User already exists
          setIsRegistered(true);
          setIsLoading(false);
          return;
        }

        // Register new user
        const registerResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/users/register`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              clerk_user_id: user.id,
              email: user.primaryEmailAddress?.emailAddress,
              name: user.fullName || user.firstName || 'Learner',
            }),
          }
        );

        const result = await registerResponse.json();

        if (result.success) {
          setIsRegistered(true);
          console.log('✅ User registered successfully:', result.user_id);
        } else {
          setError(result.error || 'Registration failed');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Registration failed');
        console.error('❌ User registration error:', err);
      } finally {
        setIsLoading(false);
      }
    }

    registerUser();
  }, [user, isLoaded]);

  return { isRegistered, isLoading, error };
}
```

### 4. Update Dashboard Component

Update `frontend/src/app/dashboard/page.tsx`:

```typescript
'use client';

import { useUser } from '@clerk/nextjs';
import { useUserRegistration } from '@/hooks/useUserRegistration';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

export default function Dashboard() {
  const { user, isLoaded } = useUser();
  const { isRegistered, isLoading, error } = useUserRegistration();

  // Show loading while Clerk loads or user registers
  if (!isLoaded || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
        <p className="ml-2">Setting up your account...</p>
      </div>
    );
  }

  // Show error if registration failed
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-red-600 mb-2">
            Registration Error
          </h2>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  // Show dashboard once user is registered
  if (isRegistered) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">
          Welcome to VEDYA, {user?.firstName}! 🎓
        </h1>
        
        {/* Your existing dashboard content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Dashboard cards */}
        </div>
      </div>
    );
  }

  return null;
}
```

## 🔧 Backend Endpoints Reference

### User Management

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/users/register` | POST | Register user from Clerk |
| `/users/clerk/{clerk_user_id}` | GET | Get user by Clerk ID |
| `/users/email/{email}` | GET | Get user by email |
| `/users/{user_id}/preferences` | PATCH | Update preferences |

### User Notifications

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/users/{user_id}/notifications/learning-plan` | POST | Send learning plan |
| `/users/{user_id}/notifications/milestone` | POST | Send milestone update |
| `/users/{user_id}/notifications/daily-summary` | POST | Send daily summary |
| `/users/{user_id}/notifications/weekly-report` | POST | Send weekly report |

## 📧 Email Notification Flow

### 1. Automatic Welcome Email
When a user registers via Clerk:
```python
# Backend automatically sends welcome email
await user_service.create_user_from_clerk(
    clerk_user_id="user_123",
    email="user@example.com", 
    name="John Doe"
)
# ✅ Welcome email sent automatically
```

### 2. Learning Plan Notifications
When agents create a learning plan:
```python
# Agent triggers learning plan email
await user_service.send_learning_plan_notification(
    user_id="uuid-123",
    plan_details={
        "title": "AI Fundamentals",
        "duration": "4 weeks",
        "topics": ["ML", "Neural Networks"]
    }
)
```

### 3. Progress Notifications
When user completes milestones:
```python
# Agent triggers milestone email
await user_service.send_progress_milestone_notification(
    user_id="uuid-123",
    milestone_data={
        "milestone": "Completed Module 1",
        "progress": 25,
        "next_steps": "Continue with Module 2"
    }
)
```

## 🎯 Agent Integration

The agents in `vedya_agents.py` can now automatically send notifications:

```python
# In NotificationAgent
class NotificationAgent:
    async def send_user_notification(self, user_id: str, notification_type: str, data: dict):
        """Send notification to specific user."""
        try:
            if notification_type == "learning_plan":
                await user_service.send_learning_plan_notification(user_id, data)
            elif notification_type == "milestone":
                await user_service.send_progress_milestone_notification(user_id, data)
            elif notification_type == "daily_summary":
                await user_service.send_daily_summary_notification(user_id, data)
            elif notification_type == "weekly_report":
                await user_service.send_weekly_report_notification(user_id, data)
            
            return {"success": True, "message": "Notification sent"}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

## 🧪 Testing the Integration

### 1. Test User Registration
```bash
# Start backend
python api_server.py

# Test registration endpoint
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "clerk_user_id": "user_test123",
    "email": "support@vayuinnovations.com",
    "name": "Test User"
  }'
```

### 2. Test User Lookup
```bash
# Get user by Clerk ID
curl "http://localhost:8000/users/clerk/user_test123"

# Get user by email
curl "http://localhost:8000/users/email/support@vayuinnovations.com"
```

### 3. Test Notifications
```bash
# Send learning plan notification
curl -X POST "http://localhost:8000/users/{user_id}/notifications/learning-plan" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Fundamentals",
    "summary": "Introduction to AI",
    "duration": "4 weeks"
  }'
```

## 🚀 Production Deployment

### Environment Variables Needed:

```env
# Database
DATABASE_URL=postgresql://...

# Clerk
CLERK_SECRET_KEY=sk_live_...
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...

# AWS SES
SES_SMTP_USERNAME=...
SES_SMTP_PASSWORD=...
SES_SMTP_HOST=email-smtp.ap-south-1.amazonaws.com
SES_FROM_EMAIL=support@vayuinnovations.com

# OpenAI
OPENAI_API_KEY=sk-...
```

## 🎉 Benefits

✅ **Seamless User Experience**: Automatic account creation and welcome emails  
✅ **Personalized Notifications**: All emails use user's actual name and preferences  
✅ **Database Integration**: User data synced between Clerk and your database  
✅ **Agent Automation**: AI agents can trigger targeted user notifications  
✅ **Production Ready**: Robust error handling and scalable architecture  

The integration ensures that every user who signs up via Clerk automatically gets:
1. A database profile created
2. A welcome email sent to their verified address  
3. Ongoing personalized learning notifications
4. Progress tracking and milestone updates

Perfect for your VEDYA education platform! 🎓
