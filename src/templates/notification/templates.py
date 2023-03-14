from enum import Enum


class NotificationTemplates(Enum):
    NOTIFICATION_FROM_SUPERVISOR = "notification/notification_from_supervisor.html"
    NEW_PRACTICE_TO_SUPERVISOR = "notification/new_practice_was_added_to_supervisor.html"
    NEW_REPORT_TO_SUPERVISOR = "notification/new_report_to_supervisor.html"
