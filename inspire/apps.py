import logging

from django.apps import AppConfig
from django.db.utils import ProgrammingError

logger = logging.getLogger(__name__)


class InspireConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "inspire"

    def ready(self):
        try:
            import inspire.signals  # noqa
        except ProgrammingError as e:
            custom_error_msg = "Error when importing signals. Make sure all migrations are applied"
            logger.critical("{}\nVerbose: {}".format(custom_error_msg, str(e)))
