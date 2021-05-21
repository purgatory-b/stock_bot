import requests
from bs4 import BeautifulSoup

class News(object):
    def __init__(self, req):
        self.type = req.get("queryResult").get("parameters").get("serviceterm")
        self.chat_id = self.chat_id = req.get("originalDetectIntentRequest").get("payload").get("data").get("callback_query").get("message").get("chat").get("id")
    
    def google(self):
        target_url = 'https://news.google.com/topstories?hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'
        print('Start parsing google news....')
        rs = requests.session()
        res = rs.get(target_url, verify=False)
        soup = BeautifulSoup(res.text, 'html.parser')

        content = ''
        for index, news in enumerate(soup.find_all(class_='NiLAwe')):
            try:
                if index == 10:
                    return content
                title = news.find(class_='DY5T1d').text
                link = 'https://news.google.com/' + \
                    news.find(class_='DY5T1d')['href']
                #image = news.find(class_='tvs3Id')['src']
                content += '{}\n{}\n\n\n'.format(title, link)
            except:
                print('')

        return content

    # TechNews
    def technews(self):
        target_url = 'https://technews.tw/'
        print('Start parsing movie ...')
        rs = requests.session()
        res = rs.get(target_url, verify=False)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        content = ""

        for index, data in enumerate(soup.select('article div h1.entry-title a')):
            if index == 12:
                return content
            title = data.text
            link = data['href']
            content += '{}\n{}\n\n'.format(title, link)
        return content

    # 泛新聞
    def panx(self):
        target_url = 'https://panx.asia/'
        print('Start parsing ptt hot....')
        rs = requests.session()
        res = rs.get(target_url, verify=False)
        soup = BeautifulSoup(res.text, 'html.parser')
        content = ""
        for data in soup.select('div.container div.row div.desc_wrap h2 a'):
            title = data.text
            link = data['href']
            content += '{}\n{}\n\n'.format(title, link)
        return content