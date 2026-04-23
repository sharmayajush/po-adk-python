"""
general_agent — Agent definition.

This agent works without any patient context or FHIR server.
It demonstrates the minimal agent pattern: tools + instruction, no callback.

To customise:
  • Change model, description, and instruction below.
  • Add or remove tools from the tools=[...] list.
  • Write new tool functions in general_agent/tools/general.py.
  • If you later need FHIR access, import extract_fhir_context from shared.fhir_hook
    and add it as before_model_callback, then import FHIR tools from shared.tools.
"""
from google.adk.agents import Agent

from .tools.general import query_hr_mcp

root_agent = Agent(
    name="staff_agent",
    model="gemini-2.5-flash",
    description=(
        "A clinical staff resource agent that finds available clinicians "
        "matching a requested specialty using the hospital HR MCP server."
    ),
    instruction=(
        "You are the Staff Resource Agent. "
        "Your job is to receive a required medical specialty query (e.g., Cardiology) "
        "and use the HR database tool to find an available clinician matching that exact specialty. "
        "Respond simply with the clinician's name, ID, and location for dispatch."
    ),
    tools=[
        query_hr_mcp,
    ],
    # No before_model_callback — this agent does not need patient/FHIR context.
    # This is intentional: it demonstrates that the FHIR hook is optional.
)
