from google.adk.tools import ToolContext
import urllib.request
import json
import logging
import os

logger = logging.getLogger(__name__)

# ── MCP Server URL Configuration ──────────────────────────────────────────────
# LOCAL: The po-community-mcp FastMCP server runs on port 8000 by default.
#        The Streamable HTTP endpoint is at /mcp (FastMCP default).
# PRODUCTION: Set MCP_HR_SERVER_URL to your deployed MCP server URL.
# Example: MCP_HR_SERVER_URL=https://your-mcp-server.example.com/mcp
MCP_HR_SERVER_URL = os.getenv("MCP_HR_SERVER_URL", "http://localhost:8000/mcp")


def query_hr_mcp(specialty: str, tool_context: ToolContext) -> dict:
    """Queries the external Hospital HR MCP Server for available clinicians of the given specialty."""
    logger.info("Executing MCP tool query_hr_mcp for specialty: %s", specialty)

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "SearchAvailableClinicians",
            "arguments": {"specialty": specialty}
        }
    }

    req = urllib.request.Request(
        MCP_HR_SERVER_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        logger.error("MCP Server Error: %s", e)
        # Fallback for hackathon testing if MCP server is down or unreachable
        return {
            "status": "error",
            "message": f"Could not reach MCP HR server at {MCP_HR_SERVER_URL}. Error: {str(e)}",
            "fallback_info": f"Please assume Dr. Test (Available) is assigned to {specialty} for the demo."
        }
