
import os

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

    return "OK"