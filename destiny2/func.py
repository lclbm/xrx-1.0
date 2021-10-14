import os
from nonebot import on_command, CommandSession
import aiohttp
import asyncio
import requests
import pydest
from hoshino import Service, R
from hoshino.typing import CQEvent
from nonebot import *
import json
import datetime
import hoshino
from PIL import Image, ImageDraw, ImageFont
import sys
import re
import time
import numpy as np



sys.path.append(os.path.join(os.getcwd(),'hoshino','modules','test'))
from data.tie import gethardlink
from daily.report import getdailyreport
from data.checklist import penguinSouvenirs, egg, 增幅s, bones, cats, 称号, exos, 暗熵碎片s, 证章, 赛季挑战, 前兆, DSC, 巅峰, 宗师, 机灵, 玉兔, 赛季, 线索,征服者,珍珠s
from query import *
from weekly_milestones import weekly_milestones, check_milestions_completion
import sqlite3

one = 2287326985
two = 2933986918
three = 3555747646
four = 2117336792

destiny2DirPath = os.path.join(os.getcwd(), 'res', 'destiny2')

class DBase:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def query(self, hash_id, definition):

        sql = """
              SELECT json FROM {}
              WHERE id = {}
              """
        self.cur.execute(sql.format(definition, hash_id))
        res = self.cur.fetchall()
        if len(res) > 0:
            return json.loads(res[0][0])
        else:
            return None

    def add(self, hash_id, Dict: dict, definition):
        sql = """
              INSERT INTO {}
              VALUES ({},'{}')
              """
        jsonStr = json.dumps(Dict)
        quer = f'''INSERT INTO {definition} VALUES(?, ?)'''
        try:
            self.cur.execute(quer, (hash_id, jsonStr))
        except Exception as e:
            print(e)







HEADERS = {"X-API-Key": '19a8efe4509a4570bee47bd9883f7d93'}
API_KEY = '19a8efe4509a4570bee47bd9883f7d93'
ROOT = 'https://www.bungie.net/Platform'

destiny = pydest.Pydest(API_KEY)

with open("record.json", 'r') as load_f:
    load_dict = json.load(load_f)
    count = load_dict['counts']


def savedata():
    with open("record.json", "w") as f:
        new_dict = {'counts': count}
        json.dump(new_dict, f)


Fail = 0
args = ''
AppendInfo = ''  # '\n❗小日向将继续免费使用至18号，具体收费请回复收费以查询'

sv = hoshino.Service('命运2')


# ⚪生涯查询 [队伍码/用户名]
# 查询玩家生涯数据
# @sv.on_fullmatch(('功能', 'd2', 'D2', '喵内嘎', '喵内', '日向', '小日向', '喵内噶'))
# async def D2Help(bot, ev):
#     global count
#     count += 1
#     await bot.send(ev, HELP_MSG)

# ⚪生涯查询 [队伍码/用户名]
# 查询玩家生涯数据
# @sv.on_fullmatch(('功能', 'd2', 'D2', '喵内嘎', '喵内', '日向', '小日向', '喵内噶'))
# async def D2Help(bot, ev):
#     global count
#     count += 1
#     await bot.send(ev, HELP_MSG)


@sv.on_fullmatch('日报')
async def daily(bot, ev, only_to_me=False):
    filename = await getdailyreport()
    if filename != False:
        png_file = os.path.join(
            os.getcwd(), 'res', 'destiny2', 'img', filename)
        cqcode = f'[CQ:image,file=file:///{png_file}]'
        await bot.send(ev, cqcode)


# @sv.on_fullmatch(('收费'))
# async def D2_say(bot, ev):
#     info = f'''⚪收费标准如下：
# 6元/月 35/半年 60/年
# 群人数≤20价格半价且后续不另收费
# 如果需要购买请加QQ群827529117'''
#     await bot.send(ev, info)


class FailToGet(Exception):
    '''当输出有误时，抛出此异常'''

    # 自定义异常类型的初始化

    def __init__(self, value, msg):
        global Fail
        self.value = value
        self.msg = msg

    # 返回异常类对象的说明信息

    def __str__(self):
        return f" {self.value} 查询失败\n错误原因：{self.msg}"


class Error_Privacy(Exception):
    '''当输出有误时，抛出此异常'''

    # 自定义异常类型的初始化

    def __init__(self, value):
        self.value = value
        global Fail

    # 返回异常类对象的说明信息

    def __str__(self):
        return f" {self.value} 查询失败\n错误原因：玩家命运2数据设置为隐私不可见"


def get_success(result, name):
    print(type(result))
    if result['ErrorCode'] != 1:
        ErrorStatus = result['ErrorStatus']
        Message = result['Message']
        raise Exception(f'{ErrorStatus}，未查询到玩家信息\n{Message}')
    else:
        return True


async def GetMembershipidAndTypeFromSteam64(credential, crType='SteamId'):
    checklist = {3: 'steam', 2: 'psn', 1: 'xbl'}
    url = ROOT + \
        f'/User/GetMembershipFromHardLinkedCredential/{crType}/{credential}'
    response = await destiny.api._get_request(url=url)
    if get_success(response, credential):
        dict = {}
        dict['membershipid'] = response['Response']['membershipId']
        dict['membershiptype_num'] = response['Response']['membershipType']
        dict['membershiptype_char'] = checklist[response['Response']
                                                ['membershipType']]
        return dict
    else:
        raise FailToGet(credential, f'无法找到该玩家信息，请检查是否输入了正确的队伍码/用户名')


async def GetMembershipidAndTypeFromSteamid(name):
    checklist = {3: 'steam', 2: 'psn', 1: 'xbl'}
    response = await destiny.api.search_destiny_player(-1, name)
    length = len(response['Response'])
    if get_success(response, name) == True:
        if length > 2:
            raise FailToGet(name, f'有{length}名玩家重名，请尝试用队伍码查询')
        else:
            if length != 0:
                if length == 1 or (length == 2 and response['Response'][0]['membershipId'] == response['Response'][1][
                        'membershipId']):
                    dict = {}
                    dict['membershipid'] = response['Response'][0]['membershipId']
                    dict['membershiptype_num'] = response['Response'][0]['membershipType']
                    dict['membershiptype_char'] = checklist[response['Response']
                                                            [0]['membershipType']]
                    return dict
                else:
                    raise FailToGet(name, f'有{length}名玩家重名，请尝试用队伍码查询')
            else:
                raise FailToGet(name, f'无法找到该玩家信息，请检查是否输入了正确的队伍码/用户名')


async def GetMembershipidAndMembershiptype(args):
    global count
    count += 1
    if args.isdigit() == True and len(args) == 17:
        # 提供的是steam64位id
        result = await GetMembershipidAndTypeFromSteam64(args)
    else:
        # 提供的是steam用户名
        result = await GetMembershipidAndTypeFromSteamid(args)
    savedata()
    return result


@on_command('pve', aliases=('PVE', 'Pve'), only_to_me=False)
async def pve(session):
    msg = '该功能已被替换，请输入 d2 查看更新菜单'
    await session.send(msg, at_sender=True)


@on_command('调试', aliases=('测试'), only_to_me=False)
async def test(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        result = await GetMembershipidAndMembershiptype(args)
        await session.send(str(result))
    except Exception as e:
        await session.send(f'{e}', at_sender=True)
        return


async def GetInfo(args, components: list) -> dict:
    for num in [100,104]:
        if num not in components:
            components.append(num)
    print(components)
    global count
    count += 1
    result = await GetMembershipidAndMembershiptype(args)
    membershipid = result['membershipid']
    membershiptype = result['membershiptype_num']
    response = await destiny.api.get_profile(membershiptype, membershipid, components)
    get_success(response, args)
    # TODO：在这里修复好检测玩家数据是不是隐私
    # TODO：添加玩家的绑定删除的消息提示
    # TODO：巅峰球查询有点简陋
    # TODO：群内抽奖
    # TODO：完成战绩查询的成败显示
    # TODO：蛋/骨头过多自动撤回
    # TODO：手机添加词库的时候插入图片比较困难
    # TODO：优化词库查询的显示
    # TODO：优化添加问答的正则表达式
    # TODO：优化raid查询的keyerror
    # if len(response['Response']['metrics']) == 1:
    #     raise Error_Privacy(args)
    for data in response['Response']:
        if 'data' not in response['Response'][data] and data != 'profileTransitoryData':
            raise Exception('🤔啊这...当前玩家命运2数据设置为隐私不可见')
    response['Response']['membershipid'] = membershipid
    response['Response']['membershiptype_num'] = membershiptype
    response['Response']['membershiptype_char'] = result['membershiptype_char']
    return response['Response']


# @ on_command('突袭', aliases=('raid', 'RAID', 'Raid'), only_to_me=False)
# async def GetPlayerProfile(session):
#     try:
#         hardlink = gethardlink(session)
#         if hardlink:
#             args = hardlink
#         else:
#             args = session.current_arg
#         info = await GetInfo(args, [900])
#         args = info['profile']['data']['userInfo']['displayName']
#         membershipid = info['profile']['data']['userInfo']['membershipId']
#         url = f'https://b9bv2wd97h.execute-api.us-west-2.amazonaws.com/prod/api/player/{membershipid}'
#         async with aiohttp.request("GET", url) as r:
#             # 或者直接await r.read()不编码，直接读取，适合于图像等无法编码文件
#             response = await r.text(encoding="utf-8")
#         raid = json.loads(response)
#         raid = raid['response']
#         clears_value = raid['clearsRank']['value']
#         if 'subtier' in raid['clearsRank']:
#             clears_rank = raid['clearsRank']['tier'] + \
#                 ' ' + raid['clearsRank']['subtier']
#         else:
#             clears_rank = raid['clearsRank']['tier']
#         speed_value = raid['speedRank']['value']
#         if 'subtier' in raid['speedRank']:
#             speed_rank = raid['speedRank']['tier'] + \
#                 ' ' + raid['speedRank']['subtier']
#         else:
#             speed_rank = raid['speedRank']['tier']
#         time = get_time_text(speed_value)
#         msg = f'''{args}
# 🎉【完成】{clears_value}次 📍{clears_rank}
# ✨【时间】{time} 🚀{speed_rank}\n'''
# # 针对小日向做了较大的更新，输入 d2 返回菜单以查看更新
# # 如果数据异常请尝试用队伍码查询'''
#         raiddict = {}
#         for i in raid['activities']:
#             raidname = await destiny.decode_hash(i['activityHash'], 'DestinyActivityDefinition')
#             raidname = raidname['displayProperties']['name']
#             clears = i['values']['clears']
#             full_clears = i['values']['fullClears']
#             sherpaCount = i['values']['sherpaCount']
#             if 'fastestFullClear' in i['values']:
#                 time = i['values']['fastestFullClear']['value']
#             else:
#                 time = 0
#             if raidname in raiddict.keys():
#                 raiddict[raidname]['clears'] += clears
#                 raiddict[raidname]['full_clears'] += full_clears
#                 raiddict[raidname]['sherpaCount'] += sherpaCount
#                 if raiddict[raidname]['time'] > time:
#                     raiddict[raidname]['time'] = time
#             else:
#                 raiddict[raidname] = {
#                     'clears': clears,
#                     'full_clears': full_clears,
#                     'sherpaCount': sherpaCount,
#                     'time': time}
#         raid_order = sorted(
#             raiddict.items(), key=lambda x: x[1]['clears'], reverse=True)
#         namedict = {
#             '世界吞噬者，利维坦: 巅峰': '世界吞噬者: 巅峰',
#             '世界吞噬者，利维坦: 普通': '世界吞噬者: 普通',
#             '忧愁王冠: 普通': '忧愁王冠',
#             '最后一愿: 等级55': '最后一愿',
#             '最后一愿: 普通': '最后一愿',
#             '利维坦，星之塔: 普通': '星之塔: 普通',
#             '利维坦，星之塔: 巅峰': '星之塔: 巅峰'
#         }
#         for i in raid_order:
#             raidname = i[0]
#             if raidname in namedict.keys():
#                 raidname = namedict[raidname]
#             clears = i[1]['clears']
#             # 利维坦，星之塔: 普通
#             full_clears = i[1]['full_clears']
#             sherpaCount = i[1]['sherpaCount']
#             time = get_time_text(i[1]['time'])
#             if get_flawless(i, info):
#                 head = f'💎{raidname}'
#             else:
#                 head = f'⚪{raidname}'
#             msg += \
#                 f'''{head}🚀{time}
#       🎐{full_clears:^3}/🎯{clears:^3}🎓{sherpaCount:^3}
# '''
#         msg += f'#回复d2以查看其他功能\n💎无暇🎐全程🎯通关🎓导师🚀最快{AppendInfo}\n❗王冠和往日无暇暂时无法查询'
#         await session.send(msg, at_sender=True)
#     except Exception as err:
#         await session.send(f'{err}', at_sender=True)


# @on_command('PVP', aliases=('pvp', 'Pvp'), only_to_me=False)
async def GetPlayerpvp(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [900, 1100])
        record = info['profileRecords']['data']['records']
        metrics = info['metrics']['data']['metrics']
        args = info['profile']['data']['userInfo']['displayName']

        kill = metrics['811894228']['objectiveProgress']['progress']
        reset = metrics['3626149776']['objectiveProgress']['progress']
        kda = int(metrics['871184140']['objectiveProgress']['progress']) / 100
        valor_now = metrics['2872213304']['objectiveProgress']['progress']
        kill_this_season = metrics['2935221077']['objectiveProgress']['progress']
        Glory = metrics['268448617']['objectiveProgress']['progress']
        第七砥柱 = record['1110690562']['objectives'][0]['progress']
        万夫莫敌 = record['1582949833']['objectives'][0]['progress']
        黑夜鬼魂 = record['3354992513']['objectives'][0]['progress']
        为你而做 = record['380324143']['objectives'][0]['progress']
        msg = f'''{args}
🤞【职业生涯】
     🎯击败对手：{kill}人
     🎉英勇重置：{reset}次\n'''
        msg += f'     🙏为你而做🙏：{为你而做}次\n' if 为你而做 != 0 else ''
        msg += f'     💎第七砥柱💎：{第七砥柱}次\n' if 第七砥柱 != 0 else ''
        msg += f'     💎万夫莫敌💎：{万夫莫敌}次\n' if 万夫莫敌 != 0 else ''
        msg += f'     💎黑夜鬼魂💎：{黑夜鬼魂}次\n' if 黑夜鬼魂 != 0 else ''
        msg += f'''🤞【当前赛季】
     🎐KDA：{kda}
     🧨生存分：{Glory}
     ✨赛季击杀：{kill_this_season}
     ⚔英勇总分：{valor_now}{AppendInfo}
#回复d2以查看其他功能'''
        print(msg)
        await session.send(msg, at_sender=True)
    except Exception as e:
        await session.send(f'{e}', at_sender=True)


def get_drop(now, localtime):
    temp = now - localtime
    if temp.days >= 365:
        return str(round(temp.days / 365)) + '年前'
    elif temp.days >= 30:
        return str(round(temp.days / 30)) + '月前'
    elif temp.days >= 7:
        return str(round(temp.days / 7)) + '周前'
    elif temp.days >= 1:
        return str(round(temp.days)) + '天前'
    elif temp.seconds >= 3600:
        return str(round(temp.seconds / 3600)) + '小时前'
    else:
        return str(round(temp.seconds / 60)) + '分钟前'


def get_kda(times):
    return str(round(times['values']['killsDeathsAssists']['basic']['value'], 1))


async def GetRaidReport(membershipid):
    try:
        url = f'https://b9bv2wd97h.execute-api.us-west-2.amazonaws.com/prod/api/player/{membershipid}'
        async with aiohttp.request("GET", url) as r:
            # 或者直接await r.read()不编码，直接读取，适合于图像等无法编码文件
            response = await r.text(encoding="utf-8")
        raid = json.loads(response)
        raid = raid['response']
        clears_value = raid['clearsRank']['value']
        if 'subtier' in raid['clearsRank']:
            clears_rank = raid['clearsRank']['tier'] + \
                ' ' + raid['clearsRank']['subtier']
        else:
            clears_rank = raid['clearsRank']['tier']
        speed_value = raid['speedRank']['value']
        if 'subtier' in raid['speedRank']:
            speed_rank = raid['speedRank']['tier'] + \
                ' ' + raid['speedRank']['subtier']
        else:
            speed_rank = raid['speedRank']['tier']
        if speed_value > 0:
            m, s = divmod(speed_value, 60)
            h, m = divmod(m, 60)
            if h == 0:
                time = f'{m}m{s}s'
            else:
                time = f'{h}h{m}m{s}s'
        msg = f'''完成：{clears_value}次  Speed：{time}\n'''
        return msg
    except Exception as e:
        raise FailToGet(membershipid, '获取队伍信息失败')


# @ on_command('战绩', aliases=('查询战绩', '战绩查询'), only_to_me=False)
# async def d2_activity(session):
#     try:
#         hardlink = gethardlink(session)
#         if hardlink:
#             args = hardlink
#         else:
#             args = session.current_arg
#         res = await GetInfo(args, [200])
#         args = res['profile']['data']['userInfo']['displayName']
#         msg = args + '\n'
#         for characterid in res['characters']['data']:
#             json = await destiny.decode_hash(res['characters']['data'][characterid]['classHash'], 'DestinyClassDefinition')
#             _class = json['displayProperties']['name']
#             re = await destiny.api.get_activity_history(res['profile']['data']['userInfo']['membershipType'], res['profile']['data']['userInfo']['membershipId'], characterid, count=4)
#             msg += '⚪' + _class + '⚪' + '\n'
#             for times in re['Response']['activities']:
#                 activityid = times['activityDetails']['directorActivityHash']
#                 utc = times['period']
#                 UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
#                 utcTime = datetime.datetime.strptime(utc, UTC_FORMAT)
#                 localtime = utcTime + datetime.timedelta(hours=8)
#                 now = datetime.datetime.now()
#                 time = get_drop(now, localtime)
#                 json = await destiny.decode_hash(activityid, 'DestinyActivityDefinition')
#                 activity = json['displayProperties']['name']
#                 msg += activity + ' ' + time + ' '
#                 msg += 'KDA：' + get_kda(times) + '\n'
#         msg += f'#回复d2以查看其他功能{AppendInfo}'
#         await session.send(msg, at_sender=True)
#     except Exception as e:
#         await session.send(f'{e}')

pvpSqlitePath = os.path.join(destiny2DirPath,'identifier1.sqlite')
userReplyPath = os.path.join(destiny2DirPath,'reply','user')
@sv.on_fullmatch(('echo','Echo'))
async def D2_condition(bot, ev):
    text = "{:,}".format(count)
    
    pvpSqliteSize = os.path.getsize(pvpSqlitePath)
    pvpSqliteSize = get_formatSize(pvpSqliteSize)
    userReplyList = os.listdir(userReplyPath)

    jsonCount = 0
    for fileName in userReplyList:
        jsonCount += 1 if '.json' in fileName else 0
    jsonCount=num2str(jsonCount)


    msg = f'调用次数：{text}\n个人词库：{jsonCount}\n数据库：{pvpSqliteSize}'
    await bot.send(ev, msg)


# @sv.on_prefix(('ELO', 'Elo', 'elo'))
# async def Elo(bot, ev):
#     try:
#         args = ev.message.extract_plain_text()
#         if args.isdigit() == True and len(args) == 17:
#             # 提供的是steam64位id
#             membershipid = await GetMembershipidFromSteam64(args)
#         else:
#             # 提供的是steam用户名
#             membershipid = await GetMembershipidFromSteamid(args)


# @ on_command('ELO', aliases=('Elo', 'elo'), only_to_me=False)
# async def Elo(session):
#     try:
#         hardlink = gethardlink(session)
#         if hardlink:
#             args = hardlink
#         else:
#             args = session.current_arg
#         info = await GetMembershipidAndMembershiptype(args)
#         membershipid = info['membershipid']
#         membershiptype = info['membershiptype_num']
#         url = f'https://api.tracker.gg/api/v2/destiny-2/standard/profile/{membershiptype}/{membershipid}/segments/playlist?season=13'
#         async with aiohttp.request("GET", url) as r:
#             # 或者直接await r.read()不编码，直接读取，适合于图像等无法编码文件
#             response = await r.text(encoding="utf-8")
#         info = json.loads(response)
#         info = info['data']
#         msg = args+'\n'
#         checkdict = {"control": "占领",
#                      "iron-banner": "铁骑",
#                      "pvecomp_gambit": "智谋",
#                      "allMayhem": "鏖战",
#                      "trials_of_osiris": "试炼",
#                      "elimination": "灭绝",
#                      "survival": "生存",
#                      "clash": "死斗",
#                      "rumble": "混战"}
#         for i in info:
#             mode = checkdict[i['attributes']['playlist']]
#             elo = i['stats']['elo']['value']
#             # rank = round(100 - i['stats']['elo']['percentile'], 1)
#             rank = i['stats']['elo']['percentile']
#             if int(rank) <= 60:
#                 rank = f'👇后{rank:<4}%'
#             else:
#                 rank = round(100 - rank, 1)
#                 rank = f'👆前{rank:<4}%'
#             kd = float(i['stats']['kd']['displayValue'])
#             if kd > 10:
#                 kd = round(kd, 1)
#             msg += f'🎉{mode}📕 Elo:{elo:<4}\n      📏Kd:{kd:^5} {rank:\u3000<11}\n'
#         msg += f'#回复d2以查看其他功能{AppendInfo}'
#         await session.send(msg, at_sender=True)
#     except TypeError:
#         await session.send('Tracker服务器繁忙，请两分钟后再试', at_sender=True)
#     except KeyError:
#         await session.send('Tracker服务器繁忙，请两分钟后再试', at_sender=True)
#     except Exception as e:
#         await session.send(f'{e}', at_sender=True)


#@on_command('队伍', aliases=('队伍查询', '火力战队', '找内鬼'), only_to_me=False)
async def getDataFireteam(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [1000])
        args = info['profile']['data']['userInfo']['displayName']
        if len(info['profileTransitoryData']) == 1:
            raise FailToGet(args, '玩家目前不在线')
        else:
            partyMembers = info['profileTransitoryData']['data']['partyMembers']
        msg = '【火力战队查询】\n'
        for i in partyMembers:
            name = i['displayName']
            membershipid = i['membershipId']
            if i['status'] == 11:
                msg += f'🦄『{name}』\n'
            else:
                msg += f'🐴『{name}』\n'
            msg += await GetRaidReport(membershipid)
        msg += f'#回复d2以查看其他功能{AppendInfo}'
        await session.send(msg, at_sender=True)
    except Exception as e:
        await session.send(f'{e}', at_sender=True)


@on_command('保存数据', aliases=('保存'), only_to_me=False)
async def savedata_hand(session):
    savedata()
    await session.send('写入成功')


def get_icon_kills(num):
    if num >= 5000:
        return '🙏'
    elif num >= 2000:
        return '😍'
    elif num >= 1000:
        return '🎉'
    else:
        return '⚪'


#@on_command('击杀数据', aliases=('击杀', '击杀查询'), only_to_me=False)
async def KillWeaponData(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        res1 = re.match(r'(7656\d{13}) +(术士|猎人|泰坦)', args)
        if res1:
            res = res1
        else:
            res = re.match(r'(.+) +(术士|猎人|泰坦)', args)
        if res:
            id = res.group(1)
            classtype = res.group(2)
            info = await GetInfo(id, [200])
            args = info['profile']['data']['userInfo']['displayName']
            membershipid = info['membershipid']
            membershiptype = info['membershiptype_char']
            classdict = {'泰坦': 3655393761, '猎人': 671679327, '术士': 2271682572}
            classhash = classdict[classtype]
            characterid = ''
            for i in info['characters']['data']:
                if classhash == info['characters']['data'][i]['classHash']:
                    characterid = info['characters']['data'][i]['characterId']
                    break
            # args = info['profile']['data']['userInfo']['displayName']
            url = f'https://api.tracker.gg/api/v2/destiny-2/standard/profile/{membershiptype}/{membershipid}/segments/detailedStat?characterId={characterid}&modeType=AllPvP'
            async with aiohttp.request("GET", url) as r:
                # 或者直接await r.read()不编码，直接读取，适合于图像等无法编码文件
                response = await r.text(encoding="utf-8")
            info1 = json.loads(response)
            info1 = info1['data']
            msg = args + '\n'
            weponlist = {'Shotgun': '霰弹',
                         'Melee': '近战',
                         'HandCannon': '手炮',
                         'Super': '超能',
                         'AutoRifle': '自动',
                         'Sniper': '狙击',
                         'Grenade': '手雷',
                         'PulseRifle': '脉冲',
                         'GrenadeLauncher': '榴弹',
                         'FusionRifle': '融合',
                         'TraceRifle': '追踪',
                         'RocketLauncher': '火箭',
                         'MachineGun': '机枪',
                         'SideArm': '手枪',
                         'Bow': '弓箭',
                         'Relic': '圣物',
                         'Sword': '刀剑',
                         'Submachinegun': '微冲',
                         'ScoutRifle': '斥候',
                         'Ability': '技能',
                         'BeamRifle': '追踪'}
            stata = {}
            for i in info1:
                if 'weapon' in i['attributes'].keys():
                    weapon = weponlist[i['attributes']['weapon']]
                    kills = int(i['stats']['weaponKills']['value'])
                    precisionkills = 0
                    if 'precisionKills' in i['stats']:
                        precisionkills = int(
                            i['stats']['precisionKills']['value'])
                    # if 'killsPrecisionKills' in i['stats']:
                    #     #str
                    #     accuracy = i['stats']['killsPrecisionKills']['displayValue']
                    # if 'earnedMedals' in i['stats']:
                    #     medals = int(i['stats']['earnedMedals']['value'])
                    # stata = {weapon: {'kills': kills,'precisionKills': precisionkills, 'accuracy': round(precisionkills/kills, 3)}}
                    if kills == 0:
                        acc = 0
                    else:
                        # {precisionkills:^5}📏
                        acc = round(precisionkills / kills * 100, 1)
                    stata[weapon] = {'kills': kills,
                                     'precisionkills': precisionkills, 'acc': acc}
            msg = f'{args}\n【熔炉枪械击杀数据】{classtype}\n'
            kills_order = sorted(
                stata.items(), key=lambda x: x[1]['kills'], reverse=True)
            if len(kills_order) >= 10:
                weapon_len = 10
            else:
                weapon_len = len(kills_order)
            if len(kills_order) == 0:
                raise Exception('❗连接Bungie服务器失败，请检查用户名/队伍码是否输入正确')
            for i in range(weapon_len):
                weapon = kills_order[i][0]
                kills = kills_order[i][1]['kills']
                precisionkills = kills_order[i][1]['precisionkills']
                acc = kills_order[i][1]['acc']
                icon_kills = get_icon_kills(kills)
                icon_acc = '🏹'
                if acc >= 58:
                    icon_acc = '🎯'
                msg += f'{icon_kills}{weapon}🔪{kills:^5}{icon_acc}{acc:>4}%\n'
            msg += f'🧨回复 d2 以查看其他功能{AppendInfo}'
            await session.send(msg, at_sender=True)
        else:
            raise Exception('\n❗指令格式错误啦\n👉击杀 码/名 职业')
    except pydest.PydestException as err:
        await session.send(f'连接Bungie服务器失败，请检查用户名/队伍码是否输入正确\n{err}', at_sender=True)
    except Exception as e:
        await session.send(f'{e}', at_sender=True)


def Check_Penguin(info):
    msg = ''
    notget = 0
    info = info['profileProgression']['data']['checklists']['817948795']
    for key in info:
        if info[key] != True:
            notget += 1
            msg += PenguinSouvenirs[key]['name']
            msg += '📍' + PenguinSouvenirs[key]['location'] + '\n'
    msg += '#回复d2以查看其他功能'
    if notget == 0:
        head = '🎉你已经收集了全部9只🐧啦，小日向会非常感谢你的！\n'
    else:
        head = f'🎐你还差{notget}只小🐧没收集哦，下面提供了它们的位置，快带它们回家吧！\n'
    head += msg
    return head


#@on_command('企鹅查询', aliases=('企鹅', '🐧'), only_to_me=False)
async def Check_Penguin_aync(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [104])
        args = info['profile']['data']['userInfo']['displayName']
        msg = f'{args}【企鹅收集】\n'
        res = msg + Check_Penguin(info)
        await session.send(res, at_sender=True)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)

        # 3981543480 现有总分
        # 3329916678 年三成就总分


def Check_egg(info):
    msg = ''
    notget = 0
    info = info['profileProgression']['data']['checklists']['2609997025']
    for key in info:
        if info[key] != True:
            notget += 1
            msg += egg[key]['name']
            msg += '📍' + egg[key]['location'] + '\n'
    msg += '#回复d2以查看其他功能'
    if notget == 0:
        head = '🎉你已经收集了全部40个🥚啦，你就是幽梦之城的守护者！\n'
    else:
        head = f'🎐你还差{notget}颗🥚没收集哦，下面提供了它们的位置，快带着碎愿者冲吧！\n'
    head += msg
    return head, notget


#@on_command('腐化卵查询', aliases=('孵化卵', '蛋', '卵', '🥚', '腐化卵'), only_to_me=False)
async def Check_egg_aync(session: CommandSession):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [104])
        args = info['profile']['data']['userInfo']['displayName']
        res, notget = Check_egg(info)

        message_id = await session.send(f'{args}\n{res}', at_sender=True)
        message_id = message_id['message_id']
        if notget > 15:
            await asyncio.sleep(1)
            await session.send('你的未收集物品过多，查询信息将在8秒内撤回，请复制保存。', at_sender=True)
            await asyncio.sleep(8)
            await session.bot.delete_msg(message_id=message_id, self_id=session.event.self_id)
        else:
            pass
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)

        # 3981543480 现有总分
        # 3329916678 年三成就总分


