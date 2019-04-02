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

    start_urls = ['https://www.meilleursagents.com/prix-immobilier/']
    allowed_domains = ['meilleursagents.com']

    ua = UserAgent()

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


    def build_api_call(self,number):
        query = 'https://geo.meilleursagents.com/geo/v1/cities/{communeNumber}?fields=viewport,slug'.format(communeNumber=number)
        return query

    ###################################
    # MAIN PARSE
    ####################################

    def parse(self, response):
        #lCom = list(range(135,38775))
        lCom = list(range(135, 300))

        random.shuffle(lCom)

        for c in lCom:
            yield scrapy.Request(self.build_api_call(c),
                                 headers={'X-Requested-With': 'XMLHttpRequest',
                                          'Content-Type': 'application/json; charset=UTF-8'},
                                 callback=self.parse_commune,meta={'id': c})

    def parse_commune(self,response):
        meta = response.meta
        if response.status == 404:
            #self.seen_404 = True
            print("END OF WORLD")
            item = COMItem()
            item['id'] = meta['id']
            item['place'] = "NA"
        else:
            item = COMItem()
            dataJson = json.loads(response.body_as_unicode())
            item['id'] = dataJson['response']['place']['id']
            item['place'] = dataJson['response']['place']['slug']
        yield item