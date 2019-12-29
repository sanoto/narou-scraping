# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from django.core.exceptions import ObjectDoesNotExist

from narou_scraper.items import TextItem
from narou.models import Novel


class TextPipeline(object):
    def process_item(self, item: TextItem, spider):
        try:
            novel = Novel.objects.get(ncode_int=item['ncode_int'])
        except ObjectDoesNotExist:
            return item

        novel.episodes.update_or_create(novel=novel, number=item['episode_num'], defaults={'text': item['text']})
        return item
