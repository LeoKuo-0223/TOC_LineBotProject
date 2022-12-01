from transitions.extensions import GraphMachine
from dictionary import get_dict_result
from jisho import get_jisho_result
import re
import configparser
import json
import requests
from linebot import LineBotApi
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReplyButton,PostbackAction,QuickReply,ImageSendMessage,
    TemplateSendMessage, MessageTemplateAction, CarouselTemplate, CarouselColumn,
    URIAction,
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
        items=[]
        self.columns=[]
        self.jishobutton = QuickReplyButton(
                    action=PostbackAction(label="英日字典", data = "英日字典", text = "英日字典")
        )
        items.append(self.jishobutton)
        self.engbutton = QuickReplyButton(
            action=PostbackAction(label="英英字典",data="英英字典", text = "英英字典")
        )
        items.append(self.engbutton)
        self.srcbutton = QuickReplyButton(
            action=PostbackAction(label="查看機器人介紹",data="機器人的資料來源", text = "查看機器人資料")
        )
        items.append(self.srcbutton)
        self.message = TextSendMessage(
            text="""嗨你好~\n
我是機器人Leo\n
我可以讓您方便快速的查詢英日語名詞解釋以及發音！\n
可以透過快速回覆按鈕省下打字的時間喔！\n
輸入\n【英英字典】\n【英日字典】\n進入字典模式！""",
            quick_reply=QuickReply(
                items=items
            )
        )

        self.leavebutton = QuickReplyButton(
            action=PostbackAction(label="離開", data = "離開", text="離開")
        )
        column=CarouselColumn(
            thumbnail_image_url="https://i.imgur.com/TmTceYh.jpg",
            title='自我介紹',
            text="""我是機器人Leo
我可以幫你找出英日語單字的重點！
右邊是我的字典資料來源~\n
趕快進入字典模式跟我互動吧！""",
            actions=[
                PostbackAction(label="回到選擇字典",data="離開", text = "離開")
            ]
        )
        self.columns.append(column)
        column=CarouselColumn(
            thumbnail_image_url="https://i.imgur.com/H49S1Zx.png",
            title='Jisho',
            text="提供強大英日翻譯的字典!!",
            actions=[
                URIAction(
                    label='馬上查看Jisho官方網站',
                    uri='https://jisho.org/'
                )
            ]
        )
        self.columns.append(column)
        column = CarouselColumn(
            thumbnail_image_url="https://i.imgur.com/ypH3J7P.png",
            title='英英字典api',
            text="提供強大、免費英英翻譯的字典!!\n幫原開發者買杯咖啡吧!",
            actions=[
                URIAction(
                    label='查看開發者Github',
                    uri='https://github.com/meetDeveloper/freeDictionaryAPI'
                )
            ]
        )
        self.columns.append(column)
        column = CarouselColumn(
            thumbnail_image_url="https://i.imgur.com/TmTceYh.jpg",
            title='離開介紹',
            text="點擊【離開】回到選擇字典狀態",
            actions=[
                PostbackAction(label="離開",data="離開", text = "離開")
            ]
        )
        self.columns.append(column)

    def is_going_to_showFsm(self, event):
        text = event.message.text
        if text!=None:
            if text in "fsm": return True
            else :return False
        return False

    def is_going_to_greet(self, event):
        text = event.message.text
        if text!=None:
            if text in ["你好", "hello", "Hello", "Hi", "嗨", "查看機器人資料"]:
                return True
            return False
        return False

    def is_going_to_intro(self, event):
        text = event.message.text
        return text=="查看機器人資料"

    def is_going_to_dict(self, event):
        text = event.message.text
        reply_token = event.reply_token
        if text!=None:
            if text in ["你好", "hello", "Hello", "Hi", "嗨", "查看機器人資料", "英日字典", "fsm"]:
                return False
            if len(text)<4: 
                line_bot_api.reply_message(reply_token,self.message)
                return False
            elif  ((text[:4] != "英英字典") and (text[:4] != "英日字典")):
                line_bot_api.reply_message(reply_token,self.message)
                return False
            elif (text[:4] == "英英字典"): return True
        line_bot_api.reply_message(reply_token,self.message)
        return False


    def is_findTanngo_again(self, event):
        text = event.message.text
        reply_token = event.reply_token
        if text!=None:
            if len(text)<=1: return False
            elif (text[:2]!="離開" and  text[:2]!="發音"): return True
            elif text[:2]=="發音": 
                items=[]
                items.append(self.leavebutton)
                message = TextSendMessage(
                    text='【英日模式】\n請輸入單字~\n輸入 離開 即可離開此模式',
                    quick_reply=QuickReply(
                        items=items
                    )
                )
                line_bot_api.reply_message(reply_token,message)
                return False
            return 
        return False

    def is_findTanngo_to_User(self, event):
        text = event.message.text
        if text!=None:
            if len(text)<=1: return False
            result = (text[:2]=="離開" or text[:2]!="發音")
            return result
        return False

    def is_going_to_jisho(self, event):
        text = event.message.text
        if text!=None:
            if len(text)<4: return False
            return (text[:4] == "英日字典")
        return False

    def is_going_to_checkWord(self,event):  #check audio
        text = event.message.text
        if text!=None:
            if len(text)<=1:return False
            return text[:2]=="發音"
        return False


    def on_enter_user(self, event):
        reply_token = event.reply_token
        try:
            line_bot_api.reply_message(reply_token,self.message)
        except:
            pass
        

    def on_enter_greet(self, event):
        reply_token = event.reply_token
        rcbutton = QuickReplyButton(
            action=PostbackAction(label="查看更多",data="機器人的資料來源", text = "查看機器人資料")
        )
        msg = TextSendMessage(
        text="""嗨你好~\n
我是機器人Leo\n
我可以讓您方便快速的查詢英日語名詞解釋以及發音！\n
""",
            quick_reply=QuickReply(
                items=[rcbutton]
            )
        )

        line_bot_api.reply_message(reply_token,msg)


    def on_enter_intro(self,event):
        reply_token = event.reply_token
        message = TemplateSendMessage(
            alt_text='點擊按鈕查看字典來源官方網站吧!',
            template=CarouselTemplate(
                columns=self.columns
            )
        )
        line_bot_api.reply_message(reply_token,message)
        

    def on_enter_showFsm(self, event):
        reply_token = event.reply_token
        img_url = "https://i.imgur.com/sxIbylt.png"
        try:
            message = ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
            line_bot_api.reply_message(reply_token,message)
        except:
            print("fail to get fsm")
        self.go_back_user(event)

    def on_enter_dict(self, event):
        print("I'm entering dictionary")
        reply_token = event.reply_token
        items=[]
        items.append(self.leavebutton)
        message = TextSendMessage(
            text='【英英模式】\n請輸入英文單字~\n輸入 離開 即可離開此模式',
            quick_reply=QuickReply(
                items=items
            )
        )
        line_bot_api.reply_message(reply_token,message)

    def on_enter_jisho(self, event):
        print("I'm entering jisho")
        reply_token = event.reply_token
        items=[]
        items.append(self.leavebutton)
        message = TextSendMessage(
            text='【英日模式】\n請輸入英文單字~\n輸入 離開 即可離開此模式',
            quick_reply=QuickReply(
                items=items
            )
        )
        line_bot_api.reply_message(reply_token,message)
        
    def on_enter_findWord(self,event):
        reply_token = event.reply_token
        if event.message.text!=None:
            if(event.message.text=="離開"):
                self.go_back_user(event)
                return
            query = re.search('[a-z]{1,}', event.message.text.lower())
            if query!=None:
                query = query.group()
                self.word = query
                if get_dict_result(event, query)==0:
                    self.go_back(event)
            else: 
                # line_bot_api.reply_message(reply_token,TextSendMessage(text="我只看得懂英文喔!"))
                self.go_back(event)
        else: 
            # line_bot_api.reply_message(reply_token,TextSendMessage(text="我只看得懂英文喔!"))
            self.go_back(event)
            
    def on_enter_findTanngo(self,event):
        reply_token = event.reply_token
        if event.message.text!=None:
            if(event.message.text=="離開"):
                self.go_back_user(event)
                return
            query = re.search('[a-z]{1,}', event.message.text.lower())
            if query!=None:
                query = query.group()
                self.word = query
                if get_jisho_result(event, query)==0:
                    self.go_back_jisho(event)
            else: 
                # line_bot_api.reply_message(reply_token,TextSendMessage(text="我只看得懂英文喔!"))
                self.go_back_jisho(event)
        self.go_back_jisho(event)
        
       


    def on_enter_checkWord(self, event):    #check specific word deeper
        reply_token = event.reply_token
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
                line_bot_api.reply_message(reply_token, message)
            else:
                line_bot_api.reply_message(reply_token,TextSendMessage(text="沒有更多資料了QQ\n回到單字查詢"))
                self.go_back(event)

        except:
            print("fail to search the word")
            line_bot_api.reply_message(reply_token,TextSendMessage(text="沒有更多資料了\n回到單字查詢"))
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
        if text!=None:
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
        event.message.text = self.word
        self.go_back_findWord(event)

