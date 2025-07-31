# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY automation/requirements.txt automation/requirements.txt
RUN pip install --no-cache-dir -r automation/requirements.txt
COPY . .
CMD ["python", "-m", "server"]
