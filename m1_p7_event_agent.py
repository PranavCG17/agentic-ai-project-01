from typing import List

import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class PlanningTask(BaseModel):
    task_id: str = Field(description="Unique ID like T1, T2")
    category: str = Field(description="One of: Venue, Schedule, Resources, Publicity, Participant Communication")
    activity: str = Field(description="Concrete actionable activity")
    priority: str = Field(description="High, Medium, or Low")
    timeline: str = Field(description="Target timeline, e.g., T-14 Days, T-7 Days, Event Day")


class EventPlan(BaseModel):
    event_title: str
    event_overview: str
    venue_requirements: List[str]
    schedule: List[str]
    resources: List[str]
    publicity_plan: List[str]
    communication_plan: List[str]
    tasks: List[PlanningTask]


DEMO_EVENT_PLAN = EventPlan(
    event_title="2-Day Hands-On Agentic AI & LLM Systems Workshop",
    event_overview="A technical workshop for 120 engineering students covering multi-agent orchestration, structured outputs, tool calling, and live deployment.",
    venue_requirements=[
        "Main Seminar Auditorium with seating capacity for 120+ participants and individual power sockets.",
        "High-speed dedicated Wi-Fi APs capable of handling 150 concurrent API connections.",
        "Dual projection screens, lapel microphones, and podium HDMI/USB-C setup."
    ],
    schedule=[
        "Day 1 (09:30 AM - 12:30 PM): Foundations of Agentic AI, Prompt Engineering & Structured Outputs.",
        "Day 1 (01:30 PM - 04:30 PM): Hands-on Lab — Building Tool-Calling & Reflection Agents.",
        "Day 2 (09:30 AM - 12:30 PM): Stateful Multi-Agent Systems & Memory Management.",
        "Day 2 (01:30 PM - 04:30 PM): Mini-Hackathon, Live Project Demos & Certificate Distribution."
    ],
    resources=[
        "120 Gemini API sandbox keys / quota tokens pre-configured for lab exercises.",
        "GitHub starter repository with boilerplate code and environment setup instructions.",
        "6 Student Volunteer Mentors for debugging Python/Streamlit setup issues.",
        "Printed attendance sheets, ID lanyards, and participation certificates."
    ],
    publicity_plan=[
        "Launch registration poster across department notice boards and WhatsApp/Discord student groups (T-10 Days).",
        "Send official department circular via HOD and faculty coordinators (T-7 Days).",
        "Post speaker spotlight and workshop syllabus teaser on LinkedIn and Instagram (T-4 Days)."
    ],
    communication_plan=[
        "T-5 Days: Registration confirmation email with laptop prerequisites (Python 3.10+, VS Code, Git).",
        "T-1 Day: Reminder email with venue map, check-in QR code, and GitHub starter repo link.",
        "Post-Event: Feedback form link, certificate download portal, and slide deck repository."
    ],
    tasks=[
        PlanningTask(task_id="T1", category="Venue", activity="Book Main Seminar Auditorium and request IT team to stress-test Wi-Fi bandwidth", priority="High", timeline="T-14 Days"),
        PlanningTask(task_id="T2", category="Resources", activity="Prepare GitHub starter repository and verify Gemini API lab keys for 120 students", priority="High", timeline="T-10 Days"),
        PlanningTask(task_id="T3", category="Publicity", activity="Release workshop poster and Google Form registration link across student channels", priority="High", timeline="T-10 Days"),
        PlanningTask(task_id="T4", category="Schedule", activity="Finalize session slide decks and hands-on lab checkpoints with speakers", priority="Medium", timeline="T-7 Days"),
        PlanningTask(task_id="T5", category="Participant Communication", activity="Send prerequisite installation guide (Python, Streamlit, Git) to registered attendees", priority="High", timeline="T-5 Days"),
        PlanningTask(task_id="T6", category="Resources", activity="Brief 6 teaching assistants on troubleshooting common environment errors", priority="Medium", timeline="T-3 Days"),
        PlanningTask(task_id="T7", category="Venue", activity="Perform audio-visual, projector, and extension cord check in the auditorium", priority="Medium", timeline="T-1 Day"),
        PlanningTask(task_id="T8", category="Participant Communication", activity="Send final Day-1 morning reminder and post-workshop feedback & certificate link", priority="Low", timeline="Event Day")
    ]
)


