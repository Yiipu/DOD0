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
table_template = None
hefeng_key = None
hefeng_url = None
location_map={
    "jize":"鸡泽县",
    "fengzhen":"丰镇市",
    "jinghai":"静海区",
    "hongshan":"洪山区"
    }
day_map = {
    'Monday':'周一',
    'Tuesday':'周二', 
    'Wednesday':'周三', 
    'Thursday':'周四', 
    'Friday':'周五'
    }


def good_morning():
    today=datetime.datetime.now()
    day=datetime.datetime(2022, 9, 21)
    # logging
    print(today.strftime("%Y年%m月%d日"))
    for user_id, user_info in users['1'].items():
        user_location_id=cities[user_info['location']]
        url_1 = f"{hefeng_index_url}type=3,5&location={user_location_id}&key={hefeng_key}"
        url_2 = f"{hefeng_3d_url}location={user_location_id}&key={hefeng_key}"
        hefeng_response_1 = requests.get(url_1).json()
        hefeng_response_2 = requests.get(url_2).json()
        if hefeng_response_1['code'] != '200':
            return client.message.send_text(user_id, "天气获取失败")
        url = hefeng_response_2['fxLink']
        daily1 = hefeng_response_1['daily']
        daily2 = hefeng_response_2['daily']
        data={
            "name": {
                "value": user_info['name'],
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
                "value": location_map[user_info['location']],
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
        re = client.message.send_template(user_id, morning_template, data, url)
        # logging
        print(re)
        
def daily_classtable():
    today=datetime.datetime.now()
    print(today.strftime("%Y年%m月%d日"))
    today = today.strftime("%A")
    if today not in table:
        print("weekend")
        return
    for user_id, user_info in users['0'].items(): 
        data = {
            "day": {
                "value": day_map[today],
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
        re = client.message.send_template(user_id, table_template, data)
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
    table = tokenupdate.init_schedule()

    users = tokenupdate.load_dict_from_json_file('users_dict.json')
    client = WeChatClient(appid, appsecret)

    schedule.every(5).seconds.do(daily_classtable)
    schedule.every().day.at("07:00").do(good_morning)
    while True:
        schedule.run_pending()
        time.sleep(1)
