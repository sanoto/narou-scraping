from rest_framework import serializers

from .models import Writer, Novel, Chapter, Episode, Word, KeyWord, NovelDetail


class WriterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Writer
        fields = ['id', 'name', 'ruby']
        extra_kwargs = {'id': {'read_only': True}}


class NovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Novel
        fields = [
            'ncode', 'ncode_int', 'title', 'writer_nickname', 'writer',
            'story', 'is_serial', 'max_episode_num',
        ]
        extra_kwargs = {}


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'novel', 'number', 'name']
        extra_kwargs = {'id': {'read_only': True}}


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = [
            'id', 'novel', 'number', 'chapter', 'title', 'foreword',
            'body', 'afterword', 'posted_at', 'fixed_at',
        ]
        extra_kwargs = {'id': {'read_only': True}}


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'episode', 'text', 'partial_of']
        extra_kwargs = {'id': {'read_only': True}}


class KeyWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyWord
        fields = ['id', 'name']
        extra_kwargs = {'id': {'read_only': True}}


class NovelDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = NovelDetail
        fields = [
            'id', 'novel', 'big_genre', 'genre', 'keywords',
            'first_publication_date', 'last_publication_date', 'length', 'is_stop', 'writer_device',
            'total_point', 'daily_point', 'weekly_rating_point', 'monthly_rating_point', 'quarter_rating_point',
            'yearly_rating_point', 'bookmark_num', 'impression_num', 'review_num', 'all_point',
            'illust_num', 'talking_row_rate', 'updated_at',
        ]
        extra_kwargs = {'id': {'read_only': True}}
