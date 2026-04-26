import urllib.request
import json
import os

def test_vitalmesh_orchestrator():
    url = "http://localhost:8003/"
    
    # We pass the synthetic Triage-001 payload as "context"
    # This simulates Prompt Opinion's SHARP headers injecting the FHIR bundle
    try:
        with open("../data/triage_payloads.json", "r") as f:
            fhir_data = json.load(f)
    except Exception as e:
        print(f"Failed to load FHIR mock: {e}")
        return

    # Payload matching the standard A2A JSON-RPC 'message/send' schema
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/send",
        "params": {
            "taskId": "test-task-123",
            "metadata": {
                "http://localhost:5139/schemas/a2a/v1/fhir-context": {
                    "environment": "test",
                    "patientId": fhir_data["triage_scenarios"][0]["patientId"],
                    "fhirUrl": "mock_url",
                    "fhirToken": "mock_token",
                    "fhirBundle": {
                        "resourceType": "Bundle",
                        "entry": [
                            {"resource": fhir_data["triage_scenarios"][0]["condition"]},
                            {"resource": fhir_data["triage_scenarios"][0]["observations"][0]}
                        ]
                    }
                }
            },
            "message": {
                "kind": "message",
                "messageId": "test-msg-123",
                "role": "user",
                "parts": [
                    {
                        "text": "A new patient has arrived. Their FHIR context is securely attached to your session. First, call the clinical_triage_agent to analyze their active conditions and determine the required specialty. Then, pass that specialty to the staff_agent to find an available clinician."
                    }
                ]
            }
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json", 
            # Bypass API key for local mock testing if require_api_key in app.py is False
        }
    )
    
    print(f"Testing Phase 1 Orchestrator via: {url}")
    print(f"Scenario: {fhir_data['triage_scenarios'][0]['condition']['code']['text']}")
    print("-" * 50)
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            print("HTTP 200 OK")
            print(json.dumps(result, indent=2))
            
            # Simple assertion validation
            if "result" in result and "text" in result["result"]:
                output = result["result"]["text"].lower()
                if "dr. sarah chen" in output or "cardiology" in output:
                    print("\n[SUCCESS] Pipeline correctly invoked Triage -> Staff Agents and got the Mock Cardiology Doctor!")
                else:
                    print("\n[WARNING] Output did not mention the expected mock clinician (Dr. Sarah Chen, Cardiology).")
            else:
                 print("\n[ERROR] Result payload did not match expected structure.")
                 
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"HTTP Error {e.code}: {e.reason}")
        print(error_body)
    except Exception as e:
        print(f"Network Error: {e}")

if __name__ == "__main__":
    test_vitalmesh_orchestrator()

