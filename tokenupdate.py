# -*- coding: utf-8 -*-
import json

def read_constant_keys(target=None):
    with open('constant_keys.json', 'r', encoding="utf-8-sig") as f:
        data = json.load(f)
    if target is not None:
        return data[target]
    return data

# user
def save_user_dict(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

def load_user_dict(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_user_dict(group, openid, key=None, value=None):
    users_dict = load_user_dict('users_dict.json')
    if key:
        users_dict[group][openid][key]=value
    save_user_dict('users_dict.json', users_dict) 

def delet_user(group, openid):
    users_dict = load_user_dict('users_dict.json')
    del users_dict[group][openid]
    save_user_dict('users_dict.json', users_dict)