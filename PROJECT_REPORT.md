# Project Report: Agentic AI Project 01

## Abstract

This project implements two autonomous AI agent systems within a single unified repository: a meeting-to-action assistant and an event planning agent. The first agent converts natural-language meeting transcripts into structured summaries, decisions, action items, and ambiguity assessments. The second agent decomposes a high-level event requirement into planning artifacts across venue, schedule, resources, publicity, and communications. Both systems are built using Python, Streamlit, Pydantic, and the Google Gemini SDK, with a deterministic offline demo mode to ensure robustness during viva presentations and low-connectivity environments.

## Problem Statement

### M1-P2: AI-Powered Meeting-to-Action Assistant
The system accepts a meeting transcript as input and converts it into structured meeting summaries, decisions, assigned tasks, deadlines, and follow-up actions. It also identifies incomplete or ambiguous action items and requests clarification when necessary.

### M1-P7: Autonomous Event Planning Agent
The system accepts a high-level event requirement such as a technical workshop and decomposes it into practical planning activities including venue requirements, schedule, resources, publicity, and participant communication. It maintains the state of the plan and identifies unfinished activities.

## Agentic System Architecture

The architecture is built around a modular Streamlit dashboard that allows the user to choose either project. The dashboard accepts either a user-supplied Gemini API key or offline demo mode. The system routes requests to the relevant project agent, which uses a schema-driven pipeline to produce structured outputs.

### Core Architecture Components

1. User Interface Layer
   - Streamlit-based dashboard
   - Sidebar configuration for API key and mode selection
   - Project selector for M1-P2 and M1-P7

2. Agent Layer
   - Meeting Agent: transcript parser, summarizer, action extractor, ambiguity critic, human-in-the-loop resolver
   - Event Agent: requirement decomposer, planning manager, state tracker, unfinished-task executor

3. Structured Output Layer
   - Pydantic `BaseModel` definitions for strict JSON schema validation
   - Task-level parsing with explicit fields like assignee, deadline, priority, and status

4. Fallback / Viva Layer
   - Offline deterministic facts for demonstrations when the model or network is unavailable
   - No crash behavior if API key is absent

## Methodology

### M1-P2 Methodology
The meeting agent initiates with transcript ingestion and converts the raw transcript into a structured `MeetingAnalysis` object. It identifies decisions and action items, then audits each task for ambiguity. Any task that lacks a clear assignee, deadline, or scope is marked as incomplete and presented to the user for a clarification response. Final action items are then locked and exported as a markdown meeting report.

### M1-P7 Methodology
The event agent starts from a general planning objective such as “organize a workshop.” It decomposes the goal into category-specific workstreams: venue, schedule, resource management, publicity, and communications. Each task is stored with a tracked state in `st.session_state`. The planner identifies unfinished items and can generate execution-ready artifact drafts to progress the plan when tasks remain incomplete.

## Pydantic Schema Design

The use of Pydantic is central to the project’s reliability. Structured schema definitions ensure that generated AI outputs match expected fields and types.

### Example Schema for Meeting Tasks

```python
class ActionItem(BaseModel):
    task_id: str
    task: str
    assignee: str
    deadline: str
    priority: str
    status: str
```

This structure guarantees that the agent’s output includes all required fields for downstream processing and UI display.

### Example Schema for Event Planning

```python
class PlanningTask(BaseModel):
    task_id: str
    category: str
    activity: str
    priority: str
    timeline: str
```

This schema provides consistent tracking across all event planning sub-tasks.

## Sample Outputs

### Meeting Agent Sample Result

- Executive summary: Team aligned on December release timeline and feature freeze.
- Decisions: Launch date fixed, freeze begins Friday, security review scheduled.
- Action items: OAuth middleware, database migration, dashboard UI, audit documentation.
- Ambiguities: Database migration ownership and deadline; audit documentation ownership and deadline.

### Event Agent Sample Result

- Event title: 2-Day Hands-On Agentic AI & LLM Systems Workshop
- Venue requirements: auditorium, Wi-Fi, screens, audio equipment
- Schedule: Day 1 and Day 2 module breakdown
- Publicity plan: posters, circulars, social media teasers
- State tracking: unfinished tasks identified and draft execution steps generated

## Implementation Notes

- Streamlit renders a dashboard with multiple tabs and stateful UI logic.
- All generated outputs are validated against strict schemas.
- Offline mode ensures the application never crashes when the API is unavailable.
- The system demonstrates the core principles of agentic AI: autonomy, state memory, decomposition, and human-in-the-loop correction.

## Conclusion

This project demonstrates a practical implementation of autonomous AI agents for two realistic tasks: converting meetings into operational action plans and orchestrating a full event planning workflow. It combines model-driven intelligence, schema validation, and user-interactive correction, making it suitable as a strong academic submission and viva demonstration.

## Viva-Voce Preparation Sheet

### Q1. What is the purpose of the Meeting-to-Action Assistant?
It converts transcripts into structured actions, decisions, and follow-up tasks and flags unclear assignments.

### Q2. Why is ambiguity detection important?
Because vague tasks like “someone should do this soon” cannot be executed reliably without ownership and deadlines.

### Q3. How does the human-in-the-loop process work?
The agent asks the user to resolve missing details and then locks a final plan.

### Q4. What does Pydantic add to the solution?
It ensures generated outputs match required schemas and prevents malformed model responses.

### Q5. What is the role of `st.session_state` in the event planning agent?
It tracks which tasks are complete or unfinished and preserves state as the user interacts with the app.

### Q6. Why use a fallback demo mode?
It guarantees the application functions during demos or when no internet or API key is available.

### Q7. What are the major planning domains in the event agent?
Venue, schedule, resources, publicity, and participant communication.

### Q8. What does the event agent generate for unfinished tasks?
A ready-to-use execution artifact or communication/checklist draft.

### Q9. Why is the app called “agentic” rather than just “AI”?
Because it performs autonomous decomposition, state tracking, decision-making, and task completion workflows beyond basic prompting.

### Q10. What makes the project suitable for viva presentation?
It demonstrates real-world reasoning, structured outputs, human oversight, and resilient fallback behavior.

## Final Remarks

The system is designed to be both academically rigorous and practically usable. It reflects the spirit of agentic AI by combining computation, structured reasoning, and interactive workflow management within a single cohesive dashboard.