def get_gambit(info):
    record = info['profileRecords']['data']['records']
    metric = info['metrics']['data']['metrics']
    击败入侵者 = record['3381316332']['intervalObjectives'][0]['progress']
    入侵击杀守护者 = record['985373860']['intervalObjectives'][0]['progress']
    守护天使 = record['1334533602']['objectives'][0]['progress']
    一人成军 = record['511083400']['objectives'][0]['progress']
    唤雨师 = record['4206114008']['objectives'][0]['progress']
    半库江山 = record['1197518485']['objectives'][0]['progress']  # 🎯🏆✨🎐🎉💊

    赛季消灭阻绝者 = metric['2709150210']['objectiveProgress']['progress']
    赛季存储荧光 = metric['2920575849']['objectiveProgress']['progress']
    赛季智谋胜场 = metric['3483580010']['objectiveProgress']['progress']
    msg = f'''【职业生涯】
🏆唤雨师：{唤雨师}次
🏆半库江山：{半库江山}次
🏆守护天使：{守护天使}次
🏆一人成军：{一人成军}次
🎯击败入侵者：{击败入侵者}人
🎯入侵击杀守护者：{入侵击杀守护者}人
【当前赛季】
🎉智谋胜场：{赛季智谋胜场}场
✨存储荧光：{赛季存储荧光}块
🎐消灭阻绝者：{赛季消灭阻绝者}只
'''
    return msg


#@on_command('智谋', aliases=('智谋查询', '千谋'), only_to_me=False)
async def gambit_info(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [900, 1100])
        args = info['profile']['data']['userInfo']['displayName']
        res = get_gambit(info)
        head = f'{args}\n' + res + '#回复d2以查看其他功能'
        await session.send(head, at_sender=True)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


def Check_zengfu(info):
    msg = ''
    notget = 0
    info = info['profileRecords']['data']['records']['1121652081']['objectives']
    for key in info:
        if key['complete'] != True:
            notget += 1
            msg += 增幅[str(key['objectiveHash'])]['name'] + '📍' + \
                增幅[str(key['objectiveHash'])]['location'] + '\n'
    msg += '#回复d2以查看其他功能'
    if notget == 0:
        head = '🎉你已经收集了全部8个地区的增幅✈啦，你就是木卫二的守护者！\n'
    else:
        head = f'🎐你还差{notget}个地区的增幅✈没收集哦，快看看周报决定去哪获得增幅吧~\n'
    head += msg
    return head


#@on_command('增幅', aliases=(), only_to_me=False)
async def Check_zengfu_aync(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [900])
        args = info['profile']['data']['userInfo']['displayName']
        res = Check_zengfu(info)
        head = f'{args}\n' + res + '#回复d2以查看其他功能'
        await session.send(head, at_sender=True)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


dungeondict = {
    1077850348: "预言",
    # 1099555105: "冥冥低语:英雄",
    1375089621: "异端深渊",
    1738383283: "先知",
    2032534090: "破碎王座",
    2124066889: "前兆:普通",
    2582501063: "异端深渊",
    # 2731208666: "行动时刻:英雄",
    4148187374: "预言",
    4212753278: "前兆:大师"}


# @ on_command('地牢', aliases=('地牢查询'), only_to_me=False)
# async def Dungeon(session):
#     try:
#         hardlink = gethardlink(session)
#         if hardlink:
#             args = hardlink
#         else:
#             args = session.current_arg
#         info = await GetInfo(args,[])
#         args = info['profile']['data']['userInfo']['displayName']
#         membershipid = info['profile']['data']['userInfo']['membershipId']
#         url = f'https://bolskmfp72.execute-api.us-west-2.amazonaws.com/dungeon/api/player/{membershipid}'
#         async with aiohttp.request("GET", url) as r:
#             # 或者直接await r.read()不编码，直接读取，适合于图像等无法编码文件
#             response = await r.text(encoding="utf-8")
#         dungeon = json.loads(response)
#         dungeon = dungeon['response']
#         clears = dungeon['clearsRank']
#         clears_count = clears['value']
#         clear_rank = clears['tier'] + ' ' + \
#             clears['subtier'] if 'subtier' in clears else clears['tier']
#         speed = dungeon['speedRank']
#         speed_count = get_time_text(speed['value'])
#         speed_rank = speed['tier'] + ' ' + \
#             speed['subtier'] if 'subtier' in speed else speed['tier']
#         activities = dungeon['activities']
#         head = f'''{args}【地牢查询】
# 🎉【完成】{clears_count}次 📍{clear_rank}
# ✨【时间】{speed_count} 🚀{speed_rank}
# '''
#         record = {}
#         for i in activities:
#             hashid = i['activityHash']
#             dungeonname = dungeondict[hashid] if hashid in dungeondict else ''
#             if not dungeonname:
#                 continue
#             entity = i['values']
#             if dungeonname in record:
#                 record[dungeonname]['clears'] += entity['clears']
#                 record[dungeonname]['fullClears'] += entity['fullClears']
#                 record[dungeonname]['sherpaCount'] += entity['sherpaCount']
#                 if 'fastestFullClear' in entity:
#                     record[dungeonname]['fastestFullClear'] = entity['fastestFullClear']['value'] if entity['fastestFullClear'][
#                         'value'] < record[dungeonname]['fastestFullClear'] else record[dungeonname]['fastestFullClear']
#                 if 'flawlessDetails' in entity:
#                     least = 3
#                     for j in entity['flawlessActivities']:
#                         least = [least, j['accountCount']
#                                  ][j['accountCount'] < least]
#                     record[dungeonname]['flawlessDetails'] = least if least < record[dungeonname]['flawlessDetails'] or record[
#                         dungeonname]['flawlessDetails'] == 0 else record[dungeonname]['flawlessDetails']
#                 if 'bestPlayerCountDetails' in entity:
#                     record[dungeonname]['bestPlayerCountDetails'] = entity['bestPlayerCountDetails']['accountCount'] if entity['bestPlayerCountDetails'][
#                         'accountCount'] < record[dungeonname]['bestPlayerCountDetails'] or record[dungeonname]['bestPlayerCountDetails'] == 0 else record[dungeonname]['bestPlayerCountDetails']
#             else:
#                 clears = entity['clears']
#                 fullClears = entity['fullClears']
#                 sherpaCount = entity['sherpaCount']
#                 fastestFullClear = entity['fastestFullClear']['value'] if 'fastestFullClear' in entity else 0
#                 if 'flawlessActivities' in entity:
#                     least = 3
#                     for j in entity['flawlessActivities']:
#                         least = [least, j['accountCount']
#                                  ][j['accountCount'] < least]
#                     flawlessDetails = least
#                 else:
#                     flawlessDetails = 0
#                 bestPlayerCountDetails = entity['bestPlayerCountDetails'][
#                     'accountCount'] if 'bestPlayerCountDetails' in entity else 0
#                 record[dungeonname] = {'clears': clears, 'fullClears': fullClears,
#                                        'sherpaCount': sherpaCount, 'fastestFullClear': fastestFullClear,
#                                        'flawlessDetails': flawlessDetails, 'bestPlayerCountDetails': bestPlayerCountDetails}

#         # 归类完成
#         dungeon_order = sorted(
#             record.items(), key=lambda x: x[1]['clears'], reverse=True)
#         for i in dungeon_order:
#             dungeonname = i[0]
#             singledict = i[1]
#             clears = singledict['clears']
#             fullClears = singledict['fullClears']
#             sherpaCount = singledict['sherpaCount']
#             fastestFullClear = get_time_text(singledict['fastestFullClear'])
#             icon1 = '💎'if singledict['flawlessDetails'] == 1 else '⚪'
#             icon2 = '🎉' if singledict['bestPlayerCountDetails'] == 1 else '⚪'
#             head += f'''{icon1}{icon2}『{dungeonname}』🚀{fastestFullClear}
#         🎯{fullClears:<3}/✅{clears:<3} 🎓{sherpaCount:<2}\n'''
#         head += '💎单人无暇 🎉单人\n🚀回复d2以查看其他功能'
#         await session.send(head, at_sender=True)
#     except Exception as e:
#         await session.send(f'获取失败，{e}', at_sender=True)


def Check_bones(info):
    msg = ''
    notget = 0
    info = info['profileProgression']['data']['checklists']['1297424116']
    for i in bones:
        if info[i] == False:
            notget += 1
            msg += bones[i]['name']
            msg += '📍' + bones[i]['location'] + '\n'
    msg += '#回复d2以查看其他功能'
    if notget == 0:
        head = '🎉你已经收集了全部16个阿罕卡拉遗骨🦴啦，你就是行遍幽梦之城的破咒者\n'
    else:
        head = f'🎐你还差{notget}个遗骨🦴没收集哦，顺便去看看这周上维挑战在哪嗷\n'
    head += msg
    return head, notget


#@on_command('骨头', aliases=('🦴'), only_to_me=False)
async def Check_bones_aync(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [104])
        args = info['profile']['data']['userInfo']['displayName']
        res, notget = Check_bones(info)
        head = f'{args}\n' + res
        message_id = await session.send(head, at_sender=True)
        message_id = message_id['message_id']
        if notget > 10:
            await asyncio.sleep(1)
            await session.send('你的未收集物品过多，查询信息将在10秒内撤回，请复制保存。', at_sender=True)
            await asyncio.sleep(10)
            await session.bot.delete_msg(message_id=message_id, self_id=session.event.self_id)
        else:
            pass

    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


def Check_cats(info):
    msg = ''
    notget = 0
    info = info['profileProgression']['data']['checklists']['2726513366']
    for i in cats:
        if info[i] == False:
            notget += 1
            msg += cats[i]['name']
            msg += '📍' + cats[i]['location'] + '\n'
    msg += '#回复d2以查看其他功能'
    if notget == 0:
        head = '🎉你已经收集了全部9只小猫🐱啦，九柱神向你表示感谢\n'
    else:
        head = f'🎐你还差{notget}只小猫🐱没收集哦，下面是它们的位置：\n'
    head += msg
    return head


#@on_command('猫', aliases=('🐱'), only_to_me=False)
async def Check_cats_aync(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [104])
        args = info['profile']['data']['userInfo']['displayName']
        res = Check_cats(info)
        head = f'{args}\n' + res
        await session.send(head, at_sender=True)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


# def Check_chenghao(info):
#     msg = ''
#     notget = 0
#     info = info['profileProgression']['data']['checklists']['1297424116']
#     for i in bones:
#         if info[i] == False:
#             notget+=1
#             msg+=bones[i]['name']
#             msg+='📍'+bones[i]['location']+'\n'
#     msg += '#回复d2以查看其他功能'
#     if notget == 0:
#         head = '🎉你已经收集了全部16个阿罕卡拉遗骨🦴啦，你就是行遍幽梦之城的破咒者\n'
#     else:
#         head = f'🎐你还差{notget}个遗骨🦴没收集哦，顺便去看看这周上维挑战在哪嗷\n'
#     head += msg
#     return head


# @ on_command('称号', only_to_me=False)
# async def Check_bchenghao_aync(session):
#     try:
#         hardlink = gethardlink(session)
#         if hardlink:
#             args = hardlink
#         else:
#             args = session.current_arg
#         info = await GetInfo(args,[])
#         args = info['profile']['data']['userInfo']['displayName']
#         res = Check_chenghao(info)
#         head = f'{args}\n' + res
#         await session.send(head, at_sender=True)
#     except Exception as e:
#         await session.send(f'获取失败，{e}', at_sender=True)


def Check_chenghao(info):
    msg = ''
    info = info['profileRecords']['data']['records']
    for i in 称号:
        objectives = info[i]['objectives'][0]
        progress = objectives['progress']
        completionValue = objectives['completionValue']
        icon = '🎯' if completionValue <= progress else '⚪'
        icon = '🏆' if 'gold' in 称号[i] and progress == 称号[i]['gold'] else icon
        name = 称号[i]['name']
        msg += f'{icon}{name}：{progress}/{completionValue}\n'
    msg += '🎉回复d2以查看其他功能'
    head = '【称号查询】\n'
    head += msg
    return head


#@on_command('称号', only_to_me=False)
async def Check_chenghao_aync(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [900])
        args = info['profile']['data']['userInfo']['displayName']
        res = Check_chenghao(info)
        head = f'{args}\n' + res
        await session.send(head, at_sender=True)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


def Check_exo(info):
    msg = ''
    notget = 0
    info = info['profileProgression']['data']['checklists']['2568476210']
    for i in Exo:
        if info[i] == False:
            notget += 1
            msg += Exo[i]['name']
            msg += '📍' + Exo[i]['location'] + '\n'
    msg += '#回复d2以查看其他功能'
    if notget == 0:
        head = '🎉你已经收集了全部9只🐾死去的Exo啦\n'
    else:
        head = f'🎐你还差{notget}只🐾死去的Exo没收集哦，下面是它们的位置：\n'
    head += msg
    return head


#@on_command('exo', aliases=('Exo', 'EXO'), only_to_me=False)
async def Check_exo_aync(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [104])
        args = info['profile']['data']['userInfo']['displayName']
        res = Check_exo(info)
        head = f'{args}\n' + res
        await session.send(head, at_sender=True)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


def Check_suipian(info):
    msg = ''
    notget = 0
    info = info['profileProgression']['data']['checklists']['1885088224']
    for i in 暗熵碎片:
        if info[i] == False:
            notget += 1
            msg += 暗熵碎片[i]['name']
            msg += '📍' + 暗熵碎片[i]['location'] + '\n'
    msg += '#回复d2以查看其他功能'
    if notget == 0:
        head = '🎉你已经收集了全部9个🔷暗熵碎片啦\n'
    else:
        head = f'🎐你还差{notget}个🔷暗熵碎片没收集哦，下面是它们的位置：\n'
    head += msg
    return head


#@on_command('碎片', aliases=('暗熵碎片', '碎片查询', '🧩'), only_to_me=False)
async def Check_suipian_aync(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [104])
        args = info['profile']['data']['userInfo']['displayName']
        res = Check_suipian(info)
        head = f'{args}\n' + res
        await session.send(head, at_sender=True)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


def Check_saijitiaozhan(info):
    msg = ''
    info = info['characterPresentationNodes']['data']
    characterid = list(info.keys())[0]
    info = info[characterid]['nodes']
    for i in 赛季挑战:
        objectives = info[i]
        progressValue = objectives['progressValue']
        completionValue = objectives['completionValue']
        icon = '✅' if completionValue == progressValue and completionValue != 0 else '⚪'
        name = 赛季挑战[i]
        msg += f'{icon}{name}：{progressValue}/{completionValue}\n'
    msg += '🎉回复d2以查看其他功能'
    head = '【赛季挑战】\n'
    head += msg
    return head


#@on_command('赛季挑战', only_to_me=False)
async def Check_saijitiaozhan_aync(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [700])
        args = info['profile']['data']['userInfo']['displayName']
        res = Check_saijitiaozhan(info)
        head = f'{args}\n' + res
        await session.send(head, at_sender=True)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


def Check_qianzhao(info):
    msg = ''
    records = info['profileRecords']['data']['records']
    格力康号线索 = info['profileProgression']['data']['checklists']['3975225462']
    notShowTag = 0
    notGetWeek = 0
    for i in 前兆['碎片']:
        objectives = records[i]['objectives'][0]
        progressValue = objectives['progress']
        completionValue = objectives['completionValue']
        icon = '✅' if completionValue == progressValue else '⚪'
        name = 前兆['碎片'][i]['name']
        msg += f'{icon}{name}：{progressValue}/{completionValue}\n'
        if progressValue != completionValue:
            notGetWeek += 1
            if notShowTag:
                continue
            else:
                notShowTag = 1
            entries = 前兆['碎片'][i]['entries']
            for check in entries:
                if not 格力康号线索[check]:
                    msg += f'{entries[check]["name"]}：{entries[check]["location"]}\n'

    for i in 前兆['成就']:
        objectives = records[i]['intervalObjectives'][11]
        progressValue = objectives['progress']
        completionValue = objectives['completionValue']
        icon = '✅' if completionValue == progressValue else '⚪'
        name = 前兆['成就'][i]
        msg += f'{icon}{name}：{progressValue}/{completionValue}\n'

    msg += '🎉回复d2以查看其他功能'
    head = '【前兆查询】\n'
    head += msg
    return head, notGetWeek


#@on_command('前兆', only_to_me=False)
async def Check_qianzhao_aync(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [900, 104])
        args = info['profile']['data']['userInfo']['displayName']
        res, notGetWeek = Check_qianzhao(info)
        head = f'{args}\n' + res
        print(head)
        await session.send(head, at_sender=True)
        if notGetWeek:
            await asyncio.sleep(2)
            await session.send(f'ヾ(•ω•`)o\n😝距离天选赛季结束还有1周\n👉[{args}]还差 {notGetWeek}周 的线索没有摸完\n👉摸完全部3周的线索可以解锁天选者称号的隐藏成就\n🤣小日向提醒你一下，别忘了噢', at_sender=True)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


classdict = {3655393761: '泰坦', 671679327: '猎人', 2271682572: '术士',
             '泰坦': 3655393761, '猎人': 671679327, '术士': 2271682572}


def Check_DSC(info):
    msg = ''
    characterProgressions = info['characterProgressions']['data']
    characters = info['characters']['data']
    Record = info['profileRecords']['data']['records']
    职业 = ''
    职业msg = ''
    关卡 = ['', '', '', '']
    for i in characterProgressions:
        characterName = classdict[characters[i]['classHash']]
        milestones = characterProgressions[i]['milestones']
        msg += f'{characterName}：'
        if '541780856' in milestones:
            phases = milestones['541780856']['activities'][0]['phases']
            for j in range(4):
                complete = phases[j]['complete']
                msg += '✅' if complete == True else '⚪'
        else:
            for j in range(4):
                msg += '✅'
        msg += '\n'

    msg += '【挑战查询】\n'
    for i in DSC['挑战']:
        name = DSC['挑战'][i]
        icon = '✅' if Record[i]['objectives'][0]['complete'] == True else '⚪'
        msg += f'{icon}{name}\n'
    msg += '🎉回复d2以查看其他功能\n❗由于Bungie数据问题，只打尾王也算完成了全程'
    head = '【深岩墓室查询】\n'
    head += msg
    return head


#@on_command('地窖', aliases=('深岩墓室'), only_to_me=False)
async def Check_DSC_aync(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200, 202, 900])
        args = info['profile']['data']['userInfo']['displayName']
        res = Check_DSC(info)
        head = f'{args}\n' + res
        await session.send(head, at_sender=True)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


def Check_dianfeng(info, characterId):
    msg = ''
    info = info['characterProgressions']['data'][characterId]['milestones']
    for i in 巅峰:
        if 'name' not in 巅峰[i]:
            # earned = info[i]['rewards'][0]['entries'][0]['earned']
            icon = '⚪' if i in info else '✅'
            name = 巅峰[i]
            msg += f'{icon}{name}\n'
        else:
            icon = '⚪' if i in info else '✅'
            # earned = info[i]['availableQuests'][0]['status']['completed']
            name = 巅峰[i]['name']
            msg += f'{icon}{name}\n'
    msg += '🎉回复d2以查看其他功能'
    head = '【巅峰球查询】\n'
    head += msg
    return head


#@on_command('巅峰', aliases=('巅峰球'), only_to_me=False)
async def Check_dianfeng_aync(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        res1 = re.match(r'(7656\d{13}) +(术士|猎人|泰坦)', args)
        res = res1 if res1 else re.match(r'(.+) +(术士|猎人|泰坦)', args)

        if res:
            id = res.group(1)
            classtype = classdict[res.group(2)]
            info = await GetInfo(id, [200, 202])
            args = info['profile']['data']['userInfo']['displayName']
            for characterId in info['characters']['data']:
                if info['characters']['data'][characterId]['classHash'] == classtype:
                    break
            msg = Check_dianfeng(info, characterId)
            head = f'{args}\n' + msg
            await session.send(head, at_sender=True)
        else:
            raise Exception('\n❗指令格式错误啦\n👉巅峰 名/码 职业')
    except Exception as e:
        await session.send(f'{e}', at_sender=True)


def get_zongshi_icon(num):
    if num == 0:
        return '⚪'
    elif num <= 15:
        return '✅'
    elif num <= 30:
        return '🎉'
    else:
        return '🙏'


# def Check_zongshi(info):
#     msg = ''
#     info = info['profileRecords']['data']['records']
#     for i in 宗师:
#         objectives = info[i]['objectives'][0]
#         progress = objectives['progress']
#         icon = get_zongshi_icon(progress)
#         name = 宗师[i]
#         msg += f'{icon}{name}：{progress}次\n'
#     msg += '🎉回复d2以查看其他功能'
#     head = '【宗师查询】\n'
#     head += msg
#     return head


# @on_command('宗师', only_to_me=False)
# async def Check_zongshi_aync(session):
#     try:
#         hardlink = gethardlink(session)
#         if hardlink:
#             args = hardlink
#         else:
#             args = session.current_arg
#         info = await GetInfo(args, [900])
#         args = info['profile']['data']['userInfo']['displayName']
#         res = Check_zongshi(info)
#         head = f'{args}\n' + res
#         await session.send(head, at_sender=True)
#     except Exception as e:
#         await session.send(f'获取失败，{e}', at_sender=True)


def Check_jiling(info):
    msg = ''
    notget = 0
    info = info['profileProgression']['data']['checklists']['1856270404']
    for i in 机灵:
        if info[i] == False:
            notget += 1
            msg += 机灵[i]['name']
            msg += '📍' + 机灵[i]['location'] + '\n'
    msg += '🎉回复d2以查看其他功能'
    if notget == 0:
        head = '🎉你已经收集了全部10个📕机灵啦\n'
    else:
        head = f'🎐你还差{notget}个📕机灵没收集哦，下面是它们的位置：\n'
    head += msg
    return head


#@on_command('机灵', aliases=('死去的机灵',), only_to_me=False)
async def Check_jiling_aync(session: CommandSession):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [104])
        args = info['profile']['data']['userInfo']['displayName']
        res = Check_jiling(info)
        head = f'{args}\n' + res
        await session.send(head, at_sender=True)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


def Check_yutu(info, characterId):
    msg = ''
    notget = 0
    info = info['characterProgressions']['data'][characterId]['checklists']['1912364094']
    for i in 玉兔:
        if info[i] == False:
            notget += 1
            msg += 玉兔[i]['name']
            msg += '📍' + 玉兔[i]['location'] + '\n'
    if notget == 0:
        head = '🎉你已经收集了全部9只🐇兔子啦\n'
    else:
        head = f'🎐你还差{notget}只🐇兔子没收集哦，下面是它们的位置：\n'
    msg += '🎉回复d2以查看其他功能'
    head += msg
    return head


@on_command('兔子', aliases=('玉兔'), only_to_me=False)
async def Check_yutu_aync(session: CommandSession):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        res1 = re.match(r'(7656\d{13}) +(术士|猎人|泰坦)', args)
        res = res1 if res1 else re.match(r'(.+) +(术士|猎人|泰坦)', args)

        if res:
            id = res.group(1)
            classtype = classdict[res.group(2)]
            info = await GetInfo(id, [200, 202])
            args = info['profile']['data']['userInfo']['displayName']
            for characterId in info['characters']['data']:
                if info['characters']['data'][characterId]['classHash'] == classtype:
                    break
            msg = Check_yutu(info, characterId)
            head = f'{args}\n' + msg
            await session.send(head, at_sender=True)
        else:
            raise Exception('\n❗指令格式错误啦\n👉兔子 名/码 职业')
    except Exception as e:
        await session.send(f'{e}', at_sender=True)


def GetDaysPlayedTotal(minutes: int) -> str:
    days = round(int(minutes)/60, 1)
    return f'{days}h'


