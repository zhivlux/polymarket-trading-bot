# ============ Stage 1: Builder ============
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ============ Stage 2: Runtime ============
FROM python:3.11-slim

RUN apt-get update && apt-get install --no-install-recommends -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home -u 1000 tradingbot

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

COPY src/ ./src/

RUN chown -R tradingbot:tradingbot /app
USER tradingbot

CMD ["python", "-u", "src/main.py"]
