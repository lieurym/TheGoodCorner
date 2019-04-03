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
            'csv': 'scrapy.exporters.CsvItemExporter',},
        'FEED_FORMAT' : 'csv',
        'FEED_URI' : 'output.csv'
    }

    start_urls = ['https://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/']
    allowed_domains = ['leboncoin.fr']

    ua = 

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
        cf_requests = []
        user_agent = self.ua.random
        self.logger.info("RANDOM user_agent = %s", user_agent)
        for url in self.start_urls:
            token , agent = cfscrape.get_tokens(url,user_agent)
            self.logger.info("token = %s", token)
            self.logger.info("agent = %s", agent)

            cf_requests.append(scrapy.Request(url=url,
                                              cookies= token,
                                              headers={'User-Agent': agent}))
        return cf_requests

    def parse(self, response):

