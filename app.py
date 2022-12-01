from __future__ import unicode_literals
import os
from flask import Flask, jsonify, request, abort, send_file
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage,PostbackEvent, AudioSendMessage
from machine import create_machine
from utils import send_text_message
import configparser
import json
import requests
import random
from jsonTool import is_json
app = Flask(__name__)
# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
parser = WebhookParser(config.get('line-bot', 'channel_secret'))
# Unique FSM for each user
machines = {}

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        # print(body, signature)
        events =parser.parse(body, signature)
        
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)


    for event in events:
        reply_token = event.reply_token
        user_id = event.source.user_id
        text = event.postback.data if event.type == 'postback' else event.message.text
        # if text == "fsm":
        #     if event.source.user_id not in machines:
        #         machines[user_id] = create_machine()
        #     machines[user_id].get_graph().draw("fsm.png", prog="dot", format="png")
        # line_bot_api.reply_message(reply_token,TextSendMessage(text="test"))
        if event.type == 'postback':
            if is_json(text):
                word_info = json.loads(text)
                audio_url = word_info["audio_url"]
                audio_text = word_info["audio_text"]
                print("postback audio_url: ", audio_url)
                # print("postback audio_text: ", audio_text)
                # line_bot_api.push_message(event.source.user_id,TextSendMessage(text=audio_text))
                if len(audio_url)==0:
                    line_bot_api.reply_message(reply_token,TextSendMessage(text="沒有提供此音檔QQ"))
                else:
                    try:
                        audio_message = AudioSendMessage(
                            original_content_url=audio_url,
                            duration=3000
                        )
                        line_bot_api.reply_message(reply_token, audio_message)
                    except:
                        line_bot_api.reply_message(reply_token,TextSendMessage(text="音檔發生問題QQ"))
            else:
                if text not in ["上一步", "離開", "發音"]:
                    line_bot_api.reply_message(reply_token,TextSendMessage(text=text))
                
            continue
        #create new fsm for new user
        if event.source.user_id not in machines:
            machines[user_id] = create_machine()

        print(f"original FSM STATE: {machines[user_id].state}")
        machines[user_id].advance(event)
        print("advance")
        print(f"New FSM STATE: {machines[user_id].state}")

    return 'OK'


if __name__ == "__main__":
    app.run()
