"""
orchestrator — Multi-agent orchestrator.

This agent delegates to specialist sub-agents using ADK's AgentTool.
Gemini decides which sub-agent to call based on the question.

Sub-agents run in-process (same Python process, not separate HTTP calls).
Session state is shared, so FHIR credentials extracted by this agent's
before_model_callback are available to the healthcare sub-agent's tools.

Sub-agents registered:
  clinical_triage_agent  — Extracts specialties from FHIR active conditions
  staff_agent            — Queries the HR MCP server for available clinicians

To add another sub-agent:
  1. Create a new agent package (copy healthcare_agent or general_agent as a template).
  2. Import its root_agent here.
  3. Add AgentTool(agent=your_new_agent) to the tools list.
  4. Update the instruction to describe when to use it.
"""
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from healthcare_agent.agent import root_agent as triage_agent
from general_agent.agent import root_agent as staff_agent
from shared.fhir_hook import extract_fhir_context

root_agent = Agent(
    name="orchestrator",
    model="gemini-2.5-flash",
    description=(
        "The VitalMesh Routing Orchestrator. It delegates FHIR triage to the Clinical Triage Agent "
        "and handles dispatch placement using the Staff Resource Agent."
    ),
    instruction=(
        "You are the Routing Orchestrator. Your job is to process an incoming dispatch request by:\n"
        "1. Calling clinical_triage_agent to analyze the patient's FHIR record and recommend a medical specialty.\n"
        "2. Passing that recommended specialty to staff_agent to find an available clinician.\n"
        "3. Responding to the user with the final matched clinician and dispatch details."
    ),
    tools=[
        AgentTool(agent=triage_agent),
        AgentTool(agent=staff_agent),
    ],
    # The orchestrator extracts FHIR context once into session state.
    # The healthcare sub-agent's tools read from that same shared state.
    before_model_callback=extract_fhir_context,
)

