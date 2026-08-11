"""gandr-mcp, the Gandr TTS MCP server.

Puts text-to-speech inside any MCP-compatible agent (Claude Desktop, Cursor,
and friends) as four tools: synthesize, list_voices, list_languages, get_usage.

Run it:
    pip install gandr-mcp
    GANDR_API_KEY=gnd_... gandr-mcp

Claude Desktop config:
    {
      "mcpServers": {
        "gandr": {
          "command": "gandr-mcp",
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

LANGUAGES = {
    "ar": "Arabic", "cs": "Czech", "da": "Danish", "de": "German",
    "el": "Greek", "en": "English", "es": "Spanish", "fi": "Finnish",
    "fr": "French", "hi": "Hindi", "it": "Italian", "ja": "Japanese",
    "ko": "Korean", "nl": "Dutch", "no": "Norwegian", "pl": "Polish",
    "pt": "Portuguese", "ro": "Romanian", "ru": "Russian", "sv": "Swedish",
    "tr": "Turkish", "uk": "Ukrainian", "zh": "Chinese",
}


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
    language: str = "en",
    sample_rate: int = 24000,
    temperature: float | None = None,
    cfg_weight: float | None = None,
) -> str:
    """Render text to speech. Returns the WAV audio base64-encoded.

    voice: one of gandr-ava, gandr-dane, gandr-jenny, gandr-leo, gandr-lewis,
    gandr-mia. language: a two-letter code, call list_languages for the 23
    supported. Any voice can speak any of them. temperature: 0.1-1.2 pitch
    range (omit for the tuned default). cfg_weight: 0.2-1.0 pacing.
    sample_rate: 8000-48000.
    """
    if not KEY:
        return "error: GANDR_API_KEY is not set, get a key at https://gandr.ai"
    if not text.strip():
        return "error: text must not be empty"
    if len(text) > 2000:
        return "error: 2000-character request cap, split the text"
    if language not in LANGUAGES:
        return (f"error: unsupported language {language!r}, "
                f"call list_languages for the {len(LANGUAGES)} supported")
    body: dict = {
        "transcript": text,
        "language": language,
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
def list_languages() -> str:
    """List the language codes synthesize accepts, with their names."""
    return "\n".join(f"{code}\t{name}"
                     for code, name in sorted(LANGUAGES.items()))


@mcp.tool()
def get_usage() -> str:
    """Tokens used vs quota for the configured API key. One token is one character."""
    if not KEY:
        return "error: GANDR_API_KEY is not set, get a key at https://gandr.ai"
    try:
        return _call("/v1/usage", None).decode()
    except Exception as e:
        return f"error: {e}"


def main() -> None:
    """Console entrypoint."""
    mcp.run()


if __name__ == "__main__":
    main()
