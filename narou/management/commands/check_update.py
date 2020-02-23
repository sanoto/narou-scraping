from django.core.management.base import BaseCommand

from narou.views import check_update
from narou_scraping.settings import NCODES


class Command(BaseCommand):
    def handle(self, *args, **options):
        re = check_update(NCODES.keys())
        self.stdout.write(re.reason)
