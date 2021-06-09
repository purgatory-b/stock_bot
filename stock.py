import os
from datetime import datetime
import requests

import numpy as np
import plotly.graph_objects as go

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Stock(object):
    def __init__(self, req):
        self.type = req.get("queryResult").get("parameters").get("serviceterm")
        self.chat_id = req.get("user").get("chat").get("id")

    def idvStock(self, req):
        stockNo = req.get("queryResult").get("parameters").get("twstock")
        url = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY'
        params = dict(
            response='json',
            date=datetime.today().strftime("%Y%m%d"),
            stockNo=req.get("queryResult").get("parameters").get("twstock")
        )
        res = requests.get(url=url, params=params)
        jsonData = res.json()
        print(jsonData)
        #轉換 list 變 numpy 陣列
        nData = np.array(jsonData.get('data'))
        return '今日:{}\r\n{}:{}, {}:{}, {}:{}, {}:{}'.format(
            params.get("date"), 
            jsonData.get('fields')[3], nData[0,3], 
            jsonData.get('fields')[4], nData[0,4], 
            jsonData.get('fields')[4], nData[0,4], 
            jsonData.get('fields')[5], nData[0,5], 
            jsonData.get('fields')[6], nData[0,6]
        )

    def inlineList(self, req, bot):
        self.chat_id = req.get("user").get("chat").get("id")
        keyboard = [
            [
                InlineKeyboardButton("日成交統計", callback_data='day stat'),
                InlineKeyboardButton("月成交統計", callback_data='month stat'),
                InlineKeyboardButton("年成交統計", callback_data='year stat'),
            ]
        ]

        replyMarkup = InlineKeyboardMarkup(keyboard)
        bot.sendMessage(chat_id=self.chat_id, text='成交資訊統計圖：', reply_markup=replyMarkup)
        speech = "已直接在 telegram 回應"
        return { 
            "textToSpeech": speech,
            "ssml": speech,
            "displayText": speech
            }
    
    #個股日成交資訊
    #https://www.twse.com.tw/zh/page/trading/exchange/STOCK_DAY.html
    def idvStockChart(self, req, bot):
        self.chat_id = req.get("user").get("chat").get("id")
        context = req.get("queryResult").get("outputContexts")[0].get("parameters")

        url = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY'
        params = dict(
            response='json',
            date=datetime.today().strftime("%Y%m%d"),
            stockNo=context.get("twstock")
        )
        res = requests.get(url=url, params=params)
        jsonData = res.json()
        #轉換 list 變 numpy 陣列
        nData = np.array(jsonData.get('data'))

        fig = go.Figure(data=[go.Candlestick(x=nData[:,0],
            open=nData[:,3],
            high=nData[:,4],
            low=nData[:,5],
            close=nData[:,6])])

        if not os.path.exists("images"):
            os.mkdir("images")

        fig.write_image("images/dayTrend.png")

        req.get("queryResult").get("outputContexts")[0].get("parameters").get("twstock")
        #https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#working-with-files-and-media
        bot.sendPhoto(chat_id=self.chat_id, photo=open('images/dayTrend.png', 'rb'), caption=context.get('twstock.original'))
        speech = context.get('twstock.original') + "個股日成交資訊"
        return { 
            "textToSpeech": speech,
            "ssml": speech,
            "displayText": speech
            }