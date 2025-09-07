---
applyTo: '**'
---
# Context
You are helping me build a AI-powered education platform named VEDYA"
The app will be part of **VAYU Innovations**, and it should follow:
- Modern, clean UI
- Scalable backend
- Modular and reusable code
- Easy to extend in the future
Since its a vayu innovation, it should be declared at the bottom of the screen and should stay fixed at a point which gives the users the information about the collaboration. 

Assume this will eventually be used in production.

---

# Project Goal
we are building a web application where users can log in, access personalized learning content, and track progress.
The application will leverage AI to provide personalized recommendations and insights and teach users with interactive content.

1. The user arrives at the platform and is greeted with a chatbox where an LLM (via the OpenAI API) takes user input and provides relevant responses.
    a. The user is greeted and asked what they want to learn.
       Example:
       {"ai": "Hi there, what do you want to learn today?", "user": "I am here to learn about AI."}
    b. OpenAI interacts with the user and collects information about learning goals and preferences, subjects of interest, and preferred learning styles. It asks follow-up questions to gather more details and clarify the user's needs.
    c. Based on the user's input, OpenAI generates a summary of the user's learning objectives and preferences and sends it to the Supervisor Agent.

2. The Supervisor Agent receives the user’s summarized objectives and delegates work to specialized agents. All agents must:
    - Keep the shared Kanban board current (tasks, status, blockers, outcomes).
    - Coordinate with peer agents when dependencies exist.
    - Surface risks and key decisions promptly.
    - Maintain user privacy and data integrity.

    The agents and their responsibilities are:
    a. Planner Agent — Produces a detailed learning plan and initializes the Kanban structure (epics, milestones, tasks).
    b. Content Curator Agent — Selects and organizes relevant learning materials; collaborates with the Research Assistant.
    c. Progress Tracker Agent — Monitors progress and engagement; updates metrics and Kanban status.
    d. Assessment Agent — Creates quizzes and assessments; records results and updates the Kanban accordingly.
    e. Feedback Agent — Gathers user feedback; synthesizes insights and improvement suggestions.
    f. Reporting Agent — Generates progress and engagement reports; posts summaries to the Kanban.
    g. Teaching Assistant Agent — Provides real-time guidance and support; logs interventions and tips to the Kanban.
    h. Resource Recommendation Agent — Suggests additional resources based on progress and interests.
    i. Classroom Monitor Agent — Ensures focus and adherence to the curriculum; flags drift or distractions.
    j. Research Assistant Agent — Finds, evaluates, and summarizes relevant papers, articles, and references.
    k. Database Agent — Manages user data, learning materials, and progress records with accuracy and consistency.
    l. Experience Agent — Curates and personalizes the overall learning experience; proposes adjustments to better fit user needs.
    m. Manager Agent — Coordinates inter-agent efforts, ensures completeness, verifies database updates and task closure, and reports overall status to the Supervisor.

3. The user will be sent an email summarizing their learning plan and next steps, next class, and progress details in a user-friendly format. It will include a summary of today’s interactions and progress, quiz results, AI’s observations, feedback to improve, and a rating on a scale of 1–10.


# Frontend
- Framework: nextjs
- Styling: tailwind
- Components:
  - [Login page]
  - [Dashboard]
  - [Course cards / Content section]
  - [Navbar + Footer]
- Connect via API calls to backend endpoints.

## Structure
- Tech: Next.js (App Router, TypeScript), Tailwind CSS.
- Goals: modern UI, modular components, protected routes, fixed VAYU Innovations badge.


# Agent Models (LLM/RAG choices)

## Conversation data storage (Aurora PostgreSQL + pgvector)
We will persist long-running chat context and learning interactions for future NN training and high-recall retrieval:
- Entities: conversations, participants, messages, embeddings, tool calls, attachments, moderation, summaries, training datasets/examples
- Vector search: pgvector IVFFLAT over message and summary embeddings (primary embedding model: text-embedding-3-large, 3072 dims)
- Notes: If you choose a different embedding model, adjust vector dimension accordingly

SQL (migration snippet)
- Base LLMs
    - Heavy planning/coordination: GPT-4o or Claude 3.5 Sonnet
    - Low-latency chat/explanations: GPT-4o-mini or Llama 3.1 8B Instruct (self-hosted)
    - Reasoning (optional for rubric/grading): o3-mini or Claude 3.5 Sonnet
- Embeddings: text-embedding-3-large (OpenAI) or bge-m3 (OSS)
- Reranker (optional for higher precision): Cohere Rerank v3 or Jina Reranker
- Knowledge store: Postgres + pgvector (preferred) or Qdrant
- Safety: Content moderation via provider’s moderation model (e.g., omnimoderation-latest) before/after LLM calls

Agent-to-model mapping
- Supervisor Agent, Manager Agent: GPT-4o (planning, tool-use); fallback GPT-4o-mini for status updates
- Planner Agent: GPT-4o with structured output (JSON) to create epics/milestones/tasks
- Content Curator Agent: RAG pipeline (pgvector/Qdrant + embeddings + reranker) + GPT-4o for synthesis
- Research Assistant Agent: Same RAG stack; GPT-4o-mini for quick summaries, GPT-4o for long-form synthesis
- Progress Tracker Agent: Rules + small instruct model (GPT-4o-mini or Llama 3.1 8B) for trend notes
- Assessment Agent: GPT-4o for quiz generation and rubric-based evaluation; deterministic templates to reduce drift
- Feedback Agent: GPT-4o-mini summarization; sentiment and actionable insights
- Reporting Agent: GPT-4o-mini to compile weekly/daily reports from logs and metrics
- Teaching Assistant Agent: GPT-4o-mini for real-time Q&A; optional code-exec sandbox tool for STEM
- Resource Recommendation Agent: Hybrid search (BM25 + vector) + small model for explanation text
- Classroom Monitor Agent: Small classifier for focus/drift flags; escalate to GPT-4o for ambiguous cases
- Database Agent: No LLM; service layer with strict schemas and transactions
- Experience Agent: GPT-4o-mini to propose UX/content tweaks from feedback + A/B results
- Manager Agent: GPT-4o for overall status, task closure verification, and inter-agent coordination

