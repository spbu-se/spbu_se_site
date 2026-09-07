# SPDX-License-Identifier: Apache-2.0

"""Canonical seed data for a deterministic, role-complete local environment.

Single source of truth for the synthetic, role-labeled accounts layered on top
of the legacy ``init_db`` lists. Consumed by ``init_db()`` (models are passed
in to avoid a circular import with ``se_models``) and, later, by the shared
test fixtures and the top-level ``e2e`` suite so every surface logs in as the
same, documented accounts — see ``docs/ROLE_FEATURE_MATRIX.md``. Ships no real
personal data.
"""

DEV_PASSWORD = "1"  # noqa: S105 — dev-only local accounts; never used in prod

ROLE_ACCOUNTS = [
    {
        "email": "admin@se.dev",
        "role": 5,
        "last_name": "Админ",
        "first_name": "Локальный",
        "staff": True,
    },
    {
        "email": "review@se.dev",
        "role": 3,
        "last_name": "Ревьюер",
        "first_name": "Локальный",
        "staff": False,
    },
    {
        "email": "thesis@se.dev",
        "role": 2,
        "last_name": "Автор",
        "first_name": "Локальный",
        "staff": False,
    },
    {
        "email": "user@se.dev",
        "role": 0,
        "last_name": "Пользователь",
        "first_name": "Локальный",
        "staff": False,
    },
]

STAFF_ACCOUNTS = [
    {
        "email": "staff@se.dev",
        "role": 3,
        "last_name": "Сотрудник",
        "first_name": "Локальный",
        "staff": True,
    },
]


def apply_seed(db, users_model, staff_model, generate_password_hash) -> None:
    """Insert the deterministic role accounts into the freshly initialised DB.

    Idempotent per email (an existing account is never duplicated). Called from
    ``init_db`` after the legacy lists, so ``user.role`` and the ``Staff`` row
    gate every surface with no post-seed mutation needed.
    """
    for account in ROLE_ACCOUNTS + STAFF_ACCOUNTS:
        if users_model.query.filter_by(email=account["email"]).first() is not None:
            continue
        user = users_model(
            email=account["email"],
            password_hash=generate_password_hash(DEV_PASSWORD, method="pbkdf2:sha256"),
            first_name=account["first_name"],
            last_name=account["last_name"],
            role=account["role"],
        )
        db.session.add(user)
        db.session.commit()
        if account.get("staff"):
            db.session.add(
                staff_model(
                    user_id=user.id,
                    official_email=account["email"],
                    position="Тестовый сотрудник",
                    still_working=True,
                )
            )
            db.session.commit()
