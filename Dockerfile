# Alkira Knowledge Plane MCP — streamable-HTTP container.
# Deployed to Cloud Run in the alkira-sales GCP project.
# Stdio entry is unused in this build path; it ships separately via uvx.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY alkira_kb_mcp ./alkira_kb_mcp

RUN pip install --no-cache-dir ".[http]"

# Cloud Run injects PORT (default 8080). The console script honors it.
EXPOSE 8080

ENTRYPOINT ["alkira-kb-mcp-http"]
