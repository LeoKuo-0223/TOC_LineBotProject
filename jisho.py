import requests
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import (
    TextSendMessage, FlexSendMessage, QuickReply, 
    QuickReplyButton, PostbackAction,TemplateSendMessage,
     MessageTemplateAction, CarouselTemplate, CarouselColumn
)
import configparser
import json

config = configparser.ConfigParser()
config.read('config.ini')
channel_secret = config.get('line-bot', 'channel_secret')
access_token = config.get('line-bot', 'channel_access_token')
line_bot_api = LineBotApi(access_token)

def get_jisho_result(event, query):
    reply_token = event.reply_token
    items=[]
    word_info={"audio_url": "", "audio_text": ""}
    try:
        print(query)
        url = 'https://jisho.org/search/'+ query
        response_API = requests.get(url)
        data = response_API.text
        soup = BeautifulSoup(data,"html.parser")
        hiragana = soup.select("div.concept_light-representation span.furigana")
        katakana = soup.select("div.concept_light-representation span.text")
        try:
            h = hiragana[0].text.split()[0]
            word = "平假名: "+ h + "\n\n漢字: " + katakana[0].text.split()[0]
        except:
            word = "片假名: " + katakana[0].text.split()[0]
        
        
        part = soup.select('div.concept_light.clearfix')
        part = BeautifulSoup(str(part[0]),"html.parser")
        tags = part.select("div.meaning-tags")[0].text
        meaning = part.select("div.meaning-definition.zero-padding")[0].text
        try:
            example = part.select("ul.japanese.japanese_gothic.clearfix")[0].text
            example = example.split("。")
            message = word +"\n\n🪧Tags: "+ tags +"\n\n📚Meaning: \n"+meaning+"\n\n🖋️Example: \n"
            for i in range(len(example)):
                message += example[i]
                message +="\n"
        except:
            message = word +"\n\n🪧Tags: "+ tags +"\n\n📚Meaning: \n"+meaning
        
        try:
            source = soup.findAll('source')[0]['src']
            word_info["audio_url"]="https:"+source
            print(word_info["audio_url"])
            word_info_str = json.dumps(word_info)
            text = "發音: \n"+hiragana[0].text.split()[0]+"\n"+katakana[0].text.split()[0]
            button = QuickReplyButton(
                    action=PostbackAction(label="發音", data = word_info_str, text = text)
            )
            items.append(button)
        except:
            pass
        button = QuickReplyButton(
                action=PostbackAction(label="離開", data = "離開", text = "離開")
        )
        items.append(button)
        msg = TextSendMessage(
                text=message,
                quick_reply=QuickReply(
                    items=items
                )
        )
        line_bot_api.reply_message(reply_token, msg)
        return 1
    except:
        print("fail to find word in jisho")
        line_bot_api.reply_message(reply_token,TextSendMessage(text="找不到單字QQ"))
        return 0



    