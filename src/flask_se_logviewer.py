# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
import re
import threading
import time
from collections import deque
from html import escape

from flask import Blueprint, g, request
from flask_login import current_user

from flask_se_rate_limit import is_rate_limited

log_viewer_bp = Blueprint("log_viewer", __name__)

_RATE_LIMIT = 10
_RATE_WINDOW = 60
_ADMIN_ROLE_LEVEL = 5

_MAX_ENTRIES = 2000
_buffer: deque[dict[str, str | None]] = deque(maxlen=_MAX_ENTRIES)
_buffer_lock = threading.Lock()

_SCRATCH_DIR = os.environ.get("SE_SCRATCH_DIR", ".tmp")
_LOG_FILE_PATH = os.path.join(_SCRATCH_DIR, "server-errors.log")

_PATH_PATTERN = re.compile(
    r"""
    (?:
        (?:/[a-zA-Z][a-zA-Z0-9_]{0,31}/)        # filesystem path roots like /home/ /var/ /tmp/ /opt/
        [^\s:"'<>|()]*                            # rest of the path
        |
        (?:[A-Za-z]:\\[^\s:"'<>|()\\]*\\[^\s:"'<>|()\\]*)  # Windows paths
    )
    """,
    re.VERBOSE,
)
_IP_PATTERN = re.compile(r"(\d{1,3}\.){3}\d{1,3}")
_EMAIL_PATTERN = re.compile(r"[\w.+-]+@([\w-]+\.[\w.]+)")
_HEX_TOKEN_PATTERN = re.compile(r"[a-fA-F0-9]{16,}")


def _sanitize(text: str) -> str:
    return _HEX_TOKEN_PATTERN.sub(
        "<token>",
        _EMAIL_PATTERN.sub(
            r"***@\1",
            _IP_PATTERN.sub(
                "x.x.x.x",
                _PATH_PATTERN.sub("<deploy-path>", text),
            ),
        ),
    )


def _read_logs_from_file() -> list[dict[str, str | None]]:
    """Read last 100 log entries from the shared file (cross-worker safe)."""
    if not os.path.exists(_LOG_FILE_PATH):
        return []
    try:
        with open(_LOG_FILE_PATH, encoding="utf-8") as f:
            lines = f.readlines()
        entries = []
        for raw_line in reversed(lines):
            ln = raw_line.strip()
            if not ln:
                continue
            try:
                entry = json.loads(ln)
                entries.append(entry)
            except json.JSONDecodeError:
                continue
            if len(entries) >= 100:
                break
    except Exception as exc:
        logging.getLogger(__name__).debug("Log file read failed: %s", exc)
        entries = []
    return entries


class LogViewerHandler(logging.Handler):
    def __init__(self, level=logging.WARNING) -> None:
        super().__init__(level)
        os.makedirs(_SCRATCH_DIR, exist_ok=True)

    def emit(self, record: logging.LogRecord) -> None:
        entry = {
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": _sanitize(record.getMessage()),
            "traceback": _sanitize(self.format(record)) if record.exc_info else None,
        }
        with _buffer_lock:
            _buffer.append(entry)
        try:
            with open(_LOG_FILE_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:  # noqa: S110
            pass


def register_log_viewer(app) -> None:
    handler = LogViewerHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logging.getLogger("flask_se").addHandler(handler)
    logging.getLogger("flask_se").setLevel(logging.WARNING)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.WARNING)

    app.register_blueprint(log_viewer_bp)


@log_viewer_bp.route("/logs")
def logs():
    ip = request.remote_addr or "unknown"
    if _is_rate_limited(ip):
        return "", 429

    entries = _read_logs_from_file()
    latest = entries[0] if entries else (_buffer[-1] if _buffer else None)

    try:
        authed = (
            not g.get("_login_disabled", False)
            and current_user.is_authenticated
            and current_user.role >= _ADMIN_ROLE_LEVEL
        )
    except Exception:
        authed = False

    nonce = getattr(g, "csp_nonce", "")

    if authed:
        return _render_logs(entries, nonce), 200, {"Content-Type": "text/html; charset=utf-8"}

    return _public_preview(latest, nonce), 200, {"Content-Type": "text/html; charset=utf-8"}


def _is_rate_limited(ip: str) -> bool:
    return is_rate_limited(ip, _RATE_LIMIT, _RATE_WINDOW)


