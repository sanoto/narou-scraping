from django.contrib import admin

from .models import Cookie, Writer, Novel, Chapter, Episode, KeyWord, NovelDetail


@admin.register(Cookie)
class CookieAdmin(admin.ModelAdmin):
    list_display = ('userl',)


@admin.register(Writer)
class WriterAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ('title', 'ncode', 'ncode_int', 'writer', 'story', 'max_episode_num', 'detail')


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('novel', 'number', 'name')


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('novel', 'number', 'chapter', 'title', 'text', 'posted_at', 'fixed_at')


@admin.register(KeyWord)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(NovelDetail)
class NovelDetailAdmin(admin.ModelAdmin):
    list_display = ('novel',)