def Check_shengya(info):
    msg = ''
    character_msg = ''
    seasons = info['profile']['data']['seasonHashes']
    characters = info['characters']['data']
    records = info['profileRecords']['data']
    传承成就分 = "{:,}".format(records['legacyScore'])
    当前成就分 = "{:,}".format(records['activeScore'])
    熔炉胜场 = records['records']['3561485187']['intervalObjectives'][0]['progress']
    智谋胜场 = records['records']['1676011372']['objectives'][0]['progress'] + \
        records['records']['2129704137']['objectives'][0]['progress'] + \
        records['records']['89114360']['objectives'][0]['progress']
    打击列表 = records['records']['2780814366']['objectives'][2]['progress']

    season_msg = '年三：'
    for season in 赛季['年三']:
        if season in seasons:
            season_msg += f'✅{赛季["年三"][season]}'
        else:
            season_msg += f'⚪{赛季["年三"][season]}'
    season_msg += '\n年四：'
    for season in 赛季['年四']:
        if season in seasons:
            season_msg += f'✅{赛季["年四"][season]}'
        else:
            season_msg += f'⚪{赛季["年四"][season]}'
    for value in characters.values():
        className = classdict[value['classHash']]
        daysPlayedTotal = GetDaysPlayedTotal(value['minutesPlayedTotal'])
        character_msg += f'📕{className}：{daysPlayedTotal}\n'

    msg = f'''
{season_msg}
🔷传承成就分：{传承成就分}
🔷当前成就分：{当前成就分}
{character_msg}🏅熔炉胜场：{熔炉胜场}次
🏅智谋胜场：{智谋胜场}次
🏅打击列表：{打击列表}次
'''
    msg += '🎉回复d2以查看其他功能'
    return msg


#@on_command('生涯', aliases=('生涯查询', '角色查询'), only_to_me=False)
async def Check_shengya_aync(session: CommandSession):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200, 900])
        args = info['profile']['data']['userInfo']['displayName']
        res = Check_shengya(info)
        head = f'{args}' + res
        await session.send(head, at_sender=True)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


# def Check_rabbit(info):
#     明日之眼 = info['profileCollectibles']['data']['collectibles']['753200559']['state']


# @ on_command('突袭周常', only_to_me=False)
# async def Check_mingrizhiyan_aync(session):
#     try:
#         hardlink = gethardlink(session)
#         if hardlink:
#             args = hardlink
#         else:
#             args = session.current_arg
#         info = await GetInfo(args,[])
#         args = info['profile']['data']['userInfo']['displayName']
#         res = Check_weeklyraid(info)
#         head = f'{args}\n' + res
#         await session.send(head, at_sender=True)
#     except Exception as e:
#         await session.send(f'获取失败，{e}', at_sender=True)


黑色 = '#000000'
灰色 = '#818181'
黑体 = ImageFont.truetype('simhei.ttf', size=20)
活动标题 = ImageFont.truetype('simhei.ttf', size=30)
标题2 = ImageFont.truetype('simhei.ttf', size=24)
绿块 = Image.new('RGB', [40, 100], '#00b034')
红块 = Image.new('RGB', [40, 100], (229, 115, 125))


奇数颜色_战绩 = '#292929'
偶数颜色_战绩 = '#1F1F1F'
奇数块_战绩 = Image.new('RGB', [1000, 100], 奇数颜色_战绩)
偶数块_战绩 = Image.new('RGB', [1000, 100], 偶数颜色_战绩)

绿色_战绩 = '#3D8D4D'
红色_战绩 = '#8F2020'
标题_战绩 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=20)
KD字体_战绩 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=36)
KD标题字体_战绩 = ImageFont.truetype('MYingHeiPRC-W4.ttf', size=20)
中字_战绩 = ImageFont.truetype('MYingHeiPRC-W5.ttf', size=16)
小字_战绩 = ImageFont.truetype('MYingHeiPRC-W4.ttf', size=16)



@ on_command('战绩', aliases=('查询战绩', '战绩查询'), only_to_me=False)
async def d2_activity(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        res = await GetInfo(args, [200])
        args = res['profile']['data']['userInfo']['displayName']

        activityList = []
        characters = res['characters']['data']

        characterIdList = list(characters.keys())
        for characterId in characterIdList:
            className = classdict[characters[characterId]['classHash']]
            activities = await destiny.api.get_activity_history(res['membershiptype_num'], res['membershipid'], characterId, 50)
            if activities['ErrorStatus'] != 'Success':
                Message = activities['Message']
                raise Exception(f'🤔啊这...战绩查询失败了，可能是玩家设置了数据隐私。\n{Message}')
            if 'activities' not in activities['Response']:
                continue
            activities = activities['Response']['activities']
            for i in activities:
                i['characterId'] = characterId
                i['className'] = className
            activityList.extend(activities)
        activityList_order = sorted(
            activityList, key=lambda x: x['period'], reverse=True)
        activityListToBeUsed = activityList_order[:50]

        Length = len(activityListToBeUsed)
        activityRaw = Image.new('RGB', [1000, 80+Length*100], '#303030')
        draw = ImageDraw.Draw(activityRaw)

        draw.text([60, 15],
                  f'小日向战绩查询: {args}',
                  font=KD字体_战绩,
                  fill='white')

        for i in range(50):
            activity = activityListToBeUsed[i]
            res = await destiny.decode_hash(activity['activityDetails']['directorActivityHash'], 'DestinyActivityDefinition')
            res2 = await destiny.decode_hash(activity['activityDetails']['referenceId'], 'DestinyActivityDefinition')
            模式 = res['displayProperties']['name']
            名称 = res2['displayProperties']['name']
            modeNum = activity['activityDetails']['modes']
            时间 = get_activity_time(activity['period'])
            K = int(activity['values']['kills']['basic']['displayValue'])
            D = int(activity['values']['deaths']['basic']['displayValue'])
            A = int(activity['values']['assists']['basic']['displayValue'])
            KD = activity['values']['killsDeathsRatio']['basic']['displayValue']
            进行时间 = activity['values']['timePlayedSeconds']['basic']['displayValue']
            Score = int(activity['values']['score']['basic']['value'])
            ScoreShow = activity['values']['score']['basic']['displayValue']

            teamScore = int(activity['values']['teamScore']['basic']['value'])
            if i % 2 == 0:
                activityRaw.paste(偶数块_战绩, [0, 80+i*100])
            else:
                activityRaw.paste(奇数块_战绩, [0, 80+i*100])

            draw.text([60, 95+i*100],
                      f'{模式}',
                      font=标题_战绩,
                      fill='white'
                      )

            draw.text([60, 125+i*100],
                      f'▢ {名称}',
                      font=小字_战绩,
                      fill='#E5E5E5'
                      )

            draw.text([60, 150+i*100],
                      f'▢ {时间} · 用时 {进行时间}',
                      font=小字_战绩,
                      fill='#E5E5E5'
                      )

            draw.text([410, 95+i*100],
                      f'K: {K}',
                      font=中字_战绩,
                      fill='white')

            draw.text([410, 120+i*100],
                      f'D: {D}',
                      font=中字_战绩,
                      fill='white'
                      )
            draw.text([410, 145+i*100],
                      f'A: {A}',
                      font=中字_战绩,
                      fill='white'
                      )

            KandD = K + D
            try:
                D长度 = int(150 * D / KandD)
            except:
                D长度 = 0
            K长度 = 150 - D长度
            KD_K = Image.new('RGB', [K长度, 10], '#03A9F4')
            KD_D = Image.new('RGB', [D长度, 10], '#E8786E')
            activityRaw.paste(KD_K, (490, 135+100*i))
            activityRaw.paste(KD_D, (490 + K长度, 135+100*i))
            w, h = KD字体_战绩.getsize(f'{KD}')
            draw.text([640-w, 90+i*100],
                      f'{KD}',
                      font=KD字体_战绩,
                      fill='white'
                      )
            draw.text([490, 150+i*100],
                      f'KD',
                      font=KD标题字体_战绩,
                      fill='white'
                      )

            try:
                if Score > teamScore:
                    teamScore = Score
                Score长度 = int(150 * Score / teamScore)
            except:
                Score长度 = 150
            其他Score长度 = 150 - Score长度
            我score = Image.new('RGB', [Score长度, 10], '#03A9F4')
            其他score = Image.new('RGB', [其他Score长度, 10], '#E8786E')
            activityRaw.paste(我score, (670, 135+100*i))
            activityRaw.paste(其他score, (670 + Score长度, 135+100*i))
            w, h = KD字体_战绩.getsize(f'{ScoreShow}')
            draw.text([820-w, 90+i*100],
                      f'{ScoreShow}',
                      font=KD字体_战绩,
                      fill='white'
                      )
            draw.text([670, 150+i*100],
                      f'SCORE',
                      font=KD标题字体_战绩,
                      fill='white'
                      )

            # draw.text([700,90+i*100],
            #     f'{Score}',
            #     font=KD字体_战绩,
            #     fill='white'
            #     )
            # draw.text([700,135+i*100],
            #     f'SCORE',
            #     font=KD标题字体_战绩,
            #     fill='white'
            #     )
            draw.text([850, 90+i*100],
                      f"{activity['className']}",
                      font=KD字体_战绩,
                      fill='white'
                      )
            draw.text([850, 135+i*100],
                      f'CHARACTER',
                      font=KD标题字体_战绩,
                      fill='white'
                      )

            if activity['activityDetails']['mode'] == 6:
                continue

            if 'standing' in activity['values']:
                if activity['values']['standing']['basic']['displayValue'] == 'Victory':
                    activityRaw.paste(绿块, (0, 80 + 100 * i))
                elif activity['values']['standing']['basic']['displayValue'] == 'Defeat':
                    activityRaw.paste(红块, (0, 80 + 100 * i))
                else:
                    if activity['values']['standing']['basic']['value'] <= 2:
                        activityRaw.paste(绿块, (0, 80 + 100 * i))
                    else:
                        activityRaw.paste(红块, (0, 80 + 100 * i))

            else:
                if activity['values']['completed']['basic']['displayValue'] == 'Yes':
                    if activity['values']['completionReason']['basic']['displayValue'] == 'Failed':
                        activityRaw.paste(红块, (0, 80 + 100 * i))
                        continue

                    activityRaw.paste(绿块, (0, 80 + 100 * i))

                else:
                    activityRaw.paste(红块, (0, 80 + 100 * i))

        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'activit_{name}.png')
        activityRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(append)
    except Exception as e:
        await session.send(f'{e}', at_sender=True)

eloModeDict = {"control": "占领",
               "iron-banner": "铁骑",
               "pvecomp_gambit": "智谋",
               "allMayhem": "鏖战",
               "trials_of_osiris": "试炼",
               "elimination": "灭绝",
               "survival": "生存",
               "clash": "死斗",
               "rumble": "混战",
               "momentum": "趋势"}


async def GetEloDict(membershiptype, membershipid):
    url = f'https://api.tracker.gg/api/v2/destiny-2/standard/profile/{membershiptype}/{membershipid}/segments/playlist?season=14'
    async with aiohttp.request("GET", url) as r:
        # 或者直接await r.read()不编码，直接读取，适合于图像等无法编码文件
        response = await r.text(encoding="utf-8")
    info = json.loads(response)
    info = info['data']
    eloDict = {}
    for i in info:
        try:
            模式 = eloModeDict[i['attributes']['playlist']]
        except:
            continue
        Elo颜色 = eval(i['stats']['elo']['metadata']['rankColor']
                     ['value'].replace('rgb(', '').replace(')', ''))
        Elo分 = i['stats']['elo']['displayValue']
        if not (Elo排名 := i['stats']['elo']['rank']):
            Elo排名 = 999999

        if not (Elo排名百分比 := i['stats']['elo']['percentile']):
            Elo排名百分比 = 0
        Elo段位 = i['stats']['elo']['metadata']['rankName'].replace('Diamond', '钻石').replace(
            'Platinum', '白金').replace('Gold', '黄金').replace('Silver', '白银').replace('Bronze', '青铜')
        Elo段位名称 = Elo段位[:2]
        胜利 = i['stats']['activitiesWon']['value']
        失败 = i['stats']['activitiesLost']['value']
        胜率 = i['stats']['wl']['displayValue']
        K = i['stats']['kills']['value']
        D = i['stats']['deaths']['value']
        A = i['stats']['assists']['value']
        KD = i['stats']['kd']['displayValue']
        KDA = i['stats']['kda']['displayValue']
        KAD = i['stats']['kad']['displayValue']
        eloDict[模式] = {
            'Elo颜色': Elo颜色,
            'Elo分': Elo分,
            'Elo排名': Elo排名,
            'Elo排名百分比': Elo排名百分比,
            'Elo段位': Elo段位,
            'Elo段位名称': Elo段位名称,
            '胜利': 胜利,
            '失败': 失败,
            '胜率': 胜率,
            'K': K,
            'D': D,
            'A': A,
            'KD': KD,
            'KDA': KDA,
            'KAD': KAD
        }
    return eloDict


标题 = ImageFont.truetype('思源黑体B.otf', size=20)
模式 = ImageFont.truetype('思源黑体B.otf', size=26)
描述文本 = ImageFont.truetype('数字字体.ttf', size=20)
段位 = ImageFont.truetype('Dengb.ttf', size=18)
Elo分 = ImageFont.truetype('数字字体.ttf', size=26)
标题文字 = '#CCCCCC'
奇数颜色 = '#292929'
偶数颜色 = '#1F1F1F'
排行白色 = '#B7B7B7'
排行灰色 = '#545454'
奇数背景 = Image.new('RGB', [1200, 80], 奇数颜色)
偶数背景 = Image.new('RGB', [1200, 80], 偶数颜色)


@ on_command('ELO', aliases=('Elo', 'elo'), only_to_me=False)
async def Elo(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [])
        args = info['profile']['data']['userInfo']['displayName']
        membershiptype = info['profile']['data']['userInfo']['membershipType']
        membershipid = info['profile']['data']['userInfo']['membershipId']
        eloDict = await GetEloDict(membershiptype, membershipid)
        eloDictLength = len(eloDict)
        img_elo = Image.new('RGB', [1050, 100+eloDictLength*80], '#303030')
        draw = ImageDraw.Draw(img_elo)
        标题块 = Image.new('RGB', [1200, 40], '#3D3D3D')
        img_elo.paste(标题块, (0, 60))
        draw.text((50, 20), f'小日向Elo查询：{args}',
                  font=模式, fill=标题文字, direction=None)
        draw.text((60, 70), f'模式/段位', font=标题, fill=标题文字, direction=None)
        draw.text((300, 70), f'排名', font=标题, fill=标题文字, direction=None)
        draw.text((550, 70), f'K/D', font=标题, fill=标题文字, direction=None)
        draw.text((800, 70), f'胜率 %', font=标题, fill=标题文字, direction=None)
        keysList = list(eloDict.keys())
        for i in range(eloDictLength):
            模式名称 = keysList[i]
            try:
                mode = eloDict[模式名称]
            except:
                continue
            Elo分数 = mode['Elo分']
            Elo排名 = "{:,}".format(mode['Elo排名'])
            Elo段位 = mode['Elo段位']
            Elo段位名称 = mode['Elo段位名称']
            段位图片 = Image.open(f'{Elo段位名称} (自定义).png')
            Elo颜色 = mode['Elo颜色']
            Elo排名百分比 = mode['Elo排名百分比']
            K = int(mode['K'])
            D = int(mode['D'])
            KD = mode['KD']
            胜利 = int(mode['胜利'])
            失败 = int(mode['失败'])
            胜率 = mode['胜率']
            if i % 2 == 0:
                img_elo.paste(偶数背景, (0, 100 + 80 * i))
                段位图片 = Image.composite(段位图片, Image.new(
                    'RGB', 段位图片.size, 偶数颜色), 段位图片)
            else:
                img_elo.paste(奇数背景, (0, 100 + 80 * i))
                段位图片 = Image.composite(段位图片, Image.new(
                    'RGB', 段位图片.size, 奇数颜色), 段位图片)
            img_elo.paste(段位图片, (60, 105+80*i))

            draw.text((135, 130+80*i), f'{模式名称}',
                      font=模式, fill='white', direction=None)
            draw.text((200, 135+80*i), f'{Elo段位}',
                      font=段位, fill=Elo颜色, direction=None)
            灰高 = int((100 - Elo排名百分比) * 0.6)
            白高 = 60-灰高
            Rating灰 = Image.new('RGB', [10, 灰高], 排行灰色)
            Rating白 = Image.new('RGB', [10, 白高], 排行白色)
            img_elo.paste(Rating灰, (300, 110+80*i))
            img_elo.paste(Rating白, (300, 110 + 灰高+80*i))
            draw.text((320, 115 + 80 * i), f'{Elo分数}',
                      font=Elo分, fill='white', direction=None)
            if Elo排名百分比 >= 70:
                temp = round(100-Elo排名百分比, 1)
                Elo排名描述性 = f'Top {temp}%'

            else:
                Elo排名描述性 = f'Bottom {Elo排名百分比}%'

            draw.text((320, 145+80*i), f'#{Elo排名} • {Elo排名描述性}',
                      font=描述文本, fill='#FCD401' if Elo排名百分比 >= 90 else '#C3C3C3', direction=None)
            绿色 = '#3D8D4D'
            红色 = '#8F2020'
            KandD = K + D
            try:
                K长度 = int(200 * K / KandD)
            except:
                K长度 = 0
            D长度 = 200 - K长度
            KD_K = Image.new('RGB', [K长度, 10], 绿色)
            KD_D = Image.new('RGB', [D长度, 10], 红色)
            img_elo.paste(KD_K, (550, 150+80*i))
            img_elo.paste(KD_D, (550 + K长度, 150+80*i))
            draw.text((550, 115+80*i), f'{KD}',
                      font=Elo分, fill='white', direction=None)
            draw.text((630, 120+80*i), f'({K} - {D})',
                      font=描述文本, fill='#C3C3C3', direction=None)
            WandL = 胜利+失败
            try:
                W长度 = int(200 * 胜利 / WandL)
            except:
                W长度 = 0
            L长度 = 200 - W长度
            WL_W = Image.new('RGB', [W长度, 10], 绿色)
            WL_L = Image.new('RGB', [L长度, 10], 红色)
            img_elo.paste(WL_W, (800, 150+80*i))
            img_elo.paste(WL_L, (800 + W长度, 150+80*i))
            draw.text((800, 115+80*i), f'{胜率}',
                      font=Elo分, fill='white', direction=None)
            draw.text((875, 120+80*i), f'({胜利} - {失败})',
                      font=描述文本, fill='#C3C3C3', direction=None)

        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'elo_{name}.png')
        img_elo.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except KeyError as err:
        await session.send(f'Tracker服务器繁忙，请两分钟后再试\n{err}', at_sender=True)
    except Exception as e:
        await session.send(f'{e}', at_sender=True)


#3711931140
#3881495763 
#1485585878


RAID_LIST = ['玻璃拱顶：大师','玻璃拱顶：传说','深岩墓室', '救赎花园', '最后一愿', '忧愁王冠', '往日之苦', '星之塔：巅峰',
             '利维坦：巅峰', '世界吞噬者：巅峰', '星之塔：普通', '世界吞噬者：普通', '利维坦：普通']
FLAWLESS_DICT = {
    6: 'Flawless',
    5: 'Flawless',
    4: 'Flawless',
    3: 'Flawless Trio',
    2: 'Flawless Duo',
    1: 'Solo Flawless'}
LOWMAN_DICT = {
    3: 'Trio',
    2: 'Duo',
    1: 'Solo'}

TAG_COLOR_DICT = {
    'Flawless': '#31b573',
    'Flawless Trio': '#FA576F',
    'Flawless Duo': '#FA576F',
    'Solo Flawless': '#FA576F',
    'Trio': '#ea68a2',
    'Duo': '#ea68a2',
    'Solo': '#00709e',
    'Day One':'#80009C',
    'Day One Challenge':'#7964FF'
}


RAID_NAEM_DICT = {
    '玻璃拱顶: 传说':'玻璃拱顶：传说',
    '玻璃拱顶: 大师':'玻璃拱顶：大师',
    '玻璃拱顶':'玻璃拱顶：传说',
    '玻璃拱顶：挑战模式':'玻璃拱顶：传说',
    '深岩墓室': '深岩墓室',
    '最后一愿: 等级55': '最后一愿',
    '最后一愿: 普通': '最后一愿',
    '救赎花园': '救赎花园',
    '往日之苦': '往日之苦',
    '忧愁王冠: 普通': '忧愁王冠',
    '利维坦: 巅峰': '利维坦：巅峰',
    '利维坦: 普通': '利维坦：普通',
    '利维坦，星之塔: 普通': '星之塔：普通',
    '利维坦，星之塔': '星之塔：普通',
    '利维坦，星之塔: 巅峰': '星之塔：巅峰',
    '世界吞噬者，利维坦: 巅峰': '世界吞噬者：巅峰',
    '世界吞噬者，利维坦: 普通': '世界吞噬者：普通',
    '世界吞噬者，利维坦': '世界吞噬者：普通',
    '利维坦': '利维坦：普通'}


def get_Activities_lowest_accountCount(Activities: list) -> int:
    accountCount = 6
    for j in Activities:
        accountCount = [accountCount, j['accountCount']
                        ][j['accountCount'] < accountCount]
    return accountCount


async def add_raid_data_dict(all_raid_data_dict: dict, single_raid_data_dict: dict):
    activity_hash = single_raid_data_dict['activityHash']
    activity_name_info = await destiny.decode_hash(activity_hash, 'DestinyActivityDefinition')
    activity_name = RAID_NAEM_DICT[activity_name_info['displayProperties']['name']]

    data_values = single_raid_data_dict['values']
    if activity_name in all_raid_data_dict:
        raid_now_dict = all_raid_data_dict[activity_name]
        raid_now_dict['clears'] += data_values['clears']
        raid_now_dict['fullClears'] += data_values['fullClears']
        raid_now_dict['sherpaCount'] += data_values['sherpaCount']
        if 'fastestFullClear' in data_values:
            if not ('fastestFullClear' in raid_now_dict) or (raid_now_dict['fastestFullClear'] > data_values['fastestFullClear']['value']):
                raid_now_dict['fastestFullClear'] = data_values['fastestFullClear']['value']
        if 'bestPlayerCountDetails' in data_values:
            accountCount = data_values['bestPlayerCountDetails']['accountCount']
            if not ('bestPlayerCountDetails' in raid_now_dict) or (accountCount < raid_now_dict['bestPlayerCountDetails']):
                raid_now_dict['bestPlayerCountDetails'] = accountCount
        if 'lowAccountCountActivities' in data_values:
            accountCount = get_Activities_lowest_accountCount(
                data_values['lowAccountCountActivities']
            )
            if not ('lowAccountCountActivities' in raid_now_dict) or (accountCount < raid_now_dict['lowAccountCountActivities']):
                raid_now_dict['lowAccountCountActivities'] = accountCount
        if 'flawlessActivities' in data_values:
            # raid_now_dict['flawlessActivities']
            accountCount = get_Activities_lowest_accountCount(
                data_values['flawlessActivities']
            )
            if not ('flawlessActivities' in raid_now_dict) or (accountCount < raid_now_dict['flawlessActivities']):
                raid_now_dict['flawlessActivities'] = accountCount
    else:
        all_raid_data_dict[activity_name] = {
            'clears': data_values['clears'],
            'fullClears': data_values['fullClears'],
            'sherpaCount': data_values['sherpaCount'],
            'fastestFullClear': data_values['fastestFullClear']['value'] if 'fastestFullClear' in data_values else 0,
        }
        if 'bestPlayerCountDetails' in data_values:
            all_raid_data_dict[activity_name]['bestPlayerCountDetails'] = data_values['bestPlayerCountDetails']['accountCount']
        if 'lowAccountCountActivities' in data_values:
            all_raid_data_dict[activity_name]['lowAccountCountActivities'] = get_Activities_lowest_accountCount(
                data_values['lowAccountCountActivities']
            )
        if 'flawlessActivities' in data_values:
            all_raid_data_dict[activity_name]['flawlessActivities'] = get_Activities_lowest_accountCount(
                data_values['flawlessActivities']
            )


突袭_奇数颜色 = '#292929'
突袭_偶数颜色 = '#1F1F1F'
突袭_奇数背景 = Image.new('RGB', [700, 120], '#292929')
突袭_偶数背景 = Image.new('RGB', [700, 120], '#1F1F1F')


玻璃拱顶大师_ = Image.open(f'玻璃拱顶.png')
玻璃拱顶_ = Image.open(f'玻璃拱顶.png')
深岩墓室_ = Image.open(f'深岩墓室.png')
救赎花园_ = Image.open(f'救赎花园.png')
最后一愿_ = Image.open(f'最后一愿.png')
忧愁王冠_ = Image.open(f'忧愁王冠.png')
往日之苦_ = Image.open(f'往日之苦.png')
星之塔巅峰_ = Image.open(f'星之塔：巅峰.png')
世界吞噬者巅峰_ = Image.open(f'世界吞噬者：巅峰.png')
利维坦巅峰_ = Image.open(f'利维坦：巅峰.png')
星之塔普通_ = Image.open(f'星之塔：普通.png')
世界吞噬者普通_ = Image.open(f'世界吞噬者：普通.png')
利维坦普通_ = Image.open(f'利维坦：普通.png')
raid双榜图_ = Image.open(f'raid双榜图 (自定义).png')


RAID_IMAGE = {
    '玻璃拱顶：大师':玻璃拱顶大师_,
    '玻璃拱顶：传说':玻璃拱顶_,
    '深岩墓室': 深岩墓室_,
    '救赎花园': 救赎花园_,
    '最后一愿': 最后一愿_,
    '忧愁王冠': 忧愁王冠_,
    '往日之苦': 往日之苦_,
    '星之塔：巅峰': 星之塔巅峰_,
    '世界吞噬者：巅峰': 世界吞噬者巅峰_,
    '利维坦：巅峰': 利维坦巅峰_,
    '星之塔：普通': 星之塔普通_,
    '世界吞噬者：普通': 世界吞噬者普通_,
    '利维坦：普通': 利维坦普通_
}

突袭_绿色 = '#31b573'
突袭_蓝色 = '#00709e'
突袭_橙色 = '#f4b757'
突袭_青色 = '#3eb8b4'
_深岩墓室 = ImageFont.truetype('思源黑体B.otf', size=24)
_导师次数 = ImageFont.truetype('思源黑体B.otf', size=16)
_FlawlessDuo = ImageFont.truetype('思源黑体B.otf', size=13)
_段位文字 = ImageFont.truetype('思源黑体B.otf', size=18)

TIER_COLOR = {
    'Challenger': '#FA576F',
    'Master': '#FA576F',
    'Diamond': '#048AB4',
    'Platinum': '#04B1A1',
    'Gold': '#FABC44',
    'Silver': '#9EA3B0',
    'Bronze': '#6A5B3F'
}

RAID_FLAWLESS_DICT = {
    '深岩墓室': '3560923614',
    '救赎花园': '1522774125',
    '最后一愿': '380332968',
    '忧愁王冠': '3292013042',
    '往日之苦': '2925485370',
}

