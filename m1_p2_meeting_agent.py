import json
from typing import List

import pandas as pd
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    task_id: str = Field(description="Unique ID like A1, A2")
    task: str = Field(description="Specific task description")
    assignee: str = Field(description="Assigned person or 'Unassigned'")
    deadline: str = Field(description="Deadline or 'Not Specified'")
    priority: str = Field(description="High, Medium, or Low")
    status: str = Field(description="'Clear' if both assignee and deadline are explicit, else 'Ambiguous/Incomplete'")


class AmbiguityItem(BaseModel):
    item_id: str = Field(description="ID matching the ambiguous ActionItem, e.g., A2")
    ambiguous_statement: str = Field(description="Quote or summary of the ambiguous task")
    missing_parameters: str = Field(description="What is missing: Assignee, Deadline, or Scope")
    clarification_question: str = Field(description="Direct question asking the user to resolve the missing info")


class MeetingAnalysis(BaseModel):
    executive_summary: str
    decisions: List[str]
    action_items: List[ActionItem]
    follow_up_actions: List[str]
    ambiguities: List[AmbiguityItem]


DEFAULT_TRANSCRIPT = """Rahul (Product Manager): Welcome everyone to the Q4 FinTech App Release sync. First, we have officially decided to set the production launch date to November 20th, 2026 and freeze all new feature requests starting Friday.
Ananya (Backend Lead): Got it. I will complete the OAuth2 token rotation and rate-limiting middleware by November 6th.
Rahul (Product Manager): Great. Also, someone needs to migrate the staging PostgreSQL database and configure automated backups soon.
Vikram (Frontend Dev): I will finalize the responsive dashboard UI components by November 8th. By the way, we should probably send the security compliance documentation to the external audit team at some point.
Rahul (Product Manager): Agreed. Let's schedule a penetration testing review meeting next Wednesday and share the staging credentials with QA."""


DEMO_MEETING_DATA = MeetingAnalysis(
    executive_summary="The team aligned on the Q4 FinTech App Release scheduled for November 20th, 2026, with a feature freeze starting Friday. Backend security middleware and frontend dashboard tasks were assigned, while database migration and audit documentation require ownership and deadline clarification.",
    decisions=[
        "Production launch date locked for November 20th, 2026.",
        "Complete feature freeze begins this Friday.",
        "Penetration testing review meeting to be held next Wednesday."
    ],
    action_items=[
        ActionItem(task_id="A1", task="Complete OAuth2 token rotation and rate-limiting middleware", assignee="Ananya", deadline="November 6, 2026", priority="High", status="Clear"),
        ActionItem(task_id="A2", task="Migrate staging PostgreSQL database and configure automated backups", assignee="Unassigned", deadline="Not Specified ('soon')", priority="High", status="Ambiguous/Incomplete"),
        ActionItem(task_id="A3", task="Finalize responsive dashboard UI components", assignee="Vikram", deadline="November 8, 2026", priority="Medium", status="Clear"),
        ActionItem(task_id="A4", task="Send security compliance documentation to external audit team", assignee="Unassigned", deadline="Not Specified ('at some point')", priority="Medium", status="Ambiguous/Incomplete")
    ],
    follow_up_actions=[
        "Schedule penetration testing review meeting for next Wednesday.",
        "Distribute staging environment credentials to the QA team."
    ],
    ambiguities=[
        AmbiguityItem(
            item_id="A2",
            ambiguous_statement="Someone needs to migrate the staging PostgreSQL database and configure automated backups soon.",
            missing_parameters="Missing Assignee ('someone') and Vague Deadline ('soon')",
            clarification_question="Who is responsible for migrating the staging PostgreSQL database, and what is the exact target completion date?"
        ),
        AmbiguityItem(
            item_id="A4",
            ambiguous_statement="We should probably send the security compliance documentation to the external audit team at some point.",
            missing_parameters="Missing Assignee ('we') and Undefined Deadline ('at some point')",
            clarification_question="Which team member will send the security compliance documentation to the audit team, and by what date?"
        )
    ]
)


