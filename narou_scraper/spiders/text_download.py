# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Response
from django.core.exceptions import ObjectDoesNotExist

from narou_scraper.items import TextItem
from narou_scraping.local_settings import NAROU_MAIL, NAROU_PASSWORD
from narou.models import Novel


class TextDownloadSpider(scrapy.Spider):
    name = 'text_download'
    allowed_domains = ['ncode.syosetu.com', 'ssl.syosetu.com']
    custom_settings = {
        'ITEM_PIPELINES': {'narou_scraper.pipelines.TextPipeline': 300},
    }

    # episode_num = 0 の場合全話一括ダウンロード
    def __init__(self, ncode_int: int, episode_num: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ncode_int = ncode_int
        self.episode_num = episode_num

    def start_requests(self):
        if self.episode_num == 0:
            return [scrapy.Request(
                url=f'https://ncode.syosetu.com/txtdownload/top/ncode/{self.ncode_int}/',
                callback=self.parse,
            )]
        else:
            return [self.create_request(self.episode_num, self.parse)]

    def create_request(self, num, callback):
        return scrapy.FormRequest(
            url=f'https://ncode.syosetu.com/txtdownload/dlstart/ncode/{self.ncode_int}/',
            formdata={'no': str(num), 'hankaku': '0', 'code': 'utf-8', 'kaigyo': 'crlf'},
            callback=callback,
            dont_filter=True,
            meta={'no': num},
        )

    def parse(self, response: Response):
        if response.url == 'https://ssl.syosetu.com/login/input/':
            self.logger.info('-------------------------log in')
            return scrapy.FormRequest.from_response(
                response,
                formdata={'narouid': NAROU_MAIL, 'pass': NAROU_PASSWORD},
                callback=self.check_login,
            )
        if self.episode_num == 0:
            return self.download()

    def parse_item(self, response: Response):
        if response.url.split('/')[-4] == 'dlstart':
            return TextItem(
                ncode_int=self.ncode_int,
                episode_num=response.meta['no'],
                text=response.body.decode("utf-8", "ignore"),
            )

    def check_login(self, response: Response):
        self.logger.info('-------------------------check login')
        self.logger.info('-------------------------url = ' + response.url)
        if response.url == 'https://ssl.syosetu.com/login/login/':
            self.logger.error("Login failed")
            return
        return self.download()

    def download(self):
        if self.episode_num == 0:
            try:
                novel = Novel.objects.get(ncode_int=self.ncode_int)
            except ObjectDoesNotExist:
                self.logger.error('This novel does not exist')
                return
            return (self.create_request(i, self.parse_item) for i in range(1, novel.max_episode_num + 1))
        else:
            return [self.create_request(self.episode_num, self.parse_item)]
