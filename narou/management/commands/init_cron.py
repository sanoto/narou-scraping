from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
import cronpi

from narou_scraping.settings import INTERVAL_MINUTES
from narou_scraping.local_settings import PYTHON_PATH


class Command(BaseCommand):
    def handle(self, *args, **options):
        manage_path = Path(settings.BASE_DIR) / 'manage.py'

        cronpi.run_custom(
            f"*/{INTERVAL_MINUTES} * * * * {PYTHON_PATH} {manage_path} check_update",
            isOverwrite=True
        )

        current = cronpi.get_job_list()
        self.stdout.write('\n'.join(current))