def render_meeting_agent(api_key: str, demo_mode: bool):
    st.title("📋 M1-P2: AI-Powered Meeting-to-Action Assistant")
    st.caption("Agentic Pipeline: Transcript Ingestion ➔ Structured Extraction ➔ Ambiguity Critic Agent ➔ Human-in-the-Loop Clarification Resolver")

    transcript = st.text_area("📄 Meeting Transcript Input:", value=DEFAULT_TRANSCRIPT, height=190)

    if "m1_p2_analysis" not in st.session_state:
        st.session_state.m1_p2_analysis = None
    if "m1_p2_resolved" not in st.session_state:
        st.session_state.m1_p2_resolved = None

    if st.button("🚀 Execute Meeting-to-Action Agent", type="primary"):
        st.session_state.m1_p2_resolved = None
        if demo_mode:
            st.session_state.m1_p2_analysis = DEMO_MEETING_DATA
            st.toast("Loaded deterministic analysis via Offline Viva Demo Mode", icon="⚡")
        elif not api_key:
            st.error("Please provide a Gemini API Key in the sidebar or enable Offline Viva Demo Mode.")
        else:
            client = genai.Client(api_key=api_key)
            with st.spinner("Agent 1 parsing transcript & Agent 2 auditing for ambiguous action items..."):
                prompt = f"""
                You are an autonomous Meeting-to-Action AI Agent.
                Analyze the meeting transcript below:
                1. Generate a concise executive summary and extract firm decisions.
                2. Extract all action items with task_id, task, assignee, deadline, priority, and status ('Clear' vs 'Ambiguous/Incomplete').
                3. Identify every incomplete or ambiguous action item (missing owner, vague deadline like 'soon' or 'at some point', or unclear scope) and generate a direct clarification question for the user.

                Transcript:
                {transcript}
                """
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=MeetingAnalysis,
                        temperature=0.1,
                    ),
                )
                st.session_state.m1_p2_analysis = MeetingAnalysis.model_validate_json(response.text)

    if st.session_state.m1_p2_analysis:
        res: MeetingAnalysis = st.session_state.m1_p2_analysis

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📌 Executive Summary")
            st.info(res.executive_summary)
            st.subheader("✅ Decisions Made")
            for dec in res.decisions:
                st.markdown(f"- {dec}")
        with c2:
            st.subheader("🔄 Follow-Up Actions")
            for fol in res.follow_up_actions:
                st.markdown(f"- {fol}")

        st.subheader("📊 Extracted Action Items (Initial Agent Pass)")
        df = pd.DataFrame([a.model_dump() for a in res.action_items])
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("⚠️ Ambiguity Critic & Human-in-the-Loop Clarification")
        if not res.ambiguities:
            st.success("No ambiguous action items detected! All tasks have clear owners and deadlines.")
        else:
            st.warning(f"Critic Agent flagged {len(res.ambiguities)} ambiguous/incomplete task(s) requiring clarification:")
            clarification_inputs = {}
            for idx, amb in enumerate(res.ambiguities):
                with st.expander(f"❓ [{amb.item_id}] {amb.missing_parameters} — \"{amb.ambiguous_statement}\"", expanded=True):
                    st.markdown(f"**Agent Clarification Request:** {amb.clarification_question}")
                    default_ans = (
                        "Assign to DevOps Engineer Karthik, deadline November 4, 2026"
                        if idx == 0 else
                        "Assign to Rahul (PM), deadline November 12, 2026"
                    )
                    clarification_inputs[amb.item_id] = st.text_input(
                        f"Your Response for {amb.item_id}:",
                        value=default_ans,
                        key=f"clarify_input_{amb.item_id}"
                    )

            if st.button("✨ Resolve Ambiguities & Lock Final Action Plan"):
                updated_items = []
                for item in res.action_items:
                    item_copy = item.model_copy(deep=True)
                    if item_copy.task_id in clarification_inputs and clarification_inputs[item_copy.task_id].strip():
                        user_reply = clarification_inputs[item_copy.task_id]
                        if demo_mode or not api_key:
                            item_copy.assignee = f"Resolved ({user_reply.split(',')[0].replace('Assign to ', '').strip()})"
                            item_copy.deadline = user_reply.split(',')[-1].replace('deadline', '').strip() if ',' in user_reply else user_reply
                            item_copy.status = "Clear (Resolved via HITL)"
                        updated_items.append(item_copy)
                    else:
                        updated_items.append(item_copy)

                if not demo_mode and api_key:
                    client = genai.Client(api_key=api_key)
                    with st.spinner("Agent merging clarifications into final action plan..."):
                        merge_prompt = f"""
                        Update the following Action Items JSON list using the user's clarifications.
                        Set status to 'Clear (Resolved via HITL)' for resolved items.
                        Original Items: {json.dumps([i.model_dump() for i in res.action_items])}
                        User Clarifications by task_id: {json.dumps(clarification_inputs)}
                        """

                        class ResolvedList(BaseModel):
                            items: List[ActionItem]

                        merge_resp = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=merge_prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                response_schema=ResolvedList,
                                temperature=0.1
                            )
                        )
                        updated_items = ResolvedList.model_validate_json(merge_resp.text).items

                st.session_state.m1_p2_resolved = updated_items

        if st.session_state.m1_p2_resolved:
            st.success("🎯 All ambiguities resolved! Final verified Action Plan:")
            final_df = pd.DataFrame([i.model_dump() for i in st.session_state.m1_p2_resolved])
            st.dataframe(final_df, use_container_width=True, hide_index=True)

            md_export = f"# Meeting Action Report\n\n## Summary\n{res.executive_summary}\n\n## Final Action Items\n"
            for i in st.session_state.m1_p2_resolved:
                md_export += f"- **[{i.task_id}] {i.task}** | Owner: {i.assignee} | Due: {i.deadline} | Status: {i.status}\n"
            st.download_button("📥 Download Final Minutes (.md)", data=md_export, file_name="meeting_action_plan.md")
