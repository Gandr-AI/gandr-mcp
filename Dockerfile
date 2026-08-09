FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY gandr_mcp ./gandr_mcp
RUN pip install --no-cache-dir .

# The server speaks MCP over stdio, so it needs no port and no inbound network
# to be introspected: a registry check starts it and lists tools over the pipe.
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["gandr-mcp"]
