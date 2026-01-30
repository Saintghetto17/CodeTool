# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install git (required for GitPython)
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Avoid "detected dubious ownership" errors for mounted volumes in CI/demo.
RUN git config --system --add safe.directory '*'

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Use PYTHONPATH instead of installing package (simpler for Docker)
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd -m -u 1000 codeagent && \
    chown -R codeagent:codeagent /app

USER codeagent

# Set entrypoint
ENTRYPOINT ["python", "-m", "code_agent.cli"]
CMD ["--help"]

