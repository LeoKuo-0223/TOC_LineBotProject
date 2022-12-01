import os
import requests
import random
import json

from linebot import LineBotApi
from linebot.models import (
    TextSendMessage, FlexSendMessage, QuickReply, QuickReplyButton, PostbackAction
)
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
channel_secret = config.get('line-bot', 'channel_secret')
access_token = config.get('line-bot', 'channel_access_token')
line_bot_api = LineBotApi(access_token)



def get_dict_result(event, query):  #find word in dictionary and send back some choices of partOfSpeech
    items = []
    reply_token = event.reply_token
    try:
        print(query)
        url = 'https://api.dictionaryapi.dev/api/v2/entries/en/'+ query
        response_API = requests.get(url)
        data = response_API.text
        parse_json = json.loads(data)
        # print(parse_json[0]['meanings'][0]['definitions'][0]['definition'])
        # text = parse_json[0]['meanings'][0]['definitions'][0]['definition']
        
        for i in range(len(parse_json[0]['meanings'])):
            # button = QuickReplyButton(
            #     action=MessageAction(label=f"{playlists[i][1]}", text=f"{playlists[i][1]}")
            # )
            definition = parse_json[0]['meanings'][i]['definitions'][0]['definition']
            partOfSpeech = parse_json[0]['meanings'][i]['partOfSpeech']
            # print(parse_json[0]['meanings'][i]['definitions'][0])
            try:
                print(parse_json[0]['meanings'][i]['definitions'][0]['example'])
                example = parse_json[0]['meanings'][i]['definitions'][0]['example']
            except:
                example="無"
            info = f"📚定義: {definition}\n\n🖋️範例句子: {example}"
            button = QuickReplyButton(
                action=PostbackAction(label=partOfSpeech, data = info, text=partOfSpeech)
            )
            items.append(button)

        button = QuickReplyButton(
            action=PostbackAction(label="發音",data="發音", text="發音")
        )
        items.append(button)

        button = QuickReplyButton(
            action=PostbackAction(label="上一步",data="上一步", text="上一步")
        )
        items.append(button)
        message = TextSendMessage(
            text='選擇你想知道的詞性或其他！',
            quick_reply=QuickReply(
                items=items
            )
        )
        line_bot_api.reply_message(reply_token, message)
        return 1
    except:
        print("fail to search the word")
        line_bot_api.reply_message(reply_token,TextSendMessage(text="找不到單字QQ"))
        return 0



