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
        # permet de gerer le nombre de secondes entre chaque requete (une requete = le scrapping d'une annonce)
        'DOWNLOAD_DELAY':'2',
        'COOKIES_ENABLED':True,
        'HTTPERROR_ALLOWED_CODES':[404],
        'FEED_EXPORTERS': {
            'csv': 'scrapy.exporters.CsvItemExporter'},
        # permet de selectionner le format du fichier en sortie
        'FEED_FORMAT' : 'csv',
        #permet de specifier l'encodage du fichier en sortie
        'FEED_EXPORT_ENCODING' : 'utf-8',
        # nomme le fichier CSV en sortie
        'FEED_URI' : 'output8.csv',
        'DEFAULT_REQUEST_HEADERS': {
        'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3'},
    }

    start_urls = ['https://www.leboncoin.fr/recherche/?category=9&locations=Paris_75013']
    allowed_domains = ['leboncoin.fr']

# user id que le site voit, il nous autorise a consulter ses pages tant qu'il ne nous considere pas comme un robot
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
        # lance la premiere requete, cree le CSV qui sera a remplir en sortie
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback = self.parse_page)

    def parse_page(self, response):
        # recupere le nombre d annonce avec un xpath pour en faire un modulo pour avoir le nombre de pages
         for p in range(1,3):
             # dans les 2 premieres pages (1 inclus à 3 exclus) on ajoute
            urls = 'https://www.leboncoin.fr/recherche/?category=9&locations=Paris_75013&real_estate_type=1,2,3&page='+ str(p)
            yield scrapy.Request(url = urls, callback = self.parse, priority=1)


    def parse(self, response):
        # recupere le nombre d annonces par page (35 normalement) ainsi que l URL de chaque page d annonce, dont on extrait
        # le "clearfix trackable" qui est l identifiant unique de chaque page sur le site du Bon Coin
        extra = response.xpath('//a[@class="clearfix trackable"]/@href').extract()
        for i in extra:
            # on concatene l'identifiant unique de chaque page avec l'URL de base du bon coin
            url2 = "https://www.leboncoin.fr"+i
            annonce = Annonces()
            annonce['url'] = url2
            print(i)
            # pour ensuite aller recuperer
            yield scrapy.Request(url=url2, callback = self.parse_annonce, meta={"annonce":annonce})

    def parse_annonce(self, response):
        # recupere les informations qui nous interesse par chaque page d annonce (comme le prix, le quartier, la taille, etc...)
        annonce = response.meta['annonce']
        annonce['titre'] = ' '.join(response.xpath('//h1[@class ="_1KQme"]/text()').extract()).replace(";"," ")
        annonce['prix'] = response.xpath('//span[@class ="_1F5u3"]/text()').extract()[0]
        #annonce['descr'] = ' '.join(response.xpath('//span[@class ="content-CxPmi"]/text()').extract()).replace(";"," ")
        annonce['time'] = self.aDate.today()
        # plus bas on récupère les infos d'une même div contenant à la fois le fait qu'il y ait ou non des honoraires à prendre
        # en compte, la surface du bien, le nombre de pièces du bien, et le type de bien (maison, appartement, etc).
        annonce['honoraires'] = response.xpath('//div[@data-qa-id="criteria_item_fai_included"]/div/div[2]/text()').extract()
        annonce['typebien'] = response.xpath('//div[@data-qa-id="criteria_item_real_estate_type"]/div/div[2]/text()').extract()
        annonce['nbpieces'] = response.xpath('//div[@data-qa-id="criteria_item_rooms"]/div/div[2]/text()').extract()
        annonce['surface'] = response.xpath('//div[@data-qa-id="criteria_item_square"]/div/div[2]/text()').extract()
        yield annonce



        #extra0 = extra.extract()
        #extra1 = extra.xpath('./span[@itemprop="href"]/text()').extract()

        #print(extra0[1])
        #print(len(extra0))
        #print("------------------------------------------------------")
        #print(extra1[39])
        #print(len(extra1))







