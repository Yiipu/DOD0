# -*- coding: utf-8 -*-
import json
import time
import os
import requests
from wechatpy.client import WeChatClient

def read_constant_keys():
    with open('constant_keys.json', 'r', encoding="utf-8-sig") as f:
        data = json.load(f)
    return data

# set api key & token
data = read_constant_keys()
appid = data['app']['appid']
appsecret = data['app']['appsecret']
wechat_api = data['url']['wechat_api']
client = WeChatClient(appid, appsecret)

# 去除字节序标记
def clean_bom(file):
    BOM = b'\xef\xbb\xbf'
    existBOM = file.read(3) == BOM
    if existBOM:
        file.seek(0)
        file.seek(3)
    return file

# 初始化课表
def init_schedule():
    file_path='schedule.txt'
    schedule = {}
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    with open(file_path, 'rb') as file:
        file = clean_bom(file)
        data = file.read().decode("utf-8")
        lines = data.strip().split("\n")
        for i, line in enumerate(lines):
            day = days[i // 4]
            course, room = line.strip().split()
            if day not in schedule:
                schedule[day] = []
            schedule[day].append((course, room))
    return schedule

# 初始化菜单
def init_menu():
    file_path='menu.txt'
    menu = {} 
    with open(file_path,'rb') as file:
        file = clean_bom(file)
        data = file.read().decode("utf-8")
        lines = data.strip().split("\n")
        for line in lines:
            In,Out = line.strip().split()
            menu[In] = Out
    return menu

# update wecaht access_token
def update_token():
    root = 'token?grant_type=client_credential&appid='+ appid+'&secret='+appsecret
    url = wechat_api + root
    response = requests.get(url).json()
    creat_time = int(time.time())
    response['creat_time'] = creat_time
    with open('WechatToken.json', 'w') as f:
        json.dump(response, f)

# read wechat access_token
def read_token():
    if not os.path.exists('WechatToken.json'):
        update_token()
    with open('WechatToken.json', 'r') as f:
        data = json.load(f)
    diff = int(time.time()) - data['creat_time']
    if diff > data['expires_in']/2:
        update_token()
        return read_token()
    return data['access_token']

# user
def save_dict_to_json_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

def load_dict_from_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_user_dict(openid, location = None, prompt = None):
    users_dict = load_dict_from_json_file('users_dict.json')
    if location:
        users_dict['1'][openid]['location']=location
    if prompt:
        users_dict['1'][openid]['prompt']=prompt
    save_dict_to_json_file('users_dict.json', users_dict)
