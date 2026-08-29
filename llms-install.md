# gandr-mcp: installation guide for AI agents

This document gives an AI agent (Cline, Claude Desktop, Cursor, or any MCP client) everything needed to install and configure the Gandr MCP server without human intervention.

## What this server does

Text to speech inside any MCP-compatible agent. 23 languages, six voices, every render watermarked. It exposes four tools over stdio:

- `synthesize`: render text to speech (WAV, returned as base64). Voice, language, sample rate 8000-48000, pitch and pacing dials.
- `list_voices`: the six available voices.
- `list_languages`: the 23 supported languages and their codes.
- `get_usage`: tokens used by the configured key. One token is one character.

## Prerequisites

1. Python 3.10 or newer.
2. Either `uv` (recommended, provides `uvx`) or `pip`.
3. A Gandr API key. Sign up at https://gandr.ai and copy the key from the dashboard. Keys start with `gnd_`. The free tier includes 50,000 tokens. Paid is $10 a month for one million tokens.

## Option A: uvx (recommended, zero install step)

If `uvx` is available on the machine, no install command is needed. Add this to the MCP client configuration:

```json
{
  "mcpServers": {
    "gandr": {
      "command": "uvx",
      "args": ["gandr-mcp"],
      "env": {
        "GANDR_API_KEY": "gnd_YOUR_KEY_HERE"
      }
    }
  }
}
```

## Option B: pip

```bash
pip install gandr-mcp
```

Then add:

```json
{
  "mcpServers": {
    "gandr": {
      "command": "gandr-mcp",
      "env": {
        "GANDR_API_KEY": "gnd_YOUR_KEY_HERE"
      }
    }
  }
}
```

If `gandr-mcp` is not on PATH after the pip install (common inside virtual environments), use the module form with the same interpreter that ran pip:

```json
{
  "mcpServers": {
    "gandr": {
      "command": "python",
      "args": ["-m", "gandr_mcp.server"],
      "env": {
        "GANDR_API_KEY": "gnd_YOUR_KEY_HERE"
      }
    }
  }
}
```

## Where the configuration goes

- Cline (VS Code): open the MCP Servers panel, choose Configure MCP Servers, and add the `gandr` entry to the `mcpServers` object in `cline_mcp_settings.json`.
- Claude Desktop: `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`).
- Cursor: `.cursor/mcp.json` in the project, or the global MCP settings.

Replace `gnd_YOUR_KEY_HERE` with the real key. `GANDR_API_KEY` is the only required setting.

## Verify the installation

1. Restart or reload the MCP client so it picks up the new server.
2. The client should list four tools: `synthesize`, `list_voices`, `list_languages`, `get_usage`.
3. Call `list_voices`. It returns the six voices.
4. Call `synthesize` with a short text. It returns base64 WAV audio.

## Troubleshooting

- `command not found: uvx`: install uv (https://docs.astral.sh/uv/) or use Option B.
- `command not found: gandr-mcp` after pip install: use the module form in Option B, or check that the pip and python binaries belong to the same environment.
- Auth errors from tools: the key is missing or wrong. It must start with `gnd_` and be set as `GANDR_API_KEY` in the server's `env` block. Keys come from https://gandr.ai.
- The server needs outbound HTTPS access to `tts.gandr.ai`.
