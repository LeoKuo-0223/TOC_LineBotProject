from transitions.extensions import GraphMachine
from dictionary import get_dict_result

import re
import configparser
import json
import requests
from linebot import LineBotApi
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReplyButton,PostbackAction,QuickReply
    )


config = configparser.ConfigParser()
config.read('config.ini')
channel_secret = config.get('line-bot', 'channel_secret')
access_token = config.get('line-bot', 'channel_access_token')
line_bot_api = LineBotApi(access_token)


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        self.word = ""

    def is_going_to_dict(self, event):
        text = event.message.text
        result = (text[:2] == "字典")
        line_bot_api.push_message(event.source.user_id,
         TextSendMessage(text="輸入【字典】進入字典功能"))
        return result



    def is_going_to_checkWord(self,event):  #check audio
        text = event.message.text
        return text[:2]=="發音"

    # def is_going_to_tmpFindWord(self,event):    #check partOfSpeech again
    #     text = event.message.text
    #     return text[:2]!="發音"

    def is_going_to_tmpCheckWord(self,event):    #check partOfSpeech again
        # text = event.message.text
        # return text[:2]=="發音"
        return True

    def on_enter_user(self, event):
        line_bot_api.push_message(event.source.user_id,
         TextSendMessage(text="輸入【字典】進入字典功能"))

    def on_enter_dict(self, event):
        print("I'm entering dictionary")
        line_bot_api.push_message(event.source.user_id,
         TextSendMessage(text="[字典模式]\n請輸入單字~\n輸入 離開 即可離開字典模式"))
        
    def on_enter_findWord(self,event):
        if(event.message.text=="離開"):
            self.go_back_user(event)
            return
        query = re.search('[a-z]{1,}', event.message.text.lower())
        if query!=None:
            query = query.group()
            self.word = query
            if get_dict_result(event, query)==0:
                self.go_back(event)
            
            

    def on_enter_checkWord(self, event):    #check specific word deeper
        if(event.message.text=="查其他字"):
            self.go_back(event)
            return
        print("checking")
        items=[]
        try:
            url = 'https://api.dictionaryapi.dev/api/v2/entries/en/'+ self.word
            response_API = requests.get(url)
            data = response_API.text
            parse_json = json.loads(data)
            
            for i in range(len(parse_json[0]['phonetics'])):
                word_info={"audio_url": "", "audio_text": ""}
                try:
                    audio_url = parse_json[0]['phonetics'][i]['audio']
                    # print("audio url: ", audio_url)
                    audio_text = parse_json[0]['phonetics'][i]['text']
                    # print("audio text: ", audio_text)
                    word_info["audio_url"] = audio_url
                    word_info["audio_text"] = audio_text
                   
                except:
                    print("no audio")
                    continue
                word_info_str = json.dumps(word_info) #dict to str
                button = QuickReplyButton(
                    action=PostbackAction(label=audio_text, data = word_info_str, text = "發音: "+audio_text)
                )
                items.append(button)

            button = QuickReplyButton(
                    action=PostbackAction(label="上一步", data = "上一步", text = "上一步")
            )
            items.append(button)

            message = TextSendMessage(
                text='選擇你想聆聽的發音！',
                quick_reply=QuickReply(
                    items=items
                )
            )
            if len(items)>=2:
                line_bot_api.push_message(event.source.user_id, message)
            else:
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text="沒有更多資料了QQ\n回到單字查詢"))
                self.go_back(event)

        except:
            print("fail to search the word")
            line_bot_api.push_message(event.source.user_id,TextSendMessage(text="沒有更多資料了\n回到單字查詢"))
            self.go_back(event)



  
    def on_enter_tmpFindWord(self,event):
        print("tmpFindWord")
        print("original text send:", event.message.text)
        text = event.message.text
        if text in ["adjective", "interjection", "verb", "noun", "adverb"]:   #if user is search for another partOfSpeech
            event.message.text = self.word 
        elif text in ["上一步"]:
            self.go_back(event)
            return
        print("after text send:", event.message.text)
        self.go_back_findWord(event)

    def on_enter_tmpCheckWord(self,event):
        print("tmpCheckWord")
        print("original text send:", event.message.text)
        text = event.message.text
        if text[:2]=="發音":   #if user is search for another partOfSpeech
            event.message.text = self.word
            print("after text send:", event.message.text)
            self.go_back_checkWord(event)
        elif text in ["上一步"]:
            event.message.text = self.word
            self.go_back_findWord(event)
        else:   #user enter another word directly
            print("after text send:", event.message.text)
            self.go_back_findWord(event)

