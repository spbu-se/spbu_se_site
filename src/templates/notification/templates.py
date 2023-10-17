from enum import Enum


class NotificationTemplates(Enum):
    NOTIFICATION_FROM_SUPERVISOR = "notification/notification_from_supervisor.html"
    NOTIFICATION_FROM_CURATOR = "notification/notification_from_curator.html"
    NEW_PRACTICE_TO_SUPERVISOR = (
        "notification/new_practice_was_added_to_supervisor.html"
    )
    NEW_REPORT_TO_SUPERVISOR = "notification/new_report_to_supervisor.html"
    SUPERVISOR_COMMENT_TO_REPORT = "notification/supervisor_comment_to_report.html"
    THESIS_WAS_ARCHIVED_BY_ADMIN = "notification/thesis_was_archived_by_admin.html"
    DIPLOMA_THEMES_REJECTED = "notification/diploma_themes_rejected.html"
    DIPLOMA_THEMES_NEED_UPDATE = "notification/diploma_themes_need_update.html"
