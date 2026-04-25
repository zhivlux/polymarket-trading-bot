# ============ Stage 1: Builder ============
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Build wheels
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ============ Stage 2: Runtime ============
FROM python:3.11-slim

# Install only runtime deps
RUN apt-get update && apt-get install --no-install-recommends -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home -u 1000 tradingbot

WORKDIR /app

# Copy wheels and requirements from builder
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# Copy application code ONLY (NOT .env!)
COPY src/ ./src/
COPY .github/ ./.github/

# Set ownership
RUN chown -R tradingbot:tradingbot /app

USER tradingbot

# Port untuk monitoring
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Entry point
CMD ["python", "-u", "src/main.py"]