def render_event_agent(api_key: str, demo_mode: bool):
    st.title("🗓️ M1-P7: Autonomous Event Planning Agent")
    st.caption("Agentic Pipeline: High-Level Goal Input ➔ Multi-Domain Task Decomposition ➔ Persistent State Memory ➔ Unfinished Task Executor")

    event_goal = st.text_input(
        "🎯 High-Level Event Requirement:",
        value="Organize a 2-day hands-on Agentic AI & LLM Systems Technical Workshop for 120 engineering students"
    )

    if "m1_p7_plan" not in st.session_state:
        st.session_state.m1_p7_plan = None
    if "m1_p7_task_state" not in st.session_state:
        st.session_state.m1_p7_task_state = {}
    if "m1_p7_draft" not in st.session_state:
        st.session_state.m1_p7_draft = None

    if st.button("🧠 Decompose Requirement & Initialize Agent State", type="primary"):
        st.session_state.m1_p7_draft = None
        if demo_mode:
            st.session_state.m1_p7_plan = DEMO_EVENT_PLAN
            st.session_state.m1_p7_task_state = {t.task_id: (idx < 2) for idx, t in enumerate(DEMO_EVENT_PLAN.tasks)}
            st.toast("Initialized decomposed plan & state memory in Offline Viva Demo Mode", icon="⚡")
        elif not api_key:
            st.error("Please enter a Gemini API Key in the sidebar or enable Offline Viva Demo Mode.")
        else:
            client = genai.Client(api_key=api_key)
            with st.spinner("Agent decomposing high-level goal into domain plans and stateful tasks..."):
                prompt = f"""
                You are an Autonomous Event Planning AI Agent.
                Decompose the following high-level event requirement into:
                1. Venue requirements
                2. Detailed Schedule
                3. Resource checklist
                4. Publicity strategy
                5. Participant communication plan
                6. 8 structured, trackable PlanningTasks across all 5 categories with task_id (T1..T8), priority, and timeline.

                Event Requirement: {event_goal}
                """
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=EventPlan,
                        temperature=0.2,
                    ),
                )
                plan = EventPlan.model_validate_json(response.text)
                st.session_state.m1_p7_plan = plan
                st.session_state.m1_p7_task_state = {t.task_id: False for t in plan.tasks}

    if st.session_state.m1_p7_plan:
        plan: EventPlan = st.session_state.m1_p7_plan
        st.header(f"📌 {plan.event_title}")
        st.write(plan.event_overview)

        tabs = st.tabs([
            "✅ Stateful Task Tracker & Unfinished Monitor",
            "🏛️ Venue & Resources",
            "⏰ Schedule",
            "📢 Publicity & Participant Comms"
        ])

        with tabs[0]:
            st.subheader("📊 Agent Plan State & Unfinished Activity Identifier")
            st.caption("Toggle tasks below to update the Agent's persistent state memory:")

            unfinished_tasks: List[PlanningTask] = []
            for t in plan.tasks:
                is_done = st.checkbox(
                    f"**[{t.task_id}] ({t.category} | Priority: {t.priority} | {t.timeline})** — {t.activity}",
                    value=st.session_state.m1_p7_task_state.get(t.task_id, False),
                    key=f"task_chk_{t.task_id}"
                )
                st.session_state.m1_p7_task_state[t.task_id] = is_done
                if not is_done:
                    unfinished_tasks.append(t)

            total = len(plan.tasks)
            completed = total - len(unfinished_tasks)
            pct = int((completed / total) * 100) if total else 0
            st.progress(completed / total if total else 0, text=f"Agent State Progress: {completed}/{total} Activities Completed ({pct}%)")

            st.divider()
            if unfinished_tasks:
                st.warning(f"🚨 Agent State Audit: {len(unfinished_tasks)} Unfinished Activity(s) Detected")
                unfinished_options = {f"[{t.task_id}] ({t.priority}) {t.activity}": t for t in unfinished_tasks}
                selected_label = st.selectbox("Select an unfinished activity for the Agent to autonomously execute/draft:", list(unfinished_options.keys()))
                selected_task = unfinished_options[selected_label]

                if st.button("🤖 Autonomously Generate Execution Artifact for Selected Unfinished Task"):
                    if demo_mode or not api_key:
                        st.session_state.m1_p7_draft = f"""### 🛠️ Autonomous Execution Artifact for `{selected_task.task_id}`
**Category:** {selected_task.category} | **Target Timeline:** {selected_task.timeline}

**Subject / Action Header:** Immediate Execution — {selected_task.activity}

**Generated Actionable Template / Checklist:**
1. **Objective:** Complete *{selected_task.activity}* prior to {selected_task.timeline}.
2. **Ready-to-Send Communication / Checklist Draft:**
   > Dear Team / Stakeholders,
   > Regarding the upcoming **{plan.event_title}**, please find the finalized action items for **{selected_task.category}**:
   > - Action Required: {selected_task.activity}
   > - Priority Level: {selected_task.priority}
   > - Verification Checkpoint: Confirm completion status in the Event Planning Tracker by {selected_task.timeline}.
"""
                    else:
                        client = genai.Client(api_key=api_key)
                        with st.spinner(f"Agent generating ready-to-use artifact for {selected_task.task_id}..."):
                            draft_resp = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=f"Event: {plan.event_title}. Generate a complete, ready-to-use email, checklist, or execution document to immediately complete this unfinished task: [{selected_task.category}] {selected_task.activity}"
                            )
                            st.session_state.m1_p7_draft = draft_resp.text

                if st.session_state.m1_p7_draft:
                    st.info(st.session_state.m1_p7_draft)
            else:
                st.success("🎉 All planning activities are marked complete in Agent State Memory!")

        with tabs[1]:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🏛️ Venue Requirements")
                for v in plan.venue_requirements:
                    st.markdown(f"- {v}")
            with c2:
                st.subheader("🧰 Resource Checklist")
                for r in plan.resources:
                    st.markdown(f"- {r}")

        with tabs[2]:
            st.subheader("⏰ Event Schedule")
            for s in plan.schedule:
                st.markdown(f"- {s}")

        with tabs[3]:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("📢 Publicity Plan")
                for p in plan.publicity_plan:
                    st.markdown(f"- {p}")
            with c2:
                st.subheader("✉️ Participant Communication")
                for c in plan.communication_plan:
                    st.markdown(f"- {c}")
