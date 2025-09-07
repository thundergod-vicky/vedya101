# AWS SES Email Setup Guide for VEDYA

## 🎯 Overview
Your AWS SES is configured and ready, but you need to verify email addresses before sending notifications.

## ✅ Current Configuration Status
- **SMTP Username**: `AKIA***************` ✅ (configured in .env)
- **SMTP Password**: `****************` ✅ (configured in .env)
- **SMTP Host**: `email-smtp.ap-south-1.amazonaws.com` ✅
- **SMTP Port**: `587` ✅
- **Region**: `ap-south-1` (Asia Pacific - Mumbai) ✅

## 🔧 Required Steps

### Step 1: Verify Email Addresses

**Why?** AWS SES starts in "sandbox mode" - you can only send emails to verified addresses.

**How to verify:**

1. **Using our verification script:**
   ```bash
   python verify_ses_emails.py
   ```

2. **Using AWS Console:**
   - Go to [SES Console](https://console.aws.amazon.com/ses)
   - Navigate to "Verified identities"
   - Click "Create identity"
   - Add your email address
   - Check your email and click verification link

### Step 2: Test Email Service

Once verified, test with:
```bash
python test_email.py
```

### Step 3: Request Production Access (Optional)

To send emails to any address (not just verified ones):

1. Go to [SES Console](https://console.aws.amazon.com/ses)
2. Click "Request production access"
3. Fill out the request form
4. Typical approval time: 1-2 business days

## 📧 Email Templates Available

### 1. Welcome Email
- **Trigger**: New user registration
- **Content**: Platform introduction, getting started guide
- **API**: `POST /notifications/welcome`

### 2. Learning Plan Ready
- **Trigger**: AI completes personalized learning plan
- **Content**: Plan summary, next steps
- **API**: `POST /notifications/learning-plan-ready`

### 3. Daily Summary
- **Trigger**: End of learning day
- **Content**: Time spent, lessons completed, quiz scores
- **API**: `POST /notifications/daily-summary`

### 4. Progress Milestones
- **Trigger**: Achievement unlocked
- **Content**: Congratulations, progress stats
- **API**: `POST /notifications/progress-milestone`

### 5. Weekly Report
- **Trigger**: Weekly schedule
- **Content**: Comprehensive learning analytics
- **API**: `POST /notifications/weekly-report`

## 🚀 Integration with VEDYA

### Frontend Integration

```typescript
// Send welcome email after user signs up
const sendWelcomeEmail = async (email: string, name: string) => {
  const response = await fetch(`${API_BASE_URL}/notifications/welcome`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, name })
  });
  return response.json();
};
```

### Agent Integration

The `NotificationAgent` automatically triggers emails:
- **Learning plan completion** → Learning plan ready email
- **Progress milestones** → Milestone achievement email
- **Daily activity** → Daily summary (if enabled)

## 📊 Monitoring & Analytics

### Check Email Status
```bash
curl http://localhost:8000/notifications/status
```

### SES Usage Monitoring
```bash
python verify_ses_emails.py
# Choose option 4 for quota and limits
```

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit SES credentials to git
2. **Rate Limiting**: SES has sending limits (200 emails/day in sandbox)
3. **Bounce Handling**: Monitor bounced emails
4. **Unsubscribe**: Include unsubscribe links in production

## 🎨 Email Branding

All emails include:
- **VEDYA branding** with purple gradient theme
- **VAYU Innovations** footer
- **Responsive design** for mobile/desktop
- **Professional styling** with modern UI

## 🐛 Troubleshooting

### Common Issues

1. **"Email address not verified"**
   - Solution: Verify recipient email in SES console

2. **"Sending quota exceeded"**
   - Solution: Request production access or wait 24 hours

3. **"Invalid SMTP credentials"**
   - Solution: Check AWS credentials in .env file

4. **Emails in spam folder**
   - Solution: Set up DKIM/SPF records (production)

### Testing Commands

```bash
# Test configuration
python test_email.py

# Verify email addresses
python verify_ses_emails.py

# Check API endpoints
curl -X POST http://localhost:8000/notifications/welcome \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User"}'
```

## 🎯 Next Steps

1. **Verify your email address** using the verification script
2. **Test the email service** with `python test_email.py`
3. **Integrate with frontend** for user registration emails
4. **Set up scheduled notifications** for daily/weekly reports
5. **Request production access** when ready for all users

Your email notification system is ready to enhance the VEDYA learning experience! 🚀
