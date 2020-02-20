from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
import cronpi

from narou_scraping.settings import INTERVAL_MINUTES


class Command(BaseCommand):
    def handle(self, *args, **options):
        manage_path = Path(settings.BASE_DIR) / 'manage.py'

        cronpi.run_custom(
            f"*/{INTERVAL_MINUTES} * * * * /usr/local/bin/python {manage_path} check_update",
            isOverwrite=True
        )

        current = cronpi.get_job_list()
        self.stdout.write('\n'.join(current))