RAID_DAYONE_DICT = {
    '玻璃拱顶：传说':'2384429092',
    '忧愁王冠':'3292013044',
    '深岩墓室':'2699580344'
}


def get_time_text(secondes):
    if secondes > 0:
        m, s = divmod(secondes, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = f'{m}m {s}s'
        else:
            time = f'{h}h {m}m {s}s'
        return time
    else:
        return '无'

def get_record_state_completion(state):
    RecordRedeemed = (state & 1) > 0
    ObjectiveNotCompleted = (state & 4) > 0
    if RecordRedeemed:
        return True
    if not ObjectiveNotCompleted:
        return True
    return False


vogNormalRaidWorldFirstDict = read_json('vogNormalRaidWorldFirstDict.json')
vogChallengeRaidWorldFirstDict = read_json('vogChallengeRaidWorldFirstDict.json')

def get_vogNormalRaid_worldFirst_from_dict(membershipId:str):
    if not isinstance(membershipId,str):
        membershipId = str(membershipId)
    if membershipId in vogNormalRaidWorldFirstDict:
        return vogNormalRaidWorldFirstDict[membershipId]
    else:
        return False

def get_vogChallengeRaid_worldFirst_from_dict(membershipId:str):
    if not isinstance(membershipId,str):
        membershipId = str(membershipId)
    if membershipId in vogChallengeRaidWorldFirstDict:
        return vogChallengeRaidWorldFirstDict[membershipId]
    else:
        return False

def get_dayOne_tag(tag_list: list, records: dict, raidname: str,membershipId):
    if raidname not in RAID_DAYONE_DICT:
        return

    record_id = RAID_DAYONE_DICT[raidname]
    print(raidname)
    if raidname == '玻璃拱顶：传说':
        for value in records['characterRecords']['data'].values():
            characterRecords = value['records']
            state = characterRecords[record_id]['state']
            subCompletion = characterRecords[record_id]['objectives'][0]['complete']
            recordCompltion = get_record_state_completion(state)
            if (rank := get_vogChallengeRaid_worldFirst_from_dict(membershipId)):
                tag_list.append(f'Day One Challenge#{rank}')
                return
            else:
                if (rank := get_vogNormalRaid_worldFirst_from_dict(membershipId)):
                    tag_list.append(f'Day One#{rank}')
            return
        
    else:
        state = records['profileRecords']['data']['records'][record_id]['state']
    
    RecordRedeemed = (state & 1) > 0
    ObjectiveNotCompleted = (state & 4) > 0
    if RecordRedeemed:
        tag_list.append('Day One')
        return
    if not ObjectiveNotCompleted:
        tag_list.append('Day One')
        return


def get_flawless_tag(tag_list: list, records: dict, raidname: str):
    if raidname not in RAID_FLAWLESS_DICT:
        return

    for tag in tag_list:
        if 'Flawless' in tag:
            return

    record_id = RAID_FLAWLESS_DICT[raidname]
    state = records[record_id]['state']
    RecordRedeemed = (state & 1) > 0
    ObjectiveNotCompleted = (state & 4) > 0
    if RecordRedeemed:
        tag_list.append('Flawless')
        return
    if not ObjectiveNotCompleted:
        tag_list.append('Flawless')
        return


@ on_command('突袭', aliases=('raid', 'RAID', 'Raid'), only_to_me=False)
async def get_raid(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [900])
        args = info['profile']['data']['userInfo']['displayName']
        profileRecords = info['profileRecords']['data']['records']
        characterRecords = info['characterRecords']['data']
        membershipid = info['profile']['data']['userInfo']['membershipId']
        url = f'https://b9bv2wd97h.execute-api.us-west-2.amazonaws.com/prod/api/player/{membershipid}'
        async with aiohttp.request("GET", url) as r:
            response = await r.text(encoding="utf-8")
        raid_info = json.loads(response)
        try:
            raid_info = raid_info['response']
        except:
            raise Exception(f'唉...你好像没有打过突袭噢，快跟小伙伴去试试吧！')

        speed_value = get_time_text(raid_info['speedRank']['value'])
        speed_tier = raid_info['speedRank']['tier']
        speed_subtier = raid_info['speedRank']['subtier'] \
            if 'subtier' in raid_info['speedRank'] else ''
        img_speed = Image.new(
            'RGB', [200, 80], TIER_COLOR[speed_tier])
        raid双榜图speed_ = Image.composite(raid双榜图_, Image.new(
            'RGB', raid双榜图_.size, TIER_COLOR[speed_tier]), raid双榜图_)

        clears_value = raid_info['clearsRank']['value']
        clears_tier = raid_info['clearsRank']['tier']
        clears_subtier = raid_info['clearsRank']['subtier'] \
            if 'subtier' in raid_info['clearsRank'] else ''
        img_clears = Image.new(
            'RGB', [200, 80], TIER_COLOR[clears_tier])
        raid双榜图clears_ = Image.composite(raid双榜图_, Image.new(
            'RGB', raid双榜图_.size, TIER_COLOR[clears_tier]), raid双榜图_)

        raid_data_dict = {}
        for i in raid_info['activities']:
            await add_raid_data_dict(raid_data_dict, i)

        raid_data_dict_len = len(raid_data_dict)
        img_raid = Image.new(
            'RGB', [700, 120 + raid_data_dict_len * 120], '#303030')
        draw = ImageDraw.Draw(img_raid)
        draw.text([40, 20], f'小日向Raid查询', '#CCCCCC', _深岩墓室)
        draw.text([40, 65], f'{args}', 'white', _深岩墓室)
        img_raid.paste(img_clears, (260, 20))
        img_raid.paste(img_speed, (480, 20))
        img_raid.paste(raid双榜图clears_, (260, 30))
        img_raid.paste(raid双榜图speed_, (480, 30))

        draw.text([320, 27], f'Full Clears Rank', 'white', _FlawlessDuo)
        draw.text([320, 50], f'{clears_tier} {clears_subtier}', 'white', _段位文字)
        draw.text([320, 75], f'{clears_value}', 'white', _FlawlessDuo)

        draw.text([540, 27], f'Speed Rank', 'white', _FlawlessDuo)
        draw.text([540, 50], f'{speed_tier} {speed_subtier}', 'white', _段位文字)
        draw.text([540, 75], f'{speed_value}', 'white', _FlawlessDuo)

        i = 0
        for raidname in RAID_LIST:
            if raidname not in raid_data_dict:
                continue

            tag_list = []
            raid_now_dict = raid_data_dict[raidname]
            clears = raid_now_dict['clears']
            fullClears = raid_now_dict['fullClears']
            sherpaCount = raid_now_dict['sherpaCount']
            fastestFullClear = get_time_text(raid_now_dict['fastestFullClear'])
            if 'flawlessActivities' in raid_now_dict:
                flawlessActivities = raid_now_dict['flawlessActivities']
            else:
                flawlessActivities = 0

            if 'lowAccountCountActivities' in raid_now_dict:
                lowAccountCountActivities = raid_now_dict['lowAccountCountActivities']
            else:
                lowAccountCountActivities = 0

            if flawlessActivities and lowAccountCountActivities:
                if flawlessActivities == lowAccountCountActivities:
                    tag_list.append(FLAWLESS_DICT[flawlessActivities])
                else:
                    if flawlessActivities:
                        tag_list.append(FLAWLESS_DICT[flawlessActivities])
                    if lowAccountCountActivities:
                        tag_list.append(LOWMAN_DICT[lowAccountCountActivities])
            else:
                if flawlessActivities:
                    tag_list.append(FLAWLESS_DICT[flawlessActivities])
                if lowAccountCountActivities:
                    tag_list.append(LOWMAN_DICT[lowAccountCountActivities])
            get_flawless_tag(tag_list, profileRecords, raidname)
            get_dayOne_tag(tag_list,info,raidname,str(membershipid))

            突袭原图片 = RAID_IMAGE[raidname]
            if i % 2 == 0:
                img_raid.paste(突袭_偶数背景, (0, 120 + 120 * i))
                突袭图片 = Image.composite(突袭原图片, Image.new(
                    'RGB', 突袭原图片.size, 突袭_偶数颜色), 突袭原图片)
            else:
                img_raid.paste(突袭_奇数背景, (0, 120 + 120 * i))
                突袭图片 = Image.composite(突袭原图片, Image.new(
                    'RGB', 突袭原图片.size, 突袭_奇数颜色), 突袭原图片)
            img_raid.paste(突袭图片, (10, 10 + 120 + 120 * i))
            draw.text([290, 15 + 120 + 120 * i], f'{raidname}', 'white', _深岩墓室)
            draw.text([290, 2+35+15 + 120 + 120 * i],
                      f'导师：{sherpaCount}次', 突袭_橙色, _导师次数)
            draw.text([290, 30 + 35 + 15 + 120 + 120 * i],
                      f'最快：{fastestFullClear}', 突袭_青色, _导师次数)
            全程次数 = fullClears
            完成次数 = clears
            全程长度 = int(全程次数 / 完成次数 * 200)
            if 全程长度:
                全程 = Image.new('RGB', [全程长度, 10], 突袭_绿色)
                完成 = Image.new('RGB', [200-全程长度, 10], 突袭_蓝色)
                img_raid.paste(全程, (450, 80 + 120 + 120 * i))
                img_raid.paste(完成, (450+全程长度, 80 + 120 + 120 * i))
            else:
                完成 = Image.new('RGB', [200, 10], 突袭_蓝色)
                img_raid.paste(完成, (450, 80 + 120 + 120 * i))
            draw.text([450, 50 + 120 + 120 * i],
                      f'{全程次数} - {完成次数}', '#dadada', _深岩墓室)
            draw.text([575, 95 + 120 + 120 * i], '全程 - 完成', '#dadada', _导师次数)

            height = 5
            for tag in tag_list:
                temp = tag.split('#')[0]
                w, h = _FlawlessDuo.getsize(tag)
                tag颜色 = TAG_COLOR_DICT[temp]
                底色 = Image.new('RGB', [w + 4, h + 4], tag颜色)
                img_raid.paste(底色, (250 - w, height + 15 + 120 + 120 * i))
                draw.text([250 - w+2, height + 15 + 120 + 120 * i+1],
                          f'{tag}', 'white', _FlawlessDuo)
                height += 25
            i += 1

        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'raid_{name}.png')
        img_raid.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)
    except Exception as err:
        await session.send(f'{err}', at_sender=True)

DUNGEON_NAEM_DICT = {
    '异域任务：前兆: 大师': '前兆: 大师',
    '异域任务：前兆: 普通': '前兆: 普通',
    '先知': '先知',
    '预言': '预言',
    '异端深渊: 普通': '异端深渊',
    '破碎王座': '破碎王座',
    '行动时刻（英雄）': '行动时刻: 英雄',
    '行动时刻': '行动时刻: 普通',
    '冥冥低语（英雄模式）': '冥冥低语: 英雄',
    '冥冥低语': '冥冥低语: 普通'
}

DUNGEON_NAEM_LIST = list(DUNGEON_NAEM_DICT.values())


async def add_dungeon_data_dict(all_dungeon_data_dict, i):
    dungeonHash = i['activityHash']
    dungeonNameInfo = await destiny.decode_hash(dungeonHash, 'DestinyActivityDefinition')
    try:
        dungeonName = DUNGEON_NAEM_DICT[dungeonNameInfo['displayProperties']['name']]
    except Exception as e:
        raise Exception(f'某个数据丢失，请及时联系小日向开发者，感谢🤞\n{e}')
    data_values = i['values']
    if dungeonName in all_dungeon_data_dict:
        dungeon_now_dict = all_dungeon_data_dict[dungeonName]
        dungeon_now_dict['clears'] += data_values['clears']
        dungeon_now_dict['fullClears'] += data_values['fullClears']
        dungeon_now_dict['sherpaCount'] += data_values['sherpaCount']
        if 'fastestFullClear' in data_values:
            if not ('fastestFullClear' in dungeon_now_dict) or (dungeon_now_dict['fastestFullClear'] > data_values['fastestFullClear']['value']):
                dungeon_now_dict['fastestFullClear'] = data_values['fastestFullClear']['value']
        if 'bestPlayerCountDetails' in data_values:
            accountCount = data_values['bestPlayerCountDetails']['accountCount']
            if not ('bestPlayerCountDetails' in dungeon_now_dict) or (accountCount < dungeon_now_dict['bestPlayerCountDetails']):
                dungeon_now_dict['bestPlayerCountDetails'] = accountCount
        if 'lowAccountCountActivities' in data_values:
            accountCount = get_Activities_lowest_accountCount(
                data_values['lowAccountCountActivities']
            )
            if not ('lowAccountCountActivities' in dungeon_now_dict) or (accountCount < dungeon_now_dict['lowAccountCountActivities']):
                dungeon_now_dict['lowAccountCountActivities'] = accountCount
        if 'flawlessActivities' in data_values:
            # dungeon_now_dict['flawlessActivities']
            accountCount = get_Activities_lowest_accountCount(
                data_values['flawlessActivities']
            )
            if not ('flawlessActivities' in dungeon_now_dict) or (accountCount < dungeon_now_dict['flawlessActivities']):
                dungeon_now_dict['flawlessActivities'] = accountCount
    else:
        all_dungeon_data_dict[dungeonName] = {
            'clears': data_values['clears'],
            'fullClears': data_values['fullClears'],
            'sherpaCount': data_values['sherpaCount'],
            'fastestFullClear': data_values['fastestFullClear']['value'] if 'fastestFullClear' in data_values else 0,
        }
        if 'bestPlayerCountDetails' in data_values:
            all_dungeon_data_dict[dungeonName]['bestPlayerCountDetails'] = data_values['bestPlayerCountDetails']['accountCount']
        if 'lowAccountCountActivities' in data_values:
            all_dungeon_data_dict[dungeonName]['lowAccountCountActivities'] = get_Activities_lowest_accountCount(
                data_values['lowAccountCountActivities']
            )
        if 'flawlessActivities' in data_values:
            all_dungeon_data_dict[dungeonName]['flawlessActivities'] = get_Activities_lowest_accountCount(
                data_values['flawlessActivities']
            )


DUNGEON_APPEND_DICT = {
    '异端深渊': {'Solo Flawless': '3950599483',
             'Solo': '3841336511',
             'Flawless': '245952203', },
    '破碎王座': {'Solo Flawless': '3205009787',
             'Solo': '3899996566',
             'Flawless': '1178448425', },
    '先知': {'Solo Flawless': '3047181179',
           'Solo': '3657275647',
           'Flawless': '2902814383'},
    '预言': {'Solo Flawless': '3191784400',
           'Solo': '3002642730',
           'Flawless': '2010041484'},
    '前兆: 大师': {'Flawless': '2335417976'},
    '前兆: 普通': {'Solo Flawless': '4206923617'}
}


def append_method(state: int, typeName: str, tag_list: list):

    RecordRedeemed = (state & 1) > 0
    ObjectiveNotCompleted = (state & 4) > 0
    if RecordRedeemed:
        tag_list.append(typeName)
        return
    if not ObjectiveNotCompleted:
        tag_list.append(typeName)
        return


def dungeon_tag_append(tag_list: list, records: dict, dungeonName: str):
    if dungeonName not in DUNGEON_APPEND_DICT:
        return

    if dungeonName != '先知':
        records = records['profileRecords']['data']['records']
    else:
        characterid = list(records['characterRecords']['data'].keys())
        characterid = characterid[0]
        records = records['characterRecords']['data'][characterid]['records']

    for tag in tag_list:
        if 'Solo Flawless' in tag:
            return

    for typeName, record_id in DUNGEON_APPEND_DICT[dungeonName].items():
        if typeName == 'Falwless Solo':
            state = records[record_id]['state']
            append_method(state, typeName, tag_list)
            return

        if typeName in tag_list:
            continue
        else:
            state = records[record_id]['state']
            append_method(state, typeName, tag_list)


前兆大师_ = Image.open(f'前兆大师.png')
前兆普通_ = Image.open(f'前兆大师.png')
先知_ = Image.open(f'先知.png')
预言_ = Image.open(f'预言.png')
异端深渊_ = Image.open(f'异端深渊.png')
破碎王座_ = Image.open(f'破碎王座.png')
行动时刻英雄_ = Image.open(f'行动时刻英雄.png')
行动时刻普通_ = Image.open(f'行动时刻英雄.png')
冥冥低语英雄_ = Image.open(f'冥冥低语英雄.png')
冥冥低语普通_ = Image.open(f'冥冥低语英雄.png')


DUNGEON_IMAGE = {
    '前兆: 大师': 前兆大师_,
    '前兆: 普通': 前兆普通_,
    '先知': 先知_,
    '预言': 预言_,
    '异端深渊': 异端深渊_,
    '破碎王座': 破碎王座_,
    '行动时刻: 英雄': 行动时刻英雄_,
    '行动时刻: 普通': 行动时刻普通_,
    '冥冥低语: 英雄': 冥冥低语英雄_,
    '冥冥低语: 普通': 冥冥低语普通_
}


@ on_command('地牢', aliases=('地牢查询'), only_to_me=False)
async def get_player_dungeon_info(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [900])
        args = info['profile']['data']['userInfo']['displayName']
        membershipid = info['profile']['data']['userInfo']['membershipId']
        url = f'https://bolskmfp72.execute-api.us-west-2.amazonaws.com/dungeon/api/player/{membershipid}'
        async with aiohttp.request("GET", url) as r:
            response = await r.text(encoding="utf-8")
        dungeon_raw_data = json.loads(response)
        if 'response' not in dungeon_raw_data:
            raise Exception('获取玩家信息失败，请检查输入的名称或尝试使用队伍码查询')
        if not (dungeon_raw_data := dungeon_raw_data['response']):
            raise Exception('获取玩家信息失败，请检查输入的名称或尝试使用队伍码查询')

        clears_value = dungeon_raw_data['clearsRank']['value']
        clears_tier = dungeon_raw_data['clearsRank']['tier']
        clears_subtier = dungeon_raw_data['clearsRank']['subtier'] \
            if 'subtier' in dungeon_raw_data['clearsRank'] else ''
        img_clears = Image.new(
            'RGB', [200, 80], TIER_COLOR[clears_tier])
        dungeon双榜图clears_ = Image.composite(raid双榜图_, Image.new(
            'RGB', raid双榜图_.size, TIER_COLOR[clears_tier]), raid双榜图_)

        speed_value = get_time_text(dungeon_raw_data['speedRank']['value'])
        speed_tier = dungeon_raw_data['speedRank']['tier']
        speed_subtier = dungeon_raw_data['speedRank']['subtier'] \
            if 'subtier' in dungeon_raw_data['speedRank'] else ''
        img_speed = Image.new(
            'RGB', [200, 80], TIER_COLOR[speed_tier])
        dungeon双榜图speed_ = Image.composite(raid双榜图_, Image.new(
            'RGB', raid双榜图_.size, TIER_COLOR[speed_tier]), raid双榜图_)

        dungeon_data_dict = {}
        for i in dungeon_raw_data['activities']:
            await add_dungeon_data_dict(dungeon_data_dict, i)

        dungeon_dictkeys_to_list = list(dungeon_data_dict.keys())
        dungeon_dict_length = len(dungeon_data_dict)
        img_dungeon = Image.new(
            'RGB', [700, 120 + dungeon_dict_length * 120], '#303030')
        draw = ImageDraw.Draw(img_dungeon)
        draw.text([40, 20], f'小日向地牢查询', '#CCCCCC', _深岩墓室)
        draw.text([40, 65], f'{args}', 'white', _深岩墓室)
        img_dungeon.paste(img_clears, (260, 20))
        img_dungeon.paste(img_speed, (480, 20))
        img_dungeon.paste(dungeon双榜图clears_, (260, 30))
        img_dungeon.paste(dungeon双榜图speed_, (480, 30))

        draw.text([320, 27], f'Full Clears Rank', 'white', _FlawlessDuo)
        draw.text([320, 50], f'{clears_tier} {clears_subtier}', 'white', _段位文字)
        draw.text([320, 75], f'{clears_value}', 'white', _FlawlessDuo)

        draw.text([540, 27], f'Speed Rank', 'white', _FlawlessDuo)
        draw.text([540, 50], f'{speed_tier} {speed_subtier}', 'white', _段位文字)
        draw.text([540, 75], f'{speed_value}', 'white', _FlawlessDuo)

        i = 0
        for dungenonName in DUNGEON_NAEM_LIST:
            if dungenonName not in dungeon_dictkeys_to_list:
                continue
            tag_list = []
            dungeon_now_dict = dungeon_data_dict[dungenonName]
            clears = dungeon_now_dict['clears']
            fullClears = dungeon_now_dict['fullClears']
            sherpaCount = dungeon_now_dict['sherpaCount']
            fastestFullClear = get_time_text(
                dungeon_now_dict['fastestFullClear'])
            if 'flawlessActivities' in dungeon_now_dict:
                flawlessActivities = dungeon_now_dict['flawlessActivities']
            else:
                flawlessActivities = 0

            if 'lowAccountCountActivities' in dungeon_now_dict:
                lowAccountCountActivities = dungeon_now_dict['lowAccountCountActivities']
            else:
                lowAccountCountActivities = 0

            if lowAccountCountActivities == 1 and flawlessActivities == lowAccountCountActivities:
                tag_list.append('Solo Flawless')
            else:
                if flawlessActivities:
                    tag_list.append('Flawless')
                if lowAccountCountActivities == 1:
                    tag_list.append('Solo')
            dungeon_tag_append(tag_list, info, dungenonName)

            地牢原图片 = DUNGEON_IMAGE[dungenonName]

            if i % 2 == 0:
                img_dungeon.paste(突袭_偶数背景, (0, 120 + 120 * i))
                地牢图片 = Image.composite(地牢原图片, Image.new(
                    'RGB', 地牢原图片.size, 突袭_偶数颜色), 地牢原图片)
            else:
                img_dungeon.paste(突袭_奇数背景, (0, 120 + 120 * i))
                地牢图片 = Image.composite(地牢原图片, Image.new(
                    'RGB', 地牢原图片.size, 突袭_奇数颜色), 地牢原图片)
            img_dungeon.paste(地牢图片, (10, 10 + 120 + 120 * i))
            draw.text([290, 15 + 120 + 120 * i],
                      f'{dungenonName}', 'white', _深岩墓室)
            draw.text([290, 2+35+15 + 120 + 120 * i],
                      f'导师：{sherpaCount}次', 突袭_橙色, _导师次数)
            draw.text([290, 30 + 35 + 15 + 120 + 120 * i],
                      f'最快：{fastestFullClear}', 突袭_青色, _导师次数)
            全程次数 = fullClears
            完成次数 = clears
            全程长度 = int(全程次数 / 完成次数 * 200)
            if 全程长度:
                全程 = Image.new('RGB', [全程长度, 10], 突袭_绿色)
                完成 = Image.new('RGB', [200-全程长度, 10], 突袭_蓝色)
                img_dungeon.paste(全程, (450, 80 + 120 + 120 * i))
                img_dungeon.paste(完成, (450+全程长度, 80 + 120 + 120 * i))
            else:
                完成 = Image.new('RGB', [200, 10], 突袭_蓝色)
                img_dungeon.paste(完成, (450, 80 + 120 + 120 * i))
            draw.text([450, 50 + 120 + 120 * i],
                      f'{全程次数} - {完成次数}', '#dadada', _深岩墓室)
            draw.text([575, 95 + 120 + 120 * i], '全程 - 完成', '#dadada', _导师次数)

            height = 5
            for tag in tag_list:
                w, h = _FlawlessDuo.getsize(tag)
                tag颜色 = TAG_COLOR_DICT[tag]
                底色 = Image.new('RGB', [w + 4, h + 4], tag颜色)
                img_dungeon.paste(底色, (250 - w, height + 15 + 120 + 120 * i))
                draw.text([250 - w+2, height + 15 + 120 + 120 * i+1],
                          f'{tag}', 'white', _FlawlessDuo)
                height += 25
            i += 1

        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'dungeon_{name}.png')
        img_dungeon.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'{e}', at_sender=True)


def Check_zhengzhang(info):
    completionDict = {}
    info_profile = info['profilePresentationNodes']['data']['nodes']
    info_character = info['characterPresentationNodes']['data']

    for name in 证章:
        completionDict[name] = {}
        for className in 证章[name]:
            nodeHashNum = str(证章[name][className])

            if name == '不朽赛季':
                for characterid in info_character:
                    characterRecords = info_character[characterid]['nodes']
                    if nodeHashNum in characterRecords:
                        progress = characterRecords[nodeHashNum]['objective']['progress']
                        completionValue = characterRecords[nodeHashNum]['objective']['completionValue']
                        completionDict[name][className] = {
                            'progress': progress, 'completionValue': completionValue}
                        break

                continue

            nodeHash = info_profile[nodeHashNum]
            if 'objective' in nodeHash:
                progress = info_profile[nodeHashNum]['objective']['progress']
                completionValue = info_profile[nodeHashNum]['objective']['completionValue']
            elif 'progressValue' in nodeHash:
                progress = nodeHash['progressValue']
                completionValue = nodeHash['completionValue']

            completionDict[name][className] = {
                'progress': progress, 'completionValue': completionValue}
    return completionDict


证章_root = os.path.join(os.getcwd(), 'res', 'destiny2', '证章')
标题_证章 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=20)
名字_证章 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=36)
数字_证章 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=40)
职业_证章 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=20)


奇数块_证章 = Image.new('RGB', [900, 160], "#292929")
偶数块_证章 = Image.new('RGB', [900, 160], '#1F1F1F')
镀金 = Image.new('RGB', [168, 104], '#FABC44')


