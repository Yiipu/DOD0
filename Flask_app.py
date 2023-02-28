
# -*- coding: utf-8 -*-

from flask import Flask, request, session
from flask_wechatpy import Wechat, wechat_required, oauth
import tokenupdate
import threading
from Handlers import handlers, handle_unsupported


app = Flask(__name__)
data = tokenupdate.read_constant_keys()
app.config['WECHAT_TOKEN'] = data['key']['WECHAT_VERIFY_TOKEN']
app.config['WECHAT_APPID'] = data['app']['appid']
app.config['WECHAT_SECRET'] = data['app']['appsecret']
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

wechat = Wechat(app)


@app.route('/')
@oauth(scope='snsapi_userinfo')
def index():
    return "hello"


@app.route('/clear')
def clear():
    if 'wechat_user_id' in session:
        session.pop('wechat_user_id')
    return "ok"


@app.route('/wechat', methods=['GET', 'POST'])
@wechat_required
def wechat_handler():
    message = request.wechat_msg
    handler = handlers.get(message.type, handle_unsupported)
    t=threading.Thread(target=handler(message))
    t.start()
    return ''


@app.route('/access_token')
def access_token():
    return "access token: {}".format(wechat.access_token)

if __name__ == '__main__':
    # 启动app
    app.run(host='0.0.0.0',port=80)
