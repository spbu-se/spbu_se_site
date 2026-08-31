# SPDX-License-Identifier: Apache-2.0

import os
import pathlib
import re
import time
from datetime import UTC, date, datetime
from unicodedata import normalize


def site_deploy_date() -> str:
    """Deploy date (YYYY-MM-DD): ``SE_SITE_LASTMOD`` at deploy, today in dev/tests.

    Single source for the sitemap static lastmod AND the asset cache-busting
    version (``?v=``) so both stay in lockstep with the release date.
    """
    return os.environ.get("SE_SITE_LASTMOD", date.today().isoformat())


SECRET_KEY_FILE = os.path.join(pathlib.Path(__file__).parent, "configs/flask_se_secret.conf")


def read_secret_from_file(filepath: str, *, fallback_len: int = 24) -> str:
    """Read a secret from a config file, or generate a dev-only fallback key.

    The fallback must never be a filesystem path — it is opaque random key
    material used only when the config file is absent (e.g. fresh checkout).
    """
    if os.path.exists(filepath):
        with open(filepath) as file:
            value = file.read().strip()
        if value:
            return value
    return os.urandom(fallback_len).hex()


SECRET_KEY = read_secret_from_file(SECRET_KEY_FILE)
MAIL_PASSWORD_FILE = os.path.join(pathlib.Path(__file__).parent, "configs/flask_se_mail.conf")
VK_CLIENT_ID = "8051225"
VK_SECRET_FILE = os.path.join(pathlib.Path(__file__).parent, "configs/flask_se_vk_secret.conf")
THESIS_SECRET_FILE = os.path.join(
    pathlib.Path(__file__).parent,
    "configs/flask_se_thesis.conf",
)
# Env override makes the secret deterministic per process (tests set it so the
# value is identical across module instances under xdist; production leaves it
# unset and reads the config file).
SECRET_KEY_THESIS = os.environ.get("SE_THESIS_SECRET") or read_secret_from_file(
    THESIS_SECRET_FILE,
    fallback_len=16,
)
MAPS_KEY_FILE = os.path.join(pathlib.Path(__file__).parent, "configs/flask_se_maps.conf")
YANDEX_MAPS_KEY_ENV = "SE_YANDEX_MAPS_KEY"
GOOGLE_MAPS_KEY_ENV = "SE_GOOGLE_MAPS_KEY"


def _read_maps_config_file() -> dict[str, str]:
    """Parse the gitignored maps config file into ``{PROVIDER_KEY: value}``.

    The file holds one ``KEY=value`` line per provider, e.g.::

        YANDEX_MAPS_KEY=...
        GOOGLE_MAPS_KEY=...

    A legacy single-value file (the whole trimmed content was the Google key)
    is still honoured so an already-provisioned key keeps working.
    """
    if not os.path.exists(MAPS_KEY_FILE):
        return {}
    with open(MAPS_KEY_FILE) as file:
        lines = [line.strip() for line in file]
    result: dict[str, str] = {}
    for line in lines:
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
        elif not result:
            result[GOOGLE_MAPS_KEY_ENV] = line
    return result


def maps_config() -> tuple[str, str]:
    """Active map provider + its browser key, by priority Yandex then Google.

    Returns ``(provider, key)`` or ``("", "")`` when neither key is
    configured — the lazy maps loader then never requests an API and the map
    templates render the "map source not set" placeholder instead. Keys are not
    secrets (they ship to the browser in the maps URL), but they stay out of
    the repo like the other per-host configs.
    """
    file_keys = _read_maps_config_file()
    yandex = os.environ.get(YANDEX_MAPS_KEY_ENV) or file_keys.get("YANDEX_MAPS_KEY", "")
    google = os.environ.get(GOOGLE_MAPS_KEY_ENV) or file_keys.get("GOOGLE_MAPS_KEY", "")
    if yandex:
        return "yandex", yandex
    if google:
        return "google", google
    return "", ""


METRICA_ID_FILE = os.path.join(pathlib.Path(__file__).parent, "configs/flask_se_metrica.conf")
METRICA_ID_ENV = "SE_YANDEX_METRICA_ID"
_METRICA_ID_RE = re.compile(r"^\d+$")


def metrica_id() -> str:
    """Yandex Metrica counter id (digits only), or ``""`` when not configured.

    Reads the gitignored ``configs/flask_se_metrica.conf`` file (the raw
    counter number) or the ``SE_YANDEX_METRICA_ID`` env override (env wins,
    mirroring the maps-key pattern). A missing or malformed value renders no
    analytics snippet at all, so the site stays tracking-free until an admin
    provisions a counter — GTM was removed in the same release (see
    ``docs/PRIVACY_COMPLIANCE.md``).
    """
    value = os.environ.get(METRICA_ID_ENV) or ""
    if not value and os.path.exists(METRICA_ID_FILE):
        with open(METRICA_ID_FILE) as file:
            value = file.read().strip()
    if _METRICA_ID_RE.fullmatch(value):
        return value
    return ""


