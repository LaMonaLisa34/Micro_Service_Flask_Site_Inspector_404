from flask import Blueprint, request
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST  # <- tu peux enlever Counter ici
from .models import SessionLocal, Hit404, init_db, _domain_from_url
from .metrics import INGESTED_TOTAL, ERRORS_TOTAL, INGEST_SECONDS, INFLIGHT, prometheus_response

bp = Blueprint("main", __name__)

@bp.route("/ingest", methods=["POST"])
def ingest():
    with INFLIGHT.track_inprogress():           # ↑ gauge en cours
        with INGEST_SECONDS.time():             # ↑ histo latence
            payload = request.get_json(force=True)

            url = payload.get("url") or payload.get("path")
            if not url:
                ERRORS_TOTAL.labels(stage="parse").inc()
                return {"error": "missing url/path"}, 400

            referrer = payload.get("referrer")
            ua = payload.get("user_agent")
            ip = payload.get("ip")
            source = payload.get("source", "unknown")

            ref_dom = _domain_from_url(referrer)
            site_domain = payload.get("site_domain")
            is_internal = bool(site_domain and ref_dom and ref_dom.endswith(site_domain))
            ua_l = (ua or "").lower()
            is_bot = any(k in ua_l for k in ["bot","crawler","spider","curl","wget","python-requests","uptime","monitor"])

            evt = Hit404(
                url=url, referrer=referrer, referrer_domain=ref_dom,
                user_agent=ua, ip=ip, source=source,
                is_internal=is_internal, is_bot=is_bot, pattern="unknown",
            )

            db = SessionLocal()
            try:
                db.add(evt)
                db.commit()
            except Exception as e:
                db.rollback()
                ERRORS_TOTAL.labels(stage="db").inc()
                return {"error": str(e)}, 500
            finally:
                db.close()

            # compteur principal (labels string)
            INGESTED_TOTAL.labels(source=source, is_bot=str(is_bot).lower()).inc()
            return {"status": "ok"}, 201

@bp.route("/metrics")
def metrics():
    return prometheus_response()

@bp.route("/health")
def health():
    return {"status": "running"}
