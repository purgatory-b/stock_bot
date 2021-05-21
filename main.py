'''
‧Tutorial_5
‧新增 services class
'''
import json
import os
import configparser

from flask import Flask
from flask import request
from flask import make_response

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from util import Switch
from services import Services
from weather import Zone, Weather
from news import News
from price import OilPrice

app = Flask(__name__)
#run_with_ngrok(app)   #starts ngrok when the app is run
@app.route("/", methods=['GET'])
def hello():
    print(bot.get_me())
    return '您好，我是 vegetabot，很高興為您服務'

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def askServices(req):
    services = Services(req)
    serviceType = services.type

    response = None
    for case in Switch(serviceType):
        if case('weather'):
            print('詢問氣象')
            response = askWeather(req)
            break
        if case('news'):
            print('詢問新聞')
            response = askNews(req)
            break
        if case('oil_price'):
            print('詢問油價')
            response = askOilPrice(req)
            break
        if case('price'):
            print('詢問某商品價格')
            response = askPrice(req)
            break
        if case('services'):
            print('詢問服務項目')
            response = services.inlineList(req, bot)
            break
        if case():
            print('無對應動作')

    return response

def askWeather(req):
    result = req.get("queryResult")
    parameters = result.get("parameters")
    zone = parameters.get("weatherlocation")

    with open('taiwan_districts.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    z = Zone(data, zone)
    fullZone = z.getFullZone()

    w = Weather(fullZone)
    speech = '您所查詢的：{}，目前的氣象如下：{}'.format(fullZone, w.yamWeather())
    print("Response:")
    print(speech)
    #回傳
    return { 
      "textToSpeech": speech,
      "ssml": speech,
      "fulfillmentText": speech,
      "displayText": speech
    }

def askNews(req):
    n = News(req)
    speech = n.google()
    print("Response:")
    print(speech)

    return {
        "textToSpeech":speech,
        "ssml":speech,
        "fulfillmentText":speech,
        "displayText":speech
    }

def askOilPrice(req):
    n = OilPrice(req)
    speech = n.price
    print("Response:")
    print(speech)

    return {
        "textToSpeech":speech,
        "ssml":speech,
        "fulfillmentText":speech,
        "displayText":speech
    }

def askPrice(req):
    return None


def doAction(req):
    response = None
    for case in Switch(req.get("queryResult").get("action")):

        if case('askServices'):
            print('詢問服務項目')
            response = askServices(req)
            break
        if case('askWeather'):
            print('詢問氣象')
            response = askWeather(req)
            break
        if case('askNews'):
            print('詢問新聞')
            response = askNews(req)
            break
        if case('askOilPrice'):
            print('詢問油價')
            response = askOilPrice(req)
            break
        if case('askPrice'):
            print('詢問某商品價格')
            response = askPrice(req)
            break
        if case():
            print('無對應動作')

    return response

def makeWebhookResult(req):
    response = doAction(req)
    if response == None:
        return {}
    
    print("Response:")
    print(response)
    #回傳
    return response

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8-sig")

    telegramToken = config['telegram']['Token']
    bot = telegram.Bot(token=telegramToken)

    app.run()