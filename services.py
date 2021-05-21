from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Services(object):
    def __init__(self, req):
        self.type = req.get("queryResult").get("parameters").get("serviceterm")
        self.chat_id = None
    
    def inlineList(self, req, bot):
        self.chat_id = req.get("originalDetectIntentRequest").get("payload").get("data").get("chat").get("id")
        keyboard = [
            [
                InlineKeyboardButton("新聞", callback_data='news'),
                InlineKeyboardButton("氣象", callback_data='weather'),
                InlineKeyboardButton("油價", callback_data='oil price'),
            ],
            [InlineKeyboardButton("商品詢價(拍賣平台)", callback_data='price')],
        ]

        replyMarkup = InlineKeyboardMarkup(keyboard)
        bot.sendMessage(chat_id=self.chat_id, text='請選擇以下服務：', reply_markup=replyMarkup)
        speech = "已直接在 telegram 回應"
        return { 
            "textToSpeech": speech,
            "ssml": speech,
            "displayText": speech
            }