@on_command('证章', only_to_me=False)
async def Check_zhengzhang_aync(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [700])
        args = info['profile']['data']['userInfo']['displayName']
        completionDict = Check_zhengzhang(info)
        证章_蓝色 = '#03A9F4'
        证章_红色 = '#E8786E'
        证章图 = Image.new('RGB', [900, 80+21*160], '#303030')
        draw = ImageDraw.Draw(证章图)

        draw.text((40, 20), f'小日向证章查询：{args}',
                  font=名字_证章, fill='white', direction=None)

        nameList = list(completionDict.keys())
        length = len(nameList)
        for i in range(length):
            name = nameList[i]
            completion = completionDict[name]
            证章图_path = os.path.join(证章_root, f'{name}.png')
            img = Image.open(证章图_path)

            if i % 2 == 0:
                证章图.paste(偶数块_证章, (0, 80+i*160))
            else:

                证章图.paste(奇数块_证章, (0, 80+i*160))
            draw.text((40, 10+80+i*160),
                      f'□ {name}', font=标题_证章, fill='white', direction=None)

            # img = img.convert('RGBA')
            # x, y = img.size # 获得长和宽
            # for i in range(x):
            #     for k in range(y):
            #         color = img.getpixel((i, k))
            #         color = color[:-1] + (150, )
            #         img.putpixel((i, k), color)
            # 证章图_path = os.path.join(证章_root, f'{name}__.png')
            # img.save(证章图_path,'png')

            classList = ['泰坦', '猎人', '术士']
            Unget = 1
            get = 0
            for j in range(3):
                className = classList[j]
                完成 = completionDict[name][className]['progress']
                总完成 = completionDict[name][className]['completionValue']
                if Unget and 完成 == 总完成:
                    Unget = 0
                if 完成 == 总完成:
                    get += 1

                完成长度 = int(150*完成/总完成)
                未完成长度 = 150-完成长度
                完成块 = Image.new('RGB', [完成长度, 10], 证章_蓝色)
                未完成块 = Image.new('RGB', [未完成长度, 10], 证章_红色)

                证章图.paste(完成块, (310+j*200, 47 + 120 + 160 * i))
                证章图.paste(未完成块, (310+j*200+完成长度, 47 + 120 + 160 * i))
                w, h = 数字_证章.getsize(f'{完成} / {总完成}')
                draw.text((460-w+200*j, 110 + 160 * i),
                          f'{完成} / {总完成}', font=数字_证章, fill='white', direction=None)
                color = '#FFF36D' if 总完成 == 完成 else 'white'
                draw.text((460-42+200*j, 65+120 + 160 * i),
                          f'{className}', font=职业_证章, fill=color, direction=None)

            if Unget:
                a = np.array(img.convert("L"))
                c = (100/255) * a + 80
                img = Image.fromarray(c.astype('uint8'))
            if get == 3:
                证章图.paste(镀金, (38, 43+80+i*160))

            证章图.paste(img, (40, 45+80+i*160))

        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'证章_{name}.png')
        证章图.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


def Check_zongshi(info):
    zsCompletionDict = {}
    recordCompletionDict = {}

    profileRecords = info['profileRecords']['data']['records']
    characterRecords = info['characterRecords']['data']

    for seasonName in 宗师:
        zsCompletionDict[seasonName] = {}
        for hashId in 宗师[seasonName]:
            progress = profileRecords[hashId]['objectives'][0]['progress']
            hashName = 宗师[seasonName][hashId]
            zsCompletionDict[seasonName][hashName] = progress

    for hashName in 征服者:
        hashId = 征服者[hashName]
        progress = profileRecords[hashId]['objectives'][0]['progress']
        completionValue = profileRecords[hashId]['objectives'][0]['completionValue']
        recordCompletionDict[hashName] = {
            'progress': progress, 'completionValue': completionValue}

    return zsCompletionDict, recordCompletionDict





# 地图_root = os.path.join(os.getcwd(), 'res', 'destiny2', '征服者')
# 完成_宗师 = Image.new('RGB', [12, 12], '#73B17D')
# 标题_宗师 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=24)
# 名字_宗师 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=36)
# 数字_宗师 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=60)
# 进度条字体_宗师 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=22)
# 宗师_蓝色 = '#03A9F4'
# 宗师_红色 = '#E8786E'

# 征服者图片_path = os.path.join(地图_root, '征服者.png')
# 征服者未完成图片_path = os.path.join(地图_root, '征服者_未完成.png')
# 征服者镀金_path = os.path.join(地图_root, '征服者_镀金.png')
# 征服者进度条_path = os.path.join(地图_root, '进度条.png')


# 征服者图片 = Image.open(征服者图片_path)
# 征服者未完成图片 = Image.open(征服者未完成图片_path)
# 征服者镀金 = Image.open(征服者镀金_path)
# 征服者进度条 = Image.open(征服者进度条_path)

# 征服者图片 = 征服者图片.resize((140, 159), Image.ANTIALIAS)
# 征服者未完成图片 = 征服者未完成图片.resize((140, 159), Image.ANTIALIAS)
# 征服者镀金 = 征服者镀金.resize((140, 159), Image.ANTIALIAS)

# 征服者图片 = Image.composite(征服者图片, Image.new(
#     'RGB', 征服者图片.size, '#303030'), 征服者图片)
# 征服者未完成图片 = Image.composite(征服者未完成图片, Image.new(
#     'RGB', 征服者未完成图片.size, '#303030'), 征服者未完成图片)
# 征服者镀金 = Image.composite(征服者镀金, Image.new(
#     'RGB', 征服者镀金.size, '#303030'), 征服者镀金)
# 征服者进度条 = Image.composite(征服者进度条, Image.new(
#     'RGB', 征服者进度条.size, '#303030'), 征服者进度条)






地图_root = os.path.join(os.getcwd(), 'res', 'destiny2', '征服者')
完成_宗师 = Image.new('RGB', [12, 12], '#73B17D')
标题_宗师 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=24)
名字_宗师 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=36)
数字_宗师 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=60)
进度条字体_宗师 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=22)
宗师_蓝色 = '#03A9F4'
宗师_红色 = '#E8786E'

征服者图片_path = os.path.join(地图_root, '征服者.png')
征服者未完成图片_path = os.path.join(地图_root, '征服者_未完成.png')
征服者镀金_path = os.path.join(地图_root, '征服者_镀金.png')
征服者进度条_path = os.path.join(地图_root, '进度条.png')


征服者图片 = Image.open(征服者图片_path)
征服者未完成图片 = Image.open(征服者未完成图片_path)
征服者镀金 = Image.open(征服者镀金_path)
征服者进度条 = Image.open(征服者进度条_path)

征服者图片 = 征服者图片.resize((140, 159), Image.ANTIALIAS)
征服者未完成图片 = 征服者未完成图片.resize((140, 159), Image.ANTIALIAS)
征服者镀金 = 征服者镀金.resize((140, 159), Image.ANTIALIAS)

征服者图片 = Image.composite(征服者图片, Image.new(
    'RGB', 征服者图片.size, '#303030'), 征服者图片)
征服者未完成图片 = Image.composite(征服者未完成图片, Image.new(
    'RGB', 征服者未完成图片.size, '#303030'), 征服者未完成图片)
征服者镀金 = Image.composite(征服者镀金, Image.new(
    'RGB', 征服者镀金.size, '#303030'), 征服者镀金)
征服者进度条 = Image.composite(征服者进度条, Image.new(
    'RGB', 征服者进度条.size, '#303030'), 征服者进度条)


@on_command('宗师', only_to_me=False)
async def Check_zongshi_aync(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [900])
        args = info['profile']['data']['userInfo']['displayName']

        宗师, 征服者 = Check_zongshi(info)

        imageRaw = Image.new('RGB', [1830, 1960], '#303030')
        draw = ImageDraw.Draw(imageRaw)

        draw.text((30, 20), f'小日向宗师查询: {args}',
                  font=名字_宗师, fill='white', direction=None)

        i, j = 0, 0

        镀金 = Image.new('RGB', [266, 106], '#ffe06d')

        for 赛季 in 宗师:
            count = 0
            for value in 宗师[赛季].values():
                count += value

            赛季_path = os.path.join(地图_root, f'{赛季}.png')

            赛季图 = Image.open(赛季_path)
            赛季图 = Image.composite(赛季图, Image.new(
                'RGB', 赛季图.size, '#303030'), 赛季图)
            imageRaw.paste(赛季图, (20, 100+330*i))

            draw.text((85, 100+330*i), f'{赛季}:  {count}次',
                      font=名字_宗师, fill='white', direction=None)

            for 图 in 宗师[赛季]:
                地图_path = os.path.join(地图_root, f'{图}.png')
                地图 = Image.open(地图_path)
                # 地图 = Image.composite(地图, Image.new(
                #     'RGB', 地图.size, '#303030'), 地图)
                # 灰色

                draw.text((25+300*j, 30+130+330*i),
                          f'▢ {图}', font=标题_宗师, fill='white', direction=None)

                完成次数 = 宗师[赛季][图]
                if 完成次数 > 0:
                    imageRaw.paste(完成_宗师, (31+300*j, 39+130+330*i))
                else:
                    a = np.array(地图.convert("L"))
                    c = (100/255) * a + 80
                    地图 = Image.fromarray(c.astype('uint8'))

                if 完成次数 >= 10:
                    imageRaw.paste(镀金, [27+300*j, 67+130+330*i])

                imageRaw.paste(地图, [30+300*j, 70+130+330*i])
                x, y = 数字_宗师.getsize(f'{完成次数}')
                draw.text([30+260+300*j-x, 100+70+130+330*i+3], f'{完成次数}',
                          font=数字_宗师, fill='white', direction=None)
                可用长度 = 260
                try:
                    完成长度 = int(完成次数 / count * 可用长度)
                except:
                    完成长度 = 0
                完成块 = Image.new('RGB', [完成长度, 10], 宗师_蓝色)
                剩余块 = Image.new('RGB', [可用长度-完成长度, 10], 'white')
                imageRaw.paste(完成块, [30+300*j, 5+240+130+330*i])
                imageRaw.paste(剩余块, [30+300*j+完成长度, 5+240+130+330*i])
                draw.text([30+300*j, 240+130+330*i-35+3], f'完成次数',
                          font=标题_宗师, fill='white', direction=None)

                j += 1

            i += 1
            j = 0

        i = 0
        for 赛季 in 征服者:
            completionValue = 征服者[赛季]['completionValue']
            progress = 征服者[赛季]['progress']

            图片 = 征服者图片
            颜色 = '#732881'

            

            

            if progress < completionValue:
                图片 = 征服者未完成图片
                颜色 = '#989899'

            if (赛季 == '永夜赛季' or 赛季 == '天选赛季' )and progress > 4:
                completionValue = 10
                图片 = 征服者图片
                颜色 = '#732881'

            if progress == 10:
                图片 = 征服者镀金
                颜色 = '#EDB25E'
                completionValue = progress

            
            填充长度 = int(400 * progress / completionValue)

            if 填充长度 < 4:
                填充长度 = 4
            填充块 = Image.new('RGB', [填充长度-4, 26], 颜色)

            imageRaw.paste(图片, [30, 1100+i*170])
            imageRaw.paste(征服者进度条, [30+170, 1170+i*170])
            imageRaw.paste(填充块, [30+170+2, 1170+i*170+2])
            msg = f'{progress} / {completionValue}'
            x, y = 进度条字体_宗师.getsize(msg)

            draw.text([30+170+400-x-10, 1170+i*170], msg,
                      font=进度条字体_宗师, fill='white', direction=None)

            draw.text([30+170, 20+1110+i*170], f'{赛季} 征服者',
                      font=标题_宗师, fill='white', direction=None)

            i += 1

        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'宗师_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)













def read_json(file):
    dict_temp = {}
    try:
        with open(file, 'r', encoding='utf-8') as f:
            dict_temp = json.load(f)
            return dict_temp
    except:
        return dict_temp

def write_json(dict_temp, path):
    with open(path, 'w', encoding='utf-8') as f:
        # 设置不转换成ascii  json字符串首缩进
        f.write(json.dumps(dict_temp, ensure_ascii=False, indent=2))





标题_pvp = ImageFont.truetype('MYingHeiPRC-W5.ttf', size=18)
大标题_pvp = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=24)
名字_pvp = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=32)
数字_pvp = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=28)
进度条字体_pvp = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=22)

时长模式字体_pvp = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=20)
时长模式数字_pvp = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=30)
时长模式小数字_pvp=ImageFont.truetype('MYingHeiPRC-W7.ttf', size=18)

pvp_蓝色 = '#03A9F4'
pvp_红色 = '#E8786E'

modeColorList = ['#D46D68', '#DEA089',
                 '#E7D1AC', '#84A091', '#4D809D', '#FF9C7C']
modeColorList = list(reversed(modeColorList))

destiny2Path = os.path.join(os.getcwd(), 'res', 'destiny2')
weaponIconDirPath = os.path.join(os.getcwd(), 'res', 'destiny2', 'weaponIcon')
sqlitePath = os.path.join(os.getcwd(), 'res', 'destiny2', 'identifier1.sqlite')


分数icon = Image.open(os.path.join(destiny2Path, '分数icon.png'))
kdaicon = Image.open(os.path.join(destiny2Path, 'kdaicon.png'))
击杀icon = Image.open(os.path.join(destiny2Path, '击杀icon.png'))
奖牌icon = Image.open(os.path.join(destiny2Path, '奖牌icon.png'))

#.convert('RGBA')
为你而做 = Image.open(os.path.join(destiny2Path, '为你而做.png'))
黑夜鬼魂 = Image.open(os.path.join(destiny2Path, '黑夜鬼魂.png'))
万夫莫敌 = Image.open(os.path.join(destiny2Path, '万夫莫敌.png'))
第七砥柱 = Image.open(os.path.join(destiny2Path, '第七砥柱.png'))
熔炉banner = Image.open(os.path.join(destiny2Path, '熔炉banner.png'))



为你而做 = Image.composite(为你而做, Image.new('RGB', 为你而做.size, '#303030'), 为你而做)
黑夜鬼魂 = Image.composite(黑夜鬼魂, Image.new('RGB', 黑夜鬼魂.size, '#303030'), 黑夜鬼魂)
万夫莫敌 = Image.composite(万夫莫敌, Image.new('RGB', 万夫莫敌.size, '#303030'), 万夫莫敌)
第七砥柱 = Image.composite(第七砥柱, Image.new('RGB', 第七砥柱.size, '#303030'), 第七砥柱)
熔炉banner = Image.composite(熔炉banner, Image.new('RGB', 熔炉banner.size, '#303030'), 熔炉banner)


#, Image.ANTIALIAS
# 为你而做 = 为你而做.resize((55, 67))
# 黑夜鬼魂 = 黑夜鬼魂.resize((55, 67))
# 万夫莫敌 = 万夫莫敌.resize((55, 67))
# 第七砥柱 = 第七砥柱.resize((55, 67))

medalsNameToImgDict = {
    '为你而做': 为你而做,
    '黑夜鬼魂': 黑夜鬼魂,
    '万夫莫敌': 万夫莫敌,
    '第七砥柱': 第七砥柱
}

奖牌名_pvp=ImageFont.truetype('MYingHeiPRC-W7.ttf', size=20)
奖牌数_pvp=ImageFont.truetype('MYingHeiPRC-W7.ttf', size=50)


@on_command('PVP', aliases=('pvp', 'Pvp'), only_to_me=False)
async def Check_pvp_aync(session:CommandSession):
    try:
        ev = session.event
        # if ev.self_id == three:
        #     await session.send('3号机生涯和PvP查询暂时禁用1周，请等待后续开放。',at_sender=True)

        #     return None
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200,900,1100])
        args = info['profile']['data']['userInfo']['displayName']
        membershipId = info['membershipid']
        membershipTypeNum = info['membershiptype_num']


        characterDict = info['characters']['data']
        activitiesList = []
        mathchCount = 20
        for characterId in characterDict:
            classHash = characterDict[characterId]['classHash']
            activities = await destiny.api.get_activity_history(membershipTypeNum, membershipId, characterId, mathchCount, 5, 0)
            # 这里可能会没有Response
            if activities['ErrorStatus'] != 'Success':
                Message = activities['Message']
                raise Exception(f'🤔啊这...战绩查询失败了。\n{Message}')
            if 'activities' not in activities['Response']:
                continue
            activitiesList.extend(activities['Response']['activities'])
        activitiesListOrdered = sorted(
            activitiesList, key=lambda x: x['period'], reverse=True)
        activitiesListToBeUsed = activitiesListOrdered[:mathchCount]

        weaponDict = {}
        modeDict = {}
        await session.send(f'开始获取最近{mathchCount}场对局详细记录，可能需要一定的时间，请耐心等待。',at_sender=True)
        
        with DBase(sqlitePath) as db:
            for i in activitiesListToBeUsed:
                instanceId = i['activityDetails']['instanceId']
                activityDetail = db.query(instanceId, 'Destiny2')
                if not activityDetail:
                    activityDetail = await destiny.api.get_post_game_carnage_report(instanceId)
                    if activityDetail['ErrorCode'] != 1:
                        continue
                    db.add(instanceId, activityDetail, 'Destiny2')
                    db.conn.commit()
                    print('add')
                if activityDetail['ErrorCode'] != 1:
                    continue
                modeInfo = await destiny.decode_hash(activityDetail['Response']['activityDetails']['directorActivityHash'],
                                                    'DestinyActivityDefinition')
                modeName = modeInfo['originalDisplayProperties']['name']

                for i in activityDetail['Response']['entries']:

                    if i['player']['destinyUserInfo']['membershipId'] == membershipId:

                        k = i['values']['kills']['basic']['value']
                        d = i['values']['deaths']['basic']['value']
                        timeNum = i['values']['timePlayedSeconds']['basic']['value']
                        
                        if modeName in modeDict:
                            modeDict[modeName]['k'] += k
                            modeDict[modeName]['d'] += d
                            modeDict[modeName]['time'] += timeNum
                        else:
                            modeDict[modeName] = {'k': k, 'd': d, 'time': timeNum}

                        if 'extended' not in i or 'weapons' not in i['extended']:
                            continue
                        for weaponData in i['extended']['weapons']:

                            uniqueWeaponKills = weaponData['values']['uniqueWeaponKills']['basic']['value']
                            uniqueWeaponPrecisionKills = weaponData['values'][
                                'uniqueWeaponPrecisionKills']['basic']['value']

                            referenceId = weaponData['referenceId']
                            weaponInfo = await destiny.decode_hash(referenceId, 'DestinyInventoryItemDefinition')
                            weaponName:str = weaponInfo['displayProperties']['name']
                            weaponName = weaponName.replace('/','')
                            weaponIconPath = os.path.join(
                                weaponIconDirPath, f'{weaponName}.png')

                            if not os.path.exists(weaponIconPath):
                                iconUrl = 'https://www.bungie.net' + \
                                    weaponInfo['displayProperties']['icon']
                                await dowload_img(iconUrl, weaponIconPath)

                            if weaponName in weaponDict:
                                weaponDict[weaponName]['uniqueWeaponKills'] += uniqueWeaponKills
                                weaponDict[weaponName]['uniqueWeaponPrecisionKills'] += uniqueWeaponPrecisionKills

                            else:
                                weaponDict[weaponName] = {
                                    'uniqueWeaponKills': uniqueWeaponKills,
                                    'uniqueWeaponPrecisionKills': uniqueWeaponPrecisionKills}

                        break
            

        WeaponDictOrdered = sorted(
            weaponDict.items(), key=lambda x: x[1]['uniqueWeaponKills'], reverse=True)
        if len(WeaponDictOrdered) > 6:
            WeaponDictOrdered = WeaponDictOrdered[:6]

        print(WeaponDictOrdered)

        WeaponDictOrderedLength = len(WeaponDictOrdered)

        imageRaw = Image.new(
            'RGB', [760, 1250], '#303030')
        draw = ImageDraw.Draw(imageRaw)
        draw.text((30, 20), f'小日向PVP查询: {args}',
                font=名字_pvp, fill='white', direction=None)
        draw.text((30, 100), f'▢ 最近{mathchCount}场熔炉数据',
                font=大标题_pvp, fill='white', direction=None)
        for i in range(len(WeaponDictOrdered)):
            weaponData = WeaponDictOrdered[i]
            weaponName = weaponData[0]
            weaponKills = weaponData[1]
            kills = int(weaponKills['uniqueWeaponKills'])
            precisionKills = int(weaponKills['uniqueWeaponPrecisionKills'])
            精准度 = precisionKills/kills
            精准度 = int(精准度*1000)/10

            weaponIconPath = os.path.join(weaponIconDirPath, f'{weaponName}.png')
            weaponIcon = Image.open(weaponIconPath)
            weaponIcon = weaponIcon.resize((70, 70))

            imageRaw.paste(weaponIcon, [30, 150+90*i])

            color = 'white'
            if 精准度 > 60:
                color = '#FFE06D'
            draw.text((110, 150+90*i), weaponName,
                    font=标题_pvp, fill='white', direction=None)
            draw.text((110, 40+150+90*i), f'{precisionKills} - {kills}',
                    font=进度条字体_pvp, fill='white', direction=None)
            x, y = 进度条字体_pvp.getsize(f'{精准度}%')
            draw.text((310-x, 40+150+90*i), f'{精准度}%',
                    font=进度条字体_pvp, fill=color, direction=None)

            精准击杀长度 = int(precisionKills/kills*200)
            精准击杀块 = Image.new('RGB', [精准击杀长度, 5], pvp_蓝色)

            剩余块 = Image.new('RGB', [200-精准击杀长度, 5], 'white')

            imageRaw.paste(精准击杀块, [110, 30+150+90*i])
            imageRaw.paste(剩余块, [110+精准击杀长度, 30+150+90*i])

        modeDictOrdered = sorted(
            modeDict.items(), key=lambda x: x[1]['time'], reverse=True)

        if len(modeDictOrdered) > 5:
            modeDictOrdered = modeDictOrdered[:5]

        modeDictOrdered = list(reversed(modeDictOrdered))
        
        timeCountAll = 0
        for i in modeDictOrdered:
            timeNum = i[1]['time']
            timeCountAll += timeNum


        lengthCountAll = 6 * 100
        BottomY = 100+lengthCountAll
        colorChooseFlag = 0
        for i in modeDictOrdered:
            modeName = i[0]
            modeData = i[1]
            k = int(modeData['k'])
            d = int(modeData['d'])
            timeNum = int(modeData['time'])

            m, s = divmod(timeNum, 60)
            h, m = divmod(m, 60)
            if h == 0:
                timeStr = f'{m}分'
            else:
                timeStr = f'{h}时 {m}分'
            
            lengthThisMode = int(timeNum/timeCountAll*lengthCountAll)
            if lengthThisMode < 80:
                lengthThisMode = 80
            print(lengthThisMode)
            try:
                color = modeColorList[colorChooseFlag]
                colorChooseFlag += 1
            except:
                color = modeColorList[0]

            lengthCountAll-=lengthThisMode
            BottomY -= lengthThisMode
            timeCountAll -= timeNum

            imgTiao = Image.new('RGB', [10, lengthThisMode], color)
            imageRaw.paste(imgTiao, [400, BottomY])
            draw.text((430, BottomY+8), modeName,
                    font=时长模式字体_pvp, fill='white', direction=None)
            try:
                k长度 = int(k/(k+d)*300)
            except:
                k长度 = 300
            k块 = Image.new('RGB', [k长度, 10], color)
            d块 = Image.new('RGB', [300-k长度, 10], '#A54944')
            imageRaw.paste(k块, [430, BottomY+37])
            imageRaw.paste(d块, [430+k长度, BottomY+37])
            try:
                kd = str(round(k/d,2))
            except:
                kd = '0.0'
            x,y = 时长模式数字_pvp.getsize(f'{kd}')
            draw.text([730-x, BottomY], f'{kd}',
                    font=时长模式数字_pvp, fill=color, direction=None)
            draw.text([730-x-45, BottomY+12], f'KD /',
                    font=时长模式小数字_pvp, fill='white', direction=None)   
            
            x,y=时长模式小数字_pvp.getsize(f'{k} - {d}')
            draw.text([730-x, BottomY+50], f'{k} - {d}',
                    font=时长模式小数字_pvp, fill=color, direction=None)
            draw.text([730-x-55, BottomY+50], f'K-D /',
                    font=时长模式小数字_pvp, fill='white', direction=None)   

            draw.text([430, BottomY+50], f'时长: {timeStr}',
                    font=时长模式小数字_pvp, fill='white', direction=None)
            

            # BottomY-=lengthThisMode

        record = info['profileRecords']['data']['records']

        metrics = info['metrics']['data']['metrics']
        kill = metrics['811894228']['objectiveProgress']['progress']
        reset = metrics['3626149776']['objectiveProgress']['progress']
        kda = int(metrics['871184140']['objectiveProgress']['progress']) / 100
        valor_now = metrics['2872213304']['objectiveProgress']['progress']
        kill_this_season = metrics['2935221077']['objectiveProgress']['progress']
        Glory = metrics['268448617']['objectiveProgress']['progress']

        medals = {
            '第七砥柱': record['1110690562']['objectives'][0]['progress'],
            '万夫莫敌': record['1582949833']['objectives'][0]['progress'],
            '黑夜鬼魂': record['3354992513']['objectives'][0]['progress'],
            '为你而做': record['380324143']['objectives'][0]['progress']
        }
        
        职业生涯 ={
            '职业生涯击败对手':"{:,}".format(kill),
            '职业生涯英勇重置':reset
        }

        赛季 = {
            '当前赛季击败对手':"{:,}".format(kill_this_season),
            '当前赛季生存分':"{:,}".format(Glory),
            '当前赛季KDA':kda
            
        
        }

        # 金色块 = Image.new('RGB', [5, 70], '#FFC965')
        medalTimesCount = 0
        for medalName in medals:
            medalGetCount = medals[medalName]
            奖牌icon = medalsNameToImgDict[medalName]
            imageRaw.paste(奖牌icon,[30,750+medalTimesCount*120])
            # imageRaw.paste(金色块,[22,7+750+medalTimesCount*120])
            
            draw.text([30+90, 60+750+medalTimesCount*120-10], medalName,
                        font=奖牌名_pvp, fill='white', direction=None)
            draw.text([30+90, 750+medalTimesCount*120-10], f'{medalGetCount}',
                        font=奖牌数_pvp, fill='white', direction=None)



            medalTimesCount+= 1

        bannerTimesCount = 0
        for itemName in 职业生涯:
            msg = 职业生涯[itemName]
            imageRaw.paste(熔炉banner,[250,750+bannerTimesCount*130])
            draw.text([250+50, 60+750+bannerTimesCount*130], itemName,
                        font=奖牌名_pvp, fill='white', direction=None)
            draw.text([250+50, 750+bannerTimesCount*130], f'{msg}',
                        font=奖牌数_pvp, fill='white', direction=None)
            bannerTimesCount+=1

        bannerTimesCount = 0
        for itemName in 赛季:
            msg = 赛季[itemName]
            imageRaw.paste(熔炉banner,[500,750+bannerTimesCount*130])
            draw.text([500+50, 60+750+bannerTimesCount*130], itemName,
                        font=奖牌名_pvp, fill='white', direction=None)
            draw.text([500+50, 750+bannerTimesCount*130], f'{msg}',
                        font=奖牌数_pvp, fill='white', direction=None)
            bannerTimesCount+=1



        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'pvp_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

















































        # characterDict = info['characters']['data']
        # activitiesList = []
        # for characterId in characterDict:
        #     classHash = characterDict[characterId]['classHash']
        #     activities = await destiny.api.get_activity_history(3, membershipId, characterId, 20, 5, 0)
        #     # 这里可能会没有Response
        #     if activities['ErrorStatus'] != 'Success':
        #         Message = activities['Message']
        #         raise Exception(f'🤔啊这...战绩查询失败了，可能是玩家设置了数据隐私。\n{Message}')
        #     if 'activities' not in activities['Response']:
        #         continue
        #     activitiesList.extend(activities['Response']['activities'])
        # activitiesListOrdered = sorted(
        #     activitiesList, key=lambda x: x['period'], reverse=True)
        # activitiesListToBeUsed = activitiesListOrdered[:20]

        # weaponDict = {}
        # with DBase(sqlitePath) as db:
        #     for i in activitiesListToBeUsed:
        #         instanceId = i['activityDetails']['instanceId']
        #         activityDetail = db.query(instanceId, 'Destiny2')
        #         if not activityDetail:
        #             activityDetail = await destiny.api.get_post_game_carnage_report(instanceId)
        #             db.add(instanceId, activityDetail, 'Destiny2')
        #             print('add')

        #         for i in activityDetail['Response']['entries']:

        #             if i['player']['destinyUserInfo']['membershipId'] == membershipId:

        #                 if 'weapons' not in i['extended']:
        #                     continue
        #                 for weaponData in i['extended']['weapons']:

        #                     uniqueWeaponKills = weaponData['values']['uniqueWeaponKills']['basic']['value']
        #                     uniqueWeaponPrecisionKills = weaponData['values'][
        #                         'uniqueWeaponPrecisionKills']['basic']['value']

        #                     referenceId = weaponData['referenceId']
        #                     weaponInfo = await destiny.decode_hash(referenceId, 'DestinyInventoryItemDefinition')
        #                     weaponName = weaponInfo['displayProperties']['name']
        #                     weaponIconPath = os.path.join(
        #                         weaponIconDirPath, f'{weaponName}.png')

        #                     if not os.path.exists(weaponIconPath):
        #                         iconUrl = 'https://www.bungie.net' + \
        #                             weaponInfo['displayProperties']['icon']
        #                         await dowload_img(iconUrl, weaponIconPath)

        #                     if weaponName in weaponDict:
        #                         weaponDict[weaponName]['uniqueWeaponKills'] += uniqueWeaponKills
        #                         weaponDict[weaponName]['uniqueWeaponPrecisionKills'] += uniqueWeaponPrecisionKills

        #                     else:
        #                         weaponDict[weaponName] = {
        #                             'uniqueWeaponKills': uniqueWeaponKills, 
        #                             'uniqueWeaponPrecisionKills': uniqueWeaponPrecisionKills}

        #                 break


        # WeaponDictOrdered = sorted(
        #     weaponDict.items(), key=lambda x: x[1]['uniqueWeaponKills'], reverse=True)
        
        
        # imageRaw = Image.new('RGB', [800, 1200], '#303030')
        # draw = ImageDraw.Draw(imageRaw)
        # draw.text((30, 20), f'小日向PVP查询: {args}',
        #             font=名字_pvp, fill='white', direction=None)
        # draw.text((30, 100), f'▢ 最近20场熔炉数据',
        #             font=大标题_pvp, fill='white', direction=None)
        # for i in range(len(WeaponDictOrdered)):
        #     weaponData = WeaponDictOrdered[i]
        #     weaponName = weaponData[0]
        #     weaponKills = weaponData[1]
        #     kills = int(weaponKills['uniqueWeaponKills'])
        #     precisionKills = int(weaponKills['uniqueWeaponPrecisionKills'])
        #     精准度 = precisionKills/kills
        #     精准度 = int(精准度*1000)/10
            
        #     weaponIconPath = os.path.join(weaponIconDirPath,f'{weaponName}.png')
        #     weaponIcon = Image.open(weaponIconPath)
        #     weaponIcon = weaponIcon.resize((70, 70))
            
            
        #     imageRaw.paste(weaponIcon,[30,150+90*i])

        #     color = 'white'
        #     if 精准度 > 60:
        #         color = '#FFE06D'
        #     draw.text((110, 150+90*i), weaponName,
        #             font=标题_pvp, fill='white', direction=None)
        #     draw.text((110, 40+150+90*i), f'{precisionKills} - {kills}',
        #             font=进度条字体_pvp, fill='white', direction=None)
        #     x,y = 进度条字体_pvp.getsize(f'{精准度}%')
        #     draw.text((310-x, 40+150+90*i), f'{精准度}%',
        #             font=进度条字体_pvp, fill=color, direction=None)
            
        #     精准击杀长度 = int(precisionKills/kills*200)
        #     精准击杀块 = Image.new('RGB', [精准击杀长度, 5], pvp_蓝色)
            
        #     剩余块 = Image.new('RGB', [200-精准击杀长度, 5], 'white')
            

        #     imageRaw.paste(精准击杀块,[110,30+150+90*i])
        #     imageRaw.paste(剩余块,[110+精准击杀长度,30+150+90*i])


















        
    
    except Exception as e:
        await session.send(f'{e}',at_sender=True)





