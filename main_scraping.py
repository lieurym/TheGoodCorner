import scrapy


# twisted est la librairie qui permet de lancer les spiders
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging


#https://doc.scrapy.org/en/latest/topics/practices.html

#from boncoin_project.spiders import Cities
from boncoin_project.spiders import locations

configure_logging()
runner = CrawlerRunner()


# on definit un runer (crawl) qui va lancer les spiders

@defer.inlineCallbacks
def crawl():
    #yield runner.crawl(Cities.Cities)
    yield runner.crawl(locations.Locations)
    #yield runner.crawl(another spyder)
    reactor.stop()

# pour les spiders, on peut définir un fichier.csg
crawl()
reactor.run()