"""gandr-mcp, the Gandr TTS MCP server.

Puts text-to-speech inside any MCP-compatible agent (Claude Desktop, Cursor,
and friends) as three tools: synthesize, list_voices, get_usage.

Run it:
    pip install mcp
    GANDR_API_KEY=gnd_... python server.py

Claude Desktop config:
    {
      "mcpServers": {
        "gandr": {
          "command": "python",
          "args": ["/path/to/server.py"],
          "env": {"GANDR_API_KEY": "gnd_..."}
        }
      }
    }
"""

from __future__ import annotations

import base64
import json
import os
import urllib.request

from mcp.server.fastmcp import FastMCP

DOOR = os.environ.get("GANDR_DOOR", "https://tts.gandr.ai")
KEY = os.environ.get("GANDR_API_KEY", "")

mcp = FastMCP("gandr")

VOICES = ["gandr-ava", "gandr-dane", "gandr-jenny",
          "gandr-leo", "gandr-lewis", "gandr-mia"]


def _call(path: str, body: dict | None) -> bytes:
    req = urllib.request.Request(
        DOOR + path,
        data=json.dumps(body).encode() if body is not None else None,
        method="POST" if body is not None else "GET",
        headers={"x-api-key": KEY, "content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


@mcp.tool()
def synthesize(
    text: str,
    voice: str = "gandr-ava",
    sample_rate: int = 24000,
    temperature: float | None = None,
    cfg_weight: float | None = None,
) -> str:
    """Render text to speech. Returns the WAV audio base64-encoded.

    voice: one of gandr-ava, gandr-dane, gandr-jenny, gandr-leo, gandr-lewis,
    gandr-mia. temperature: 0.1-1.2 pitch range (omit for the tuned default).
    cfg_weight: 0.2-1.0 pacing. sample_rate: 8000-48000.
    """
    if not text.strip():
        return "error: text must not be empty"
    if len(text) > 2000:
        return "error: 2000-character request cap, split the text"
    body: dict = {
        "transcript": text,
        "language": "en",
        "voice": {"mode": "id", "id": voice},
        "output_format": {"sample_rate": sample_rate},
    }
    if temperature is not None:
        body["temperature"] = temperature
    if cfg_weight is not None:
        body["cfg_weight"] = cfg_weight
    try:
        audio = _call("/v1/tts/bytes", body)
    except Exception as e:  # the door's own message is the useful part
        return f"error: {e}"
    return base64.b64encode(audio).decode()


@mcp.tool()
def list_voices() -> str:
    """List the available Gandr voices with their ids."""
    return "\n".join(VOICES)


@mcp.tool()
def get_usage() -> str:
    """Characters used vs quota for the configured API key."""
    try:
        return _call("/v1/usage", None).decode()
    except Exception as e:
        return f"error: {e}"


if __name__ == "__main__":
    if not KEY:
        raise SystemExit("GANDR_API_KEY is not set, get a key at https://gandr.ai")
    mcp.run()
