from django.contrib import admin

from .models import VoteParser, Voting, Vote, WriterDetail


@admin.register(VoteParser)
class VoteParserAdmin(admin.ModelAdmin):
    list_display = ('regex',)


@admin.register(Voting)
class VotingAdmin(admin.ModelAdmin):
    list_display = ('name', 'novel', 'start_time', 'end_time', 'in_impression', 'in_writer_report')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voting', 'participant', 'posted_at', 'content')


@admin.register(WriterDetail)
class WriterDetailAdmin(admin.ModelAdmin):
    list_display = ('writer', 'twitter_id')
