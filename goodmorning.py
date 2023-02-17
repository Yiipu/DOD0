import tokenupdate
import schedule
import datetime
import time
import requests
from wechatpy.client import WeChatClient

users = None
appid = None
appsecret = None
morning_template = None
hefeng_key = None
hefeng_url = None
location_map={
    "jize":"鸡泽县",
    "fengzhen":"丰镇市",
    "jinghai":"静海区",
    "wuhan":"武汉市"
    }

def good_morning():
    for user in users["1"]:
        today=datetime.datetime.now()
        # logging
        print(today.strftime("%Y年%m月%d日"))
        day=datetime.datetime(2022, 9, 21)
        user_location_id=cities[user['location']]
        url_1 = f"{hefeng_index_url}type=3,5&location={user_location_id}&key={hefeng_key}"
        url_2 = f"{hefeng_3d_url}location={user_location_id}&key={hefeng_key}"
        hefeng_response_1 = requests.get(url_1).json()
        hefeng_response_2 = requests.get(url_2).json()
        if hefeng_response_1['code'] != '200':
            return client.message.send_text(user, "天气获取失败")
        url = hefeng_response_2['fxLink']
        daily1 = hefeng_response_1['daily']
        daily2 = hefeng_response_2['daily']
        data={
            "name": {
                "value": user['name'],
                "color": "#FFA07A"
                },
            "time":{
                "value": today.strftime("%Y年%m月%d日"),
                "color": "#777777"
                },
            "number":{
                "value": (today-day).days,
                "color": "#777777"
                },
            "location": {
                "value": location_map[user['location']],
                "color": "#FFA07A"
                },
            "day": {
                "value": daily2[0]['textDay'],
                "color": "#777777"
                },
            "night": {
                "value": daily2[0]['textNight'],
                "color": "#777777"
                },
            "tlv":{
                "value": daily1[0]['category'],
                "color": colors['temperature_color'][daily1[0]['level']]
                },
            "tad":{
                "value": daily1[0]['text'],
                "color": "#777777"
                },
            "plv":{
                "value": daily1[1]['category'],
                "color": colors['purple_color'][daily1[1]['level']]
                },
            "pad":{
                "value": daily1[1]['text'],
                "color": "#777777"
                },
            "remark":{
                "value": "Have a nice day!",
                "color": "#FFA07A"
                }
            }
        re = client.message.send_template(user, morning_template, data, url)
        # logging
        print(re)

if __name__ == "__main__":
    data = tokenupdate.read_constant_keys()
    appid = data['app']['appid']
    appsecret = data['app']['appsecret']
    morning_template = data['template']['morning']
    hefeng_key = data['key']['hefeng']
    hefeng_index_url = data['url']['hefeng_api']['index']
    hefeng_3d_url = data['url']['hefeng_api']['3d']
    cities = data['cities']
    colors = data['colors']

    users = tokenupdate.update_user_dict()
    client = WeChatClient(appid, appsecret)

    # schedule.every(5).seconds.do(good_morning)
    schedule.every().day.at("08:00").do(good_morning)
    while True:
        schedule.run_pending()
        time.sleep(1)