gambitDirPath = os.path.join(destiny2DirPath, '智谋')
emblemDirPath = os.path.join(destiny2DirPath, '名片')


智谋banner = Image.open(os.path.join(destiny2DirPath, '智谋banner.png'))
智谋banner = Image.composite(
    智谋banner, Image.new('RGB', 智谋banner.size, '#303030'), 智谋banner)
智谋banner = 智谋banner.resize((21, 63), Image.ANTIALIAS)

账户banner = Image.open(os.path.join(destiny2DirPath, '账户banner.png'))
账户banner = Image.composite(
    账户banner, Image.new('RGB', 账户banner.size, '#303030'), 账户banner)
账户banner = 账户banner.resize((29, 84), Image.ANTIALIAS)

奖牌名_智谋 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=16)
奖牌数_智谋 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=40)
玩家名字_智谋 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=28)
声明_智谋 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=18)

分数icon = Image.open(os.path.join(
    destiny2DirPath, '分数icon.png')).convert("RGBA")
kdaicon = Image.open(os.path.join(
    destiny2DirPath, 'kdaicon.png')).convert("RGBA")
击杀icon = Image.open(os.path.join(
    destiny2DirPath, '击杀icon.png')).convert("RGBA")
奖牌icon = Image.open(os.path.join(
    destiny2DirPath, '奖牌icon.png')).convert("RGBA")
恶行icon = Image.open(os.path.join(
    destiny2DirPath, '恶行icon.png')).convert("RGBA")
萤光icon = Image.open(os.path.join(
    destiny2DirPath, '萤光icon.png')).convert("RGBA")
胜场icon = Image.open(os.path.join(
    destiny2DirPath, '胜场icon.png')).convert("RGBA")

分数icon = Image.composite(分数icon, Image.new(
    'RGB', 分数icon.size, '#303030'), 分数icon)
kdaicon = Image.composite(kdaicon, Image.new(
    'RGB', kdaicon.size, '#303030'), kdaicon)
击杀icon = Image.composite(击杀icon, Image.new(
    'RGB', 击杀icon.size, '#303030'), 击杀icon)
奖牌icon = Image.composite(奖牌icon, Image.new(
    'RGB', 奖牌icon.size, '#303030'), 奖牌icon)
恶行icon = Image.composite(恶行icon, Image.new(
    'RGB', 恶行icon.size, '#303030'), 恶行icon)
萤光icon = Image.composite(萤光icon, Image.new(
    'RGB', 萤光icon.size, '#303030'), 萤光icon)
胜场icon = Image.composite(胜场icon, Image.new(
    'RGB', 胜场icon.size, '#303030'), 胜场icon)

职业生涯IconDict = {
    '职业生涯智谋胜场': 胜场icon,
    '职业生涯智谋重置': 恶行icon,
    # '职业生涯消灭古昧':get_metric_data_str(3740642975,metrics),
    '职业生涯存储萤光': 萤光icon,
    '职业生涯消灭阻绝者': 击杀icon,
    '职业生涯击败入侵者': 击杀icon,
    '职业生涯入侵击杀守护者': 击杀icon
}

赛季IconDict = {
    '当前赛季智谋胜场': 胜场icon,
    '当前赛季存储萤光': 萤光icon,
    '当前赛季击杀入侵者': 击杀icon,
    '当前赛季消灭阻绝者': 击杀icon,
    '当前赛季恶行获得数': 恶行icon,
    '本周智谋胜场': 胜场icon
}


gambitMedalsList = ['一人成军', '横刀夺粒', '守护天使', '连环杀手','名垂千古', '唤雨师', '半库江山']
gambitMedalsDict = read_json('gambitMedals.json')


def get_metric_data_str(hashId, metrics):
    return "{:,}".format(metrics[str(hashId)]['objectiveProgress']['progress'])


def get_record_data_str(hashId, records):
    hashIdStr = str(hashId)

    if 'intervalObjectives' in records[hashIdStr]:
        return "{:,}".format(records[hashIdStr]['intervalObjectives'][0]['progress'])

    if 'objectives' in records[hashIdStr]:
        return "{:,}".format(records[hashIdStr]['objectives'][0]['progress'])






@on_command('智谋', aliases=('千谋', 'gambit'), only_to_me=False)
async def Check_gambit_aync(session:CommandSession):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200,900,1100])


        membershipId = info['membershipid']
        membershipTypeNum = info['membershiptype_num']

        metrics = info['metrics']['data']['metrics']
        records = info['profileRecords']['data']['records']

        args = info['profile']['data']['userInfo']['displayName']
        args = args[:12]

        imgFileName = ''
        characterDict = info['characters']['data']
        activitiesList = []
        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            imgFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, imgFileName)
            break

        for characterId in characterDict:
            classHash = characterDict[characterId]['classHash']
            activities = await destiny.api.get_activity_history(membershipTypeNum, membershipId, characterId, 104, 63, 0)
            # 这里可能会没有Response
            if activities['ErrorStatus'] != 'Success':
                Message = activities['Message']
                raise Exception(f'🤔啊这...战绩查询失败了，可能是玩家设置了数据隐私。\n{Message}')
            if 'activities' not in activities['Response']:
                continue
            activitiesList.extend(activities['Response']['activities'])
        activitiesListOrdered = sorted(
            activitiesList, key=lambda x: x['period'], reverse=True)
        activitiesListToBeUsed = activitiesListOrdered[:104]

        imageRaw = Image.new(
            'RGB', [900, 1600], '#303030')

        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(imgFileName)  # .resize([379,77])
        
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                  font=玩家名字_智谋, fill='white', direction=None)
        x1, y1 = 玩家名字_智谋.getsize(args)
        
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])
        seasonLevel = get_season_level_from_profile(info)
        
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                  font=声明_智谋, fill='white', direction=None)
        
        x2, y2 = 声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                  font=声明_智谋, fill='white', direction=None)
        
        x,y = 声明_智谋.getsize('小日向智谋查询')
        draw.text([524-x, 90], '小日向智谋查询',
              font=声明_智谋, fill='white', direction=None)
        
        
        
        职业生涯 = {
            '职业生涯智谋胜场': "{:,}".format(records['1676011372']['objectives'][0]['progress'] +
                                    records['2129704137']['objectives'][0]['progress'] +
                                    records['89114360']['objectives'][0]['progress']),
            '职业生涯智谋重置': get_metric_data_str(1963785799, metrics),
            # '职业生涯消灭古昧':get_metric_data_str(3740642975,metrics),
            '职业生涯存储萤光': get_metric_data_str(1462038198, metrics),
            '职业生涯消灭阻绝者': get_metric_data_str(87898835, metrics),
            '职业生涯击败入侵者': get_metric_data_str(3227312321, metrics),
            '职业生涯入侵击杀守护者': get_record_data_str(985373860, records),
        }

        赛季 = {
            '当前赛季智谋胜场': get_metric_data_str(3483580010, metrics),
            '当前赛季恶行获得数': get_metric_data_str(250859887, metrics),
            '当前赛季存储萤光': get_metric_data_str(2920575849, metrics),
            '当前赛季消灭阻绝者': get_metric_data_str(2709150210, metrics),
            '当前赛季击杀入侵者': get_metric_data_str(921988512, metrics),
            '本周智谋胜场': get_metric_data_str(2354466953, metrics)
        }
        itemCount = 0
        for itemName in 职业生涯:
            itemData = 职业生涯[itemName]
            imageRaw.paste(智谋banner, [80, 10+140+100*itemCount])
            smallIcon = 职业生涯IconDict[itemName]
            imageRaw.paste(smallIcon, [40, 20+140+100*itemCount])
            draw.text([110, 50+140+100*itemCount], itemName,
                    font=奖牌名_智谋, fill='white', direction=None)
            draw.text([110, 5+140+100*itemCount], f'{itemData}',
                    font=奖牌数_智谋, fill='white', direction=None)
            itemCount += 1

        itemCount = 0
        for itemName in 赛季:
            itemData = 赛季[itemName]
            smallIcon = 赛季IconDict[itemName]
            imageRaw.paste(smallIcon, [310, 20+140+100*itemCount])
            imageRaw.paste(智谋banner, [350, 10+140+100*itemCount])
            draw.text([380, 50+140+100*itemCount], itemName,
                    font=奖牌名_智谋, fill='white', direction=None)
            draw.text([380, 5+140+100*itemCount], f'{itemData}',
                    font=奖牌数_智谋, fill='white', direction=None)
            itemCount += 1

        绿块 = Image.new('RGB', [30, 30], '#5CFC7B')
        红块 = Image.new('RGB', [30, 30], '#FC5C5C')

        activityCount = 0
        WinCount = 0
        LeftX = 560
        TopY = 140
        for activity in activitiesListToBeUsed:
            flag = activity['values']['standing']['basic']['displayValue']
            if flag == 'Victory':
                imageRaw.paste(绿块, [LeftX, TopY])
                WinCount += 1
            else:
                imageRaw.paste(红块, [LeftX, TopY])
            LeftX += 38
            activityCount += 1
            if activityCount % 8 == 0:

                LeftX = 560
                TopY += 38

        if activityCount % 8 != 0:
            TopY += 38
        imageRaw.paste(账户banner, [560, TopY+10])

        try:
            winLength = int((WinCount/activityCount)*260)
        except:
            winLength = 0
        loseLength = 260-winLength
        win块 = Image.new('RGB', [winLength, 15], '#5CFC7B')
        lose块 = Image.new('RGB', [loseLength, 15], '#FC5C5C')

        imageRaw.paste(win块, [600, TopY+50])
        imageRaw.paste(lose块, [600+winLength, TopY+50])

        draw.text([600, TopY+25], f'{WinCount}W - {activityCount-WinCount}L',
                font=奖牌名_智谋, fill='white', direction=None)

        winRate = str(int(WinCount/activityCount*1000)/10)

        x, y = 奖牌数_智谋.getsize(f'{winRate}%')
        draw.text([600+260-x, TopY], f'{winRate}%',
                font=奖牌数_智谋, fill='white', direction=None)

        draw.text([600, TopY+70], '最近104场智谋比赛散点图',
                font=奖牌名_智谋, fill='white', direction=None)
        
        leftX = 20
        TopY = 750
        for i in range(len(gambitMedalsList)):
            medalName = gambitMedalsList[i]
            medalIconPath = os.path.join(gambitDirPath, f'{medalName}.png')
            medalIconImg = Image.open(medalIconPath)
            medalIconImg = Image.composite(medalIconImg,
                Image.new('RGB', medalIconImg.size, '#303030'),
                medalIconImg)
            medalHashId = gambitMedalsDict[medalName]['hash']
            medalDescription = gambitMedalsDict[medalName]['description']
            medalValue = get_record_data_str(medalHashId,records)
            
            imageRaw.paste(medalIconImg,[leftX, TopY])
            draw.text([leftX+100, TopY], medalValue,
                font=奖牌数_智谋, fill='white', direction=None)
            draw.text([leftX+100, TopY+46], medalName,
                font=奖牌名_智谋, fill='white', direction=None)
            draw.text([leftX+100, TopY+70], medalDescription,
                font=奖牌名_智谋, fill='#898989', direction=None)
            

            TopY+=120


        
        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'gambit_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'{e}',at_sender=True)



eggsDirPath = os.path.join(destiny2DirPath,'eggs')
bonesDirPath = os.path.join(destiny2DirPath,'bones')