# Consent-cookie name. The value is a comma-separated list of granted
# categories (e.g. ``essential,statistics``), written by JS and read by Flask
# so analytics snippets render only after explicit acceptance.
CONSENT_COOKIE_NAME = "se_consent"


def consent_categories() -> dict[str, bool]:
    """Consent categories: ``{name: enabled-by-default}``.

    ``essential`` (strictly-necessary cookies like ``se_session``) is always
    on. Optional categories — ``statistics`` (Yandex Metrica) and
    ``marketing`` (GTM/Google, currently removed from the site) — start
    disabled and are enabled only by explicit visitor acceptance via the
    consent banner. The server gates every analytics snippet on the granted
    ``se_consent`` cookie, so nothing loads before consent (see
    ``docs/PRIVACY_COMPLIANCE.md`` §4.1).
    """
    return {
        "essential": True,
        "statistics": False,
        "marketing": False,
    }


SQLITE_DATABASE_NAME: str = "se.db"
SQLITE_DATABASE_PATH: str = pathlib.Path("databases/").absolute().as_posix()
SQLITE_DATABASE_URI: str = (
    "sqlite:///" + pathlib.Path(SQLITE_DATABASE_PATH, SQLITE_DATABASE_NAME).as_posix()
)

if os.path.exists(MAIL_PASSWORD_FILE):
    with open(MAIL_PASSWORD_FILE) as file:
        mail_password = file.read().rstrip()
else:
    mail_password = os.urandom(16).hex()
MAIL_PASSWORD = mail_password

if os.path.exists(VK_SECRET_FILE):
    with open(VK_SECRET_FILE) as file:
        vk_secret = file.read().rstrip()
else:
    vk_secret = ""
VK_CLIENT_SECRET = vk_secret


current_data = datetime.today().strftime("%Y-%m-%d")
SQLITE_DATABASE_BACKUP_NAME = "se_backup_" + current_data + ".db"

type_id_string = [
    "",
    "Bachelor_Report",
    "Bachelor_Thesis",
    "Master_Thesis",
    "Autumn_practice_2nd_year",
    "Spring_practice_2nd_year",
    "Autumn_practice_3rd_year",
    "Spring_practice_3rd_year",
    "Production_practice",
    "Pre_graduate_practice",
]

_windows_device_files = (
    "CON",
    "AUX",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "LPT1",
    "LPT2",
    "LPT3",
    "PRN",
    "NUL",
)

_filename_strip_re = re.compile(r"[^A-Za-zа-яА-ЯёЁ0-9_.-]")


def secure_filename(filename: str) -> str:
    if isinstance(filename, str):
        if len(filename) > 255:
            filename = filename[:255]
        filename = normalize("NFKD", filename)

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")

    filename = str(_filename_strip_re.sub("", "_".join(filename.split()))).strip("._")

    if os.name == "nt" and filename and filename.split(".")[0].upper() in _windows_device_files:
        filename = "_{filename}"

    return filename


# https://felx.me/2021/08/29/improving-the-hacker-news-ranking-algorithm.html
def post_ranking_score(upvotes=1, age=0, views=1):
    upvotes = max(upvotes, 0)
    age = max(age, 0)
    views = max(views, 0)
    u = upvotes**0.8
    a = (age + 2) ** 1.8
    return (u / a) / (views + 1)


def get_hours_since(date):
    time_diff = datetime.now(UTC).replace(tzinfo=None) - date
    return int(time_diff.total_seconds() / 3600)


def plural_hours(n):
    hours = ["час", "часа", "часов"]
    days = ["день", "дня", "дней"]

    if n > 24:
        n = int(n / 24)
        if n % 10 == 1 and n % 100 != 11:
            p = 0
        elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
            p = 1
        else:
            p = 2

        return str(n) + " " + days[p]

    if n == 0:
        return "меньше часа"
    if n % 10 == 1 and n % 100 != 11:
        p = 0
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        p = 1
    else:
        p = 2

    return str(n) + " " + hours[p]


def get_thesis_type_id_string(id):
    if id < 1 or id > len(type_id_string):
        return ""
    return type_id_string[id - 1]


class RateLimiter:
    """Simple in-memory sliding-window rate limiter keyed by a string.

    Not a substitute for a full proxy-level limiter, but mitigates brute
    force on login/register without new dependencies. Per-worker state on
    multi-process deployments, which is acceptable defense-in-depth.
    """

    def __init__(self, *, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = {}

    def allow(self, key: str, now: float | None = None) -> bool:
        now = now if now is not None else time.monotonic()
        hits = self._hits.setdefault(key, [])
        cutoff = now - self.window_seconds
        hits[:] = [t for t in hits if t > cutoff]
        if len(hits) >= self.limit:
            return False
        hits.append(now)
        return True


LOGIN_RATE_LIMITER = RateLimiter(limit=10, window_seconds=300)
REGISTER_RATE_LIMITER = RateLimiter(limit=5, window_seconds=3600)
PASSWORD_RECOVERY_RATE_LIMITER = RateLimiter(limit=5, window_seconds=3600)
