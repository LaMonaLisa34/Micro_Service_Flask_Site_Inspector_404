from flask import Blueprint, request
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter
from .models import SessionLocal, Hit404, init_db, _domain_from_url

bp = Blueprint("main", __name__)

# compteur prometheus pour vérifier le flux
c_ingested = Counter("inspector_ingested_total", "404 events ingested", ["source", "is_bot"])


@bp.route("/ingest", methods=["POST"])
def ingest():
    payload = request.get_json(force=True)

    url = payload.get("url") or payload.get("path")  # compat si tu envoies juste le path
    if not url:
        return {"error": "missing url/path"}, 400

    referrer = payload.get("referrer")
    ua = payload.get("user_agent")
    ip = payload.get("ip")
    source = payload.get("source", "unknown")

    # heuristiques simples
    ref_dom = _domain_from_url(referrer)
    site_domain = payload.get("site_domain")  # optionnel, sinon déduis côté app
    is_internal = bool(site_domain and ref_dom and ref_dom.endswith(site_domain))

    ua_l = (ua or "").lower()
    is_bot = any(k in ua_l for k in ["bot", "crawler", "spider", "curl", "wget", "python-requests", "uptime", "monitor"])

    evt = Hit404(
        url=url,
        referrer=referrer,
        referrer_domain=ref_dom,
        user_agent=ua,
        ip=ip,
        source=source,
        is_internal=is_internal,
        is_bot=is_bot,
        pattern="unknown",
    )

    db = SessionLocal()
    try:
        db.add(evt)
        db.commit()
    except Exception as e:
        db.rollback()
        return {"error": str(e)}, 500
    finally:
        db.close()

    c_ingested.labels(source=source, is_bot=str(is_bot).lower()).inc()
    return {"status": "ok"}, 201

@bp.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

@bp.route("/health")
def health():
    return {"status": "running"}
