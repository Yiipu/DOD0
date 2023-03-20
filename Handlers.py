# -*- coding: utf-8 -*-
from wechatpy.client import WeChatClient
from file_loader import (load_json, 
                         write_user, 
                         delet_user
                         )
import requests
import datetime

config_file = 'constant_keys.json'
wxuser_file = 'users_dict.json'
is_ChatGPT_available = True

app = load_json(config_file, 'app')
client = WeChatClient(app['appid'], app['appsecret'])

def SubReddit(msg,sub=None):
    import feedparser
    feed = None
    reddit=load_json(config_file, 'url')['reddit']
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
        feed = 'feed 订阅源\n如：\nfeed wordnews\nfeed showerthoughts\n'
    return client.message.send_text(msg.source, feed)


def get_group(openid):
    users = load_json(wxuser_file)
    group = None
    for group_id, user_list in users.items():
        if openid in user_list:
            group = group_id
            break
    return group


# 注册消息处理器
handlers = {}

def register_handler(msg_type):
    def decorator(func):
        handlers[msg_type] = func
        return func
    return decorator

@register_handler('text')
def handle_text(msg):

    # 注册文本消息处理器
    text_handlers = {}

    def register_text_handler(prefix):
        def decorator_1(func):
            text_handlers[prefix] = func
            return func
        return decorator_1

    @register_text_handler('feed')
    def subreddit_customized(msg):
        return SubReddit(msg, msg.content[5:])

    @register_text_handler('make')
    def DALLE2(msg):
        import openai
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
        api_url = load_json(config_file, 'url')['netease']
        song_name = msg.content[5:]
        song_media_id = load_json(config_file, 'Media_ID')['song_thumb']
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

    def Davinci(msg):
        import openai
        openid = msg.source
        openai.api_key = load_json(config_file, 'key')['openai']
        users = load_json(wxuser_file)
        group = get_group(openid)
        try:
            preview=users[group][openid]['prompt']
        except:
            write_user(wxuser_file, group, openid,{"prompt":" "})
            preview=" "
        response = openai.Completion.create(
           model="text-davinci-003",
           prompt=(f"{preview}\n{msg.content}"),
           max_tokens=600,
           temperature=0.9,
        )
        reply_content = response["choices"][0]["text"]
        new_preview=preview+msg.content+reply_content
        write_user(wxuser_file, group, msg.source,{"prompt":new_preview})
        return client.message.send_text(openid, reply_content)


    def ChatGPT(msg):
        if is_ChatGPT_available is False:
            return Davinci(msg)
        import openai
        from requests.exceptions import Timeout
        openai.api_retry = False
        openai.api_timeout = 7
        openai.api_key = load_json(config_file, 'key')['openai']
        openid = msg.source
        group = get_group(openid)
        users = load_json(wxuser_file)
        try:
            messages=users[group][openid]['messages']
        except:
            write_user(wxuser_file, group, openid,{'messages':[]})
            messages=[]
        new_usercontent =  {'role':'user','content':msg.content}
        messages.append(new_usercontent.copy())
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
        except:
            is_ChatGPT_available = False
            client.message.send_text(openid, 'ChatGPT请求失败，下面返回text-davinci-003的回答')
            return Davinci(msg)
        reply_content = response['choices'][0]['message']['content']
        new_assis = {'role':'assistant','content':reply_content}
        new_messages = messages + [new_assis.copy()]
        write_user(wxuser_file, group, openid,{"messages":new_messages})
        return client.message.send_text(openid, reply_content)
        
    text_handler = text_handlers.get(msg.content[:4], ChatGPT)
    return text_handler(msg)


