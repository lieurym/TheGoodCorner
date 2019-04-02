import scrapy

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging


#https://doc.scrapy.org/en/latest/topics/practices.html

from boncoin_project.spiders import Cities

configure_logging()
runner = CrawlerRunner()

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(Cities.Cities)
    #yield runner.crawl(another spyder)
    reactor.stop()

crawl()
reactor.run()