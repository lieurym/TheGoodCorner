from bs4 import BeautifulSoup
import scrapy
import cfscrape
from fake_useragent import UserAgent
import pendulum
import json
import random
from boncoin_project.items.Items import *
import csvkit
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

class Locations(scrapy.Spider):
    name = "locations"

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
        'FEED_URI' : 'locationOUT.csv',
        'DEFAULT_REQUEST_HEADERS': {
        'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3'},
    }

    start_urls = ['https://www.leboncoin.fr/recherche/?category=10&real_estate_type=1,2']
    allowed_domains = ['leboncoin.fr']

# user id que le site voit, il nous autorise a consulter ses pages tant qu'il ne nous considere pas comme un robot
    ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'

    def __init__(self, aDate = pendulum.today()):
        super(Locations, self).__init__()
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
        # on importe tout d'abord le CSV qu'on veut (celui avec les éléments qui nous intéressent pour construire l'URL
         csvcible1 = pd.read_csv('All_Com_IN_6.csv')
        # ensuite, pour chaque ligne ("NomCommune_CodePostal" dans la colonne qui nous interesse, on demande au programme
        # de compléter l'URL en immisçant au milieu "ligne" et en rajoutant le numéro de page à la fin
         for ligne1 in csvcible1.loc[: ,"ID_URL"].replace("É", "E").replace("' ", "'").replace(" '","'"):
             print(ligne1)
             urllen = 'https://www.leboncoin.fr/recherche/?category=10&locations='+ ligne1 + '&real_estate_type=1,2'
             print(urllen)
             yield scrapy.Request(url = urllen, callback= self.parse_nbpages, meta={"ligne1":ligne1})


    def parse_nbpages (self, response):
        # on récupère le nom de la commune de la fonction 'parse_page'
            ligne1 = response.meta['ligne1']


        # on concatene pour chaque commune le nombre d'annonces qui est dans un /span
            nbannonces = str(' '.join(response.xpath('//p/span[@class="_2ilNG"]/text()').extract()).replace(" ", ""))
        # on passe le nb d'annonce en integrer pour faciliter le calcul plus bas
            nbpages = int(nbannonces)
        # petit test pour voir si on a bien le bon nombre d'annonces
            print(nbpages)
        # on divise le nombre d'annonce total par le nombre d'annonces par page (35) + 2 pour aussi avoir les annonces
        # sur la dernière page, et aussi être une page au dessus (au cas où)
            nbpages = round(nbpages/35)+2
            print(nbpages)
        # et on lance une boucle pour récupérer, dans chaque page, le bon nombre d'URL qui seront utilisées dans la fonction
        # suivante ('parse')
            for p in range(1,3): #nbpages
                print(p)
                    # modifier l'URL (en prenant en compte le "&page=" pour avoir l'extraction sur le nombre de pages voulues)
                    # la boucle permet de mettre un nombre (de n a x) en fin d'URL specifiant le numéro de page qu'on veut scraper
                    # en ajoutant "ligne" on glisse le "NomCommune_CodePostal" récupéré plus haut
                urls = 'https://www.leboncoin.fr/recherche/?category=10&locations=' + ligne1 + '&real_estate_type=1,2'+'&page='+ str(p)
                yield scrapy.Request(url = urls, callback = self.parse, priority=1, meta= {"ligne1" : ligne1})


    def parse(self, response):
        # recupere le nombre d annonces par page (35 normalement) ainsi que l URL de chaque page d annonce, dont on extrait
        # le "clearfix trackable" qui est l identifiant unique de chaque page sur le site du Bon Coin
        extra = response.xpath('//a[@class="clearfix trackable"]/@href').extract()
        ligne1 = response.meta['ligne1']
        for i in extra:
            # on concatene l'identifiant unique de chaque page avec l'URL de base du bon coin
            url2 = "https://www.leboncoin.fr"+i
            annonce = AnnonceLoc()
            annonce['url'] = url2
            annonce['ID_URL'] = ligne1
            print(i)
            # pour ensuite aller recuperer
            yield scrapy.Request(url=url2, callback = self.parse_annonce, meta={"annonce":annonce})



    def parse_annonce(self, response):
        # recupere les informations qui nous interesse par chaque page d annonce (comme le prix, le quartier, la taille, etc...)
        annonce = response.meta['annonce']

        # on récupère ici le titre de l'annonce
        annonce['annoncet'] = ' '.join(response.xpath('//h1[@class="_246DF _2S4wz"]/text()').extract()).replace(";"," ")

        # on récupère ici le prix de l'annonce
        annonce['logprix'] = response.xpath('//span[@class ="_1F5u3"]/text()').extract()[0]

        # si on veut récupèrer la description complète de l'annonce (texte parfois assez long...)
        #annonce['descr'] = ' '.join(response.xpath('//span[@class ="content-CxPmi"]/text()').extract()).replace(";"," ")

        # on récupère l'heure et la date auxquelles on a scrappé l'annonce (sorte d'ID de temps en gros)
        #annonce['scraptime'] = self.aDate.today()
        annonce['scrapdate'] = self.aDate.today().to_date_string().replace("-","/")
        annonce['scrapheure'] = self.aDate.today().to_time_string() #.replace(":","/") (SI BESOIN)

        # plus bas on récupère les infos d'une même div contenant à la fois le fait qu'il y ait ou non des honoraires à prendre
        # en compte, la surface du bien, le nombre de pièces du bien, et le type de bien (maison, appartement, etc).
        # si il y a des charges a prendre en compte dans le loyer
        annonce['logcharges'] = response.xpath('//div[@class="_2B0Bw _1nLtd"]//text()').extract()[1]

        # quel type de bien (appartement, maison, terrain)
        annonce['logtypebien'] = response.xpath('//div[@data-qa-id="criteria_item_real_estate_type"]/div/div[2]/text()').extract()

        # le nombre de pièces du bien
        annonce['lognbpieces'] = response.xpath('//div[@data-qa-id="criteria_item_rooms"]/div/div[2]/text()').extract()

        # la surface en m2 du bien (en virant le "m2" à la fin de chaque ligne)
        annonce['logsurface'] = ' '.join(response.xpath('//div[@data-qa-id="criteria_item_square"]/div/div[2]/text()').extract())[:-2]

        # on essaye ici de récupérer la classe d'energie du bien immobilier ('A','B','C','D','E','F' ou 'G') en se basant sur
        # la partie de la div mise en exergue quand cette classe doit ressortir (en plus grand) = "_1sd0z"
        # apparemment xpath boucle automatiquement, donc pas besoin de rechercher dans chaque div. On essaye avec ça (et ça marche !):
        # la classe d'energie du bien ("contains" permet de récupérer la div avec l'ID qui nous intéresse):
        annonce['energieclass'] = response.xpath('//div[@class="_2Fdg- _1kx3G"]/div[contains(@class,"_1sd0z")]/text()').extract()

        # le GES (Gaz a Effet de Serre) emis par le bien immobilier ("contains" permet de récupérer la div avec l'ID qui nous intéresse):
        annonce['energieges'] = response.xpath('//div[@class="_2Fdg- QGdfG"]/div[contains(@class,"_1sd0z")]/text()').extract()

        # ici on récupère la date et l'heure auxquelles l'annonce a été postée
        #annonce['dhannonce'] = ' '.join(response.xpath('//div[@data-qa-id="adview_date"]/text()').extract()).replace("à"," ")

        # on essaye de récupérer juste l'heure de l'annonce
        annonce['annonceh'] = ' '.join(response.xpath('//div[@data-qa-id="adview_date"]/text()').extract())[-5:]

        # et on essaye de récupérer juste la date de l'annonce
        annonce['annonced'] = ' '.join(response.xpath('//div[@data-qa-id="adview_date"]/text()').extract())[:10]

        # on récupère les données de l'agence immobilière si c'en est une :
        # if response.xpath('//div[@data-qa-id="storebox_container"'):
        annonce['agenceimmonom'] = response.xpath('//span[@data-qa-id="storebox_title"]/text()').extract()
        annonce['agenceimmoadresse'] = response.xpath('//li[@data-qa-id="storebox_address"]/div/text()').extract()
        annonce['agenceimmosiret'] = ' '.join(response.xpath('//li[@data-qa-id="storebox_siret"]/div/text()').extract())[10:]
        annonce['agenceimmosiren'] = ' '.join(response.xpath('//li[@data-qa-id="storebox_siren"]/div/text()').extract())[10:]
        '''
        driver = webdriver.Firefox()
        webdriver.find_element_by_css_selector('class="_2sNbI ObuDQ GXQkc _2xk2l"').click()
        annonce['agenceimmotel'] = ' '.join(response.xpath('//a[@class="_2sNbI ObuDQ GXQkc _2BP2c"]/text()').extract())
        '''

        # on récupère le nom de la commune (il faut le faire en MAJ ou UPPERCASE pour le comparer ensuite à la BDD INSEE)
        # (ça fait l'inverse de ce qu'on lui demande: les communes avec les SAINT qu'on veut garder passent en ST )
        listeSaints = ('Lieusaint','Saints','Saintry-sur-Seine', 'Saintlieu', 'Saint-Symphorien-le-Château', 'Saint-Maur-de-Fossés', 'Saints', "Saint-Cyr-l'Ecole")
        if response.xpath('//div[@data-qa-id="adview_location_informations"]//text()').extract()[0] not in listeSaints:
            annonce['logville'] = response.xpath('//div[@data-qa-id="adview_location_informations"]//text()').extract()[0]\
            .replace("á", "a").replace("à", "a").replace("â", "a").replace("ä", "a") \
            .replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e") \
            .replace("í", "i").replace("ì", "i").replace("î", "i").replace("ï", "i") \
            .replace("ó", "o").replace("ò", "o").replace("ô", "o").replace("ö", "o") \
            .replace("ú", "u").replace("ù", "u").replace("û", "u").replace("ü", "u") \
            .replace("'", " ").replace("-", " ").replace("É", "e").replace("ç", "c") \
            .replace("Ç ","c").replace("Ÿ","Y").replace("ÿ","y").replace("Î","I")\
            .upper().replace(" SAINT "," ST ").replace(" SAINTS "," ST ").replace("-SAINT ", "-ST ")\
            .replace("-SAINTS ", "-ST ").replace(" SAINT-"," ST-").replace(" SAINTS-"," ST-") \
            .replace("-SAINT-", "-ST-").replace("-SAINTS-", "-ST-").replace("SAINT","ST")\
            .replace("SAINTS","ST")
        elif response.xpath('//div[@data-qa-id="adview_location_informations"]//text()').extract()[0] in listeSaints:
            annonce['logville'] = response.xpath('//div[@data-qa-id="adview_location_informations"]//text()').extract()[0] \
            .replace("á", "a").replace("à", "a").replace("â", "a").replace("ä", "a") \
            .replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e") \
            .replace("í", "i").replace("ì", "i").replace("î", "i").replace("ï", "i") \
            .replace("ó", "o").replace("ò", "o").replace("ô", "o").replace("ö", "o") \
            .replace("ú", "u").replace("ù", "u").replace("û", "u").replace("ü", "u") \
            .replace("Ç ","c").replace("'", " ").replace("-", " ").replace("É", "e").replace("ç", "c").upper()

        # et on récupère le code postal de la commune, a ne pas confondre avec le code INSEE de la commune
        annonce['logcodepost'] = str(response.xpath('//div[@data-qa-id="adview_location_informations"]//text()').extract()[2]).zfill(5)



        yield annonce

    # On cherche désormais a joindre les données récupérées dans le nouveau tableau par scraping aux données existantes dans
    # le tableau "code_postaux_INSEE.CSV" pour obtenir les codes INSEE et non pas les codes postaux de chaque commune scrapée
    # On se base pour cela sur les noms des communes en MAJUSCULE pour faire correspondre les deux tables ("ville" == "nom de
    # la commune")








