# SPDX-License-Identifier: Apache-2.0

import time
from collections import defaultdict

from flask import Blueprint, current_app, json, request

csp_report_bp = Blueprint("csp_report", __name__)

_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT = 100
_RATE_WINDOW = 60


def _is_rate_limited(ip: str) -> bool:
    now = time.monotonic()
    window_start = now - _RATE_WINDOW
    timestamps = _rate_limit_store[ip]
    timestamps[:] = [t for t in timestamps if t > window_start]
    if len(timestamps) >= _RATE_LIMIT:
        return True
    timestamps.append(now)
    return False


@csp_report_bp.route("/csp-report", methods=["POST"])
def csp_report():
    ip = request.remote_addr or "unknown"
    if _is_rate_limited(ip):
        return "", 429

    content_type = request.content_type or ""
    if "application/csp-report" in content_type or "application/json" in content_type:
        try:
            report = request.get_json(force=True, silent=True)
            if report is None:
                return "", 400
        except Exception:
            return "", 400
    else:
        return "", 400

    current_app.logger.warning("CSP violation: %s", json.dumps(report, ensure_ascii=False))
    return "", 204


def register_csp_report(app) -> None:
    app.register_blueprint(csp_report_bp)
