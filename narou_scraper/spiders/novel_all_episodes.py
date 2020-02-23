# -*- coding: utf-8 -*-
from math import ceil

import scrapy
from scrapy import signals
from scrapy.http import HtmlResponse, Request
from scrapy.selector import Selector, SelectorList
from scrapy.exceptions import CloseSpider
from itertools import zip_longest
from logging import Logger
from typing import List
import datetime
from django.db.models import Q
import tweepy

from narou_scraper.items import NovelItem, ChapterItem, EpisodeItem
from narou_scraper.handler import spider_error
from narou.models import Episode, Novel
from narou_scraping.local_settings import TWITTER_CK, TWITTER_CS, TWITTER_AT, TWITTER_AS
from narou_scraping.settings import NCODES, INTERVAL_MINUTES


def safe_get(array: list, index: int):
    try:
        return array[index]
    except IndexError or TypeError:
        return None


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def build_datetime(raw_datetime: str):
    return datetime.datetime.strptime(raw_datetime, '%Y/%m/%d %H:%M') if raw_datetime else None


def validate(obj_name: str, logger: Logger, obj: any) -> any:
    if not obj:
        logger.error(f'!!!!PARSE ERROR!!!! {obj_name} is wrong!!!!')
        raise CloseSpider(f'{obj_name} is null')
    return obj


def parse_href_end_num(obj_name: str, logger: Logger, selector: SelectorList) -> int:
    logger.info('--------------------------parse_href_end_num()')
    url: str = validate(obj_name, logger, selector.xpath('@href').get())  # e.g. 'https://hoge.com/huga/114514/'
    return int(validate(obj_name, logger, safe_get(url.split('/'), -2)))


def parse_body(obj_name: str, logger: Logger, selectors: SelectorList) -> str:
    logger.info('--------------------------parse_body()')

    def parse_line(selector: Selector) -> str:
        if selector.css('br'):
            return '\n'

        texts = validate(f"a line of {obj_name}", logger, selector.xpath('text()').getall())
        if len(texts) == 1:
            return texts[0]

        larges = selector.css('rb::text').getall()
        smalls = selector.css('rt::text').getall()
        ruby_texts = [f'|{large}《{small}》' for large, small in zip(larges, smalls)]
        return ''.join([''.join(pair) for pair in zip_longest(texts, ruby_texts, fillvalue='')])

    return '\n'.join(map(parse_line, selectors))


def parse_writer(response: HtmlResponse, contents: Selector, logger: Logger) -> (int, str, str):
    writer_link_selector = response.css('#novel_footer').xpath('//a[contains(text(), "作者マイページ")]')
    writer_id = parse_href_end_num('writer ID', logger, writer_link_selector)
    writer_name_selector = contents.css('.novel_writername')
    writer_name = writer_nickname = writer_name_selector.css('a::text').get()
    if not writer_nickname:
        # e.g. '作者：硬梨菜'
        nickname_str: str = validate('writer text', logger, writer_name_selector.xpath('text()').get())
        writer_nickname = validate('writer name', logger, safe_get(nickname_str.split('：'), 1))
    return writer_id, writer_name, writer_nickname


