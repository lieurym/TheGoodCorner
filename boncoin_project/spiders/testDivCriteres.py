def parse_annonce(self, response):
    # recupere les informations qui nous interesse par chaque page d annonce (comme le prix, le quartier, la taille, etc...)
    annonce = response.meta['annonce']
    annonce['titre'] = ' '.join(response.xpath('//h1[@class ="_1KQme"]/text()').extract()).replace(";", " ")
    annonce['prix'] = response.xpath('//span[@class ="_1F5u3"]/text()').extract()[0]
    annonce['descr'] = ' '.join(response.xpath('//span[@class ="content-CxPmi"]/text()').extract()).replace(";", " ")
    annonce['time'] = self.aDate.today()
    annonce['honoraires'] = response.xpath('//div[@class ="_3Jxf3"]/text()').extract()[0]
    annonce['typebien'] = response.xpath('//div[@class ="_3Jxf3"]/text()').extract()[1]
    annonce['nbpieces'] = response.xpath('//div[@class ="_3Jxf3"]/text()').extract()[2]
    annonce['surface'] = response.xpath('//div[@class ="_3Jxf3"]/text()').extract()[3]
    yield annonce

def parse_annonce(self, response):
    # recupere les informations qui nous interesse par chaque page d annonce (comme le prix, le quartier, la taille, etc...)
    annonce = response.meta['annonce']
    annonce['titre'] = ' '.join(response.xpath('//h1[@class ="_1KQme"]/text()').extract()).replace(";"," ")
    annonce['prix'] = response.xpath('//span[@class ="_1F5u3"]/text()').extract()[0]
    annonce['descr'] = ' '.join(response.xpath('//span[@class ="content-CxPmi"]/text()').extract()).replace(";"," ")
    annonce['time'] = self.aDate.today()
    for critere in response.xpath('//div[@class ="_3Jxf3"]/text()'):
        if critere == "Honoraires":
            annonce['honoraires'] = response.xpath('//div[@class ="_3Jxf3"]/text()').extract()
        if critere == "Type de bien":
            annonce['typebien'] = response.xpath('//div[@class ="_3Jxf3"]/text()').extract()
        if critere == "Pièces":
            annonce['nbpieces'] = response.xpath('//div[@class ="_3Jxf3"]/text()').extract()
        if critere == "Surface":
            annonce['surface'] = response.xpath('//div[@class ="_3Jxf3"]/text()').extract()
        yield annonce