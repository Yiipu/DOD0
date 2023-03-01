# -*- coding: utf-8 -*-
import json

def load_json(file_path, target=None):
    with open(file_path, 'r', encoding="utf-8-sig") as f:
        data = json.load(f)
    if target is not None:
        return data[target]
    return data

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def write_user(file_path, group, openid, key=None, value=None):
    users_dict = load_json(file_path)
    if key:
        users_dict[group][openid][key]=value
    save_json(file_path, users_dict) 

def delet_user(file_path, group, openid):
    users_dict = load_json(file_path)
    del users_dict[group][openid]
    save_json(file_path, users_dict)