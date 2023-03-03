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
    return

def write_user(file_path, group, openid, dict=None):
    users_dict = load_json(file_path)
    if openid in users_dict[group]:
        if dict:
            # copy = dict.copy()
            users_dict[group][openid].update(dict)
    else:
        users_dict[group][openid]={"name":"","location":"","messages":[],"table":{}}
    save_json(file_path, users_dict) 
    return

def delet_user(file_path, group, openid):
    users_dict = load_json(file_path)
    del users_dict[group][openid]
    save_json(file_path, users_dict)
    return
    
def move_user(file_path, openid, from_g, to_g):
    delet_user(file_path, from_g, openid)
    write_user(file_path, to_g, openid)
    return