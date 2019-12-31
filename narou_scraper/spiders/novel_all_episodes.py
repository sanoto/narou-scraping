# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals
from scrapy.http import HtmlResponse, Request
from scrapy.selector import Selector, SelectorList
from itertools import zip_longest
from logging import Logger
from typing import List

from narou_scraper.items import NovelItem, ChapterItem, EpisodeItem
from narou_scraper.handler import spider_error


def parse_href_end_num(selector: SelectorList, logger: Logger) -> int or None:
    logger.debug('--------------------------parse_href_end_num()')
    url: str = selector.xpath('@href').get()  # e.g. 'https://hoge.com/huga/114514/'
    return int(url.split('/')[-2]) if url else None


def parse_body(selectors: SelectorList, logger: Logger) -> str:
    logger.debug('--------------------------parse_body()')

    def parse_line(selector: Selector) -> str:
        # logger.debug('--------------------------parse_line()')
        if selector.css('br'):
            return '\n'

        texts = selector.xpath('text()').getall()
        if len(texts) == 1:
            return texts[0]

        larges = selector.css('rb::text').getall()
        smalls = selector.css('rt::text').getall()
        ruby_texts = [f'|{large}《{small}》' for large, small in zip(larges, smalls)]
        return ''.join([''.join(pair) for pair in zip_longest(texts, ruby_texts, fillvalue='')])

    return '\n'.join(map(parse_line, selectors))


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
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider_error, signal=signals.spider_error)
        return spider

    def parse(self, response: HtmlResponse):
        self.logger.debug('--------------------------parse()')
        impression_selector = response.css('#novel_header').xpath('//a[contains(text(), "感想")]')
        ncode_int = parse_href_end_num(impression_selector, self.logger)

        contents_selector = response.css('#novel_contents').xpath('div[1]')

        title = contents_selector.css('.novel_title::text').get()

        writer_link_selector = response.css('#novel_footer').xpath('//a[contains(text(), "作者マイページ")]')
        writer_id = parse_href_end_num(writer_link_selector, self.logger)
        writer_name_selector = contents_selector.css('.novel_writername')
        writer_name = writer_name_selector.css('a::text').get()
        if not writer_name:
            writer_str: str = writer_name_selector.xpath('text()').get()  # e.g. '作者：硬梨菜'
            writer_name = writer_str.split('：')[1]

        story = contents_selector.css('#novel_ex::text').get()

        novel_raw = {
            'title': title,
            'ncode': self.ncode,
            'ncode_int': ncode_int,
            'writer_id': writer_id,
            'writer_name': writer_name,
            'story': story,
        }

        indexes_selectors: List[Selector] = contents_selector.css('.index_box > *')
        if not indexes_selectors:
            yield NovelItem(is_serial=False, max_episode_num=1, **novel_raw)
            yield self.parse_episode(response)
            return

        latest_episode_selector = indexes_selectors[-1].css('dd > a')
        max_episode_num = parse_href_end_num(latest_episode_selector, self.logger)

        yield NovelItem(is_serial=True, max_episode_num=max_episode_num, **novel_raw)

        chapter_num = 0
        episode_num = 0
        for i_selector in indexes_selectors:
            self.logger.debug(f'--------------------------chapter{chapter_num} episode{episode_num}')
            if i_selector.xpath('@class').get() == 'chapter_title':
                chapter_num += 1
                chapter_name = i_selector.xpath('text()').get()
                yield ChapterItem(ncode=self.ncode, number=chapter_num, name=chapter_name)

            else:
                episode_num += 1
                episode_url = i_selector.css('dd > a').xpath('@href').get()  # e.g. '/n6169dz/6/'

                if not episode_url:
                    self.logger.error('episode url not found')
                posted_at: str = i_selector.css('dt::text').get()
                fixed_at: str = i_selector.xpath('//span/@title').get()

                yield scrapy.Request(
                    url=response.urljoin(episode_url),
                    callback=self.parse_episode,
                    cb_kwargs={
                        'number': episode_num,
                        'chapter_num': chapter_num if chapter_num != 0 else None,
                        'posted_at': posted_at.strip('\n'),
                        'fixed_at': fixed_at[:-3] if fixed_at else None,
                    }
                )

    def parse_episode(self, response: HtmlResponse, number=1, chapter_num=None, posted_at=None, fixed_at=None):
        self.logger.debug('--------------------------parse_episode()')
        contents_selector = response.css('#novel_contents').xpath('div[1]')

        title = contents_selector.css('.novel_subtitle::text').get()
        foreword = parse_body(contents_selector.css('#novel_p > p'), self.logger)
        body = parse_body(contents_selector.css('#novel_honbun > p'), self.logger)
        afterword = parse_body(contents_selector.css('#novel_a > p'), self.logger)

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
