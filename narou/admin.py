from django.contrib import admin

from .models import Cookie, Writer, Novel, Chapter, Episode, Word, KeyWord, NovelDetail


@admin.register(Cookie)
class CookieAdmin(admin.ModelAdmin):
    list_display = ('id', 'userl',)


@admin.register(Writer)
class WriterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'ruby')


@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'ncode', 'ncode_int', 'writer', 'writer_nickname',
        'story', 'is_serial', 'max_episode_num', 'detail'
    )


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'novel', 'number', 'name')


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'novel', 'number', 'chapter', 'title',
        'foreword', 'body', 'afterword',
        'posted_at', 'fixed_at',
    )


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('id', 'episode', 'text')


@admin.register(KeyWord)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(NovelDetail)
class NovelDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'novel')