# Backend
- Tech stack
    - Runtime: Node.js (TypeScript)
    - Framework: Express + modular services
    - ORM: Prisma
    - DB: PostgreSQL (pgvector for RAG)
    - Search (optional): Meilisearch/OpenSearch
    - Object storage: S3-compatible
    - API schema: OpenAPI (Swagger)
    - Validation: zod
    - Auth: Clerk's authentication
    - Observability: pino logging, OpenTelemetry traces/metrics

- Service/modules layout
    - auth: login, signup, refresh, OAuth, role/permission checks
    - users: profile, preferences, progress snapshots
    - courses: CRUD courses/lessons, content ingestion
    - assessments: quiz gen, attempts, grading, rubrics
    - progress: tracking events, completion, streaks
    - recommendations: RAG/hybrid ranking, personalization
    - agents: supervisor/orchestrator, agent runs, Kanban updates
    - reports: weekly/daily summaries, exports, email PDFs
    - email: transactional mail (learning plan, results)
    - files: uploads, signed URLs
    - search: keyword + vector endpoints

- Suggested routes (JSON: { success, data, error })
    - POST /auth/login, POST /auth/signup, POST /auth/refresh, GET /auth/me
    - GET /users/:id, PATCH /users/:id
    - GET /courses, POST /courses, GET /courses/:id, PATCH /courses/:id
    - POST /courses/:id/lessons, GET /courses/:id/lessons
    - POST /assessments/generate, POST /assessments/:id/attempt, POST /assessments/:id/grade
    - GET /progress/:userId, POST /progress/event
    - GET /recommendations/:userId
    - POST /agents/supervisor/ingestObjectives, GET /agents/kanban, GET /agents/runs/:id
    - POST /reports/compile, GET /reports/:id
    - POST /email/sendPlan
    - POST /search/query

- Events and queues
    - Queues: emailQueue, reportQueue, assessmentQueue, ingestionQueue
    - Pub/Sub events: UserSignedUp, PlanCreated, AssessmentCompleted, ProgressUpdated, ReportReady

- Data model (core tables)
    - User(id, email, hash, role, prefs)
    - Course(id, title, desc, meta)
    - Lesson(id, courseId, title, contentRef)
    - Enrollment(userId, courseId, status)
    - Progress(id, userId, courseId, lessonId, pct, lastAt)
    - Quiz(id, courseId, specJSON, createdByAgentRunId)
    - Question(id, quizId, stem, choicesJSON, answerKey)
    - Attempt(id, quizId, userId, answersJSON, score, rubricJSON)
    - Plan(id, userId, summary, goalsJSON)
    - KanbanTask(id, planId, title, status, assigneeAgent)
    - AgentRun(id, agent, inputJSON, outputJSON, status)
    - Recommendation(id, userId, itemsJSON, rationale)
    - Feedback(id, userId, text, sentiment)
    - Report(id, userId, range, contentRef)

- Directory structure
    - /backend
        - src/
            - app.ts, server.ts
            - config/
            - db/ (prisma client, migrations)
            - middleware/ (auth, rate-limit, cors, error)
            - modules/
                - auth/, users/, courses/, lessons/, assessments/, progress/
                - recommendations/, agents/, reports/, email/, files/, search/
            - rag/ (embeddings, vector store, retrievers, reranker)
            - queues/, events/, utils/
        - prisma/schema.prisma
        - openapi.yaml
        - package.json, .env

- Security and prod
    - Rate limiting, input validation, CSRF for cookies, CORS
    - Secrets in .env + vault in prod
    - DB migrations CI step, health/readiness probes
    - Backups for Postgres and object storage

---

# General Guidelines
- Put frontend and backend in separate folders (`/frontend`, `/backend`)
- Use `.env` for secrets and configs
- Add comments only for non-trivial logic
- Use placeholder data where real logic isn’t implemented yet
- Code should be modular and production-ready


🔴 CORE LEADERSHIP AGENTS
Supervisor Agent = gpt-5 ✅
Manager Agent = o1-pro ✅
Planner Agent = o3 ✅
🟡 EDUCATION & CONTENT AGENTS
Content Curator Agent = chatgpt-4o-latest ✅
Teaching Assistant Agent = chatgpt-4o-latest ✅
Assessment Agent = gpt-4o ✅
Research Assistant Agent = o4-mini-deep-research ✅
🟢 MONITORING & ANALYTICS GROUP
Progress Tracker Agent = gpt-4o-2024-08-06 ✅
Feedback Agent = gpt-4o-2024-08-06 ✅
Reporting Agent = gpt-4o-2024-08-06 ✅
🟢 SUPPORT & EXPERIENCE GROUP
Resource Recommendation Agent = gpt-4o ✅
Experience Agent = gpt-4o ✅
Classroom Monitor Agent = gpt-4-0314 ✅
🟢 DATA MANAGEMENT
Database Agent = gpt-3.5-turbo ✅