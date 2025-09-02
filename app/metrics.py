# app/metrics.py
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from flask import Response

# --- Compteurs principaux ---
# Total des événements 404 ingérés (déjà utilisé via routes.py)
INGESTED_TOTAL = Counter(
    "inspector_ingested_total",
    "404 events ingested",
    ["source", "is_bot"],
)

# Erreurs applicatives lors de l’ingest/DB
ERRORS_TOTAL = Counter(
    "inspector_errors_total",
    "Errors while ingesting/persisting 404 events",
    ["stage"],  # ex: "db", "parse", "unknown"
)

# Durée de traitement d'un /ingest (du POST jusqu'à commit DB)
INGEST_SECONDS = Histogram(
    "inspector_ingest_seconds",
    "Latency of /ingest handler",
    buckets=(0.01, 0.05, 0.1, 0.2, 0.5, 1, 2, 5),
)

# Optionnel: files d'attente ou tâches en cours (si un jour tu ajoutes du background)
INFLIGHT = Gauge(
    "inspector_ingest_inflight",
    "Number of /ingest requests being processed",
)

def prometheus_response():
    """Expose toutes les métriques au format Prometheus/OpenMetrics."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
