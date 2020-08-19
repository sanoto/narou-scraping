from django.db import models
from enum import Enum

from users.models import User


class Cookie(models.Model):
    userl = models.CharField(verbose_name='userl', max_length=100)


class Writer(models.Model):
    name = models.CharField(verbose_name='名前', max_length=100)
    ruby = models.CharField(verbose_name='ふりがな', max_length=100)


class Novel(models.Model):
    ncode = models.CharField(verbose_name='Nコード', max_length=10, primary_key=True)
    ncode_int = models.IntegerField(verbose_name='数字版Nコード', unique=True, blank=True)
    readers = models.ManyToManyField(User, related_name='novels', verbose_name='読者')
    title = models.CharField(verbose_name='タイトル', max_length=500)
    writer_nickname = models.CharField(verbose_name='ペンネーム', max_length=100)
    writer = models.ForeignKey(Writer, on_delete=models.CASCADE, related_name='novels', verbose_name='作者')
    story = models.TextField(verbose_name='あらすじ', blank=True, null=True)
    is_serial = models.BooleanField(verbose_name='連載')
    max_episode_num = models.IntegerField(verbose_name='全話数')


class Chapter(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='chapters', verbose_name='小説')
    number = models.IntegerField(verbose_name='章')
    name = models.CharField(verbose_name='名前', max_length=500)


class Episode(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='episodes', verbose_name='小説')
    number = models.IntegerField(verbose_name='話')
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.SET_NULL,
        related_name='episode',
        verbose_name='章',
        blank=True,
        null=True,
    )
    title = models.CharField(verbose_name='タイトル', max_length=500, blank=True, null=True)
    foreword = models.TextField(verbose_name='まえがき', blank=True, null=True)
    body = models.TextField(verbose_name='本文')
    afterword = models.TextField(verbose_name='あとがき', blank=True, null=True)
    posted_at = models.DateTimeField(verbose_name='投稿日時', blank=True, null=True)
    fixed_at = models.DateTimeField(verbose_name='最終改稿日時', blank=True, null=True)


class Word(models.Model):
    class PartialOf(models.IntegerChoices):
        BODY = 1, '本文'
        FOREWORD = 2, 'まえがき'
        AFTERWORD = 3, 'あとがき'

    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='words', verbose_name='話')
    text = models.CharField(verbose_name='セリフ', max_length=1000)
    partial_of = models.IntegerField(verbose_name='区分', choices=PartialOf.choices)


class KeyWord(models.Model):
    name = models.CharField(verbose_name='名前', max_length=100)

    class Required(Enum):
        R15 = 'R15'
        BL = 'ボーイズラブ'
        GL = 'ガールズラブ'
        DANGEROUS = '残酷な描写あり'
        WORLD_REINCARNATION = '異世界転生'
        WORLD_TRANSFER = '異世界転移'


class NovelDetail(models.Model):
    BIG_GENRE = [
        (1, '恋愛'),
        (2, 'ファンタジー'),
        (3, '文芸'),
        (4, 'SF'),
        (99, 'その他'),
        (98, 'ノンジャンル'),
    ]
    GENRE = [
        (101, '異世界〔恋愛〕'),
        (102, '現実世界〔恋愛〕'),
        (201, 'ハイファンタジー〔ファンタジー〕'),
        (202, 'ローファンタジー〔ファンタジー〕'),
        (301, '純文学〔文芸〕'),
        (302, 'ヒューマンドラマ〔文芸〕'),
        (303, '歴史〔文芸〕'),
        (304, '推理〔文芸〕'),
        (305, 'ホラー〔文芸〕'),
        (306, 'アクション〔文芸〕'),
        (307, 'コメディー〔文芸〕'),
        (401, 'VRゲーム〔SF〕'),
        (402, '宇宙〔SF〕'),
        (403, '空想科学〔SF〕'),
        (404, 'パニック〔SF〕'),
        (9901, '童話〔その他〕'),
        (9902, '詩〔その他〕'),
        (9903, 'エッセイ〔その他〕'),
        (9904, 'リプレイ〔その他〕'),
        (9999, 'その他〔その他〕'),
        (9801, 'ノンジャンル〔ノンジャンル〕'),
    ]
    WRITER_DEVICE = [
        (1, '携帯のみ'),
        (2, 'PCのみ'),
        (3, 'PCと携帯'),
    ]

    novel = models.OneToOneField(Novel, on_delete=models.CASCADE, related_name='detail', verbose_name='小説')
    big_genre = models.IntegerField(verbose_name='大ジャンル', choices=BIG_GENRE)
    genre = models.IntegerField(verbose_name='ジャンル', choices=GENRE)
    keywords = models.ManyToManyField(KeyWord, related_name='novels', verbose_name='キーワード')
    first_publication_date = models.DateTimeField(verbose_name='初回掲載日')
    last_publication_date = models.DateTimeField(verbose_name='最終掲載日')
    length = models.IntegerField(verbose_name='文字数')
    is_stop = models.BooleanField(verbose_name='長期連載停止中')
    writer_device = models.IntegerField(verbose_name='投稿時使用端末', choices=WRITER_DEVICE)
    total_point = models.IntegerField(verbose_name='総合評価ポイント')
    daily_point = models.IntegerField(verbose_name='日韓ポイント')
    weekly_rating_point = models.IntegerField(verbose_name='週間ポイント')
    monthly_rating_point = models.IntegerField(verbose_name='月間ポイント')
    quarter_rating_point = models.IntegerField(verbose_name='四半期ポイント')
    yearly_rating_point = models.IntegerField(verbose_name='年間ポイント')
    bookmark_num = models.IntegerField(verbose_name='ブックマーク数')
    impression_num = models.IntegerField(verbose_name='感想数')
    review_num = models.IntegerField(verbose_name='レビュー数')
    all_point = models.IntegerField(verbose_name='評価点')
    illust_num = models.IntegerField(verbose_name='挿絵数')
    talking_row_rate = models.IntegerField(verbose_name='小説内の会話率')
    updated_at = models.DateTimeField(verbose_name='更新日時')
