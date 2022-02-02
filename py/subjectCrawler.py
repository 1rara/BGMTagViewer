import scrapy
import json
import random
from scrapy.crawler import CrawlerProcess


class Spider(scrapy.Spider):
    name = 'bgm3'

    start_urls = []
    years = []
    data = {}
    for i in json.load(open('../data/scrapeIndex.json')):
        data.update(i)
    print(len(data))

    for i in data:
        if data[i] and i != '':
            start_urls.append(
                'https://api.bgm.tv/v0/subjects/'+i)
        else:
            print('year not exist:', i)
    #start_urls = random.sample(start_urls, 20)

    def parse(self, response):
        res = json.loads(response.text)
        res['year'] = self.data[str(res['id'])]
        res.pop('summary', None)
        res.pop('images', None)

        yield res


process = CrawlerProcess(settings={
    'FEEDS': {
        '../data/subject.json': {
            'format': 'json',
            'overwrite': True,
        },
    },
    'FEED_EXPORT_ENCODING': 'utf-8',
    'DEFAULT_REQUEST_HEADERS': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en',
        'Authorization': 'Bearer 43051348633aefda11d427ba046339960f2e337a',
    },
    'ROBOTSTXT_OBEY': False,
    'LOG_FILE': 'log.txt',
    'LOG_LEVEL': 'INFO',
})
process.crawl(Spider)
process.start()
