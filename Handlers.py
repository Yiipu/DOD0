# -*- coding: utf-8 -*-
from wechatpy.client import WeChatClient
from tokenupdate import (read_constant_keys, 
                         load_user_dict, 
                         write_user_dict, 
                         delet_user,
                         read_token,
                         init_schedule)
import openai
import requests
import feedparser
import datetime

app = read_constant_keys('app')
client = WeChatClient(app['appid'], app['appsecret'])

def send_typing(msg):
    data={
        "touser" : msg.source,
        "command" : "Typing"
        }
    wechat_api = read_constant_keys('url')['wechat_api']
    ACCESS_TOKEN =  read_token()
    return requests.post(wechat_api 
                             + "message/custom/typing?access_token="
                             + ACCESS_TOKEN, json = data).json()

def SubReddit(msg,Sub=None):
    if Sub:
        sub = Sub
    else:
        sub = msg.content[5:]
    feed = None
    reddit=read_constant_keys('url')['reddit']
    if sub:
        feed = '来自'+ sub + '的订阅\n<····\t····>\n'
        rss = feedparser.parse(reddit+sub+'.rss')
        count = 0
        for post in rss.entries:
            count+=1
            feed += post.title + '\n\n'
            if count == 5:
                break
    else :
        feed = 'feed 订阅源\n如：\nfeed wordnews\nfeed showerthoughts\n更多订阅源请参考\n' 
        feed += '<a href="https://zhuanlan.zhihu.com/p/556225966">最新 Reddit 使用指南</a>\n'
        feed += '<a href="https://www.zhihu.com/question/22391673/answer/176643379">小众但好玩的subreddits版块</a>\n'
    return client.message.send_text(msg.source, feed)

# 注册消息处理器
handlers = {}

def register_handler(msg_type):
    def decorator(func):
        handlers[msg_type] = func
        return func
    return decorator

@register_handler('text')
def handle_text(msg):

    text_handlers = {}

    def register_text_handler(prefix):
        def decorator_1(func):
            text_handlers[prefix] = func
            return func
        return decorator_1

    @register_text_handler('feed')
    def subreddit_customized(msg):
        return SubReddit(msg)

    @register_text_handler('make')
    def DALLE2(msg):
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

    @register_text_handler('play')
    def Netease(msg):
        api_url = read_constant_keys('url')['netease']
        song_name = msg.content[5:]
        song_media_id = read_constant_keys('Media_ID')['song_thumb']
        if song_name:
            song_info=requests.get(api_url + 'search?keywords=' 
                                  + song_name 
                                  + '&limit=1').json()['result']['songs'][0]
            ID=song_info['id']
            song_url = requests.get(api_url + 'song/url/v1?id=' 
                                    + str(ID) 
                                    + '&level=exhigh').json()['data'][0]['url']
            return client.message.send_music(msg.source,song_url,song_url,
                                      song_media_id,title=song_info['name'],
                                      description=song_info['artists'][0]['name'])
        else:
            return client.message.send_text(msg.source, "没有找到歌曲")

    def GPT(msg):
        openid=msg.source
        users = load_user_dict('users_dict.json')
        preview=users['1'][openid]['prompt']
        response = openai.Completion.create(
           model="text-davinci-003",
           prompt=(f"{preview}\n{msg.content}"),
           max_tokens=600,
           temperature=0.9,
        )
        reply_content = response["choices"][0]["text"]
        new_preview=preview+msg.content+reply_content
        write_user_dict(msg.source,prompt=new_preview)
        return client.message.send_text(openid, reply_content)

    send_typing(msg)
    text_handler = text_handlers.get(msg.content[:4], GPT)
    return text_handler(msg)


@register_handler('image')
def handle_image(msg):
    return ''

@register_handler('voice')
def handle_voice(msg):
    return ''

@register_handler('video')
def handle_video(msg):
    return ''

@register_handler('location')
def handle_location(msg):
    return ''

@register_handler('link')
def handle_link(msg):
    return ''

@register_handler('event')
def handle_event(msg):

    event_handlers = {}

    def register_event_handler(event):
        def decorator_2(func):
            event_handlers[event] = func
            return func
        return decorator_2

    @register_event_handler('subscribe')
    def handle_subscribe(msg):
        openid=msg.source
        users = load_user_dict('users_dict.json')
        if openid not in users['1']:
            write_user_dict(openid)
        print(openid + '关注')
        return client.message.send_text(openid, '欢迎来到渡渡鸟出版')

    @register_event_handler('unsubscribe')
    def handle_unsubscribe(msg):
        openid=msg.source
        users = load_user_dict('users_dict.json')
        if openid in users['1']:
            delet_user(openid)
        print (openid + '取消关注')
        return

    @register_event_handler('click')
    def handle_click(msg):

        click_handlers={}

        def register_click_handler(key):
            def decorator_3(func):
                click_handlers[key] = func
                return func
            return decorator_3

        @register_click_handler('kb')
        def Classtable(msg, plus=0):
            table = init_schedule()
            table_template = read_constant_keys('template')['table']
            today = datetime.datetime.now() 
            today = today + datetime.timedelta(days=plus)
            today = today.strftime("%A")
            if today not in table:
                print("weekend")
                return
            data = {
                "day": {
                    "value": today,
                    "color": "#FFA07A"
                }
            }
            for i in range(4):
                data.update({
                    f"class{i+1}": {
                        "value": table[today][i][0],
                        "color": "#777777"
                    },
                    f"room{i+1}": {
                        "value": table[today][i][1],
                        "color": "#777777"
                    }
                })
            return client.message.send_template(msg.source, table_template, data)

        @register_click_handler('r/')
        def subreddit_defult(msg, suffix):
            return SubReddit(msg, suffix)
            
        @register_click_handler('he')
        def Help(msg, _):
            help_template = read_constant_keys('template')['help']
            data={}
            menu=read_constant_keys('menu')
            for i in range(len(menu['inputs'])):
                data.update({
                    f"input{i+1}": {
                        "value": menu['inputs'][i],
                        "color": "#777777"
                    },
                    f"output{i+1}":{
                        "value": menu['outputs'][i],
                        "color": "#777777"
                    }
                })
            return client.message.send_template(msg.source, help_template, data)

        send_typing(msg)
        click_handler = click_handlers.get(msg.key[:2])
        return click_handler(msg, msg.key[2:])

    def handle_unsupported_event(msg):
        return ''

    event_handler = event_handlers.get(msg.event, handle_unsupported_event)
    return event_handler(msg)

def handle_unsupported(msg):
    return ''