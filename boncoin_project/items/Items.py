# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Annonces(scrapy.Item):
    #permet de presenter les informations scrappees
    annoncet = scrapy.Field()
    logprix = scrapy.Field()
    url = scrapy.Field()
    #descr = scrapy.Field()
    loghonoraires = scrapy.Field()
    logtypebien = scrapy.Field()
    lognbpieces = scrapy.Field()
    logsurface = scrapy.Field()
    energieclass = scrapy.Field()
    energieges = scrapy.Field()
    #dhannonce = scrapy.Field()
    annonceh = scrapy.Field()
    annonced = scrapy.Field()
    logcodepost = scrapy.Field()
    logville = scrapy.Field()
    #scraptime = scrapy.Field()
    scrapdate = scrapy.Field()
    scrapheure = scrapy.Field()
    ID_URL = scrapy.Field()
    agenceimmonom = scrapy.Field()
    agenceimmoadresse = scrapy.Field()
    agenceimmosiret = scrapy.Field()
    agenceimmosiren = scrapy.Field()
    agenceimmotel = scrapy.Field()


class AnnonceLoc(scrapy.Item):
    #permet de presenter les informations scrappees
    annoncet = scrapy.Field()
    logprix = scrapy.Field()
    url = scrapy.Field()
    #descr = scrapy.Field()
    logcharges = scrapy.Field()
    logtypebien = scrapy.Field()
    lognbpieces = scrapy.Field()
    logsurface = scrapy.Field()
    energieclass = scrapy.Field()
    energieges = scrapy.Field()
    #dhannonce = scrapy.Field()
    annonceh = scrapy.Field()
    annonced = scrapy.Field()
    logcodepost = scrapy.Field()
    logville = scrapy.Field()
    #scraptime = scrapy.Field()
    scrapdate = scrapy.Field()
    scrapheure = scrapy.Field()
    ID_URL = scrapy.Field()
    agenceimmonom = scrapy.Field()
    agenceimmoadresse = scrapy.Field()
    agenceimmosiret = scrapy.Field()
    agenceimmosiren = scrapy.Field()
    agenceimmotel = scrapy.Field()