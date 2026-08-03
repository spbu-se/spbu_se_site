# SPDX-License-Identifier: Apache-2.0

import os
import pathlib
import re
import time
from datetime import UTC, datetime
from unicodedata import normalize

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
SECRET_KEY_THESIS = read_secret_from_file(THESIS_SECRET_FILE, fallback_len=16)
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
