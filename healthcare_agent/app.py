"""
healthcare_agent — A2A application entry point.

Start the server with:
    uvicorn healthcare_agent.app:a2a_app --host 0.0.0.0 --port 8001

The agent card is served publicly at:
    GET http://localhost:8001/.well-known/agent-card.json

All other endpoints require an X-API-Key header (see shared/middleware.py).
"""
import os

from a2a.types import AgentSkill
from shared.app_factory import create_a2a_app

from .agent import root_agent

# PRODUCTION: Uncomment the line below for debugging platform URL issues.
# print(os.getenv('PO_PLATFORM_BASE_URL'))

a2a_app = create_a2a_app(
    agent=root_agent,
    name="clinical_triage_agent",
    description=(
        "A clinical triage assistant that analyzes a patient's active conditions "
        "and recent observations to determine the strictly required medical specialty for dispatch."
    ),
    url=os.getenv("HEALTHCARE_AGENT_URL", os.getenv("BASE_URL", "http://localhost:8001")),
    port=8001,
    # LOCAL: Disable API key for local development testing.
    # PRODUCTION: Remove this line (defaults to True) and set API_KEYS in .env.
    require_api_key=False,
    # This URI is the key under which callers send FHIR credentials in the
    # A2A message metadata.  Update to match your Prompt Opinion workspace URL.
    fhir_extension_uri=f"{os.getenv('PO_PLATFORM_BASE_URL', 'http://localhost:5139')}/schemas/a2a/v1/fhir-context",
    # SMART-on-FHIR scopes — one per FHIR resource type accessed by the tools.
    # All are marked required because each tool will fail without its scope.
    fhir_scopes=[
        {"name": "patient/Condition.rs",         "required": True},   # get_active_conditions
        {"name": "patient/Observation.rs",       "required": True},   # get_recent_observations
    ],
    skills=[
        AgentSkill(
            id="active-conditions",
            name="active-conditions",
            description="Get the patient's active conditions and diagnoses.",
            tags=["conditions", "fhir"],
        ),
        AgentSkill(
            id="recent-observations",
            name="recent-observations",
            description="Retrieve recent vitals, lab results, and social history.",
            tags=["observations", "fhir"],
        ),
    ],
)

