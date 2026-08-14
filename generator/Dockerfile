# ==============================================================================
# Stage 1: Build & Dependency Installation
# ==============================================================================
FROM python:3.12-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies if required for compiling C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt-get/lists/*

# Copy dependency definition
COPY requirements.txt .

# Install dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# Stage 2: Final Runtime Image
# ==============================================================================
FROM python:3.12-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Ensure src is automatically included on PYTHONPATH
    PYTHONPATH="/app/src" \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Create a non-root user for security best practices
RUN adduser --disabled-password --gecos "" appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application source code and pyproject.toml
COPY pyproject.toml .
COPY src/ ./src/

# Change ownership of app directory to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose FastAPI default port
EXPOSE 8000

# Health check to ensure container status monitoring works in Docker Compose
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Launch FastAPI app using Uvicorn
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]