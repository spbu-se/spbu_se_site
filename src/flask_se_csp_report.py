# SPDX-License-Identifier: Apache-2.0

from flask import Blueprint, current_app, json, request

from flask_se_rate_limit import is_rate_limited

csp_report_bp = Blueprint("csp_report", __name__)

_RATE_LIMIT = 100
_RATE_WINDOW = 60


def _is_rate_limited(ip: str) -> bool:
    return is_rate_limited(ip, _RATE_LIMIT, _RATE_WINDOW)


@csp_report_bp.route("/csp-report", methods=["POST"])
def csp_report():
    ip = request.remote_addr or "unknown"
    if _is_rate_limited(ip):
        current_app.logger.warning("csp-report rejected: rate-limited ip=%s", ip)
        return "", 429

    content_type = request.content_type or ""
    if (
        "application/csp-report" in content_type
        or "application/json" in content_type
        or "application/reports+json" in content_type
    ):
        report = request.get_json(force=True, silent=True)
        if report is None:
            current_app.logger.warning("csp-report rejected: empty body ip=%s", ip)
            return "", 400
    else:
        current_app.logger.warning(
            "csp-report rejected: unsupported content-type %r ip=%s", content_type, ip
        )
        return "", 400

    current_app.logger.warning("CSP violation: %s", json.dumps(report, ensure_ascii=False))
    return "", 204


def register_csp_report(app) -> None:
    app.register_blueprint(csp_report_bp)
