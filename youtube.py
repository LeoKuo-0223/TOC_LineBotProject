import os

from linebot import LineBotApi
from linebot.models import (
    TemplateSendMessage, MessageTemplateAction, CarouselTemplate, CarouselColumn
)

from googleapiclient.discovery import build

access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
line_bot_api = LineBotApi(access_token)


def send_youtube_video(reply_token, query):
    youTubeApiKey = os.getenv("YOUTUBE_API_KEY", None)
    youtube = build('youtube', 'v3', developerKey=youTubeApiKey)
    request = youtube.search().list(part='snippet', q=query, type='video')
    response = request.execute()
    Videos = response['items'][0:3]
    videoIds = [Videos[i]['id']['videoId'] for i in range(3)]
    videoUrls = [f'https://www.youtube.com/watch?v={videoId}' for videoId in videoIds]

    message = TemplateSendMessage(
        alt_text='選歌聽吧！',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url=Videos[0]['snippet']['thumbnails']['high']['url'],
                    title='是這個？',
                    text=Videos[0]['snippet']['title'][:60],
                    actions=[
                        MessageTemplateAction(
                            label='聽這個！',
                            text=videoUrls[0]
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url=Videos[1]['snippet']['thumbnails']['high']['url'],
                    title='這個？',
                    text=Videos[1]['snippet']['title'][:60],
                    actions=[
                        MessageTemplateAction(
                            label='聽這個！',
                            text=videoUrls[1]
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url=Videos[2]['snippet']['thumbnails']['high']['url'],
                    title='還是這個呢？',
                    text=Videos[2]['snippet']['title'][:60],
                    actions=[
                        MessageTemplateAction(
                            label='聽這個！',
                            text=videoUrls[2]
                        )
                    ]
                )
            ]
        )
    )

    line_bot_api.reply_message(reply_token, message)

    return "OK"