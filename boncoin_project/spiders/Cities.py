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
        'FEED_URI' : 'ParisScrap2.csv',
        'DEFAULT_REQUEST_HEADERS': {
        'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3'},
    }

    start_urls = ['https://www.leboncoin.fr/recherche/?category=9&locations=d_75&real_estate_type=1,2,3']
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
         for p in range(1,7):
             # modifier l'URL (en prenant en compte le "&page=" pour avoir l'extraction sur le nombre de pages voulues
             # la boucle permet de mettre un nombre (de n a m) en fin d'URL specifiant le numéro de page qu'on veut scraper
            urls = 'https://www.leboncoin.fr/recherche/?category=9&locations=d_75&real_estate_type=1,2,3&page='+ str(p)
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

        # on récupère ici le titre de l'annonce
        annonce['titre'] = ' '.join(response.xpath('//h1[@class ="_1KQme"]/text()').extract()).replace(";"," ")

        # on récupère ici le prix de l'annonce
        annonce['prix'] = response.xpath('//span[@class ="_1F5u3"]/text()').extract()[0]

        # si on veut récupèrer la description complète de l'annonce (texte parfois assez long...)
        #annonce['descr'] = ' '.join(response.xpath('//span[@class ="content-CxPmi"]/text()').extract()).replace(";"," ")
        # on récupère l'heure et la date auxquelles on a scrappé l'annonce (sorte d'ID de temps en gros)
        annonce['time'] = self.aDate.today()

        # plus bas on récupère les infos d'une même div contenant à la fois le fait qu'il y ait ou non des honoraires à prendre
        # en compte, la surface du bien, le nombre de pièces du bien, et le type de bien (maison, appartement, etc).
        # si il y a des honoraires pour agent a prendre en compte
        annonce['honoraires'] = response.xpath('//div[@data-qa-id="criteria_item_fai_included"]/div/div[2]/text()').extract()

        # quel type de bien (appartement, maison, terrain)
        annonce['typebien'] = response.xpath('//div[@data-qa-id="criteria_item_real_estate_type"]/div/div[2]/text()').extract()

        # le nombre de pièces du bien
        annonce['nbpieces'] = response.xpath('//div[@data-qa-id="criteria_item_rooms"]/div/div[2]/text()').extract()

        # la surface en m2 du bien (essayer de virer le "m2" à la fin de chaque ligne)
        annonce['surface'] = response.xpath('//div[@data-qa-id="criteria_item_square"]/div/div[2]/text()').extract()

        # on essaye ici de récupérer la classe d'energie du bien immobilier ('A','B','C','D','E','F' ou 'G') en se basant sur
        # la partie de la div mise en exergue quand cette classe doit ressortir (en plus grand) = "_1sd0z"
        # apparemment xpath boucle automatiquement, donc pas besoin de rechercher dans chaque div. On essaye avec ça (et ça marche !):
        # la classe d'energie du bien ("contains" permet de récupérer la div avec l'ID qui nous intéresse):
        annonce['classenergie'] = response.xpath('//div[@class="_2Fdg- _1kx3G"]/div[contains(@class,"_1sd0z")]/text()').extract()

        # le GES (Gaz a Effet de Serre) emis par le bien immobilier ("contains" permet de récupérer la div avec l'ID qui nous intéresse):
        annonce['ges'] = response.xpath('//div[@class="_2Fdg- QGdfG"]/div[contains(@class,"_1sd0z")]/text()').extract()

        # ici on récupère la date et l'heure auxquelles l'annonce a été postée
        annonce['dhannonce'] = ' '.join(response.xpath('//div[@data-qa-id="adview_date"]/text()').extract()).replace("à"," ")

        # on essaye de récupérer juste l'heure de l'annonce MARCHE PAS POUR L'INSTANT
        #annonce['annonceh'] = response.xpath('//div[@data-qa-id="adview_date"]/text[-5;-0]()').extract()

        # et on essaye de récupérer juste la date de l'annonce MARCHE PAS POUR L'INSTANT
        #annonce['annonced'] = response.xpath('//div[@data-qa-id="adview_date"]/text()').extract()[0]

        # on récupère le nom de la commune (il faut le faire en MAJ ou UPPERCASE pour le comparer ensuite à la BDD INSEE)
        # (bon c'est assez laid mais ça marche)
        annonce['ville'] = response.xpath('//div[@data-qa-id="adview_location_informations"]//text()').extract()[0]\
        .replace("á", "a").replace("à", "a").replace("â", "a").replace("ä", "a") \
        .replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e") \
        .replace("í", "i").replace("ì", "i").replace("î", "i").replace("ï", "i") \
        .replace("ó", "o").replace("ò", "o").replace("ô", "o").replace("ö", "o") \
        .replace("ú", "u").replace("ù", "u").replace("û", "u").replace("ü", "u") \
        .replace("'", " ").replace("-", " ").upper()

        # et on récupère le code postal de la commune, a ne pas confondre avec le code INSEE de la commune
        annonce['codepost'] = response.xpath('//div[@data-qa-id="adview_location_informations"]//text()').extract()[2]


        yield annonce

    # On cherche désormais a joindre les données récupérées dans le nouveau tableau par scraping aux données existantes dans
    # le tableau "code_postaux_INSEE.CSV" pour obtenir les codes INSEE et non pas les codes postaux de chaque commune scrapée
    # On se base pour cela sur les noms des communes en MAJUSCULE pour faire correspondre les deux tables ("ville" == "nom de
    # la commune")








