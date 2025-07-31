# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r automation/requirements.txt
CMD ["python", "-m", "server"]