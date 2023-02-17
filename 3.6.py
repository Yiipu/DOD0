# -*- coding: utf-8 -*-
from urllib import response
from flask import Flask, request, render_template
from wechatpy import parse_message, create_reply
from wechatpy.replies import MusicReply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.replies import EmptyReply
from wechatpy.events import SubscribeEvent
from wechatpy.client import WeChatClient
import tokenupdate
import threading
import feedparser
import openai
import requests
import logging
import datetime
import io

# set api key & token
openai.api_key=None
WECHAT_VERIFY_TOKEN = None
wechat_api = None
reddit = None
appid = None
appsecret = None
client=None
ACCESS_TOKEN=None

# debug
dbug=0
file = io.open('wechat.log', 'a', encoding='utf-8')
logging.basicConfig(level=logging.DEBUG,
                    handlers=[logging.StreamHandler(file)],
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )

# values
song_media_id = 'BxiB6DV4wu1xwKBZ9FhLrUS28eoAgbg8ITXewFJqoot6p2FjoxF1axpDIuRnG_vm'
homepage_pic_url=None
menu=None
schedule=None

## start of handlers

def send_menu(msg,plus=None):
    help_content='操作指令如下\n<-输入->\t\t\t<-输出->\n'
    for (In,Out) in menu.items():
        help_content += In+'\t\t\t'+Out+'\n'
    return create_reply(help_content, msg)

def send_table(msg,plus=0):
    today = datetime.datetime.now()
    plus = int(plus)
    if plus==0:
        table='今日'
    elif plus==1:
        table='明日'
    future_date = today + datetime.timedelta(days=plus)
    today = future_date.strftime("%A")
    table += "("+today+")"
    if today in schedule:
        courses = schedule[today]
        table += '课表:\n'
        for(course,room) in courses:
            table += course + '\t\t' + room + '\n'
        reply = create_reply(table, msg)
    else:
        reply = create_reply('今天没有课', msg)
    return reply

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

def GPT3(msg):
    openid=msg.source
    preview=users['1'][openid]['prompt']
    response = openai.Completion.create(
       model="text-davinci-003",
       prompt=(f"{preview}\n{msg.content}"),
       max_tokens=128,
       temperature=0.3,
    )
    reply_content = response["choices"][0]["text"]
    new_preview=preview+msg.content+reply_content
    tokenupdate.write_user_dict(msg.source,prompt=new_preview)
    return client.message.send_text(openid, reply_content)

def new_chat(msg,plus=None):
    tokenupdate.write_user_dict(msg.source,prompt=' ')
    return create_reply('GPT记忆清空！', msg)

def send_song(msg):
    api_url = "https://netease-cloud-music-api-olive-five.vercel.app/"
    song_name = msg.content[5:]
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
    
def send_home(msg):
    guide=[
        {
            'title': '漫游指南',
            'description': '欢迎造访超级渡渡鸟出版公司，发送 help 获取操作说明',
            'image': homepage_pic_url,
            'url': 'http://pathpanic.gitee.io/dod0379'
        }
    ]
    return create_reply(guide, msg)

def send_rss(msg,Sub=None):
    if Sub:
        sub = Sub
    else:
        sub = msg.content[5:]
    feed = None
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
    client.message.send_text(msg.source, feed)
    return

 ## end of handlers

click_handler_map_1={
    "he" : send_menu,
    "kb" : send_table,
    "nc" : new_chat
    }

click_handler_map_2={
    "r/" : send_rss
    }

text_handler_map_2={
    "make" : dalle2,
    "play" : send_song,
    "feed" : send_rss
    }

# 输入状态
def send_typing(msg):
    data={
        "touser" : msg.source,
        "command" : "Typing"
        }
    ACCESS_TOKEN =  tokenupdate.read_token()
    response = requests.post(wechat_api 
                             + "message/custom/typing?access_token="
                             + ACCESS_TOKEN, json = data).json()
    return ""

app_wechat = Flask(__name__)
app_page = Flask(__name__, template_folder='DOD0397')

@app_page.route("/dodo")
def dodo():
    return render_template("index.html")

@app_wechat.route("/wechat", methods=["GET", "POST"])
def wechat():
    # 服务器认证
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    echo_str = request.args.get("echostr", "")
    try:
        check_signature(WECHAT_VERIFY_TOKEN, signature, 
                        timestamp, nonce)
    except InvalidSignatureException:
        return "invalid signature"

    if request.method == "GET":
        return echo_str

    if request.method == "POST":
        msg = parse_message(request.data)
        if msg.type == "event":
            if msg.event == "subscribe":
                reply = send_home(msg)
            elif msg.event == "click":
                handler = click_handler_map_2.get(msg.key[:2])
                if handler:
                    t=threading.Thread(target=handler, args=(msg,msg.key[2:]))
                    t.start()
                    return send_typing(msg)
                else:
                    handler = click_handler_map_1.get(msg.key[:2])
                    if handler:
                        reply = handler(msg,msg.key[2:])
            else:
                return ""
            
        elif msg.type == "text":
            prefix = msg.content[:4]
            handler=text_handler_map_2.get(prefix)
            if handler:
                t=threading.Thread(target=handler, args=(msg,))
                t.start()
                return send_typing(msg)
            else:
                t=threading.Thread(target=GPT3, args=(msg,))
                t.start()
                return send_typing(msg)
        else:
            return ""
    return reply.render()

if __name__ == "__main__":
    # 词典初始化
    menu = tokenupdate.init_menu()
    schedule = tokenupdate.init_schedule()
    users = tokenupdate.load_dict_from_json_file('users_dict.json')
    # constant keys初始化
    data = tokenupdate.read_constant_keys()
    openai.api_key= data['key']['openai']
    WECHAT_VERIFY_TOKEN = data['key']['WECHAT_VERIFY_TOKEN']
    appid = data['app']['appid']
    appsecret = data['app']['appsecret']
    reddit = data['url']['reddit']
    wechat_api = data['url']['wechat_api']
    # 客服初始化
    client = WeChatClient(appid, appsecret)
    # 启动app
    app_wechat.run(host='0.0.0.0',port=80)
    app_page.run(host='0.0.0.0',port=81)
