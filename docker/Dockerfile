# ============ Stage 1: Build ============
FROM python:3.11-slim as builder

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

# Create non-root user
RUN useradd --create-home -u 1000 tradingbot

WORKDIR /app

# Copy wheels and install
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# Copy app
COPY src/ ./src/
COPY .env .env

RUN chown -R tradingbot:tradingbot /app

USER tradingbot

EXPOSE 8000

CMD ["python", "-u", "src/main.py"]
