import requests
import tokenupdate

# Access Token 需要您自行获取
ACCESS_TOKEN = None
appid = None
appsecret = None
wechat_api = None

# 创建自定义菜单
def create_menu(menu_data):
    url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=" + ACCESS_TOKEN
    response = requests.post(url, data=menu_data)
    result = response.json()
    return result

# 上传素材
def upload_material(media_file):
    url = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=" + ACCESS_TOKEN + "&type=thumb"
    files = {"media": (media_file, open(media_file, "rb"))}
    response = requests.post(url, files=files)
    result = response.json()
    return result

# get media by name
def search_media(type, name): 
    # type : 图片（image）、视频（video）、语音 （voice）、图文（news）
    response = requests.get(wechat_api+'material/get_materialcount?access_token=' 
                            + ACCESS_TOKEN).json()
    num = response[type+'_count']
    print(num)
    offset = 0
    while offset<num:
        data = {
            "type":type,
            "offset":offset,
            "count":20
            }
        response = requests.post(wechat_api+'material/batchget_material?access_token=' 
                                 + ACCESS_TOKEN,
                                 json = data).json()
        for media in response['item']:
            if media['name']==name:
                return media
        offset += 20
    return None

if __name__ == "__main__":
    # wechat_token初始化
    data = tokenupdate.read_constant_keys()
    appid = data['app']['appid']
    appsecret = data['app']['appsecret']
    wechat_api = data['url']['wechat_api']
    ACCESS_TOKEN = tokenupdate.read_token()
    # 菜单数据，请按照微信公众号接口的格式填写
    menu_data = """
    {
        "button": [
            {
                "name": "课表",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "今日课表",
                        "key": "kb0"
                    },
                    {
                        "type": "click",
                        "name": "明日课表",
                        "key": "kb1"
                    }
                ]
            },
            {
                "name": "reddit",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "idea",
                        "key": "r/showerthoughts"
                    },
                    {
                        "type": "click",
                        "name": "news",
                        "key": "r/worldnews"
                    }
                ]
            },
            {
                "name": "菜单",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "主页",
                        "url": "http://101.42.37.141:81"
                    },
                    {
                        "type": "click",
                        "name": "帮助",
                        "key": "he"
                    }
                ]
            }
        ]
    }
    """
    menu_data = menu_data.encode('utf-8')

    # 创建自定义菜单
    result = create_menu(menu_data)
    print("创建自定义菜单的结果：", result)

    # 上传素材
    # result = upload_material("songthumb.jpg")
    # print("上传素材的结果：", result)

    #homepage_pic_url=search_media('image','maindodo.png')['url']
    #song_media_id=search_media('image','songthumb.jpg')['media_id']
