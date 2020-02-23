from django.shortcuts import render
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
from typing import List

from .models import Episode, Word


def check_update(ncodes: List[str]):
    responses = [
        requests.post(
            'http://scrapy:6800/schedule.json',
            data={'project': 'narou_scraper', 'spider': 'novel_all_episodes', 'ncode': ncode}
        ) for ncode in ncodes
    ]
    return responses[0]


@receiver(post_save, sender=Episode)
def extract_words(instance: Episode, **kwargs):
    def extract_words_from_lines(text: str, partial_of: int) -> None:
        if not text:
            return
        for line in text.split('\n'):
            if not line:
                continue
            stripped = line.strip()
            if (
                    stripped.startswith('「') and stripped.endswith('」')
            ) or (
                    stripped.startswith('『') and stripped.endswith('』')
            ):
                Word.objects.create(episode=instance, text=stripped, partial_of=partial_of)

    instance.words.all().delete()
    extract_words_from_lines(instance.body, Word.PartialOf.BODY)
    extract_words_from_lines(instance.foreword, Word.PartialOf.FOREWORD)
    extract_words_from_lines(instance.afterword, Word.PartialOf.AFTERWORD)
