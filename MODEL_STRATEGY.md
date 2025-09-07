# VEDYA Model Usage Strategy

## Overview
Based on the project instructions, VEDYA uses an **OpenAI-first approach** with Bedrock as backup for specific use cases.

## Correct Model Assignments

### 🟢 **Primary: OpenAI Models**

**For User-Facing Operations:**
- **User Conversations**: `gpt-4o` (main chat interface)
- **Summarization**: `gpt-4o` (user objectives summary)
- **Embeddings**: `text-embedding-3-large` (3072 dimensions)

**For Agent Operations:**
- **Supervisor Agent**: `gpt-4o` (coordination and delegation)
- **Planner Agent**: `gpt-4o` (structured JSON learning plans)
- **Content Curator Agent**: `gpt-4o` (material selection and organization)
- **Assessment Agent**: `gpt-4o` (quiz generation and grading)
- **Manager Agent**: `gpt-4o` (coordination and verification)

**For High-Frequency Operations:**
- **Teaching Assistant**: `gpt-4o-mini` (real-time Q&A)
- **Progress Tracker**: `gpt-4o-mini` (metrics and trend analysis)
- **Feedback Agent**: `gpt-4o-mini` (sentiment analysis)
- **Reporting Agent**: `gpt-4o-mini` (report compilation)
- **Resource Recommendation**: `gpt-4o-mini` (recommendation explanations)

### 🟡 **Secondary: Bedrock Models (Backup/Specific Use Cases)**

**Heavy Processing (when OpenAI is unavailable):**
- **Claude 3.5 Sonnet**: Complex reasoning, long-form content
- **Claude 3 Haiku**: Fast responses, simple tasks

**Specialized Use Cases:**
- **Amazon Titan**: Text embeddings (alternative to OpenAI)
- **Claude models**: Content moderation, specialized analysis

## Why OpenAI-First?

### ✅ **Advantages:**
1. **Faster Response Times**: Lower latency than Bedrock
2. **Better Rate Limits**: Higher requests per minute
3. **Cost Effective**: GPT-4o-mini for high-volume operations
4. **Proven Reliability**: More stable for production workloads
5. **Better Function Calling**: Superior tool/API integration
6. **JSON Mode**: Structured output for agent coordination

### 🔄 **Fallback Strategy:**
```javascript
async function callWithFallback(primaryModel, fallbackModel, prompt) {
  try {
    return await callOpenAI(primaryModel, prompt);
  } catch (error) {
    if (error.message.includes('rate limit') || error.message.includes('503')) {
      console.log('Falling back to Bedrock...');
      return await callBedrock(fallbackModel, prompt);
    }
    throw error;
  }
}
```

## Updated Environment Variables

```env
# Primary Models (OpenAI)
OPENAI_MODEL_CHAT=gpt-4o
OPENAI_MODEL_CHAT_FALLBACK=gpt-4o-mini
OPENAI_MODEL_SUMMARY=gpt-4o
OPENAI_MODEL_EMBEDDING=text-embedding-3-large

# Agent-Specific Models
SUPERVISOR_AGENT_MODEL=gpt-4o
PLANNER_AGENT_MODEL=gpt-4o
CONTENT_CURATOR_MODEL=gpt-4o
TEACHING_ASSISTANT_MODEL=gpt-4o-mini
PROGRESS_TRACKER_MODEL=gpt-4o-mini
ASSESSMENT_AGENT_MODEL=gpt-4o
FEEDBACK_AGENT_MODEL=gpt-4o-mini
REPORTING_AGENT_MODEL=gpt-4o-mini
RESOURCE_RECOMMENDATION_MODEL=gpt-4o-mini
MANAGER_AGENT_MODEL=gpt-4o

# Fallback Models (Bedrock)
BEDROCK_SUPERVISOR_FALLBACK=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_PLANNER_FALLBACK=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_TEACHING_FALLBACK=anthropic.claude-3-haiku-20240307-v1:0
```

## Cost Optimization

### **Model Selection by Use Case:**

| Use Case | Primary Model | Reason | Cost Impact |
|----------|---------------|---------|-------------|
| User Chat | `gpt-4o` | Best conversation quality | Medium |
| Agent Planning | `gpt-4o` | Complex reasoning needed | Medium |
| Real-time Help | `gpt-4o-mini` | Fast + cheap | Low |
| Progress Updates | `gpt-4o-mini` | Simple data processing | Low |
| Content Creation | `gpt-4o` | Quality content needed | Medium |
| Quiz Generation | `gpt-4o` | Accuracy critical | Medium |

### **Estimated Monthly Costs (1000 active users):**
- **OpenAI (primary)**: ~$800-1200/month
- **Bedrock (fallback)**: ~$200-400/month
- **Total**: ~$1000-1600/month

## Current Issues Fixed

### ❌ **Previous Problem:**
```
Bedrock API call failed for anthropic.claude-3-sonnet-20240229-v1:0: 
Too many requests, please wait before trying again.
```

### ✅ **Solution Applied:**
1. Changed primary models from Bedrock to OpenAI
2. Updated test scripts to use OpenAI APIs
3. Added fallback mechanisms
4. Optimized model selection for cost/performance

## Next Steps

1. **Test the updated configuration** with OpenAI-first approach
2. **Monitor API usage** and adjust rate limits
3. **Implement fallback logic** in production code
4. **Add cost monitoring** dashboards
5. **Optimize token usage** with better prompts

---

*This strategy ensures reliable, cost-effective operation while maintaining high-quality AI responses for VEDYA users.*
