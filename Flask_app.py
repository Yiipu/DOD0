
# -*- coding: utf-8 -*-

from flask import Flask, request, session, jsonify, redirect
from wechatpy.client import WeChatClient
from wechatpy.oauth import WeChatOAuth
from flask_wechatpy import Wechat, wechat_required, oauth
from tokenupdate import read_constant_keys, load_user_dict
import threading
import requests
from Handlers import handlers, handle_unsupported


app = Flask(__name__)

data = read_constant_keys()
app.config['WECHAT_TOKEN'] = data['key']['WECHAT_VERIFY_TOKEN']
app.config['WECHAT_APPID'] = data['app']['appid']
app.config['WECHAT_SECRET'] = data['app']['appsecret']
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

client = WeChatClient(app.config['WECHAT_APPID'], app.config['WECHAT_SECRET'])
wechat = Wechat(app)

def send_typing(msg):
    data={
        "touser" : msg.source,
        "command" : "Typing"
        }
    wechat_api = read_constant_keys('url')['wechat_api']
    return requests.post(wechat_api 
                             + "message/custom/typing?access_token="
                             + wechat.access_token, json = data).json()


def get_group(openid):
    users = load_user_dict('users_dict.json')
    group = '1' if openid in users['1'] else '2'
    return group


@app.route('/')
@oauth(scope='snsapi_userinfo')
def index():
    root = read_constant_keys('url')['root']
    openid = session['wechat_user_id']
    return redirect(f'{root}{openid}')


@app.route('/clear')
def clear():
    if 'user_id' in session:
        session.pop('user_id')
        response = {'status': 'ok', 'message': 'User deleted successfully'}
    else:
        response = {'status': 'failed', 'message': 'User not found'}

    return jsonify(response)
 
 
@app.route('/<openid>', methods=['GET', 'POST'])
def display_timetable(openid):
    if request.method == 'GET':
        group = get_group(openid)
        try:
            return read_constant_keys[group][openid]['table']
        except:
            return "No timetable found"
    else:
        return "POST"


@app.route('/wechat', methods=['GET', 'POST'])
@wechat_required
def wechat_handler():
    message = request.wechat_msg
    handler = handlers.get(message.type, handle_unsupported)
    t=threading.Thread(target=handler,args=(message,))
    send_typing(message)
    t.start()
    return ""


@app.route('/access_token')
def access_token():
    return "access token: {}".format(wechat.access_token)

if __name__ == '__main__':
    # 启动app
    app.run(host='0.0.0.0',port=80)
