from scrapy.spiders import Spider
from scrapy.http import Response
from twisted.python.failure import Failure


def spider_error(failure: Failure, response: Response, spider: Spider):
    spider.logger.error("##### HANDLE ERROR #####")
    spider.logger.error(f'in {spider}')
    spider.logger.error(failure.type)
    spider.logger.error(failure.getErrorMessage())
    spider.logger.error("###### TRACE BACK ######")
    spider.logger.error(failure.getTraceback())
    spider.logger.error('########################')
