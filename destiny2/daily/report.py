import datetime
import json
import aiohttp
import os
from hoshino import Service, R


link = 'http://www.tianque.top/d2api/today/'
png_folder = os.path.join(os.getcwd(),'res','destiny2','img')

def get_filename():
    time = datetime.datetime.now()
    year = time.year
    month = time.month
    day = time.day
    hour = time.hour
    if hour < 1:
        day = day - 1
    file_name = f'{year:4d}-{month:02d}-{day:02d}.png'
    return file_name

def need_to_update():
    time = datetime.datetime.now()
    year = time.year
    month = time.month
    day = time.day
    hour = time.hour
    if hour < 1:
        day = day - 1
    file_name = f'{year:4d}-{month:02d}-{day:02d}.png' 
    img_file = os.path.join(png_folder,file_name)
    if not os.path.exists(img_file):
        return True
    else:
        return False




headers = {
    'Host': 'cdn.max-c.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.54',
    'Connection': 'keep-alive',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br'
}


async def get_downloadinfo(link='http://www.tianque.top/d2api/today/'):
    response = {}
    async with aiohttp.request("GET", link) as r:
        response = await r.text(encoding="utf-8")
        response = json.loads(response)
    return response


async def get_img(img_link):
    async with aiohttp.ClientSession() as session:
        response = await session.get(img_link)
        content = await response.read()
    return content


async def update(link='http://www.tianque.top/d2api/today/'):
    response = await get_downloadinfo()
    file_name = response['img_name']
    img_file = os.path.join(png_folder,file_name)
    if not os.path.exists(img_file):
        img_link = response['img_url']
        content = await get_img(img_link)  # 获取图片的进制文件
        with open(img_file, 'wb') as f:
            f.write(content)


async def getdailyreport():
    file_name = get_filename()
    img_file = os.path.join(png_folder,file_name)
    if need_to_update():
        await update()
        if not os.path.exists(img_file):
            raise Exception('日报获取失败，日报服务器的日报url已过期')
        return file_name
    else:
        return file_name