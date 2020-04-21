import time
import json
import requests
import threading
import os
from bs4 import BeautifulSoup

_Request_URL = "https://accounts.pixiv.net/login?lang=zh"
_Login_URL = "https://accounts.pixiv.net/api/login?lang=zh"
_BaseImg_URL = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id="

_Save_URL = os.getcwd()

_Base_RequestHeader = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    "Referer": "https://www.pixiv.net/artworks/80442686",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cookie": ""
}

_Ranking_Types = {
    "daily": "daily",
    "original": "original",
    "weekly": "weekly",
    "monthly": "monthly",
    "male": "male",
    "female": "female"
}

def login():
    request = requests.session()

    response = request.get(_Request_URL)
    soup = BeautifulSoup(response.text, "lxml")

    parms = {
        "pixiv_id": "1339544914@qq.com",
        "password": "qq13417716082",
        "return_to": "https://www.pixiv.net/",
        "post_key": soup.select('input[name="post_key"]')[0].attrs["value"],
    }

    print(request.post("https://accounts.pixiv.net/api/login?lang=zh", data = parms, headers = _Base_RequestHeader))

    #print("登录成功" if request.post("https://accounts.pixiv.net/api/login?lang=zh", data = parms, headers = _Base_RequestHeader).status_code == 200 else "登录失败")

    return request

def download_Img(request, img_id:str):
    header = _Base_RequestHeader
    header["Referer"] = _BaseImg_URL + img_id

    txt = request.get(_BaseImg_URL + img_id, headers = header, verify=False).text

    soup = BeautifulSoup(txt, "lxml")
    f = open("htest.html", 'w+', encoding='UTF-8')
    f.write(txt)
    f.close()

    print(soup.find_all("a", attrs = {"class": "sc-pZExJ jCRIIQ"}))

def download_Img2(img_id:str, filename:str, saveurl = _Save_URL, rank = 0):
    img_json = {}

    try:
        img_jsons = json.loads(requests.get("https://www.pixiv.net/ajax/illust/"+img_id, verify=False).text)
    except Exception:
        download_Img2(img_id, filename, saveurl, rank)
        return
    #URL:"+jsons["body"]["urls"]["original"]

    #print("作品信息获取状态-"+ "成功" if ~img_jsons["error"] else "失败")

    tagstr = ""
    for v in img_jsons["body"]["tags"]["tags"]:
        tagstr = tagstr + v["tag"] + "  "

    #saveurl+str(rank)+img_jsons["body"]["illustId"]+".png"

    with open(("%s%s%s" % (saveurl, str(rank) + "_" + filename, ".png")), "wb+") as png:
        try:
            png.write(requests.get(img_jsons["body"]["urls"]["original"], headers = _Base_RequestHeader, verify = False).content)
        except Exception:
            download_Img2(img_id, filename, saveurl, rank)

        png.close()

        print(("#ID:%s  #名字:%s  #标签:%s") % (img_jsons["body"]["illustId"], img_jsons["body"]["title"], tagstr))
        print(("#点赞:%d  #收藏:%d  #浏览:%d") % (img_jsons["body"]["likeCount"], img_jsons["body"]["bookmarkCount"], img_jsons["body"]["viewCount"]))

    print("==================================================")

def download(dic:dict, saveurl):
    for k in dic.keys():
        download_Img2(str(dic[k]["id"]), str(dic[k]["id"]), saveurl, k)


def get_ranking_dict(page:str, mode:str):
    data = {

        "mode": mode,
        "p": page,
        "format": "json"
    }
    
    ranks_jsons = json.loads(requests.get("https://www.pixiv.net/ranking.php", params = data, verify=False).text)
    today_ranks = {}

    for tag in ranks_jsons["contents"]:
        today_ranks[tag["rank"]] = {
                "id": tag["illust_id"], 
                "title": tag["title"]
            }
    
    return today_ranks



def _download_Ranking(page:str, mode:str):
    items = get_ranking_dict(page, mode)
    date_str = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    try:
        #os.path.exists(_Save_URL + "\\img\\" + mode +"\\" + date_str + "\\"):
        os.makedirs(_Save_URL + "\\img\\" + mode +"\\" + date_str + "\\")
    except Exception:
        print("")
        #

    i = 1
    while i <= 5:
        threading.Thread(target=download, args=(cut_dict(items, i * 10 - 10 + 1, i * 10), _Save_URL + "\\img\\" + mode +"\\" + date_str + "\\")).start()
        i+=1
    
def cut_dict(dic:dict, start, end):
    #print(start)
    #print(end)
    dicc = {}
    keys = dic.keys()
    
    while start <= end:
        dicc[start] = dic[list(keys)[start - 1]]

        start +=1

    return dicc



#sess = login()
#download_Img2("80463452")
#print(cut_dict(get_rank("1"), 30, 45))
requests.packages.urllib3.disable_warnings()
_download_Ranking(input("页面:"), input("Mode:"))
#for k,v in cut_dict(get_rank("1"), 30, 45):
#    print(str(k)+"   "+str(v["title"]))



