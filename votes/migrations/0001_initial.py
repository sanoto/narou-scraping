# Generated by Django 3.0.1 on 2020-01-09 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('narou', '0005_auto_20200109_0839'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posted_at', models.DateTimeField(verbose_name='投票時刻')),
                ('content', models.CharField(max_length=1000, verbose_name='投票内容')),
                ('participant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='narou.Writer', verbose_name='投票者')),
            ],
        ),
        migrations.CreateModel(
            name='VoteParser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('regex', models.CharField(max_length=500, verbose_name='投票文字列パース用正規表現')),
            ],
        ),
        migrations.CreateModel(
            name='WriterDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twitter_id', models.CharField(max_length=100, verbose_name='Twitter ID')),
                ('writer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='detail', to='narou.Writer', verbose_name='作者')),
            ],
        ),
        migrations.CreateModel(
            name='Voting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='イベント名')),
                ('start_time', models.DateTimeField(verbose_name='開始時刻')),
                ('end_time', models.DateTimeField(verbose_name='終了時間')),
                ('in_impression', models.BooleanField(default=False, verbose_name='感想欄からの投票')),
                ('in_writer_report', models.BooleanField(default=False, verbose_name='活動報告からの投票')),
                ('novel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voting_list', to='narou.Novel', verbose_name='対象小説')),
                ('parsers', models.ManyToManyField(related_name='voting_list', to='votes.VoteParser', verbose_name='投票文字列用パーサー')),
                ('participants', models.ManyToManyField(related_name='voting_list', through='votes.Vote', to='narou.Writer', verbose_name='参加者')),
            ],
        ),
        migrations.AddField(
            model_name='vote',
            name='voting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='votes.Voting', verbose_name='投票イベント'),
        ),
    ]
