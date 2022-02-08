import scrapy
import itertools
import re
from scrapy.crawler import CrawlerProcess


class Spider(scrapy.Spider):
    name='bgmIndexSpider'
    start_urls = [
        'http://mirror.bgm.rincat.ch/anime/browser',
    ]

    pageCnt = itertools.count(2)
    #pageCnt = (i for i in range(285, 288))

    def parse(self, response):
        for subject in response.css('li.item'):
            yr = re.search('(20\d\d)|(19\d\d)',
                           subject.css('p.info::text').get())
            yield {subject.css('a::attr(href)').get().split('/')[2]: yr.group() if yr else ''}

        pageNum = next(self.pageCnt, None)
        if response.css('li.item').get() is not None:
            next_page = response.urljoin(
                'http://mirror.bgm.rincat.ch/anime/browser/?page='+str(pageNum))
            print(next_page)
            yield scrapy.Request(next_page, callback=self.parse)


process = CrawlerProcess(settings={
    'FEEDS': {
        './data/scrapeIndex.json': {
            'format': 'json',
            'overwrite': True,
        },
    },
    'FEED_EXPORT_ENCODING': 'utf-8',
    'ROBOTSTXT_OBEY': False,
    'LOG_FILE': 'log.txt',
    'LOG_LEVEL': 'INFO',
})
process.crawl(Spider)
process.start()
