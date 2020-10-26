# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from scrapy.exceptions import DropItem
from scrapy import Item, Spider
from scrapy.pipelines.images import ImagesPipeline
from logging import Logger
import requests

from narou_scraper.items import TextItem, NovelItem, ChapterItem, EpisodeItem, IllustItem
from narou.models import Writer, Novel, Chapter, Episode, Illust


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


class TextPipeline(object):
    def process_item(self, item: TextItem, spider):
        try:
            novel = Novel.objects.get(ncode_int=item['ncode_int'])
        except ObjectDoesNotExist:
            return item

        novel.episodes.update_or_create(novel=novel, number=item['episode_num'], defaults={'body': item['text']})
        return item


class NovelPipeline(object):
    def drop_by_narou_api(self, response, logger: Logger, **kwargs):
        logger.error('##### NAROU API ERROR: narou user API is wrong #####')
        logger.error(response)
        raise DropItem(kwargs)

    def get_writer(self, writer_id: int, writer_name: str, logger: Logger) -> Writer:
        writer_qs = Writer.objects.filter(id=writer_id)
        if writer_qs and writer_name:
            writer = writer_qs.first()
            if writer.name == writer_name:
                return writer

        response = requests.get(
            'https://api.syosetu.com/userapi/api/',
            params={'userid': writer_id, 'of': 'n-y', 'out': 'json'}
        )
        json: list = response.json()
        if len(json) < 2:
            self.drop_by_narou_api(response, logger, id=writer_id, name=writer_name)
        data: dict = json[1]
        writer_name, writer_ruby = data.get('name'), data.get('yomikata')
        if not (writer_name and writer_ruby):
            self.drop_by_narou_api(response, logger, id=writer_id, name=writer_name)

        writer, created = Writer.objects.update_or_create(
            id=writer_id,
            defaults={'name': writer_name, 'ruby': writer_ruby}
        )
        return writer

    def process_item(self, item: NovelItem, spider: Spider):
        if not isinstance(item, NovelItem):
            return item

        if 'is_serial' not in item.keys():
            raise DropItem(str(item))

        no_check = ['writer_name']
        if not item['is_serial']:
            no_check += ['story']
        check_null(item, spider.logger, NovelPipeline, no_check)

        ncode = item.pop('ncode')
        dict_item = dict(item)
        writer_name = item.get('writer_name')
        dict_item['writer'] = self.get_writer(item.pop('writer_id'), writer_name, spider.logger)
        if 'writer_name' in dict_item:
            del dict_item['writer_name']
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

        dict_item['posted_at'] = dict_item.pop('posted_at')
        dict_item['fixed_at'] = dict_item.pop('fixed_at')
        number = dict_item.pop('number')
        Episode.objects.update_or_create(novel=novel, number=number, defaults=dict_item)

        return item


class IllustPipeline(ImagesPipeline):
    def item_completed(self, results, item: IllustItem, info):
        _item = super(IllustPipeline, self).item_completed(results, item, info)
        check_null(_item, info.spider.logger, IllustPipeline, ['image_urls', 'images'])

        ok, data = results[0]
        file_path = data['path']
        if not ok or not file_path:
            raise DropItem(f'failed illust downloading. {_item["unique_id"]}')

        dict_item = dict(_item)
        del dict_item['image_urls']
        del dict_item['images']
        unique_id = dict_item['unique_id']
        dict_item['episode'] = get_model_instance(
            Episode,
            item,
            novel__ncode=dict_item.pop('ncode'),
            number=dict_item.pop('episode_num'),
        )

        file = File(open(file_path))
        illust = Illust(**dict_item)
        illust.file.save(unique_id, file)
        illust.save()

        return _item
