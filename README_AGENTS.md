# VEDYA Agents - Python Implementation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![VAYU Innovations](https://img.shields.io/badge/Built%20by-VAYU%20Innovations-green.svg)](https://vayu-innovations.com)

## 🎓 Overview

VEDYA is an AI-powered education platform featuring a sophisticated multi-agent system that creates personalized learning experiences. This Python implementation provides a complete agent orchestration system that follows the OpenAI-first strategy outlined in the project specifications.

## 🏗️ Architecture

The system consists of 13 specialized agents working together:

- **SupervisorAgent**: Orchestrates the entire learning process
- **PlannerAgent**: Creates detailed learning plans with milestones
- **ContentCuratorAgent**: Selects and organizes learning materials
- **TeachingAssistantAgent**: Provides real-time guidance and support
- **ProgressTrackerAgent**: Monitors learning progress and engagement
- **AssessmentAgent**: Generates quizzes and evaluates performance
- **FeedbackAgent**: Collects and analyzes user feedback
- **ReportingAgent**: Generates progress and analytics reports
- **ResourceRecommendationAgent**: Suggests additional learning resources
- **ClassroomMonitorAgent**: Ensures focus and curriculum adherence
- **ResearchAssistantAgent**: Finds and evaluates relevant content
- **DatabaseAgent**: Manages all data operations
- **ManagerAgent**: Coordinates inter-agent efforts and verification

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL with pgvector extension
- Redis (for queuing)
- OpenAI API key
- AWS Bedrock access (for fallback models)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd /path/to/vedya
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv vedya_env
   source vedya_env/bin/activate  # On Windows: vedya_env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and configuration
   ```

5. **Run the demo:**
   ```bash
   python demo_agents.py
   ```

## 🔧 Configuration

### Environment Variables

The system uses a comprehensive `.env` file for configuration. Key variables include:

```env
# OpenAI Configuration (Primary)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL_CHAT=gpt-4o
OPENAI_MODEL_EMBEDDING=text-embedding-3-large

# Agent-Specific Models
SUPERVISOR_AGENT_MODEL=gpt-4o
PLANNER_AGENT_MODEL=gpt-4o
TEACHING_ASSISTANT_MODEL=gpt-4o-mini

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/vedya

# Fallback Models (Bedrock)
BEDROCK_SUPERVISOR_FALLBACK=anthropic.claude-3-sonnet-20240229-v1:0
```

### Model Strategy

Following the `MODEL_STRATEGY.md` specifications:

| Agent Type | Primary Model | Fallback Model | Rationale |
|------------|---------------|----------------|-----------|
| Heavy Planning | GPT-4o | Claude 3.5 Sonnet | Complex reasoning needed |
| High-Frequency | GPT-4o-mini | Claude 3 Haiku | Speed and cost optimization |
| Real-time | GPT-4o-mini | Claude 3 Haiku | Low latency required |

## 📚 Usage Examples

### Basic Learning Request

```python
from vedya_agents import VEDYAAgentSystem

# Initialize system
system_config = {
    'database': {...},
    'models': {...}
}
system = VEDYAAgentSystem(system_config)

# Process learning request
user_request = {
    'user_id': 'user_123',
    'objectives': {
        'subject': 'Artificial Intelligence',
        'goals': ['Understand ML basics', 'Learn neural networks'],
        'learning_style': 'visual',
        'difficulty_level': 'beginner'
    }
}

result = await system.process_learning_request(user_request)
```

### Custom Agent Configuration

```python
# Create specialized agent
from vedya_agents import ContentCuratorAgent

agent = ContentCuratorAgent({
    'model': 'gpt-4o',
    'temperature': 0.6,
    'max_tokens': 2500
})

# Execute agent task
result = await agent.execute({
    'plan_id': 'plan_123',
    'user_context': user_context
})
```

### Kanban Board Integration

```python
from vedya_agents import KanbanBoard, KanbanTask, TaskStatus

# Create task
task = KanbanTask(
    id="task_123",
    title="Generate Learning Content",
    assignee_agent="ContentCuratorAgent",
    status=TaskStatus.TODO
)

# Update task progress
await kanban.update_task(
    task.id, 
    TaskStatus.COMPLETED,
    outcomes={'content_generated': True}
)
```

## 🎯 Demo Features

The included demo script (`demo_agents.py`) showcases:

1. **Multi-User Processing**: Handles different learning styles and subjects
2. **Agent Coordination**: Shows real-time agent collaboration
3. **Progress Tracking**: Demonstrates Kanban board updates
4. **Email Generation**: Creates personalized learning summaries
5. **System Monitoring**: Displays agent status and health metrics

### Running the Demo

```bash
python demo_agents.py
```

**Demo Output Example:**
```
🎓 VEDYA - AI-Powered Education Platform
════════════════════════════════════════
Multi-Agent Learning System Demo
By VAYU Innovations

