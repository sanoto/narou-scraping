from django.core.management.base import BaseCommand

from narou.views import check_update
from narou_scraping.settings import NCODE


class Command(BaseCommand):
    def handle(self, *args, **options):
        re = check_update(NCODE)
        self.stdout.write(re.reason)
