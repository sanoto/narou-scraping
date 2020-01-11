from django.db import models

from narou.models import Writer, Novel


class VoteParser(models.Model):
    regex = models.CharField(verbose_name='投票文字列パース用正規表現', max_length=500)


class Voting(models.Model):
    name = models.CharField(verbose_name='イベント名', max_length=200)
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='voting_list', verbose_name='対象小説')
    start_time = models.DateTimeField(verbose_name='開始時刻')
    end_time = models.DateTimeField(verbose_name='終了時間')
    in_impression = models.BooleanField(verbose_name='感想欄からの投票', default=False)
    in_writer_report = models.BooleanField(verbose_name='活動報告からの投票', default=False)
    parsers = models.ManyToManyField(VoteParser, related_name='voting_list', verbose_name='投票文字列用パーサー')
    participants = models.ManyToManyField(
        Writer,
        through='Vote',
        through_fields=('voting', 'participant'),
        related_name='voting_list',
        verbose_name='参加者',
    )


class Vote(models.Model):
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE, related_name='votes', verbose_name='投票イベント')
    participant = models.ForeignKey(
        Writer,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='投票者',
        blank=True,
        null=True,
    )
    posted_at = models.DateTimeField(verbose_name='投票時刻')
    content = models.CharField(verbose_name='投票内容', max_length=1000)


class WriterDetail(models.Model):
    writer = models.OneToOneField(Writer, on_delete=models.CASCADE, related_name='detail', verbose_name='作者')
    twitter_id = models.CharField(verbose_name='Twitter ID', max_length=100)