class NovelAllEpisodesSpider(scrapy.Spider):
    name = 'novel_all_episodes'
    allowed_domains = ['ncode.syosetu.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'narou_scraper.pipelines.NovelPipeline': 100,
            'narou_scraper.pipelines.ChapterPipeline': 200,
            'narou_scraper.pipelines.EpisodePipeline': 300,
        },
    }

    def __init__(self, ncode: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ncode = ncode
        self.start_urls = [
            f'https://ncode.syosetu.com/{ncode}/',
            # f'https://novel18.syosetu.com/{ncode}/',
        ]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider: NovelAllEpisodesSpider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider_error, signal=signals.spider_error)
        crawler.signals.connect(spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response: HtmlResponse):
        self.logger.info('--------------------------parse()')
        impression_selector = response.css('#novel_header').xpath('//a[contains(text(), "感想")]')
        contents_selector = response.css('#novel_contents').xpath('div[1]')

        ncode_int = parse_href_end_num('ncode_int', self.logger, impression_selector)
        title = validate('title', self.logger, contents_selector.css('.novel_title::text').get())
        writer_id, writer_name, writer_nickname = parse_writer(response, contents_selector, self.logger)

        novel_raw = {
            'title': title,
            'ncode': self.ncode,
            'ncode_int': ncode_int,
            'writer_id': writer_id,
            'writer_name': writer_name,
            'writer_nickname': writer_nickname,
        }

        indexes_selectors: List[Selector] = contents_selector.css('.index_box > *')
        if not indexes_selectors:  # 短編はここまで
            yield NovelItem(is_serial=False, max_episode_num=1, **novel_raw)
            yield self.parse_episode(response)
            return

        # ここから連載作品のみ

        latest_episode_selector = indexes_selectors[-1].css('dd > a')
        max_episode_num = parse_href_end_num('max_episode_num', self.logger, latest_episode_selector)
        story = validate('story', self.logger, contents_selector.css('#novel_ex::text').get())
        yield NovelItem(is_serial=True, max_episode_num=max_episode_num, story=story, **novel_raw)

        chapter_num = 0
        episode_num = 0
        num = ceil(len(indexes_selectors) / 40)
        for chunk in chunks(indexes_selectors, num):
            for i_selector in chunk:
                self.logger.info(f'--------------------------chapter{chapter_num} episode{episode_num + 1}')

                # 章だった場合
                if i_selector.xpath('@class').get() == 'chapter_title':
                    chapter_num += 1
                    self.logger.info(f'--------------------------find chapter{chapter_num}')
                    chapter_name = validate(f'name of chapter{chapter_num}', self.logger, i_selector.xpath('text()').get())
                    chapter_item = ChapterItem(ncode=self.ncode, number=chapter_num, name=chapter_name)
                    self.logger.info(f'--------------------------collect chapter{chapter_num}: {chapter_item}')
                    yield chapter_item
                    continue

                # 話だった場合
                episode_num += 1
                episode_selector = i_selector.css('dd > a')
                episode_url = validate(
                    f'url of episode{episode_num}', self.logger,
                    episode_selector.xpath('@href').get()  # e.g. '/n6169dz/6/'
                )
                posted_at_raw: str = validate(
                    f'posted_at of episode{episode_num}', self.logger,
                    i_selector.css('dt::text').get()
                ).strip('\n')
                fixed_at_text: str = i_selector.css('dt > span').xpath('@title').get()
                fixed_at_raw = fixed_at_text[:-3] if fixed_at_text and len(fixed_at_text) >= 3 else None
                posted_at, fixed_at = build_datetime(posted_at_raw), build_datetime(fixed_at_raw)

                # サブタイと更新日時が一致するものがDBになければ更新対象とみなす
                que = Q(novel__ncode=self.ncode, title=episode_selector.xpath('text()').get(), posted_at=posted_at)
                if fixed_at:
                    que &= Q(fixed_at=fixed_at)
                if not Episode.objects.filter(que).exists():
                    yield scrapy.Request(
                        url=response.urljoin(episode_url),
                        callback=self.parse_episode,
                        cb_kwargs={
                            'number': episode_num,
                            'chapter_num': chapter_num if chapter_num != 0 else None,
                            'posted_at': posted_at,
                            'fixed_at': fixed_at,
                        }
                    )

    def parse_episode(self, response: HtmlResponse, number=1, chapter_num=None, posted_at=None, fixed_at=None):
        self.logger.info('--------------------------parse_episode()')
        contents_selector = response.css('#novel_contents').xpath('div[1]')

        title = contents_selector.css('.novel_subtitle::text').get()
        foreword = parse_body('foreword', self.logger, contents_selector.css('#novel_p > p'))
        body = validate(
            'body', self.logger,
            parse_body('body', self.logger, contents_selector.css('#novel_honbun > p'))
        )
        afterword = parse_body('afterword', self.logger, contents_selector.css('#novel_a > p'))

        return EpisodeItem(
            ncode=self.ncode,
            number=number,
            chapter_num=chapter_num,
            title=title,
            foreword=foreword,
            body=body,
            afterword=afterword,
            posted_at=posted_at,
            fixed_at=fixed_at,
        )


def spider_closed(spider: NovelAllEpisodesSpider):
    spider.logger.error('##########################spider_closed')
    if spider.ncode not in NCODES:
        return

    novels = Novel.objects.filter(ncode__in=NCODES).all()
    min_time = datetime.datetime.now() - datetime.timedelta(minutes=INTERVAL_MINUTES)
    novels_updates = {
        NCODES[novel.ncode]: novel.episodes.filter(posted_at__gt=min_time).values_list('number', 'title').all()
        for novel in novels
    }
    update_texts = [
        f'{name}\n' + '\n'.join(map(lambda number, title: f'・{title} ({spider.start_urls[0]}{number}/)', updates))
        for name, updates in novels_updates.items() if updates
    ]

    auth = tweepy.OAuthHandler(TWITTER_CK, TWITTER_CS)
    auth.set_access_token(TWITTER_AT, TWITTER_AS)
    api = tweepy.API(auth)

    updates_len = sum(map(len, novels_updates))
    spider.logger.error(f'##########################{updates_len}話更新されたよ！\n{"".join(update_texts)}')
    try:
        api.update_status(f'{updates_len}話更新されたよ！\n' + '\n'.join(update_texts))
    except tweepy.TweepError as e:
        spider.logger.error(e)
