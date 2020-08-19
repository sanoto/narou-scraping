from django.shortcuts import render
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, viewsets
from typing import List
from urllib.parse import urljoin
import requests
import hashlib
import hmac
import base64
import tweepy

from .models import Writer, Novel, Chapter, Episode, Word, KeyWord, NovelDetail
from .serializer import WriterSerializer, NovelSerializer, ChapterSerializer, EpisodeSerializer, WordSerializer, \
    KeyWordSerializer, NovelDetailSerializer
from narou_scraping.settings import NCODES, SCRAPY_HOST
from narou_scraping.local_settings import TWITTER_USER_ID, TWITTER_CK, TWITTER_CS, TWITTER_AT, TWITTER_AS


class WriterViewSet(viewsets.ModelViewSet):
    queryset = Writer.objects.all()
    serializer_class = WriterSerializer


class NovelViewSet(viewsets.ModelViewSet):
    queryset = Novel.objects.all()
    serializer_class = NovelSerializer


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer


class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer


class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer


class KeyWordViewSet(viewsets.ModelViewSet):
    queryset = KeyWord.objects.all()
    serializer_class = KeyWordSerializer


class NovelDetailViewSet(viewsets.ModelViewSet):
    queryset = NovelDetail.objects.all()
    serializer_class = NovelDetailSerializer


def check_update(ncodes: List[str]):
    responses = [
        requests.post(
            urljoin(SCRAPY_HOST, 'schedule.json'),
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


def send_random_word_in_reply(target_tweet_id: str) -> None:
    auth = tweepy.OAuthHandler(TWITTER_CK, TWITTER_CS)
    auth.set_access_token(TWITTER_AT, TWITTER_AS)
    api = tweepy.API(auth)
    random_word: Word = Word.objects.filter(episode__novel__ncode__in=NCODES.keys()).order_by('?').first()
    word_tweet = api.update_status(
        random_word.text,
        in_reply_to_status_id=target_tweet_id,
        auto_populate_reply_metadata=True
    )
    if 'id_str' in word_tweet:
        random_word_episode = random_word.episode
        api.update_status(
            f'引用元:\n'
            f'{NCODES[random_word_episode.novel.ncode]} 第{random_word_episode.number}話\n'
            f'{random_word.episode.title}\n'
            f'URL: https://ncode.syosetu.com/{random_word_episode.number}/',
            in_reply_to_status_id=word_tweet['id_str']
        )


class TwitterWebhook(APIView):
    def get(self, request: Request):
        crc_token = request.query_params.get('crc_token')
        if not crc_token:
            return Response('parameter "crc_token" not found', status=status.HTTP_400_BAD_REQUEST)
        sha256_hash_digest = hmac.new(TWITTER_CS.encode(), msg=crc_token.encode(), digestmod=hashlib.sha256).digest()
        response = {'response_token': 'sha256=' + base64.b64encode(sha256_hash_digest).decode()}
        return Response(response)

    def post(self, request: Request):
        ok = Response('OK', status=status.HTTP_200_OK)
        data: dict = request.data
        if 'tweet_create_events' in data.keys():
            tweet = data['tweet_create_events'][0]
            if tweet['in_reply_to_user_id_str'] != TWITTER_USER_ID:
                return ok
            send_random_word_in_reply(tweet['id_str'])

        return ok
