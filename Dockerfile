# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY automation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Set transport mode to HTTP
ENV TRANSPORT=http

COPY . .

EXPOSE 8081

CMD ["python", "-m", "server"]
