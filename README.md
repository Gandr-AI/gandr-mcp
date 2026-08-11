# gandr-mcp

The official **Gandr MCP server**, text to speech inside any MCP-compatible agent (Claude Desktop, Cursor, and friends).

## Tools

| Tool | What it does |
|---|---|
| `synthesize` | Render text to speech (WAV, base64). Voice, language, sample rate 8000-48000, pitch and pacing dials. |
| `list_voices` | The six available voices. |
| `list_languages` | The 23 supported languages and their codes. |
| `get_usage` | Tokens used by the configured key. One token is one character. |

## Install

```bash
pip install gandr-mcp
```

Claude Desktop (add to `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gandr": {
      "command": "gandr-mcp",
      "env": {
        "GANDR_API_KEY": "gnd_..."
      }
    }
  }
}
```

Get a key at [gandr.ai](https://gandr.ai). Docs: [gandr.ai/docs](https://gandr.ai/docs).

---

mcp-name: io.github.Gandr-AI/gandr-mcp
