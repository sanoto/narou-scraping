# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TextItem(scrapy.Item):
    ncode_int = scrapy.Field()
    episode_num = scrapy.Field()
    text = scrapy.Field()


class NovelItem(scrapy.Item):
    title = scrapy.Field()
    ncode = scrapy.Field()
    ncode_int = scrapy.Field()
    writer_id = scrapy.Field()
    writer_name = scrapy.Field()
    writer_nickname = scrapy.Field()
    story = scrapy.Field()  # 短編だと取得できない
    is_serial = scrapy.Field()
    max_episode_num = scrapy.Field()


# Novelを作ってから
class ChapterItem(scrapy.Item):
    ncode = scrapy.Field()
    number = scrapy.Field()
    name = scrapy.Field()


# Novel, Chapterを作ってから
class EpisodeItem(scrapy.Item):
    ncode = scrapy.Field()
    number = scrapy.Field()
    chapter_num = scrapy.Field()  # 無い可能性あり
    title = scrapy.Field()  # 短編だと取得できない
    foreword = scrapy.Field()  # 無い可能性あり
    body = scrapy.Field()
    afterword = scrapy.Field()  # 無い可能性あり
    posted_at = scrapy.Field()  # 短編だと取得できない
    fixed_at = scrapy.Field()  # 無い可能性あり
