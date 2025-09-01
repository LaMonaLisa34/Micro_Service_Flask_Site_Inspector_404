FROM python:3.11-slim

# dépendances système nécessaires à psycopg2 + netcat pour le wait
RUN apt-get update && apt-get install -y --no-install-recommends \
      gcc libpq-dev netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# deps Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# code
COPY . .

EXPOSE 5000