🚀 Initializing VEDYA Agent System...
✅ System Status: operational
🤖 Active Agents: 7
📋 Kanban Board Ready: 0 tasks

🎯 Processing Learning Request 1/3
👤 Student: Alex - AI Enthusiast
📚 Subject: Artificial Intelligence
⏱️  Timeline: 8 weeks
🎨 Learning Style: visual

✅ Learning Plan Created Successfully!
📝 Plan ID: plan_abc123
📊 Tasks Generated: 4
📧 Email Subject: Your Artificial Intelligence Learning Plan is Ready!
```

## 🔄 Integration with Backend

The Python agents are designed to integrate with the Node.js backend through:

### API Endpoints

```typescript
// Backend integration points
POST /agents/supervisor/ingestObjectives  // Trigger agent processing
GET /agents/kanban                       // Get Kanban board status
GET /agents/runs/:id                     // Get agent execution details
```

### Message Queues

```python
# Queue integration
from vedya_agents import VEDYAAgentSystem

# Process via queue
async def process_learning_request_from_queue(message):
    result = await system.process_learning_request(message)
    await send_email_summary(result['email_summary'])
```

### Database Integration

```python
# Database agent handles all persistence
class DatabaseAgent:
    async def store_learning_plan(self, plan_data):
        # Store in PostgreSQL with pgvector
        
    async def store_agent_run(self, run: AgentRun):
        # Store execution logs
        
    async def store_kanban_task(self, task: KanbanTask):
        # Store task updates
```

## 📊 Monitoring & Analytics

### Agent Performance Metrics

- **Execution Times**: Track agent response times
- **Success Rates**: Monitor completion vs failure rates
- **Resource Usage**: Track token consumption and costs
- **User Satisfaction**: Measure learning outcome effectiveness

### Kanban Board Analytics

- **Task Flow**: Visualize task progression through stages
- **Bottlenecks**: Identify agents causing delays
- **Completion Rates**: Track milestone achievement
- **Dependency Analysis**: Monitor task relationships

## 🛡️ Security & Privacy

### Data Protection

- **User Privacy**: All personal data encrypted at rest
- **Content Moderation**: AI-powered content safety checks
- **Access Control**: Role-based permissions for agents
- **Audit Logging**: Complete activity trail for compliance

### Model Safety

- **Input Validation**: Sanitize all user inputs
- **Output Filtering**: Content moderation on AI responses
- **Fallback Mechanisms**: Graceful degradation when models fail
- **Rate Limiting**: Prevent abuse and manage costs

## 🚀 Production Deployment

### Docker Configuration

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "-m", "vedya_agents"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vedya-agents
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vedya-agents
  template:
    spec:
      containers:
      - name: vedya-agents
        image: vedya/agents:latest
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: vedya-secrets
              key: database-url
```

### Health Checks

```python
# Health check endpoint
async def health_check():
    status = await system.get_system_status()
    return {
        'status': 'healthy' if status['system_status'] == 'operational' else 'unhealthy',
        'agents': status['agent_count'],
        'timestamp': datetime.now().isoformat()
    }
```

## 📈 Performance Optimization

### Caching Strategy

- **Content Cache**: Redis cache for learning materials
- **Model Cache**: Cache frequent AI responses
- **User Context**: Session-based context caching
- **Vector Cache**: Cache embeddings for content search

### Scaling Considerations

- **Horizontal Scaling**: Multiple agent instances
- **Load Balancing**: Distribute agent workloads
- **Database Sharding**: Partition user data
- **CDN Integration**: Cache static learning content

## 🧪 Testing

### Unit Tests

```bash
pytest tests/test_agents.py -v
```

### Integration Tests

```bash
pytest tests/test_integration.py -v
```

### Load Testing

```bash
# Test agent performance under load
python tests/load_test_agents.py
```

## 📝 API Documentation

### Agent System API

```python
class VEDYAAgentSystem:
    async def process_learning_request(
        self, 
        user_objectives: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process user learning request through agent system.
        
        Args:
            user_objectives: User learning goals and preferences
            
        Returns:
            Complete learning plan with agent results
        """
```

### Individual Agent APIs

```python
class BaseAgent:
    async def execute(
        self, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute agent-specific functionality.
        
        Args:
            input_data: Agent-specific input parameters
            
        Returns:
            Agent execution results
        """
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black .
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 About VAYU Innovations

VEDYA is proudly built by **VAYU Innovations**, a forward-thinking technology company specializing in AI-powered educational solutions. Our mission is to democratize access to personalized, high-quality education through innovative technology.

### Contact

- **Website**: [https://vayu-innovations.com](https://vayu-innovations.com)
- **Email**: contact@vayu-innovations.com
- **Support**: support@vedya.com

---

**Built with ❤️ by VAYU Innovations**

*Empowering learners worldwide through AI-driven personalized education*
