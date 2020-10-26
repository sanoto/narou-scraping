# -*- coding: utf-8 -*-
from math import ceil
import scrapy
from scrapy import signals
from scrapy.http import HtmlResponse, Request
from scrapy.selector import Selector, SelectorList
from scrapy.exceptions import CloseSpider
from itertools import zip_longest
from logging import Logger
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from django.db.models import Q, Model, QuerySet
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import tweepy

from narou_scraper.items import NovelItem, ChapterItem, EpisodeItem, IllustItem
from narou_scraper.handler import spider_error
from narou.models import Episode, Novel, Illust
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


def safe_queryset_get(queryset: QuerySet, **get_kwarg) -> Model or None:
    try:
        return queryset.get(**get_kwarg)
    except ObjectDoesNotExist or MultipleObjectsReturned:
        return None


def build_datetime(raw_datetime: str):
    return datetime.strptime(raw_datetime, '%Y/%m/%d %H:%M') if raw_datetime else None


def validate(obj_name: str, logger: Logger, obj: any) -> any:
    if not obj:
        logger.error(f'!!!!PARSE ERROR!!!! {obj_name} is wrong!!!!')
        raise CloseSpider(f'{obj_name} is null')
    return obj


def parse_href_end_num(obj_name: str, logger: Logger, selector: SelectorList) -> int:
    logger.info('--------------------------parse_href_end_num()')
    url: str = validate(f'url of {obj_name}', logger, selector.xpath('@href').get())  # e.g. 'https://hoge.com/huga/114514/'
    return int(validate(f'{obj_name} in url', logger, safe_get(url.split('/'), -2)))


def parse_mitemin_href(obj_name: str, logger: Logger, selector: Selector) -> (str, str):
    logger.info('--------------------------parse_mitemin_href()')
    url: str = 'https:' + validate(f'url of {obj_name}', logger, selector.css('a').xpath('@href').get())  # e.g. 'https://23.mitemin.net/i3724/'
    user_id: str = validate(f'user_id in {obj_name}', logger, safe_get((safe_get(url.split('//'), 1) or '').split('.'), 0))
    icode: str = validate(f'icode in {obj_name}', logger, safe_get(url.split('/'), -2))
    return url, f'<{icode}|{user_id}>'


def parse_body(obj_name: str, logger: Logger, selectors: SelectorList) -> str or None:
    logger.info(f'--------------------------parse_body() {obj_name}, selectors[0]: {selectors.get(default="")[:50] or None}')

    if obj_name != 'body' and not selectors.get():
        return

    def parse_line(selector: Selector) -> str:
        if selector.css('br').get():
            return ''
        elif selector.css('a[href*="mitemin"]').get():
            return parse_mitemin_href(f'an illust in {obj_name}', logger, selector)[1]

        texts = validate(f"a line of {obj_name}", logger, selector.css("*::text").getall())
        if len(texts) == 1:
            return texts[0]

        larges = validate(f"words in a line of {obj_name}", logger, selector.css('rb::text').getall())
        smalls = validate(f"rubies in a line of {obj_name}", logger, selector.css('rt::text').getall())
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


def parse_chapter(selector: Selector, ncode: str, chapter_num: int, logger: Logger) -> ChapterItem:
    # self.logger.info(f'--------------------------find chapter{chapter_num}')
    chapter_name = validate(f'name of chapter{chapter_num}', logger, selector.xpath('text()').get())
    return ChapterItem(ncode=ncode, number=chapter_num, name=chapter_name)


def parse_episode_info(selector: Selector, episode_num: int, chapter_num: int, logger: Logger) -> dict:
    episode_selector = selector.css('dd > a')
    episode_url = validate(
        f'url of episode{episode_num}', logger,
        episode_selector.xpath('@href').get()  # e.g. '/n6169dz/6/'
    )
    posted_at_raw: str = validate(
        f'posted_at of episode{episode_num}', logger,
        selector.css('dt::text').get()
    ).strip('\n')
    fixed_at_text: str = selector.css('dt > span').xpath('@title').get()
    fixed_at_raw = fixed_at_text[:-3] if fixed_at_text and len(fixed_at_text) >= 3 else None
    posted_at, fixed_at = build_datetime(posted_at_raw), build_datetime(fixed_at_raw)
    episode_title = validate(
        f'title of episode{episode_num}', logger,
        episode_selector.xpath('text()').get()
    )

    return {
        'number': episode_num,
        'chapter_num': chapter_num,
        'url': episode_url,
        'title': episode_title,
        'posted_at': posted_at,
        'fixed_at': fixed_at,
    }


def parse_table(indexes_selectors: List[Selector], ncode: str, logger: Logger) -> Tuple[List[ChapterItem], List[dict]]:
    chapter_num, episode_num = 0, 0
    chapters, episode_info_list = [], []
    for selector in indexes_selectors:
        # self.logger.info(f'--------------------------chapter{chapter_num} episode{episode_num + 1}')

        # 章だった場合
        if selector.xpath('@class').get() == 'chapter_title':
            chapter_num += 1
            chapters += parse_chapter(selector, ncode, chapter_num, logger)

        # 話だった場合
        else:
            episode_num += 1
            episode_info_list += parse_episode_info(selector, episode_num, chapter_num, logger)

    return chapters, episode_info_list


