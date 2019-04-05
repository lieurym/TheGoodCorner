# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Annonces(scrapy.Item):
    #permet de presenter les informations scrappees
    titre = scrapy.Field()
    prix = scrapy.Field()
    url = scrapy.Field()
    time = scrapy.Field()
    #descr = scrapy.Field()
    honoraires = scrapy.Field()
    typebien = scrapy.Field()
    nbpieces = scrapy.Field()
    surface = scrapy.Field()