@register_handler('event')
def handle_event(msg):

    # 注册事件消息处理器
    event_handlers = {}

    def register_event_handler(event):
        def decorator_2(func):
            event_handlers[event] = func
            return func
        return decorator_2

    @register_event_handler('subscribe')
    def handle_subscribe(msg):
        openid=msg.source
        users = load_json(wxuser_file)
        root = load_json(config_file, 'url')['root']
        if openid not in users['2']:
            write_user(wxuser_file, '2', openid)
        print(openid + '关注')
        return client.message.send_text(openid, f'<a href="{root}:81/">欢迎来到渡渡鸟出版</a>')

    @register_event_handler('unsubscribe')
    def handle_unsubscribe(msg):
        openid=msg.source
        users = load_json(wxuser_file)
        if openid in users['2']:
            delet_user(wxuser_file, '2', openid)
        print(openid + '取消关注')
        return

    @register_event_handler('click')
    def handle_click(msg):

        # 注册点击菜单消息处理器   
        click_handlers={}

        def register_click_handler(key):
            def decorator_3(func):
                click_handlers[key] = func
                return func
            return decorator_3

        @register_click_handler('kb')
        def Classtable(msg, plus=0):
            openid = msg.source
            group = get_group(openid)
            users = load_json(wxuser_file)
            try:
                table = users[group][openid]['table']
            except:
                return client.message.send_text(openid, '您还没有上传课表')
            table_template = load_json(config_file, 'template')['table']
            today = datetime.datetime.now()
            plus = int(plus)
            today = today + datetime.timedelta(days=plus)
            today = today.strftime("%A")
            if today not in table:
                return client.message.send_text(msg.source, '今天是周末')
            data = {
                "day": {
                    "value": today,
                    "color": "#FFA07A"
                }
            }
            for i in range(4):
                data.update({
                    f"class{i+1}": {
                        "value": table[today]['class'][i],
                        "color": "#777777"
                    },
                    f"room{i+1}": {
                        "value": table[today]['room'][i],
                        "color": "#777777"
                    }
                })
            return client.message.send_template(openid, table_template, data)

        @register_click_handler('r/')
        def subreddit_defult(msg, suffix):
            return SubReddit(msg, suffix)
            
        @register_click_handler('he')
        def Help(msg, _):
            help_template = load_json(config_file, 'template')['help']
            data={}
            menu=load_json(config_file, 'menu')
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

        @register_click_handler('nc')
        def new_chat(msg, _):
            openid=msg.source
            group = get_group(openid)
            write_user(wxuser_file, group, openid, {"messages":[]})
            write_user(wxuser_file, group, openid, {"prompt":""})
            is_ChatGPT_available = True
            return client.message.send_text(openid, '新对话')
            
        @register_click_handler('tq')
        def good_morning(msg, _):
            openid, group = msg.source, get_group(openid)
            today, special_day=datetime.datetime.now(), datetime.datetime(2022, 9, 21)
            Config = load_json(config_file)
            morning_template=Config['templates']['morning'][group]
            hefeng_index_url, hefeng_3d_url = Config['url']['hefeng_api']['index'], Config['url']['hefeng_api']['3d']
            hefeng_key = Config['key']['hefeng']
            url_1 = f"{hefeng_index_url}type=3,5&location={location_id}&key={hefeng_key}"
            url_2 = f"{hefeng_3d_url}location={location_id}&key={hefeng_key}"
            hefeng_response_1, hefeng_response_2 = requests.get(url_1).json(), requests.get(url_2).json()
            if hefeng_response_1['code'] != '200':
                return client.message.send_text(openid, "天气获取失败")
            url = hefeng_response_2['fxLink']
            daily1, daily2= hefeng_response_1['daily'], hefeng_response_2['daily']
            data={
                "time":{"value": today.strftime("%Y年%m月%d日"), "color": "#777777"},
                "number":{"value": (today-day).days, "color": "#777777"},
                "location": {"value": location_map[user_info['location']], "color": "#FFA07A"},
                "day": {"value": daily2[0]['textDay'], "color": "#777777"},
                "night": {"value": daily2[0]['textNight'], "color": "#777777"},
                "tlv":{"value": daily1[0]['category'], "color": colors['temperature_color'][daily1[0]['level']]},
                "tad":{"value": daily1[0]['text'], "color": "#777777"},
                "plv":{"value": daily1[1]['category'], "color": colors['purple_color'][daily1[1]['level']]},
                "pad":{"value": daily1[1]['text'], "color": "#777777"},
                "remark":{"value": "Have a nice day!", "color": "#FFA07A"}
                }
            re = client.message.send_template(openid, morning_template, data, url)
            print(re)
        

        click_handler = click_handlers.get(msg.key[:2])
        return click_handler(msg, msg.key[2:])


    def handle_unsupported_event(msg):
        return ''


    event_handler = event_handlers.get(msg.event, handle_unsupported_event)
    return event_handler(msg)


def handle_unsupported(msg):
    return ''