@on_command('骨头', aliases=('🦴'), only_to_me=False)
async def Check_bones_aync2(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [104,200,900])
        args = info['profile']['data']['userInfo']['displayName']
        records = info['profileRecords']['data']['records']
        args = args[:12]

        emblemFileName = ''
        characterDict = info['characters']['data']
        bonesChecklistDict = info['profileProgression']['data']['checklists']['1297424116']
        
        boneNotGet = 0
        for i in bonesChecklistDict:
            boneNotGet += 0 if bonesChecklistDict[i] else 1
        print(boneNotGet)

        
        imageRaw = Image.new(
            'RGB', [900, 150+240*boneNotGet], '#303030')


        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break


        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1,y1=玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2,y2=声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x,y = 声明_智谋.getsize('小日向阿罕卡拉遗骨查询')
        draw.text([524-x, 116-y], '小日向阿罕卡拉遗骨查询',
                font=声明_智谋, fill='white', direction=None)

        msg = f'阿罕卡拉遗骨收集: {16-boneNotGet}/16'
        draw.text([550, 53-15],msg ,
                font=玩家名字_智谋, fill='white', direction=None)
        
        x,y = 玩家名字_智谋.getsize(msg)
        未收集长度 = int(boneNotGet/16*x)
        已收集长度 = x-未收集长度
        绿块 = Image.new('RGB', [已收集长度, 10], '#5CFC7B')
        红块 = Image.new('RGB', [未收集长度, 10], '#FC5C5C')
        imageRaw.paste(绿块,[550,53+30])
        imageRaw.paste(红块,[550+已收集长度,53+30])

        单块长度 = 240
        topY = 150
        leftX= 100
        boneCount = 1
        奇数块 = Image.new('RGB', [900, 单块长度], '#292929')
        偶数块 = Image.new('RGB', [900, 单块长度], '#1F1F1F')
        boneLoreImg = Image.open(os.path.join(destiny2DirPath,'骨头故事书.png')).resize([40,40]).convert('RGBA')
        

        for hashId in bones:
            if bonesChecklistDict[hashId]:
                continue
            boneLocation = bones[hashId]['location']
            boneName = bones[hashId]['name']
            boneLoreName = bones[hashId]['lore']


            x,y = 声明_智谋.getsize('破碎王座')
            x1,y1 = 玩家名字_智谋.getsize('破碎王座')
            if boneCount % 2 == 0:
                imageRaw.paste(偶数块,[0,topY])
                backgroundColor = '#1F1F1F'
            else:
                imageRaw.paste(奇数块,[0,topY])
                backgroundColor = '#292929'

            if '上维挑战' in boneLocation:
                boneTagName = '上维挑战'
            elif '破碎王座' in boneLocation:
                boneTagName = '破碎王座'
            elif '最后一愿' in boneLocation:
                boneTagName = '最后一愿'
            elif '腐化' in boneLocation:
                boneTagName = '腐化'
            else:
                boneTagName = '破碎王座'


            



            boneTagIconPath = os.path.join(destiny2DirPath,f'{boneTagName}.png')
            boneTagIcon = Image.open(boneTagIconPath).convert('RGBA')
            boneTagIcon = Image.composite(boneTagIcon,
                Image.new('RGB', boneTagIcon.size, backgroundColor),
                boneTagIcon)

            imageRaw.paste(boneTagIcon,[20,topY+20+100-84//2-30])


            boneIconPath = os.path.join(bonesDirPath,f'{boneName}.png')
            if os.path.exists(boneIconPath):
                boneIcon = Image.open(boneIconPath).resize([400,200])
            else:
                boneIcon =Image.new('RGB', [400, 200], '#282C34')
            
            imageRaw.paste(boneIcon,[leftX+350,topY+20])
            draw.text([leftX+20, topY+20+100-y1//2-30],boneLocation ,
                font=玩家名字_智谋, fill='white', direction=None)
                

            boneLoreImgUsed = Image.composite(boneLoreImg,
                Image.new('RGB', boneLoreImg.size, backgroundColor),
                boneLoreImg)
            imageRaw.paste(boneLoreImgUsed,[leftX+20,topY+20+100+y1-30])
            draw.text([leftX+20+45,topY+20+100+y1+8-30], boneLoreName,
                font=声明_智谋, fill='white', direction=None)

            
            boneCount+=1
            topY+=单块长度
        

        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'bones_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


@on_command('腐化卵查询', aliases=('孵化卵', '蛋', '卵', '🥚', '腐化卵'), only_to_me=False)
async def Check_eggs_aync2(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [104,200,900])
        args = info['profile']['data']['userInfo']['displayName']
        records = info['profileRecords']['data']['records']
        args = args[:12]
        

        emblemFileName = ''
        characterDict = info['characters']['data']
        eggsChecklistDict = info['profileProgression']['data']['checklists']['2609997025']
        
        eggNotGet = 0
        for i in eggsChecklistDict:
            eggNotGet += 0 if eggsChecklistDict[i] else 1
        print(eggNotGet)

        
        imageRaw = Image.new(
            'RGB', [900, 150+240*eggNotGet], '#303030')


        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break


        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1,y1=玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2,y2=声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x,y = 声明_智谋.getsize('小日向腐化卵查询')
        draw.text([524-x, 116-y], '小日向腐化卵查询',
                font=声明_智谋, fill='white', direction=None)

        msg = f'腐化卵收集: {40-eggNotGet}/40'
        draw.text([590, 53-15],msg ,
                font=玩家名字_智谋, fill='white', direction=None)
        
        x,y = 玩家名字_智谋.getsize(msg)
        未收集长度 = int(eggNotGet/40*x)
        已收集长度 = x-未收集长度
        绿块 = Image.new('RGB', [已收集长度, 10], '#5CFC7B')
        红块 = Image.new('RGB', [未收集长度, 10], '#FC5C5C')
        imageRaw.paste(绿块,[590,53+30])
        imageRaw.paste(红块,[590+已收集长度,53+30])

        单块长度 = 240
        topY = 150
        leftX= 100
        eggCount = 1
        奇数块 = Image.new('RGB', [900, 单块长度], '#292929')
        偶数块 = Image.new('RGB', [900, 单块长度], '#1F1F1F')
        for hashId in egg:
            if eggsChecklistDict[hashId]:
                continue
            eggLocation = egg[hashId]['location']
            eggName = egg[hashId]['name']
            x,y = 声明_智谋.getsize('破碎王座')
            x1,y1 = 玩家名字_智谋.getsize('破碎王座')
            if eggCount % 2 == 0:
                imageRaw.paste(偶数块,[0,topY])
                backgroundColor = '#1F1F1F'
            else:
                imageRaw.paste(奇数块,[0,topY])
                backgroundColor = '#292929'

            if '上维挑战' in eggLocation:
                eggTagName = '上维挑战'
            elif '破碎王座' in eggLocation:
                eggTagName = '破碎王座'
            elif '最后一愿' in eggLocation:
                eggTagName = '最后一愿'
            elif '腐化' in eggLocation:
                eggTagName = '腐化'
            else:
                eggTagName = '破碎王座'

            eggTagIconPath = os.path.join(destiny2DirPath,f'{eggTagName}.png')
            eggTagIcon = Image.open(eggTagIconPath).convert('RGBA')
            eggTagIcon = Image.composite(eggTagIcon,
                Image.new('RGB', eggTagIcon.size, backgroundColor),
                eggTagIcon)

            imageRaw.paste(eggTagIcon,[20,topY+20+100-84//2])

            eggIconPath = os.path.join(eggsDirPath,f'{eggName}.png')
            if os.path.exists(eggIconPath):
                eggIcon = Image.open(eggIconPath).resize([400,200])
            else:
                eggIcon =Image.new('RGB', [400, 200], '#282C34')
            
            imageRaw.paste(eggIcon,[leftX+350,topY+20])
            draw.text([leftX+20, topY+20+100-y1//2],eggLocation ,
                font=玩家名字_智谋, fill='white', direction=None)
                

            eggCount+=1
            topY+=单块长度
        




        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'eggs_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)



exosDirPath = os.path.join(destiny2DirPath,'exos')
@on_command('exo', aliases=('Exo', 'EXO'), only_to_me=False)
async def Check_exo_aync2(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200,104,900])
        args = info['profile']['data']['userInfo']['displayName']
        records = info['profileRecords']['data']['records']
        args = args[:12]
            
        emblemFileName = ''
        characterDict = info['characters']['data']
        exosChecklistDict = info['profileProgression']['data']['checklists']['2568476210']
        
        exoNotGet = 0
        for i in exosChecklistDict:
            exoNotGet += 0 if exosChecklistDict[i] else 1
        print(exoNotGet)

        
        imageRaw = Image.new(
            'RGB', [900, 150+240*exoNotGet], '#303030')


        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break


        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1,y1=玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2,y2=声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x,y = 声明_智谋.getsize('小日向死去的Exo查询')
        draw.text([524-x, 116-y], '小日向死去的Exo查询',
                font=声明_智谋, fill='white', direction=None)

        msg = f'死去的Exo收集: {9-exoNotGet}/9'
        draw.text([590, 53-15],msg ,
                font=玩家名字_智谋, fill='white', direction=None)
        
        x,y = 玩家名字_智谋.getsize(msg)
        未收集长度 = int(exoNotGet/9*x)
        已收集长度 = x-未收集长度
        绿块 = Image.new('RGB', [已收集长度, 10], '#5CFC7B')
        红块 = Image.new('RGB', [未收集长度, 10], '#FC5C5C')
        imageRaw.paste(绿块,[590,53+30])
        imageRaw.paste(红块,[590+已收集长度,53+30])

        单块长度 = 240
        topY = 150
        leftX= 100
        exoCount = 1
        奇数块 = Image.new('RGB', [900, 单块长度], '#292929')
        偶数块 = Image.new('RGB', [900, 单块长度], '#1F1F1F')
        for hashId in exos:
            if exosChecklistDict[hashId]:
                continue
            exoLocation = exos[hashId]['location']
            exoName = exos[hashId]['name']
            x,y = 声明_智谋.getsize('破碎王座')
            x1,y1 = 玩家名字_智谋.getsize('破碎王座')
            if exoCount % 2 == 0:
                imageRaw.paste(偶数块,[0,topY])
                backgroundColor = '#1F1F1F'
            else:
                imageRaw.paste(奇数块,[0,topY])
                backgroundColor = '#292929'

            exoTagName = '企鹅'
            

            exoTagIconPath = os.path.join(destiny2DirPath,f'{exoTagName}.png')
            exoTagIcon = Image.open(exoTagIconPath).convert('RGBA')
            exoTagIcon = Image.composite(exoTagIcon,
                Image.new('RGB', exoTagIcon.size, backgroundColor),
                exoTagIcon)

            imageRaw.paste(exoTagIcon,[20,topY+20+100-84//2])

            exoIconPath = os.path.join(exosDirPath,f'{exoName}.png')
            if os.path.exists(exoIconPath):
                exoIcon = Image.open(exoIconPath).resize([400,200])
            else:
                exoIcon =Image.new('RGB', [400, 200], '#282C34')
            
            imageRaw.paste(exoIcon,[leftX+350,topY+20])
            draw.text([leftX+20, topY+20+100-y1//2],exoLocation ,
                font=玩家名字_智谋, fill='white', direction=None)
                

            exoCount+=1
            topY+=单块长度
        




        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'exos_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)



增幅sDirPath = os.path.join(destiny2DirPath,'增幅s')
@on_command('增幅', aliases=(), only_to_me=False)
async def Check_zengfu_aync2(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200,900])
        args = info['profile']['data']['userInfo']['displayName']
        records = info['profileRecords']['data']['records']
        args = args[:12]


        emblemFileName = ''
        characterDict = info['characters']['data']
        增幅sChecklistDict = records['1121652081']['objectives']
        
        增幅NotGet = 0
        for i in 增幅sChecklistDict:
            增幅NotGet += 0 if i['complete'] else 1
        print(增幅NotGet)

        
        imageRaw = Image.new(
            'RGB', [900, 150+240*增幅NotGet], '#303030')


        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break


        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1,y1=玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2,y2=声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x,y = 声明_智谋.getsize('小日向木卫二增幅查询')
        draw.text([524-x, 116-y], '小日向木卫二增幅查询',
                font=声明_智谋, fill='white', direction=None)


        dictLength = len(增幅s)
        msg = f'木卫二增幅收集: {dictLength-增幅NotGet}/{dictLength}'
        draw.text([590, 53-15],msg ,
                font=玩家名字_智谋, fill='white', direction=None)
        
        

        x,y = 玩家名字_智谋.getsize(msg)
        未收集长度 = int(增幅NotGet/dictLength*x)
        已收集长度 = x-未收集长度
        绿块 = Image.new('RGB', [已收集长度, 10], '#5CFC7B')
        红块 = Image.new('RGB', [未收集长度, 10], '#FC5C5C')
        imageRaw.paste(绿块,[590,53+30])
        imageRaw.paste(红块,[590+已收集长度,53+30])

        单块长度 = 240
        topY = 150
        leftX= 100
        增幅Count = 1
        奇数块 = Image.new('RGB', [900, 单块长度], '#292929')
        偶数块 = Image.new('RGB', [900, 单块长度], '#1F1F1F')
        for i in 增幅sChecklistDict:
            if i['complete']:
                continue
            hashId = str(i['objectiveHash'])
            增幅Location = 增幅s[hashId]['location']
            增幅Name = 增幅s[hashId]['name']
            x,y = 声明_智谋.getsize('破碎王座')
            x1,y1 = 玩家名字_智谋.getsize('破碎王座')
            if 增幅Count % 2 == 0:
                imageRaw.paste(偶数块,[0,topY])
                backgroundColor = '#1F1F1F'
            else:
                imageRaw.paste(奇数块,[0,topY])
                backgroundColor = '#292929'

            增幅TagName = '企鹅'
            

            增幅TagIconPath = os.path.join(destiny2DirPath,f'{增幅TagName}.png')
            增幅TagIcon = Image.open(增幅TagIconPath).convert('RGBA')
            增幅TagIcon = Image.composite(增幅TagIcon,
                Image.new('RGB', 增幅TagIcon.size, backgroundColor),
                增幅TagIcon)

            imageRaw.paste(增幅TagIcon,[20,topY+20+100-84//2])

            增幅IconPath = os.path.join(增幅sDirPath,f'{增幅Name}.png')
            if os.path.exists(增幅IconPath):
                增幅Icon = Image.open(增幅IconPath).resize([400,200])
            else:
                增幅Icon =Image.new('RGB', [400, 200], '#282C34')
            
            imageRaw.paste(增幅Icon,[leftX+350,topY+20])
            draw.text([leftX+20, topY+20+100-y1//2],增幅Location ,
                font=玩家名字_智谋, fill='white', direction=None)
                

            增幅Count+=1
            topY+=单块长度




        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'增幅s_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


penguinSouvenirsDirPath = os.path.join(destiny2DirPath,'penguinSouvenirs')
@on_command('企鹅查询', aliases=('企鹅', '🐧'), only_to_me=False)
async def Check_Penguin_aync2(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200,104,900])
        args = info['profile']['data']['userInfo']['displayName']
        records = info['profileRecords']['data']['records']
        args = args[:12]
        
        emblemFileName = ''
        characterDict = info['characters']['data']
        penguinSouvenirsChecklistDict = info['profileProgression']['data']['checklists']['817948795']
        
        penguinSouvenirNotGet = 0
        for i in penguinSouvenirsChecklistDict:
            penguinSouvenirNotGet += 0 if penguinSouvenirsChecklistDict[i] else 1
        print(penguinSouvenirNotGet)

        
        imageRaw = Image.new(
            'RGB', [900, 150+240*penguinSouvenirNotGet], '#303030')


        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break


        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1,y1=玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2,y2=声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x,y = 声明_智谋.getsize('小日向薄暮企鹅查询')
        draw.text([524-x, 116-y], '小日向薄暮企鹅查询',
                font=声明_智谋, fill='white', direction=None)


        dictLength = len(penguinSouvenirs)
        msg = f'薄暮企鹅收集: {dictLength-penguinSouvenirNotGet}/{dictLength}'
        draw.text([590, 53-15],msg ,
                font=玩家名字_智谋, fill='white', direction=None)
        
        

        x,y = 玩家名字_智谋.getsize(msg)
        未收集长度 = int(penguinSouvenirNotGet/dictLength*x)
        已收集长度 = x-未收集长度
        绿块 = Image.new('RGB', [已收集长度, 10], '#5CFC7B')
        红块 = Image.new('RGB', [未收集长度, 10], '#FC5C5C')
        imageRaw.paste(绿块,[590,53+30])
        imageRaw.paste(红块,[590+已收集长度,53+30])

        单块长度 = 240
        topY = 150
        leftX= 100
        penguinSouvenirCount = 1
        奇数块 = Image.new('RGB', [900, 单块长度], '#292929')
        偶数块 = Image.new('RGB', [900, 单块长度], '#1F1F1F')
        for hashId in penguinSouvenirs:
            if penguinSouvenirsChecklistDict[hashId]:
                continue
            penguinSouvenirLocation = penguinSouvenirs[hashId]['location']
            penguinSouvenirName = penguinSouvenirs[hashId]['name']
            x,y = 声明_智谋.getsize('破碎王座')
            x1,y1 = 玩家名字_智谋.getsize('破碎王座')
            if penguinSouvenirCount % 2 == 0:
                imageRaw.paste(偶数块,[0,topY])
                backgroundColor = '#1F1F1F'
            else:
                imageRaw.paste(奇数块,[0,topY])
                backgroundColor = '#292929'

            penguinSouvenirTagName = '企鹅'
            

            penguinSouvenirTagIconPath = os.path.join(destiny2DirPath,f'{penguinSouvenirTagName}.png')
            penguinSouvenirTagIcon = Image.open(penguinSouvenirTagIconPath).convert('RGBA')
            penguinSouvenirTagIcon = Image.composite(penguinSouvenirTagIcon,
                Image.new('RGB', penguinSouvenirTagIcon.size, backgroundColor),
                penguinSouvenirTagIcon)

            imageRaw.paste(penguinSouvenirTagIcon,[20,topY+20+100-84//2])

            penguinSouvenirIconPath = os.path.join(penguinSouvenirsDirPath,f'{penguinSouvenirName}.png')
            if os.path.exists(penguinSouvenirIconPath):
                penguinSouvenirIcon = Image.open(penguinSouvenirIconPath).resize([400,200])
            else:
                penguinSouvenirIcon =Image.new('RGB', [400, 200], '#282C34')
            
            imageRaw.paste(penguinSouvenirIcon,[leftX+350,topY+20])
            draw.text([leftX+20, topY+20+100-y1//2],penguinSouvenirLocation ,
                font=玩家名字_智谋, fill='white', direction=None)
                

            penguinSouvenirCount+=1
            topY+=单块长度
        


        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'qies_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)

暗熵碎片sDirPath = os.path.join(destiny2DirPath,'暗熵碎片s')
@on_command('碎片', aliases=('暗熵碎片', '碎片查询', '🧩'), only_to_me=False)
async def Check_suipian_aync2(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200,104,900])
        args = info['profile']['data']['userInfo']['displayName']
        records = info['profileRecords']['data']['records']
        args = args[:12]

        emblemFileName = ''
        characterDict = info['characters']['data']
        暗熵碎片sChecklistDict = info['profileProgression']['data']['checklists']['1885088224']
        
        暗熵碎片NotGet = 0
        for i in 暗熵碎片sChecklistDict:
            暗熵碎片NotGet += 0 if 暗熵碎片sChecklistDict[i] else 1
        print(暗熵碎片NotGet)

        
        imageRaw = Image.new(
            'RGB', [900, 150+240*暗熵碎片NotGet], '#303030')


        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break


        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1,y1=玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2,y2=声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x,y = 声明_智谋.getsize('小日向木卫二暗熵碎片查询')
        draw.text([524-x, 116-y], '小日向木卫二暗熵碎片查询',
                font=声明_智谋, fill='white', direction=None)


        dictLength = len(暗熵碎片s)
        msg = f'木卫二暗熵碎片收集: {dictLength-暗熵碎片NotGet}/{dictLength}'
        draw.text([560, 53-15],msg ,
                font=玩家名字_智谋, fill='white', direction=None)
        
        

        x,y = 玩家名字_智谋.getsize(msg)
        未收集长度 = int(暗熵碎片NotGet/dictLength*x)
        已收集长度 = x-未收集长度
        绿块 = Image.new('RGB', [已收集长度, 10], '#5CFC7B')
        红块 = Image.new('RGB', [未收集长度, 10], '#FC5C5C')
        imageRaw.paste(绿块,[560,53+30])
        imageRaw.paste(红块,[560+已收集长度,53+30])

        单块长度 = 240
        topY = 150
        leftX= 100
        暗熵碎片Count = 1
        奇数块 = Image.new('RGB', [900, 单块长度], '#292929')
        偶数块 = Image.new('RGB', [900, 单块长度], '#1F1F1F')
        for hashId in 暗熵碎片s:
            if 暗熵碎片sChecklistDict[hashId]:
                continue
            暗熵碎片Location = 暗熵碎片s[hashId]['location']
            暗熵碎片Name = 暗熵碎片s[hashId]['name']
            x,y = 声明_智谋.getsize('破碎王座')
            x1,y1 = 玩家名字_智谋.getsize('破碎王座')
            if 暗熵碎片Count % 2 == 0:
                imageRaw.paste(偶数块,[0,topY])
                backgroundColor = '#1F1F1F'
            else:
                imageRaw.paste(奇数块,[0,topY])
                backgroundColor = '#292929'

            暗熵碎片TagName = '企鹅'
            

            暗熵碎片TagIconPath = os.path.join(destiny2DirPath,f'{暗熵碎片TagName}.png')
            暗熵碎片TagIcon = Image.open(暗熵碎片TagIconPath).convert('RGBA')
            暗熵碎片TagIcon = Image.composite(暗熵碎片TagIcon,
                Image.new('RGB', 暗熵碎片TagIcon.size, backgroundColor),
                暗熵碎片TagIcon)

            imageRaw.paste(暗熵碎片TagIcon,[20,topY+20+100-84//2])

            暗熵碎片IconPath = os.path.join(暗熵碎片sDirPath,f'{暗熵碎片Name}.png')
            if os.path.exists(暗熵碎片IconPath):
                暗熵碎片Icon = Image.open(暗熵碎片IconPath).resize([400,200])
            else:
                暗熵碎片Icon =Image.new('RGB', [400, 200], '#282C34')
            
            imageRaw.paste(暗熵碎片Icon,[leftX+350,topY+20])
            draw.text([leftX+20, topY+20+100-y1//2],暗熵碎片Location ,
                font=玩家名字_智谋, fill='white', direction=None)
                

            暗熵碎片Count+=1
            topY+=单块长度
        





        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'assps_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)


catsDirPath = os.path.join(destiny2DirPath,'cats')
@on_command('猫', aliases=('🐱'), only_to_me=False)
async def Check_cats_aync2(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [104,200,900])
        args = info['profile']['data']['userInfo']['displayName']
        records = info['profileRecords']['data']['records']
        args = args[:12]
        
        emblemFileName = ''
        characterDict = info['characters']['data']
        catsChecklistDict = info['profileProgression']['data']['checklists']['2726513366']
        
        catNotGet = 0
        for i in catsChecklistDict:
            catNotGet += 0 if catsChecklistDict[i] else 1
        print(catNotGet)

        
        imageRaw = Image.new(
            'RGB', [900, 150+240*catNotGet], '#303030')


        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break


        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1,y1=玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2,y2=声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x,y = 声明_智谋.getsize('小日向幽梦之城猫雕像查询')
        draw.text([524-x, 116-y], '小日向幽梦之城猫雕像查询',
                font=声明_智谋, fill='white', direction=None)


        dictLength = len(cats)
        msg = f'幽梦之城猫雕像收集: {dictLength-catNotGet}/{dictLength}'
        draw.text([560, 53-15],msg ,
                font=玩家名字_智谋, fill='white', direction=None)
        
        

        x,y = 玩家名字_智谋.getsize(msg)
        未收集长度 = int(catNotGet/dictLength*x)
        已收集长度 = x-未收集长度
        绿块 = Image.new('RGB', [已收集长度, 10], '#5CFC7B')
        红块 = Image.new('RGB', [未收集长度, 10], '#FC5C5C')
        imageRaw.paste(绿块,[560,53+30])
        imageRaw.paste(红块,[560+已收集长度,53+30])

        单块长度 = 240
        topY = 150
        leftX= 100
        catCount = 1
        奇数块 = Image.new('RGB', [900, 单块长度], '#292929')
        偶数块 = Image.new('RGB', [900, 单块长度], '#1F1F1F')
        for hashId in cats:
            if catsChecklistDict[hashId]:
                continue
            catLocation = cats[hashId]['location']
            catName = cats[hashId]['name']
            x,y = 声明_智谋.getsize('破碎王座')
            x1,y1 = 玩家名字_智谋.getsize('破碎王座')
            if catCount % 2 == 0:
                imageRaw.paste(偶数块,[0,topY])
                backgroundColor = '#1F1F1F'
            else:
                imageRaw.paste(奇数块,[0,topY])
                backgroundColor = '#292929'

            catTagName = '破碎王座'
            

            catTagIconPath = os.path.join(destiny2DirPath,f'{catTagName}.png')
            catTagIcon = Image.open(catTagIconPath).convert('RGBA')
            catTagIcon = Image.composite(catTagIcon,
                Image.new('RGB', catTagIcon.size, backgroundColor),
                catTagIcon)

            imageRaw.paste(catTagIcon,[20,topY+20+100-84//2])

            catIconPath = os.path.join(catsDirPath,f'{catName}.png')
            if os.path.exists(catIconPath):
                catIcon = Image.open(catIconPath).resize([400,200])
            else:
                catIcon =Image.new('RGB', [400, 200], '#282C34')
            
            imageRaw.paste(catIcon,[leftX+350,topY+20])
            draw.text([leftX+20, topY+20+100-y1//2],catLocation ,
                font=玩家名字_智谋, fill='white', direction=None)
                

            catCount+=1
            topY+=单块长度
        

        
        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'cats_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)




milestonesIconPath = os.path.join(destiny2DirPath, 'milestones')
icon球 = Image.open(os.path.join(milestonesIconPath, '球.png'))
icon球 = Image.composite(icon球, Image.new(
    'RGB', icon球.size, '#303030'), icon球)

@on_command('巅峰', aliases=('巅峰球','周常'), only_to_me=False)
async def Check_dianfeng_aync2(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200,202,204,900])
        args = info['profile']['data']['userInfo']['displayName']
        records = info['profileRecords']['data']['records']
        args = args[:12]
        
        emblemFileName = ''
        characterDict = info['characters']['data']
        

        单块长度 = 80
        IMAGEX = 900
        IMAGEY = 150+50*3+21*单块长度
        imageRaw = Image.new(
            'RGB', [IMAGEX, IMAGEY], '#303030')
        奇数颜色 = '#292929'
        偶数颜色 = '#1F1F1F'
        奇数块 = Image.new('RGB', [IMAGEX, 单块长度], 奇数颜色)
        偶数块 = Image.new('RGB', [IMAGEX, 单块长度], 偶数颜色)

        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break

        classNameDict = []
        for characterId in characterDict:
            classNameDict.append(
                classdict[characterDict[characterId]['classHash']])

        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1, y1 = 玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2, y2 = 声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x, y = 声明_智谋.getsize('小日向周常挑战查询')
        draw.text([524-x, 116-y], '小日向周常挑战查询',
                font=声明_智谋, fill='white', direction=None)

        msg = f'小日向周常挑战查询'
        x, y = 玩家名字_智谋.getsize(msg)
        x = 524+int((IMAGEX-524-x)/2)
        y = 20+int((96-y)/2)
        draw.text([x, y], msg,
                font=玩家名字_智谋, fill='white', direction=None)

        milestoneCount = 0
        topY = 140
        
        for milestonesTypeName in weekly_milestones:
            leftX = 20

            milestones = weekly_milestones[milestonesTypeName]
            imageRaw.paste(icon球, [leftX, get_mid_height(topY, topY+80, 36)])
            draw.text([leftX+45, get_mid_height(topY, topY+80, 31)], milestonesTypeName,
                    font=玩家名字_智谋, fill='#FF8B7C', direction=None)
            tempX = 350
            文本x = 56
            单个职业长度 = 150
            for className in classNameDict:

                xLocation = get_mid_height(tempX, tempX+单个职业长度, 文本x)
                yLocation = get_mid_height(topY, topY+80, 31)
                draw.text([xLocation, yLocation], className,
                        font=玩家名字_智谋, fill='#F8D9B7', direction=None)
                
                tempX += 190


            leftX += 30
            topY += 80
            for key, value in milestones.items():
                if milestoneCount % 2 == 0:
                    imageRaw.paste(偶数块, [0, topY])
                    backgroundColor = 偶数颜色
                else:
                    imageRaw.paste(奇数块, [0, topY])
                    backgroundColor = 奇数颜色

                milestoneName = value['name']
                milestoneIcon = Image.open(os.path.join(
                    milestonesIconPath, f'{key}.png')).convert('RGBA').resize([60, 60])
                milestoneIcon = Image.composite(milestoneIcon,
                                                Image.new(
                                                    'RGB', milestoneIcon.size, backgroundColor),
                                                milestoneIcon)

                imageRaw.paste(milestoneIcon, [
                            leftX, get_mid_height(topY+10, topY+60+10, 60)])
                x, y = 玩家名字_智谋.getsize(milestoneName)
                draw.text([leftX+70, get_mid_height(topY+10, topY+60+10, 31)], milestoneName,
                        font=玩家名字_智谋, fill='white', direction=None)
                
                milestoneCount += 1
                topY += 80
        
        
        白框 = Image.new('RGB', [30, 30], '#F7F7F7')
        完成 = Image.new('RGB', [22, 22], '#5CFC7B')
        奇数小块 = Image.new('RGB', [26,26], 奇数颜色)
        偶数小块 = Image.new('RGB', [26,26], 偶数颜色)
        milestoneCount = 0
        单个职业长度 = 150
        tempX = 350
        for characterId in info['characters']['data']:
            Milestones = info['characterProgressions']['data'][
                characterId]['milestones']
            Activities = info['characterActivities']['data'][
                characterId]['availableActivities']
            checkdict = check_milestions_completion(Milestones, Activities)
            
            topY = 140
            for milestoneTypeName in checkdict:
                milestonesDict = checkdict[milestoneTypeName]
                topY+=80
                for milestoneHashId in milestonesDict:
                    milestoneName = milestonesDict[milestoneHashId]['name']
                    milestoneCompletion = milestonesDict[milestoneHashId]['completion']

                    if isinstance(milestoneCompletion,list):
                        总数目 = milestoneCompletion[0]
                        已完成 = milestoneCompletion[1]
                        msg = f'{已完成}/{总数目}'
                        x,y = 玩家名字_智谋.getsize(msg)
                        xLocation = get_mid_height(tempX, tempX+单个职业长度, x)
                        draw.text([xLocation, topY+20], msg,
                        font=玩家名字_智谋, fill='white', direction=None)
                        已完成长度 = int(已完成/总数目*单个职业长度)
                        未完成长度 = 单个职业长度-已完成长度
                        绿块 = Image.new('RGB', [已完成长度, 10], '#5CFC7B')
                        红块 = Image.new('RGB', [未完成长度, 10], '#FC5C5C')
                        imageRaw.paste(绿块,[tempX,topY+60])
                        imageRaw.paste(红块,[tempX+已完成长度,topY+60])
                    else:
                        xLocation = get_mid_height(tempX, tempX+单个职业长度, 30)
                        yLocation = get_mid_height(topY, topY+80, 30)
                        imageRaw.paste(白框,[xLocation,yLocation])
                        if milestoneCount % 2 == 0:
                            imageRaw.paste(偶数小块, [xLocation+2,yLocation+2])
                        else:
                            imageRaw.paste(奇数小块, [xLocation+2,yLocation+2])
                        
                        if milestoneCompletion:
                            imageRaw.paste(完成,[xLocation+4,yLocation+4])
                            
                    
                    topY+=80
                    milestoneCount+=1
            tempX+=190
            milestoneCount=0

        topY+=10
        draw.text([20, topY], '由于milestones数据的特殊性，周常挑战查询功能可能会有些错误。如果你的数据有较大的问题请尽快联系小日向开发者。',
                        font=奖牌名_智谋, fill='white', direction=None)
        draw.text([20, topY+30], '数据错误具体表现在玩家该活动没解锁但显示已完成。',
                        font=奖牌名_智谋, fill='white', direction=None)

        
        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'weekly_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)



@on_command('生涯', aliases=('生涯查询', '角色查询'), only_to_me=False)
async def Check_shengya_aync2(session: CommandSession):
    try:
        ev = session.event
        # if ev.self_id == three:
        #     await session.send('3号机生涯和PvP查询暂时禁用1周，请等待后续开放。',at_sender=True)
        #     return None
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200,900])
        membershipId = info['membershipid']
        membershipType = info['membershiptype_num']

        args = info['profile']['data']['userInfo']['displayName']
        records = info['profileRecords']['data']['records']
        args = args[:12]

        emblemFileName = ''
        characterDict = info['characters']['data']

        IMAGEX = 1000
        IMAGEY = 2050
        imageRaw = Image.new(
            'RGB', [IMAGEX, IMAGEY], '#303030')
        奇数颜色 = '#292929'
        偶数颜色 = '#1F1F1F'
        # 奇数块 = Image.new('RGB', [IMAGEX, 单块长度], 奇数颜色)
        # 偶数块 = Image.new('RGB', [IMAGEX, 单块长度], 偶数颜色)

        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break

        # classNameDict = []
        # for characterId in characterDict:
        #     classNameDict.append(
        #         classdict[characterDict[characterId]['classHash']])

        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1, y1 = 玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2, y2 = 声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x, y = 声明_智谋.getsize('小日向生涯数据查询')
        draw.text([524-x, 116-y], '小日向生涯数据查询',
                font=声明_智谋, fill='white', direction=None)

        msg = f'小日向生涯数据查询'
        x, y = 玩家名字_智谋.getsize(msg)
        x = 524+int((IMAGEX-524-x)/2)
        y = 20+int((96-y)/2)
        draw.text([x, y], msg,
                font=玩家名字_智谋, fill='white', direction=None)

        charactersList = await destiny.api.get_historical_stats_for_account(membershipType,membershipId)
        charactersList = [x['characterId'] for x in charactersList['Response']['characters']]

        
        
        await session.send('开始获取生涯数据，可能需要1分钟的时间，期间请不要发送任何消息。',at_sender=True)
        shengyaData = await get_shengya_data(info['profileRecords'], info['profile'], info['characters']['data'],membershipType,membershipId,charactersList)
        basicData = shengyaData[0]
        yearsDict = shengyaData[1]
        activitiesTime = shengyaData[2]
        characterTimeDict = shengyaData[3]


        tempY = 200
        for yearName in seasonsAndYearsDict:
            tempX = 50

            seasonsDict = seasonsAndYearsDict[yearName]
            seasonsDictToCheck = yearsDict[yearName]
            for seasonHash in seasonsDict:
                seasonName = seasonsDict[seasonHash]
                seasonIconPath = os.path.join(destiny2DirPath, '赛季图',f'{seasonName}.png')
                seasonIcon = Image.open(seasonIconPath).resize((200, 100), Image.ANTIALIAS)

                # 有这个赛季
                if seasonsDictToCheck[seasonName]:
                    fontColor = 'white'
                else:
                    seasonIcon = get_grey_img(seasonIcon)
                    fontColor = '#525252'

                imageRaw.paste(seasonIcon, [tempX, tempY])
                fontX,fontY = 声明_智谋.getsize(seasonName)
                draw.text([get_mid_height(tempX,tempX+200,fontX), tempY-30], seasonName,
                        font=声明_智谋, fill=fontColor, direction=None)
                tempX += 240
            tempY += 160

        tempX = 80
        for typeName in basicData:
            tempY = 570
            iconColor = basicDataNameToImgColor[typeName]
            bannerPath = os.path.join(
                destiny2DirPath, f'{basicDataNameToImgName[typeName]}.png')
            banner = Image.open(bannerPath).resize((29, 84), Image.ANTIALIAS)
            icon = Image.new('RGB', [140, 10], iconColor)
            banner = Image.composite(banner, Image.new(
                'RGB', banner.size, '#303030'), banner)
            value = basicData[typeName]

            imageRaw.paste(banner, [tempX-35, tempY-40])
            imageRaw.paste(icon, [tempX, tempY])
            fontX,fontY = 奖牌数_智谋.getsize(value)
            xLocation = get_mid_height(tempX,tempX+140,fontX)
            draw.text([xLocation, tempY-50], value,
                    font=奖牌数_智谋, fill='white', direction=None)

            x, y = 声明_智谋.getsize(typeName)
            xLocation = get_mid_height(tempX,tempX+140,x)
            draw.text([xLocation, tempY+15], typeName,
                    font=声明_智谋, fill='white', direction=None)

            tempX += 190

        graphX = 900
        graphY = 400

        usedGraphY = graphY-40
        tempX = 50
        tempY = 750

        bottomY = tempY+graphY
        max: float = activitiesTime['max']
        # min:float = activitiesTime['min']
        min: float = 0.0
        timeY = max-min
        activities = activitiesTime['response']
        activitiesLength = len(activities)
        try:
            singleX = int(graphX/activitiesLength/2)
        except:
            singleX = 0

        try:
            avghour = int(activitiesTime['total'] / activitiesLength*10)/10
        except:
            avghour = 0.0
        draw.text([tempX, tempY-80], f'玩家最近{activitiesLength}天活跃时长柱形图',
                font=玩家名字_智谋, fill='white', direction=None)
        draw.text([tempX, tempY-40], f'日均活跃: {avghour}h',
                font=声明_智谋, fill='white', direction=None)
        draw.line((tempX, tempY, tempX, bottomY+3), fill='white', width=3)
        draw.line((tempX, bottomY+3, tempX+graphX,
                bottomY+3), fill='white', width=3)

        halfTime = int(timeY*10/2)/10
        fontx, fonty = 声明_智谋.getsize(f'{halfTime}h')
        draw.text([50-fontx-4, int(bottomY-usedGraphY/2)], f'{halfTime}h',
                font=声明_智谋, fill='#9CDDFD', direction=None)

        fontx, fonty = 声明_智谋.getsize(f'{max}h')
        draw.text([50-fontx-4, bottomY-usedGraphY], f'{max}h',
                font=声明_智谋, fill='#9CDDFD', direction=None)

        dateList = list(activities.keys())
        startDate = dateList[0].replace('2021-', '')
        endDate = dateList[-1].replace('2021-', '')

        draw.text([tempX, bottomY+10], f'{startDate}',
                font=声明_智谋, fill='#9CDDFD', direction=None)
        draw.text([tempX+graphX-singleX*2, bottomY+10], f'{endDate}',
                font=声明_智谋, fill='#9CDDFD', direction=None)

        for dateStr in activities:
            hour = activities[dateStr]
            try:
                y = int(hour/timeY*usedGraphY)
            except:
                y = 0
            y = y if y else 4
            img = Image.new('RGB', [singleX, y], '#9C9DFD')
            tempX += singleX
            imageRaw.paste(img, [tempX, bottomY-y])
            tempX += singleX

        tempY = 1230
        for characterName, timeDict in characterTimeDict.items():
            if characterName == '已删除角色':
                continue
            tempX = 50
            totalHour = timeDict["总计"]
            iconPath = os.path.join(destiny2DirPath, f'{characterName}.png')
            # .resize((29, 84), Image.ANTIALIAS)
            icon = Image.open(iconPath).convert('RGBA')
            icon = Image.composite(icon, Image.new(
                'RGB', icon.size, '#303030'), icon)
            imageRaw.paste(icon, [tempX, tempY])

            yLocation = get_mid_height(tempY, tempY+80, 31)
            draw.text([tempX+85, yLocation], f'{characterName}',
                    font=玩家名字_智谋, fill='white', direction=None)
            draw.text([tempX+85+70, yLocation+10], f'总计: {totalHour}h',
                    font=声明_智谋, fill='white', direction=None)
            tempY += 110
            for modeName, hour in timeDict.items():
                if modeName == '总计':
                    continue
                modeColor = modeColorDict[modeName]
                if totalHour == 0:
                    continue
                xlength = int(hour/totalHour*900)
                img = Image.new('RGB', [xlength, 10], modeColor)
                imageRaw.paste(img, [tempX, tempY])
                fontx, fonty = 声明_智谋.getsize(modeName)
                if fontx > xlength:
                    xLocation = tempX
                else:
                    xLocation = get_mid_height(tempX, tempX+xlength, fontx)
                draw.text([xLocation, tempY-30], modeName,
                        font=声明_智谋, fill='white', direction=None)

                # percentageStr = int(hour/totalHour*1000)/10
                # percentageStr = f'{percentageStr}%'
                percentageStr = f'{hour}h'
                fontx, fonty = 声明_智谋.getsize(percentageStr)
                if fontx > xlength:
                    xLocation = tempX
                else:
                    xLocation = get_mid_height(tempX, tempX+xlength, fontx)
                draw.text([xLocation, tempY+17], percentageStr,
                        font=声明_智谋, fill='white', direction=None)

                tempX += xlength
            tempY += 80

        draw.text([50, tempY-20], '由于Bungie数据的问题，部分活动数据会有缺失，小日向对数据进行了缺省处理。',
                        font=声明_智谋, fill='white', direction=None)
        draw.text([50, tempY-20+35], '由于上述问题，智谋时长会略微少于正常统计。',
                        font=声明_智谋, fill='white', direction=None)


        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'生涯_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)
        
    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)



珍珠sDirPath = os.path.join(destiny2DirPath,'珍珠s')
@on_command('珍珠', aliases=('玻璃宝库'), only_to_me=False)
async def Check_珍珠_aync2(session):
    try:
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200,900])
        args = info['profile']['data']['userInfo']['displayName']
        records = info['profileRecords']['data']['records']
        args = args[:12]

        emblemFileName = ''
        characterDict = info['characters']['data']
        珍珠sChecklistDict:list = records['932039090']['objectives']
        
        珍珠NotGet = 0
        for i in 珍珠sChecklistDict:
            珍珠NotGet += 0 if i['complete'] else 1
        print(珍珠NotGet)

        
        imageRaw = Image.new(
            'RGB', [900, 150+240*珍珠NotGet], '#303030')


        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break


        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1,y1=玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2,y2=声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x,y = 声明_智谋.getsize('小日向玻璃拱顶珍珠查询')
        draw.text([524-x, 116-y], '小日向玻璃拱顶珍珠查询',
                font=声明_智谋, fill='white', direction=None)


        dictLength = len(珍珠s)
        msg = f'玻璃拱顶珍珠收集: {dictLength-珍珠NotGet}/{dictLength}'
        draw.text([560, 53-15],msg ,
                font=玩家名字_智谋, fill='white', direction=None)
        
        

        x,y = 玩家名字_智谋.getsize(msg)
        未收集长度 = int(珍珠NotGet/dictLength*x)
        已收集长度 = x-未收集长度
        绿块 = Image.new('RGB', [已收集长度, 10], '#5CFC7B')
        红块 = Image.new('RGB', [未收集长度, 10], '#FC5C5C')
        imageRaw.paste(绿块,[560,53+30])
        imageRaw.paste(红块,[560+已收集长度,53+30])

        单块长度 = 240
        topY = 150
        leftX= 100

        珍珠Count = -1
        drawCount = 0
        奇数块 = Image.new('RGB', [900, 单块长度], '#292929')
        偶数块 = Image.new('RGB', [900, 单块长度], '#1F1F1F')

        for i in 珍珠sChecklistDict:
            珍珠Count+=1
            if i['complete']:
                continue
            珍珠Location = 珍珠s[珍珠Count]
            珍珠Name = 珍珠Count
            x,y = 声明_智谋.getsize('破碎王座')
            x1,y1 = 玩家名字_智谋.getsize('破碎王座')
            if drawCount % 2 == 0:
                imageRaw.paste(偶数块,[0,topY])
                backgroundColor = '#1F1F1F'
            else:
                imageRaw.paste(奇数块,[0,topY])
                backgroundColor = '#292929'

            TagName = '珍珠'
            drawCount+=1
            

            珍珠TagIconPath = os.path.join(destiny2DirPath,f'{TagName}.png')
            珍珠TagIcon = Image.open(珍珠TagIconPath).convert('RGBA')
            珍珠TagIcon = Image.composite(珍珠TagIcon,
                Image.new('RGB', 珍珠TagIcon.size, backgroundColor),
                珍珠TagIcon)

            imageRaw.paste(珍珠TagIcon,[20,topY+20+100-84//2])

            珍珠IconPath = os.path.join(珍珠sDirPath,f'{珍珠Name}.png')
            if os.path.exists(珍珠IconPath):
                珍珠Icon = Image.open(珍珠IconPath).resize([400,200])
            else:
                珍珠Icon =Image.new('RGB', [400, 200], '#282C34')
            
            imageRaw.paste(珍珠Icon,[leftX+350,topY+20])
            draw.text([leftX+10, topY+20+100-y1//2],珍珠Location ,
                font=玩家名字_智谋, fill='white', direction=None)
                

            topY+=单块长度
        





        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'珍珠_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)




@on_command('队伍', aliases=('队伍查询', '火力战队', '找内鬼'), only_to_me=False)
async def getDataFireteam_2(session):
    try:
        ev = session.event
        # if ev.self_id == three:
        #     return None
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200,204,1000])
        membershipId = info['membershipid']
        membershipType = info['membershiptype_num']
        args = info['profile']['data']['userInfo']['displayName']
        characterActivities = info['characterActivities']['data']
        args = args[:12]

        emblemFileName = ''
        characterDict = info['characters']['data']

        try:
            profileTransitoryData = info['profileTransitoryData']['data']
        except:
            raise Exception('所查询的玩家目前不在线')
        timeMsg = get_activity_time(profileTransitoryData['currentActivity']['startTime'])
        
        currentActivityHash = 0
        characterIdPlayNow = get_recent_play_characterId(characterActivities)
        currentActivityHash = characterActivities[characterIdPlayNow]['currentActivityHash']
        partyMembersData,basicData = await get_partyMemberInfo(profileTransitoryData['partyMembers'],currentActivityHash)
        



        IMAGEX = 900
        IMAGEY = 130+(basicData[3]*260)
        imageRaw = Image.new(
            'RGB', [IMAGEX, IMAGEY], '#303030')
        奇数颜色 = '#292929'
        偶数颜色 = '#1F1F1F'
        # 奇数块 = Image.new('RGB', [IMAGEX, 单块长度], 奇数颜色)
        # 偶数块 = Image.new('RGB', [IMAGEX, 单块长度], 偶数颜色)

        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break

        # classNameDict = []
        # for characterId in characterDict:
        #     classNameDict.append(
        #         classdict[characterDict[characterId]['classHash']])

        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1, y1 = 玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2, y2 = 声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x, y = 声明_智谋.getsize('小日向火力战队查询')
        draw.text([524-x, 116-y], '小日向火力战队查询',
                font=声明_智谋, fill='white', direction=None)

        msg = f'{basicData[1]}，{basicData[0]}'
        x, y = 声明_智谋.getsize(msg)
        x = get_mid_height(524,IMAGEX,x)
        y = 40
        draw.text([x, y], msg,
                font=声明_智谋, fill='white', direction=None)



        x, y = 声明_智谋.getsize(timeMsg)
        x = get_mid_height(524,IMAGEX,x)
        y = 70
        draw.text([x, y], timeMsg,
                font=声明_智谋, fill='white', direction=None)


        # tempX = get_mid_height(0,900,474)
        tempX = 75
        tempY=150
        队长块 = Image.new(
            'RGB', [10, 96], '#00A4EF')
        队员块 = Image.new(
            'RGB', [10, 96], '#4CD266')
        
        characterCount=0
        单块长度 = 260
        奇数颜色 = '#292929'
        偶数颜色 = '#1F1F1F'
        奇数块 = Image.new('RGB', [IMAGEX, 单块长度], 奇数颜色)
        偶数块 = Image.new('RGB', [IMAGEX, 单块长度], 偶数颜色)

        for partyMemberData in partyMembersData:
            name = partyMemberData['name']
            # name = name[:14]
            className = partyMemberData['className']
            level = partyMemberData['level']
            title = partyMemberData['title']
            emblem = partyMemberData['emblem']
            status = partyMemberData['status']
            
            if characterCount % 2==0:
                imageRaw.paste(偶数块, [0, tempY])
                color = 偶数颜色
            else:
                imageRaw.paste(奇数块, [0, tempY])
                color = 奇数颜色

            tempY+=25

            emblemImg = Image.open(emblem)  # .resize([379,77])
            imageRaw.paste(emblemImg, [tempX, tempY])
            imageRaw.paste(队长块 if status == '队长' else 队员块, [tempX-25, tempY])


            
            draw.text([tempX+125, tempY], name,
                    font=玩家名字_智谋, fill='white', direction=None)
            上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

            draw.text([tempX+125, get_mid_height(tempY+31,tempY+96-20,20)], f'赛季等级: {level}',
                    font=声明_智谋, fill='white', direction=None)
            draw.text([tempX+125, tempY+96-20], f'{className}',
                    font=声明_智谋, fill='white', direction=None)
            
            x,y = 声明_智谋.getsize(title)
            draw.text([get_mid_height(tempX,tempX+96,x), tempY+105], f'{title}',
                    font=声明_智谋, fill='#F7B23B', direction=None)

            tempY+=110


            for dataShow in partyMemberData['dataList']:
                Name = dataShow['name']
                Icon = dataShow['icon']
                Progress = dataShow['progress']
                
                x,y = 声明_智谋.getsize(Name)
                draw.text([tempX+125+45, tempY+70], f'{Name}',
                    font=声明_智谋, fill='white', direction=None)

                色块 = Image.new('RGB', [x, 10], '#EB4A42')
                imageRaw.paste(色块, [tempX+125+45, tempY+53])
                numx,numy=奖牌数_智谋.getsize(Progress)
                draw.text([get_mid_height(tempX+125+45,tempX+125+45+x,numx), tempY], f'{Progress}',
                    font=奖牌数_智谋, fill='white', direction=None)
                


                emblemImg = Image.open(Icon).resize([29,84]).convert('RGBA')
                emblemImg = Image.composite(emblemImg, Image.new(
                'RGB', emblemImg.size, color), emblemImg)
                imageRaw.paste(emblemImg, [tempX+125, get_mid_height(tempY,tempY+90,84)])
                
            
            tempY+=110
            characterCount+=1




        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'fireteam_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)




@on_command('名片', aliases=('名片查询', 'mpcx'), only_to_me=False)
async def checkemblem(session):
    try:
        ev = session.event
        # if ev.self_id != four:
        #     return None
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200,800])
        membershipId = info['membershipid']
        membershipType = info['membershiptype_num']
        args = info['profile']['data']['userInfo']['displayName']
        args = args[:12]
        
        res = await destiny.decode_hash(1166184619,'DestinyPresentationNodeDefinition')
        emblemsAllCount = len(res['children']['collectibles'])
        collectibles = info['profileCollectibles']['data']['collectibles']
        emblemToDrawList = []
        for emblemInfoRaw in res['children']['collectibles']:
            emblemHash = emblemInfoRaw['collectibleHash']
            if (acquired := get_emblem_acquired(emblemHash,collectibles)):
                emblemInfo = await destiny.decode_hash(emblemHash,'DestinyCollectibleDefinition')
                name = emblemInfo['displayProperties']['name']
                icon = 'https://www.bungie.net' + emblemInfo['displayProperties']['icon']
                iconPath = os.path.join(iconSmallDirPath,f'{emblemHash}.png')
                await dowload_img(icon,iconPath)
                itemHash = emblemInfo['itemHash']
                itemInfo = await destiny.decode_hash(itemHash,'DestinyInventoryItemDefinition')
                secondaryIcon = 'https://www.bungie.net' +itemInfo['secondaryIcon']
                secondaryIconPath = os.path.join(emblemDirPath,f'{itemHash}.png')
                await dowload_img(secondaryIcon,secondaryIconPath)
                emblemToDrawList.append(
                    {
                        'name':name,
                        'icon':iconPath,
                        'secondaryIcon':secondaryIconPath
                    }
                )


        emblemCount = len(emblemToDrawList)
        IMAGEX = 900
        IMAGEY = 160+int(emblemCount/2+0.5)*120
        imageRaw = Image.new(
                'RGB', [IMAGEX, IMAGEY], '#303030')


        emblemFileName = ''
        characterDict = info['characters']['data']

        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break
        
        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1,y1=玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2,y2=声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x,y = 声明_智谋.getsize('小日向综合名片查询')
        draw.text([524-x, 116-y], '小日向综合名片查询',
                font=声明_智谋, fill='white', direction=None)



        msg = f'综合名片查询: {emblemCount}/{emblemsAllCount}'
        x, y = 玩家名字_智谋.getsize(msg)
        x = 524+int((IMAGEX-524-x)/2)
        y = 20+int((96-y)/2)
        draw.text([x, y-10], msg,
                font=玩家名字_智谋, fill='white', direction=None)
        
        fontX,fontY = 玩家名字_智谋.getsize(msg)
        已收集长度 = int(emblemCount/emblemsAllCount*fontX)
        未收集长度 = fontX-已收集长度
        绿块 = Image.new('RGB', [已收集长度, 10], '#5CFC7B')
        红块 = Image.new('RGB', [未收集长度, 10], '#FC5C5C')
        imageRaw.paste(绿块,[x,53+40])
        imageRaw.paste(红块,[x+已收集长度,53+40])

        单块长度 = 120
        times = 0.6
        lineCount = 0
        emblemSingleX,emblemSingleY = int(474*times),int(96*times)
        tempY = 160-单块长度

        奇数颜色 = '#292929'
        偶数颜色 = '#1F1F1F'
        奇数块 = Image.new('RGB', [IMAGEX, 单块长度], 奇数颜色)
        偶数块 = Image.new('RGB', [IMAGEX, 单块长度], 偶数颜色)


        for i in range(emblemCount):
            if i % 2 == 0:
                tempX = 50
                tempY+=单块长度
                if lineCount%2==0:
                    imageRaw.paste(偶数块, [0, tempY])
                    backgroundColor = 偶数颜色
                else:
                    imageRaw.paste(奇数块, [0, tempY])
                    backgroundColor = 奇数颜色

                lineCount+=1

            embleData = emblemToDrawList[i]
            name = embleData['name']
            iconPath = embleData['icon']
            secondaryIconPath = embleData['secondaryIcon']
            
            makrX = tempX
            icon = Image.open(iconPath).resize([emblemSingleY, emblemSingleY])
            secondaryIcon = Image.open(secondaryIconPath).resize([emblemSingleX, emblemSingleY])
            imageRaw.paste(icon,[tempX,get_mid_height(tempY,tempY+单块长度,emblemSingleY)-5])
            tempX += emblemSingleY + 10
            
            
            imageRaw.paste(secondaryIcon,[tempX,get_mid_height(tempY,tempY+单块长度,emblemSingleY)-5])
            fontX,fontY = 奖牌名_智谋.getsize(name)
            draw.text([get_mid_height(makrX,tempX+emblemSingleX, fontX), 
            tempY+单块长度-30], 
            name,
                            font=奖牌名_智谋, 
                            fill='white', 
                            direction=None)
            
            tempX += emblemSingleX + 100

            
        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'emblem_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)



@on_command('称号', aliases=('称号查询', 'chcx'), only_to_me=False)
async def checkchenghao(session):
    try:
        ev = session.event
        # if ev.self_id != four:
        #     return None
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200,900])
        membershipId = info['membershipid']
        membershipType = info['membershiptype_num']
        args = info['profile']['data']['userInfo']['displayName']
        args = args[:12]
        records = info['profileRecords']['data']['records']
        
        emblemFileName = ''
        characterDict = info['characters']['data']
        sealsData = check_seals_completion(records)


        单块长度 = 140
        IMAGEX = 1070
        IMAGEY = 160+11*单块长度+50
        imageRaw = Image.new(
                'RGB', [IMAGEX, IMAGEY], '#303030')


        emblemFileName = ''
        characterDict = info['characters']['data']

        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break
        
        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1,y1=玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2,y2=声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x,y = 声明_智谋.getsize('小日向称号印章查询')
        draw.text([524-x, 116-y], '小日向称号印章查询',
                font=声明_智谋, fill='white', direction=None)



        msg = f'小日向现有称号/传承印章查询'
        x, y = 玩家名字_智谋.getsize(msg)
        x = 524+int((IMAGEX-524-x)/2)
        y = 30+int((96-y)/2)
        draw.text([x, y-10], msg,
                font=玩家名字_智谋, fill='white', direction=None)

        
        sealSingleX,sealSingleY = 100,100
        tempX = 50
        tempY = 160-单块长度
        gap = (单块长度-sealSingleX)//2


        奇数颜色 = '#292929'
        偶数颜色 = '#1F1F1F'
        奇数块 = Image.new('RGB', [IMAGEX, 单块长度], 奇数颜色)
        偶数块 = Image.new('RGB', [IMAGEX, 单块长度], 偶数颜色)

        for i in range(len(sealsData)):
            sl = sealsData[i]
            sealsCount = 0
            for value in sl.values():
                sealsCount+=1
                if sealsCount % 3 == 1:
                    tempX=50
                    tempY+=单块长度
                    if (sealsCount // 3) % 2 == 0:
                        imageRaw.paste(偶数块,[0,tempY])
                        backGroundColor = 偶数颜色
                    else:
                        imageRaw.paste(奇数块,[0,tempY])
                        backGroundColor = 奇数颜色


                icon = value['icon']
                name = value['name']
                progress = value['progress']
                completionValue = value['completionValue']
                if progress>completionValue:
                    completionValue = progress

                
                sealIcon=Image.open(icon).resize([sealSingleX, sealSingleY]).convert('RGBA')
                sealIcon = Image.composite(sealIcon, Image.new(
                    'RGB', sealIcon.size, backGroundColor), sealIcon)

                imageRaw.paste(sealIcon,[tempX,tempY+gap])
                completionLen = int(progress/completionValue*sealSingleY)
                unCompletionLen = sealSingleY-completionLen
                completionSquare = Image.new('RGB', [10, completionLen], blue)
                unCompletionSquare = Image.new('RGB', [10, unCompletionLen], red)
                imageRaw.paste(unCompletionSquare,[tempX+sealSingleX+20,tempY+gap])
                imageRaw.paste(completionSquare,[tempX+sealSingleX+20,tempY+gap+unCompletionLen])
                
                fontX,fontY = 玩家名字_智谋.getsize(name)
                xLocation = tempX+sealSingleX+20+10+20
                yLocation = tempY+gap+10
                draw.text([xLocation, yLocation], name,
                font=玩家名字_智谋, fill='white', direction=None)
                msg = f'{progress} / {completionValue}'
                yLocation+=fontY+20
                draw.text([xLocation, yLocation], msg,
                font=font_24, fill='white', direction=None)


                tempX+=360
            tempY+=50

    
        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'称号_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)



@on_command('异域武器皮肤', aliases=('皮肤'), only_to_me=False)
async def checkpifu(session):
    try:
        ev = session.event
        # if ev.self_id != four:
        #     return None
        hardlink = gethardlink(session)
        if hardlink:
            args = hardlink
        else:
            args = session.current_arg
        info = await GetInfo(args, [200,800])
        membershipId = info['membershipid']
        membershipType = info['membershiptype_num']
        args = info['profile']['data']['userInfo']['displayName']
        args = args[:12]
        args = info['profile']['data']['userInfo']['displayName']
        args = args[:12]
        profileCollectibles = info['profileCollectibles']['data']['collectibles']
        characterId = list(info['characterCollectibles']['data'])[0]
        characterCollectibles = info['characterCollectibles']['data'][characterId]['collectibles']
        
        emblemFileName = ''
        characterDict = info['characters']['data']
        skinsData = check_weaponsskins_completion(profileCollectibles,characterCollectibles)

        间隔块数 = len(skinsData)
        行数 = 0
        for value in skinsData.values():
            weaponLen = len(value)
            if weaponLen % 5 != 0:
                行数+=1
            行数+=weaponLen//5
        单块长度 = 60
        间隔块长度 = 50
        IMAGEX = 1100
        IMAGEY = 130+行数*单块长度+间隔块长度*间隔块数
        imageRaw = Image.new(
                'RGB', [IMAGEX, IMAGEY], '#303030')


        emblemFileName = ''
        characterDict = info['characters']['data']

        for characterId in characterDict:
            emblemBackgroundPath = characterDict[characterId]['emblemBackgroundPath']
            emblemHash = characterDict[characterId]['emblemHash']
            emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
            emblemFileName = os.path.join(emblemDirPath, f'{emblemHash}.png')
            await dowload_img(emblemUrl, emblemFileName)
            break
    
        draw = ImageDraw.Draw(imageRaw)
        emblemImg = Image.open(emblemFileName)  # .resize([379,77])
        imageRaw.paste(emblemImg, [50, 20])
        draw.text([145, 25], args,
                font=玩家名字_智谋, fill='white', direction=None)
        x1,y1=玩家名字_智谋.getsize(args)
        上次在线时间 = get_activity_time(info['profile']['data']['dateLastPlayed'])

        seasonLevel = get_season_level_from_profile(info)
        draw.text([145, 25+y1+5], f'赛季等级: {seasonLevel}',
                font=声明_智谋, fill='white', direction=None)
        x2,y2=声明_智谋.getsize('赛季等级')
        draw.text([145, 25+y1+y2+5+5], f'上次活动: {上次在线时间}',
                font=声明_智谋, fill='white', direction=None)

        x,y = 声明_智谋.getsize('小日向异域武器皮肤查询')
        draw.text([524-x, 116-y], '小日向异域武器皮肤查询',
                font=声明_智谋, fill='white', direction=None)



        msg = f'小日向异域武器皮肤查询'
        x, y = 玩家名字_智谋.getsize(msg)
        x = 524+int((IMAGEX-524-x)/2)
        y = 30+int((96-y)/2)
        draw.text([x, y-10], msg,
                font=玩家名字_智谋, fill='white', direction=None)

        
        iconSingleX,iconSingleY = 42,42
        tempX = 50
        tempY = 180-间隔块长度
        gap = (单块长度-iconSingleY)//2


        奇数颜色 = '#292929'
        偶数颜色 = '#1F1F1F'
        色块宽度= 6
        奇数块 = Image.new('RGB', [IMAGEX, 单块长度], 奇数颜色)
        偶数块 = Image.new('RGB', [IMAGEX, 单块长度], 偶数颜色)
        红块 = Image.new('RGB', [色块宽度, iconSingleY], red)
        蓝块 = Image.new('RGB', [色块宽度, iconSingleY], blue)
        
        
        for weaponType,weapons in skinsData.items():
            
            tempX = 50
            imageRaw.paste(皮肤Icon,[tempX,get_mid_height(tempY,tempY+间隔块长度,36)])
            tempX += 44
            fontX,fontY = font_24.getsize(weaponType)
            yLocation = get_mid_height(tempY,tempY+间隔块长度,fontY)
            draw.text([tempX, yLocation], weaponType,
                font=font_24, fill='white', direction=None)
            weaponCount = 0
            tempY+=间隔块长度
            tempX = 50
            for weapon in weapons:
                weaponCount+=1
                if (weaponCount % 5) == 1:
                    tempX = 50
                    tempY+=单块长度 if weaponCount !=1 else 0
                    if (weaponCount // 5) % 2 == 1:
                        imageRaw.paste(奇数块,[0,tempY])
                    else:
                        imageRaw.paste(偶数块,[0,tempY])
                    




                weaponHash = weapon['hash']
                weaponIcon = weapon['icon']
                weaponname = weapon['name'].replace('_','/')
                weaponHighResIcon = weapon['highResIcon']
                weaponScreenShot = weapon['screenshot']
                weaponAcquired = weapon['acquired']
                
                icon = Image.open(weaponIcon).resize([iconSingleX,iconSingleY])
                if not weaponAcquired:
                    icon = get_grey_img(icon)
                imageRaw.paste(icon,[tempX,tempY+gap])
                tempX+=iconSingleX+10
                imageRaw.paste(蓝块 if weaponAcquired else 红块,[tempX,tempY+gap])
                tempX+=色块宽度+10
                draw.text([tempX, tempY+gap], weaponname,
                font=声明_智谋, fill='white', direction=None)
                tempX+=140
            tempY+=单块长度



        name = time.time()
        path = os.path.join(os.getcwd(), 'res', 'destiny2',
                            'cache', f'皮肤_{name}.png')
        imageRaw.save(path, 'png')
        append = f'[CQ:image,file=file:///{path}]'
        await session.send(f'{append}', at_sender=False)

    except Exception as e:
        await session.send(f'获取失败，{e}', at_sender=True)