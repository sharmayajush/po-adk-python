"""
healthcare_agent — Agent definition.

This agent has read-only access to a patient's FHIR R4 record.
FHIR credentials (server URL, bearer token, patient ID) are injected via the
A2A message metadata by the caller (e.g. Prompt Opinion) and extracted into
session state by extract_fhir_context before every LLM call.

To customise:
  • Change model, description, and instruction below.
  • Add or remove tools from the tools=[...] list.
  • Add new FHIR tools in shared/tools/fhir.py and export from shared/tools/__init__.py.
  • Add non-FHIR tools in shared/tools/ or locally in a tools/ folder here.
"""
from google.adk.agents import Agent

from shared.fhir_hook import extract_fhir_context
from shared.tools import (
    get_active_conditions,
    get_active_medications,
    get_patient_demographics,
    get_recent_observations,
)

root_agent = Agent(
    name="clinical_triage_agent",
    model="gemini-2.5-flash",
    description=(
        "A clinical triage assistant that analyzes a patient's active conditions "
        "and recent observations to determine the strictly required medical specialty for dispatch."
    ),
    instruction=(
        "You are the Clinical Triage Agent. Your job is to analyze the patient's FHIR record "
        "using your tools (especially active conditions and recent observations). "
        "Based on the patient's acute symptoms (like myocardial infarction or stroke), determine which medical specialty "
        "is most urgently required (e.g., 'Cardiology', 'Neurology', 'Trauma Surgery'). "
        "Respond simply with the required specialty and a brief 1-sentence justification, format: 'SPECIALTY: [Specialty]\nJUSTIFICATION: [Reason]'"
    ),
    tools=[
        get_active_conditions,
        get_recent_observations,
    ],
    # Runs before every LLM call.
    # Reads fhir_url, fhir_token, and patient_id from A2A message metadata
    # and writes them into session state so tools can call the FHIR server.
    before_model_callback=extract_fhir_context,
)