def _public_preview(latest: dict[str, str | None] | None, nonce: str) -> str:
    if latest:
        msg = escape(latest["message"] or "")
        tb = latest.get("traceback")
        extra = ""
        if tb:
            lines = [ln for ln in tb.split("\n") if ln.strip()]
            if lines:
                exc_line = escape(lines[-1].strip())
                extra = f'<p class="exception">{exc_line}</p>'
        line = f'<p class="error">{msg}</p>{extra}'
    else:
        line = '<p class="empty">Нет записей об ошибках.</p>'

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Журнал ошибок</title>
<style nonce="{nonce}">
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:"SF Mono","Consolas","Liberation Mono",monospace;font-size:14px;background:#1e1e2e;color:#cdd6f4;padding:2rem;text-align:center;}}
h1{{font-size:1.2rem;color:#b4befe;margin-bottom:1rem;}}
p{{margin:1rem 0;}}
.error{{color:#f38ba8;background:#181825;padding:1rem;border-radius:6px;word-break:break-word;text-align:left;}}
.exception{{color:#fab387;background:#1e1e2e;padding:0.5rem 1rem;border-radius:6px;word-break:break-word;text-align:left;font-size:0.9rem;border:1px solid #313244;}}
.empty{{color:#6c7086;}}
.admin-link{{margin-top:2rem;font-size:0.85rem;}}
.admin-link a{{color:#89b4fa;}}
</style>
</head>
<body>
<h1>Последняя ошибка</h1>
{line}
<div class="admin-link"><a href="/logs">Полный журнал (только для администраторов)</a></div>
</body>
</html>"""


def _render_logs(entries: list[dict[str, str | None]], nonce: str) -> str:
    rows = "".join(_log_row(e, nonce) for e in entries)
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Журнал ошибок</title>
<style nonce="{nonce}">
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:"SF Mono","Consolas","Liberation Mono",monospace;font-size:13px;background:#1e1e2e;color:#cdd6f4;padding:1rem;}}
h1{{font-size:1.3rem;margin-bottom:1rem;color:#b4befe;}}
table{{width:100%;border-collapse:collapse;}}
th,td{{text-align:left;padding:6px 8px;border-bottom:1px solid #313244;vertical-align:top;}}
th{{background:#181825;color:#a6adc8;font-weight:600;position:sticky;top:0;}}
tr:hover td{{background:#313244;}}
.level-WARNING{{color:#f9e2af;}}
.level-ERROR{{color:#f38ba8;font-weight:700;}}
.level-CRITICAL{{color:#eba0ac;font-weight:700;background:#450a0a;}}
.logger{{color:#a6adc8;font-size:0.9em;}}
.message{{word-break:break-word;}}
.tb-summary{{color:#89b4fa;cursor:pointer;font-size:0.85em;}}
.tb-details{{background:#11111b;padding:8px 12px;border-radius:4px;margin-top:4px;white-space:pre-wrap;font-size:0.9em;color:#bac2de;line-height:1.4;}}
.tb-details summary{{cursor:pointer;color:#89b4fa;}}
.empty{{text-align:center;padding:3rem;color:#6c7086;font-size:1rem;}}
.footer{{margin-top:1rem;color:#6c7086;font-size:0.8rem;text-align:center;}}
.footer a{{color:#89b4fa;}}
</style>
</head>
<body>
<h1>&#128270; Журнал ошибок</h1>
<table>
<thead><tr><th>Время</th><th>Уровень</th><th>Логгер</th><th>Сообщение</th></tr></thead>
<tbody>
{rows if entries else '<tr><td colspan="4" class="empty">Нет записей</td></tr>'}
</tbody>
</table>
<div class="footer">Показаны последние {len(entries)} записей &middot; <a href="/logs">Обновить</a></div>
</body>
</html>"""


def _log_row(entry: dict[str, str | None], nonce: str) -> str:  # noqa: ARG001
    level = escape(entry["level"] or "")
    logger = escape(entry["logger"] or "")
    message = escape(entry["message"] or "")
    ts = escape(entry["time"] or "")
    tb = entry.get("traceback")
    if tb:
        tb_esc = escape(tb)
        trace = f"""<details class="tb-details"><summary class="tb-summary">&#9654; Traceback</summary>{tb_esc}</details>"""
    else:
        trace = ""
    return f"""<tr class="level-{level}">
<td>{ts}</td>
<td><span class="level-{level}">{level}</span></td>
<td class="logger">{logger}</td>
<td class="message">{message}{trace}</td>
</tr>"""
