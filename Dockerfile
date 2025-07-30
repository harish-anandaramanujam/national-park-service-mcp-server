# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-alpine

# Install the project into `/app`
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies (simplified for Smithery)
RUN uv sync --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# MCP servers typically run on stdio, but if Smithery needs a port:
ENV PORT=8080
EXPOSE 8080

# Run the MCP server
CMD ["python", "nps.py"]