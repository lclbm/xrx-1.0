import os
import random


from nonebot.exceptions import CQHttpError
from nonebot import MessageSegment


from hoshino import R, Service, priv


sv = Service('mawo', enable_on_default=True, visible=False)
xcw_folder = R.get('record/mawo/').path
lbw_folder = R.get('record/55k/').path
ai_folder = R.get('record/ai/').path
dsm_folder = R.get('record/dsm/').path
shabi_folder= R.get('record/shabi/').path
chongju_folder = R.get('record/chongju/').path


def get_xcw():
    files = os.listdir(xcw_folder)
    filename = random.choice(files)
    rec = R.get('record/mawo/', filename)
    return rec

def get_lbw():
    files = os.listdir(lbw_folder)
    filename = random.choice(files)
    rec = R.get('record/55k/', filename)
    return rec

def get_ai():
    files = os.listdir(ai_folder)
    filename = random.choice(files)
    rec = R.get('record/ai/', filename)
    return rec

def get_dsm():
    files = os.listdir(dsm_folder)
    filename = random.choice(files)
    rec = R.get('record/dsm/', filename)
    return rec

def get_shabi():
    files = os.listdir(shabi_folder)
    filename = random.choice(files)
    rec = R.get('record/shabi/', filename)
    return rec

def get_chongju():
    files = os.listdir(chongju_folder)
    filename = random.choice(files)
    rec = R.get('record/chongju/', filename)
    return rec



@sv.on_prefix(['骂','笨蛋','老婆'], only_to_me=True)
async def xcw(bot, ev) -> MessageSegment:
    # conditions all ok, send a xcw.
    file = get_xcw()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")

@sv.on_prefix(['lbw','55','卢本伟'], only_to_me=True)
async def lbw(bot, ev) -> MessageSegment:
    # conditions all ok, send a xcw.
    file = get_lbw()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")


@sv.on_prefix(['爱','么么'], only_to_me=True)
async def ai(bot, ev) -> MessageSegment:
    # conditions all ok, send a xcw.
    file = get_ai()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")

@sv.on_prefix(['大司马','芜湖','dsm','男同','男酮'], only_to_me=True)
async def dsm(bot, ev) -> MessageSegment:
    # conditions all ok, send a xcw.
    file = get_dsm()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")


@sv.on_prefix(['傻逼'], only_to_me=True)
async def shabi(bot, ev) -> MessageSegment:
    # conditions all ok, send a xcw.
    file = get_shabi()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")



@sv.on_prefix(['尸飕','虫狙','冥冥低语'], only_to_me=True)
async def chongju(bot, ev) -> MessageSegment:
    # conditions all ok, send a xcw.
    file = get_chongju()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")