import requests
from bs4 import BeautifulSoup

class OilPrice(object):
    def __init__(self, req):
        self.type = req.get("queryResult").get("parameters").get("serviceterm")
        self.chat_id = self.chat_id = req.get("originalDetectIntentRequest").get("payload").get("data").get("callback_query").get("message").get("chat").get("id")
    
    def price(self):
        target_url = 'https://gas.goodlife.tw/'
        rs = requests.session()
        res = rs.get(target_url, verify=False)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')

        title = soup.select('#main')[0].text.replace('\n', '').split('(')[0]
        gas_price = soup.select('#gas-price')[0].text.replace('\n\n\n', '').replace(' ', '')
        cpc = soup.select('#cpc')[0].text.replace(' ', '')
        content = '{}\n{}{}'.format(title, gas_price, cpc)
        return content