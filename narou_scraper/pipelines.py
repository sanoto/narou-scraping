# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from django.core.exceptions import ObjectDoesNotExist
from scrapy.exceptions import DropItem
from scrapy import Item, Spider
from datetime import datetime
from logging import Logger

from narou_scraper.items import TextItem, NovelItem, ChapterItem, EpisodeItem
from narou.models import Writer, Novel, Chapter, Episode


def check_null(item: Item, logger: Logger, pipeline_class, no_check_keys: list = None):
    if no_check_keys:
        null_keys = [key for key, value in item.items() if value is None and key not in set(no_check_keys)]
    else:
        null_keys = [key for key, value in item.items() if not value]
    if null_keys:
        logger.error(f"##### ERROR: {', '.join(null_keys)} are null in {pipeline_class}#####")
        raise DropItem(str(item))


def get_model_instance(model, item, **get_kwarg):
    try:
        instance = model.objects.get(**get_kwarg)
    except ObjectDoesNotExist:
        raise DropItem(f'{type(model)} does not exist in {item}')

    return instance


def build_datetime(raw_datetime: str):
    if raw_datetime:
        return datetime.strptime(raw_datetime, '%Y/%m/%d %H:%M')


class TextPipeline(object):
    def process_item(self, item: TextItem, spider):
        try:
            novel = Novel.objects.get(ncode_int=item['ncode_int'])
        except ObjectDoesNotExist:
            return item

        novel.episodes.update_or_create(novel=novel, number=item['episode_num'], defaults={'body': item['text']})
        return item


class NovelPipeline(object):
    def process_item(self, item: NovelItem, spider: Spider):
        if not isinstance(item, NovelItem):
            return item

        if 'is_serial' not in item.keys():
            raise DropItem(str(item))

        no_check = None if item['is_serial'] else ['story']
        check_null(item, spider.logger, NovelPipeline, no_check)

        writer, created = Writer.objects.update_or_create(
            id=item.pop('writer_id'),
            defaults={'name': item.pop('writer_name')}
        )
        ncode = item.pop('ncode')
        dict_item = dict(item)
        dict_item['writer'] = writer
        Novel.objects.update_or_create(ncode=ncode, defaults=dict_item)

        return item


class ChapterPipeline(object):
    def process_item(self, item: ChapterItem, spider: Spider):
        if not isinstance(item, ChapterItem):
            return item

        check_null(item, spider.logger, ChapterPipeline)

        novel = get_model_instance(Novel, item, ncode=item.pop('ncode'))
        number = item.pop('number')
        Chapter.objects.update_or_create(novel=novel, number=number, defaults=dict(item))

        return item


class EpisodePipeline(object):
    def process_item(self, item: EpisodeItem, spider: Spider):
        if not isinstance(item, EpisodeItem):
            return item

        if 'ncode' not in item.keys():
            raise DropItem(str(item))

        novel = get_model_instance(Novel, item, ncode=item.pop('ncode'))

        no_check = ['chapter_num', 'foreword', 'afterword', 'fixed_at']
        if not novel.is_serial:
            no_check += ['title', 'posted_at']
        check_null(item, spider.logger, EpisodePipeline, no_check)

        dict_item = dict(item)
        chapter_num = dict_item.pop('chapter_num')
        if chapter_num:
            dict_item['chapter'] = get_model_instance(Chapter, item, novel=novel, number=chapter_num)

        dict_item['posted_at'] = build_datetime(dict_item.pop('posted_at'))
        dict_item['fixed_at'] = build_datetime(dict_item.pop('fixed_at'))
        number = dict_item.pop('number')
        Episode.objects.update_or_create(novel=novel, number=number, defaults=dict_item)

        return item
