FROM python:3.12.3-bookworm

WORKDIR /app/backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    iputils-ping \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app:/app/frontend \
    DJANGO_SETTINGS_MODULE=card_game.settings \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
