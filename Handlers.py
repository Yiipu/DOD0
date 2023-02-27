from urllib import response
from flask import Flask, request
from wechatpy import parse_message, create_reply
from wechatpy.replies import TextReply
from wechatpy.client import WeChatClient
from tokenupdate import read_constant_keys
import openai

app = read_constant_keys('app')
appid = app['appid']
appsecret = app['appsecret']
client = WeChatClient(appid, appsecret)

# 注册消息处理器
handlers = {}

def register_handler(msg_type):
    def decorator(func):
        handlers[msg_type] = func
        return func
    return decorator

@register_handler('text')
def handle_text(message):

    text_handlers = {}

    def register_text_handler(prefix):
        def decorator_1(func):
            text_handlers[prefix] = func
            return func
        return decorator_1

    @register_text_handler('r/')
    def send_rss(msg,Sub=None):
        feed=''
        return client.message.send_text(msg.source, feed)

    @register_text_handler('play')
    def dalle2(msg):
        prompt = msg.content[5:]
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        articles=[
               {
                    'title': '画好啦',
                    'description': prompt,
                    'image': image_url,
                    'url': image_url
               }
            ]
        return client.message.send_articles(msg.source, articles)

    def handle_defult():
        pass

    text_handler = text_handlers.get(message.content[:4], handle_defult)
    return text_handler(message)


@register_handler('image')
def handle_image(message):
    reply = TextReply(content='Received an image message', message=message)
    return reply

@register_handler('voice')
def handle_voice(message):
    reply = TextReply(content='Received a voice message', message=message)
    return reply

@register_handler('video')
def handle_video(message):
    reply = TextReply(content='Received a video message', message=message)
    return reply

@register_handler('location')
def handle_location(message):
    reply = TextReply(content='Received a location message', message=message)
    return reply

@register_handler('link')
def handle_link(message):
    reply = TextReply(content='Received a link message', message=message)
    return reply

@register_handler('event')
def handle_event(message):
    reply = TextReply(content='Received an event message', message=message)
    return reply