from bs4 import BeautifulSoup
import scrapy
import cfscrape
from fake_useragent import UserAgent
import pendulum
import json
import random
from boncoin_project.items.Items import *

class Cities(scrapy.Spider):
    name = "cities"

    custom_settings = {
        'CONCURRENT_REQUESTS': '1',
        'DOWNLOAD_DELAY':'3',
        'COOKIES_ENABLED':True,
        'HTTPERROR_ALLOWED_CODES':[404],
        'FEED_EXPORTERS': {
            'csv': 'scrapy.exporters.CsvItemExporter'},
        'FEED_FORMAT' : 'csv',
        'FEED_EXPORT_ENCODING' : 'utf-8',
        'FEED_URI' : 'output.csv',
        'DEFAULT_REQUEST_HEADERS': {
        'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3'},
    }

    start_urls = ['https://www.leboncoin.fr/recherche/?category=9&locations=Paris_75013']
    allowed_domains = ['leboncoin.fr']

    ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'

    def __init__(self, aDate = pendulum.today()):
        super(Cities, self).__init__()
        self.aDate = aDate
        self.timestamp = self.aDate.timestamp()
        print("PENDULUM UTC TODAY", self.aDate.today())
        print("PENDULUM UTC TIMESTAMP TODAY ", self.timestamp)
    def clean_html(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        return soup.get_text()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback = self.parse)

    def parse(self, response):
        extra = response.xpath('//a[@class="clearfix trackable"]/@href').extract()
        for i in extra:
            url2 = "https://www.leboncoin.fr"+i
            annonce = Annonces()
            annonce['url'] = url2
            yield scrapy.Request(url=url2, callback = self.parse_page, meta={"annonce":annonce})

    def parse_page(self, response):
        annonce = response.meta['annonce']
        annonce['titre'] = ' '.join(response.xpath('//h1[@class ="_1KQme"]/text()').extract()).replace(";"," ")
        annonce['prix'] = response.xpath('//span[@class ="_1F5u3"]/text()').extract()[0]
        yield annonce


        #extra0 = extra.extract()
        #extra1 = extra.xpath('./span[@itemprop="href"]/text()').extract()

        #print(extra0[1])
        #print(len(extra0))
        #print("------------------------------------------------------")
        #print(extra1[39])
        #print(len(extra1))







