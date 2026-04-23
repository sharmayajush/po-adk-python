"""
orchestrator — A2A application entry point.

Start the server with:
    uvicorn orchestrator.app:a2a_app --host 0.0.0.0 --port 8003

The agent card is served publicly at:
    GET http://localhost:8003/.well-known/agent-card.json

All other endpoints require an X-API-Key header (see shared/middleware.py).
"""
import os

from a2a.types import AgentSkill
from shared.app_factory import create_a2a_app

from .agent import root_agent

a2a_app = create_a2a_app(
    agent=root_agent,
    name="orchestrator",
    description=(
        "The VitalMesh Routing Orchestrator. It delegates FHIR triage to the Clinical Triage Agent "
        "and handles dispatch placement using the Staff Resource Agent."
    ),
    url=os.getenv("ORCHESTRATOR_URL", os.getenv("BASE_URL", "http://localhost:8003")),
    port=8003,
    # LOCAL: Disable API key for local development testing.
    # PRODUCTION: Remove this line (defaults to True) and set API_KEYS in .env.
    require_api_key=False,
    # The orchestrator supports FHIR context so it can pass credentials through
    # to the healthcare sub-agent.
    fhir_extension_uri=f"{os.getenv('PO_PLATFORM_BASE_URL', 'http://localhost:5139')}/schemas/a2a/v1/fhir-context",
    # Same SMART scopes as healthcare_agent — the orchestrator delegates to it
    # in-process and the credentials flow through shared session state.
    fhir_scopes=[
        {"name": "patient/Condition.rs",         "required": True},   # via clinical_triage_agent
        {"name": "patient/Observation.rs",       "required": True},   # via clinical_triage_agent
    ],
    skills=[
        AgentSkill(
            id="clinical-dispatch-routing",
            name="clinical-dispatch-routing",
            description="Routes dispatch requests by triaging the patient condition and pulling available HR staff.",
            tags=["dispatch", "orchestrator", "routing"],
        ),
    ],
)


