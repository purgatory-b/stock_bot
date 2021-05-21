import requests
from bs4 import BeautifulSoup

class Zone(object):
    def __init__(self, data, zoneName):
        self.data = data
        self.zoneName = zoneName
        self.county = None
        self.town = None

    def findCounty(self):
        isCounty = None
        for zone in self.data:
            if zone['name'] == self.zoneName:
                self.county = zone['name']
                self.town = zone['districts'][0]['name']
                isCounty = True
        return isCounty

    def getFullZone(self):
        self.findCounty()
        return '{}/{}'.format(self.town, self.county)

class Weather(object):
    def __init__(self, fullZone):
        self.fullZone = fullZone

    # YAM 氣象
    def yamWeather(self):
        target_url = 'https://weather.yam.com/' + self.fullZone
        print('Start parsing weather ...')
        rs = requests.session()
        res = rs.get(target_url, verify=False)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        content = ''
        descs = soup.find(class_='info').find(class_='container').find_all('p')
        for desc in descs:
            content += '\n{}'.format(desc.text)

        today = soup.find(class_='today')
        temperature = today.find(class_='tempB').text
        content += '\n氣溫：{}\n'.format(temperature)

        others = today.select('.right .wrap .detail')[0].find_all('p')
        for other in others:
            content += '\n{}'.format(other.text)

        return content