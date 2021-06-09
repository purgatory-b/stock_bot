'''
‧Tutorial_8
‧記錄到資料庫
'''
import json
import configparser

from flask import Flask
from flask import request
from flask import make_response

import telegram

from util import Switch
from services import Services
from weather import Zone, Weather
from news import News
from price import OilPrice
from stock import Stock

from chatdb import ChatDB

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
        if case('stock'):
            print('詢問股票行情')
            response = askStockList(req, bot)
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
    #回傳
    return { 
      "textToSpeech": speech,
      "ssml": speech,
      "fulfillmentText": speech,
      "displayText": speech
    }

def askOilPrice(req):
    p = OilPrice(req)
    speech = p.price()
    print("Response:")
    print(speech)
    #回傳
    return { 
      "textToSpeech": speech,
      "ssml": speech,
      "fulfillmentText": speech,
      "displayText": speech
    }

def askPrice(req):
    return None

def askStock(req, bot):
    s = Stock(req)
    speech = s.idvStock(req)
    s.inlineList(req, bot)
    print("Response:")
    print(speech)
    #回傳
    return { 
      "textToSpeech": speech,
      "ssml": speech,
      "fulfillmentText": speech,
      "displayText": speech
    }

def askStockList(req):
    s = Stock(req)
    speech = s.stockList(req)
    print("Response:")
    print(speech)
    #回傳
    return { 
      "textToSpeech": speech,
      "ssml": speech,
      "fulfillmentText": speech,
      "displayText": speech
    }

def askStockChart(req, bot):
    s = Stock(req)
    speech = s.idvStockChart(req, bot)
    print("Response:")
    print(speech)
    #回傳
    return { 
      "textToSpeech": speech,
      "ssml": speech,
      "fulfillmentText": speech,
      "displayText": speech
    }


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
        if case('askStock'):
            print('詢問股票行情')
            response = askStock(req, bot)
            break
        if case('askStock-chart'):
            print('查詢股票圖表')
            response = askStockChart(req, bot)
            break
        if case():
            print('無對應動作')

    return response

def reqRefactor(req):
    if req.get("originalDetectIntentRequest").get("payload").get("data").get("callback_query"):
        req["user"] = req.get("originalDetectIntentRequest").get("payload").get("data").get("callback_query")
    else:
        req["user"] = req.get("originalDetectIntentRequest").get("payload").get("data")

    if req.get("user").get("message"):
        req["user"]["chat"] = req.get("user").get("message").get("chat")

    return req

def recordToDB(req, res):
    db = ChatDB(config['mysql'])
    db.connect()

    user = {
        'user_id': req.get("user").get("from").get("id"),
        'chat_id': req.get("user").get("chat").get("id"), 
        'nicename': req.get("user").get("from").get("username"),
        'display_name': req.get("user").get("from").get("first_name") + " " + req.get("user").get("from").get("last_name")
    }
    
    userID = db.find_user(user)
    if userID == None :
        userID = db.create_user(user)

    print("userID:" + str(userID))

    chat = {
        'chat_user': userID,
        'chat_ask': req.get("queryResult").get("queryText"),
        'bot_response': json.dumps(res, ensure_ascii=False),
        'bot_response_type': 'text', 
        'chat_parent': 0,
        'chat_intent': req.get("queryResult").get("intent").get("displayName"),
        'chat_action': req.get("queryResult").get("action"), 
        'chat_entity': json.dumps(req.get("queryResult").get("parameters"), ensure_ascii=False),
        'chat_context': json.dumps(req.get("queryResult").get("outputContexts"), ensure_ascii=False)
    }

    db.create_chat(chat)

    db.close()

def makeWebhookResult(req):
    req = reqRefactor(req)
    res = doAction(req)
    recordToDB(req, res)
    if res == None:
        return {}
    
    print("Response:")
    print(res)
    #回傳
    return res

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8-sig")

    telegramToken = config['telegram']['Token']
    bot = telegram.Bot(token=telegramToken)

    app.run()