class NovelAllEpisodesSpider(scrapy.Spider):
    name = 'novel_all_episodes'
    allowed_domains = ['ncode.syosetu.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'narou_scraper.pipelines.NovelPipeline': 100,
            'narou_scraper.pipelines.ChapterPipeline': 200,
            'narou_scraper.pipelines.EpisodePipeline': 300,
            'narou_scraper.pipelines.IllustItem': 400,
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

    def parse(self, response: HtmlResponse, **kwargs):
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
            yield from self.parse_episode(response)
            return

        # ここから連載作品のみ

        latest_episode_selector = indexes_selectors[-1].css('dd > a')
        max_episode_num = parse_href_end_num('max_episode_num', self.logger, latest_episode_selector)
        story = validate('story', self.logger, contents_selector.css('#novel_ex::text').get())
        yield NovelItem(is_serial=True, max_episode_num=max_episode_num, story=story, **novel_raw)

        # 更新日時とサブタイor話数が一致するものがDBになければ更新対象とみなす
        # que = Q(novel__ncode=self.ncode, posted_at=posted_at) & (Q(title=episode_title) | Q(number=episode_num))
        # if fixed_at:
        #     que &= Q(fixed_at=fixed_at)
        # existing_episode = safe_queryset_get(Episode.objects.filter(que))
        # if not existing_episode:
        #     yield scrapy.Request(
        #         url=response.urljoin(episode_url),
        #         callback=self.parse_episode,
        #         cb_kwargs={
        #             'number': episode_num,
        #             'chapter_num': chapter_num if chapter_num != 0 else None,
        #             'posted_at': posted_at,
        #             'fixed_at': fixed_at,
        #         },
        #     )

        chapters, episode_info_list = parse_table(indexes_selectors, self.ncode, self.logger)
        yield from chapters

        existing_episode_dicts = Episode.objects.filter(
            novel__ncode=self.ncode
        ).order_by('number').values('number', 'title', 'posted_at', 'fixed_at')
        if existing_episode_dicts:
            def is_equal_episode(ep_info: dict):
                ex_ep: dict = safe_get(existing_episode_dicts, ep_info['number'] - 1)
                return ep_info['posted_at'] == ex_ep and (ep_info['title'] == ex_ep or ep_info['number'] == ex_ep)
            for episode_dict in existing_episode_dicts:
                equal_episode = next(ep_info for ep_info in episode_info_list if is_equal_episode(ep_info))





    def parse_episode(self, response: HtmlResponse, number=1, chapter_num=None, posted_at=None, fixed_at=None):
        self.logger.info(f'--------------------------parse_episode() number: {number}')
        contents_selector = response.css('#novel_contents').xpath('div[1]')

        title = contents_selector.css('.novel_subtitle::text').get()
        foreword = parse_body('foreword', self.logger, contents_selector.css('#novel_p > p'))
        body = validate(
            'body', self.logger,
            parse_body('body', self.logger, contents_selector.css('#novel_honbun > p'))
        )
        afterword = parse_body('afterword', self.logger, contents_selector.css('#novel_a > p'))

        mitemin_selectors = contents_selector.css('a[href*="mitemin"]')
        illust_count = len(mitemin_selectors)
        if illust_count:

            existing_illusts = Illust.objects.filter(
                episode__novel__ncode=self.ncode,
                episode__number=number,
            ).values_list('unique_id', flat=True)

            self.logger.info(f'## found {illust_count} illusts')

            for selector in mitemin_selectors:
                url, illust_str = parse_mitemin_href('an illust in episode', self.logger, selector)
                self.logger.info(f'## found illust: {illust_str} in {url}')
                if illust_str not in existing_illusts:
                    self.logger.info(f'## -> {illust_str} is new illust!!')
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_illust,
                        cb_kwargs={
                            'unique_id': illust_str,
                            'episode_num': number,
                        },
                    )

        yield EpisodeItem(
            ncode=self.ncode,
            number=number,
            chapter_num=chapter_num,
            title=title,
            foreword=foreword,
            body=body,
            afterword=afterword,
            posted_at=posted_at,
            fixed_at=fixed_at,
            illust_count=illust_count,
        )

    def parse_illust(self, response: HtmlResponse, unique_id=None, episode_num=None):
        self.logger.info('--------------------------parse_illust()')
        if response.xpath('//.main_error').get():
            self.logger.error(f'###### an illust link was broken!! {unique_id} ######')
            return

        title: str = validate('illust title', self.logger, response.xpath('//.img_title/text()'))
        illust_url: str = validate(
            'illust_url',
            self.logger,
            response.xpath('//.imageview/a[contains(@href, mitemin)]/@href').get()
        )

        yield IllustItem(
            unique_id=unique_id,
            ncode=self.ncode,
            episode_num=episode_num,
            title=title,
            image_urls=[illust_url],
        )



def spider_closed(spider: NovelAllEpisodesSpider):
    spider.logger.error('##########################spider_closed')
    if spider.ncode not in NCODES:
        return

    try:
        novel = Novel.objects.get(ncode=spider.ncode)
    except ObjectDoesNotExist:
        return

    min_time = datetime.now() - timedelta(minutes=INTERVAL_MINUTES)
    updates = novel.episodes.filter(posted_at__gt=min_time).values_list('number', 'title').all()
    if not updates:
        spider.logger.error(f'##########################更新されなかったよ！')
        return

    update_texts = f'{NCODES[spider.ncode]}\n' + '\n'.join(
        map(lambda number, title: f'・{title} ({spider.start_urls[0]}{number}/)', updates)
    )

    auth = tweepy.OAuthHandler(TWITTER_CK, TWITTER_CS)
    auth.set_access_token(TWITTER_AT, TWITTER_AS)
    api = tweepy.API(auth)

    updates_len = len(updates)
    spider.logger.error(f'##########################{updates_len}話更新されたよ！\n{"".join(update_texts)}')
    try:
        api.update_status(f'{updates_len}話更新されたよ！\n' + '\n'.join(update_texts))
    except tweepy.TweepError as e:
        spider.logger.error(e)
