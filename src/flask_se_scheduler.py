# SPDX-License-Identifier: Apache-2.0

from apscheduler.schedulers.background import BackgroundScheduler

# APScheduler runs in every gunicorn/uwsgi worker; the job *functions* carry
# their own guards (NotificationLog idempotency claim, SE_STAGING env gate),
# so only the scheduling mechanics live here. Starting the scheduler is
# explicit: production (wsgi.py) starts it, tests and the import pipeline
# (extract_text.py, thesesImport.py) never do.
scheduler = BackgroundScheduler(timezone="UTC")


def configure_scheduler(
    jobs: list[tuple[str, object, int]],
    start_scheduler: bool,
) -> None:
    """Register ``(job_id, func, seconds)`` interval jobs and start when asked."""
    for job_id, func, seconds in jobs:
        scheduler.add_job(
            id=job_id,
            func=func,
            trigger="interval",
            seconds=seconds,
        )
    if start_scheduler:
        scheduler.start()
