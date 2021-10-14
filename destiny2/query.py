from langconv import *
import json
import asyncio
from typing import Dict, Tuple
import aiohttp
from weekly_milestones import destiny
import copy
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import datetime
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'hoshino', 'modules', 'test'))


destiny2DirPath = os.path.join(os.getcwd(), 'res', 'destiny2')
gambitDirPath = os.path.join(destiny2DirPath, '智谋')
emblemDirPath = os.path.join(destiny2DirPath, '名片')
iconSmallDirPath = os.path.join(destiny2DirPath, 'iconSmall')
emblemSmallDirPath = os.path.join(destiny2DirPath, '名片small')
pgcrDirPath = os.path.join(destiny2DirPath, 'pcgrImage')
metricIconDirPath = os.path.join(destiny2DirPath, 'metricIcon')
recordSealsIconDirPath = os.path.join(destiny2DirPath, 'recordSeals')
collectibleIconsDirPath = os.path.join(destiny2DirPath, 'collectibleIcons')
collectiblehighResIconsDirPath = os.path.join(
    destiny2DirPath, 'collectiblehighResIcons')
screenshotsDirPath = os.path.join(destiny2DirPath, 'screenshotsDirPath')
perkScreenshotsDirPath = os.path.join(
    destiny2DirPath, 'perkScreenshotsDirPath')
perkiconsDirPath = os.path.join(destiny2DirPath, 'perkiconsDirPath')


blue = '#03A9F4'
red = '#E8786E'


奖牌名_智谋 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=16)
奖牌数_智谋 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=40)
玩家名字_智谋 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=28)
声明_智谋 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=18)
font_24 = ImageFont.truetype('MYingHeiPRC-W7.ttf', size=24)


皮肤Icon = Image.open(os.path.join(destiny2DirPath, '皮肤.png')
                    ).convert('RGBA').resize([36, 36])
皮肤Icon = Image.composite(皮肤Icon, Image.new(
    'RGB', 皮肤Icon.size, '#303030'), 皮肤Icon)


titleDict = {
    "命中": "伤害",
    "射程": "射程",
    "穩定性": "稳定性",
    "操作性": "操控性",
    "填裝速度": "填装速度",
    "每分鐘發射量": "每分钟发射数",
    "彈匣": "弹匣",
    "瞄準輔助": "辅助瞄准",
    "物品欄容量": "物品栏空间",
    "瞄準焦距": "变焦",
    "後座力方向": "后坐力方向",
    "精準度": "精度",
    "充能時間": "搭弓时间",
    "拉弓時間": "蓄力时间",
    "揮舞速度": "挥舞速度",
    "彈藥容量": "弹药容量",
    "護手效率": "防御效率",
    "護手反抗": "防御抗性",
    "BounceIntensity": "BounceIntensity",
    "BounceDirection": "BounceDirection",
}


def Traditional2Simplified(sentence):
    '''
    将sentence中的繁体字转为简体字
    :param sentence: 待转换的句子
    :return: 将句子中繁体字转换为简体字之后的句子
    '''
    sentence = Converter('zh-hans').convert(sentence)
    return sentence


def get_activity_time(period):
    UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    utcTime = datetime.datetime.strptime(period, UTC_FORMAT)
    localtime = utcTime + datetime.timedelta(hours=8)
    now = datetime.datetime.now()
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


def get_bitmask(state: int, bit: int) -> bool:
    return True if (state & bit) > 0 else False


def get_emblem_acquired(emblemHash, collectibles):
    state = collectibles[str(emblemHash)]['state']
    return not get_bitmask(state, 1)


def get_collectible_acquired(collectibleHash, profileCollectibles, characterCollectibles):
    try:
        state = profileCollectibles[str(collectibleHash)]['state']
    except:
        state = characterCollectibles[str(collectibleHash)]['state']
    return not get_bitmask(state, 1)


def get_formatSize(size: int) -> str:
    try:
        bytes = float(size)
        kb = bytes / 1024
    except:
        return "格式错误"

    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%.2fG" % (G)
        else:
            return "%.2fM" % (M)
    else:
        return "%.2fkb" % (kb)


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


def num2str(num: int) -> str:
    return "{:,}".format(num)


def get_season_level_from_records(records):
    seasonLevel = records['1878734479']['intervalObjectives'][3]['progress']
    return num2str(seasonLevel)


def get_season_level_from_profile(info):
    level = int(info['profileProgression']['data']['seasonalArtifact']
                ['powerBonusProgression']['currentProgress'])//100000+1
    return num2str(level)


def get_mid_height(topY: int, bottomY: int, height: int) -> int:
    return int(topY+(bottomY-topY-height)/2)


async def get_dict_from_url(url: str) -> dict:
    async with aiohttp.request("GET", url) as r:
        response = await r.text(encoding="utf-8")
        return json.loads(response)


async def requests_url(url: str) -> dict:
    async with aiohttp.request("GET", url) as r:
        response = await r.text(encoding="utf-8")
        return response


async def dowload_img(url, path):
    if os.path.exists(path):
        return
    if url.startswith('/common/'):
        url = 'https://www.bungie.net' + url
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        content = await response.read()
    with open(path, 'wb') as f:
        f.write(content)


def seconds_to_hours(seconds: int) -> float:
    return int(seconds/3600*10)/10


def get_grey_img(img):
    return img.convert('L')


async def get_activitiesModeTime_dict(membershipType, membershipId, characterId):
    print('start')
    timeDict = {'crucible': 0,
                'gambit': 0,
                'raid': 0,
                'story': 0,
                'strikes': 0,
                'total': 0}
    page = 0
    while 1:
        res = await destiny.api.get_activity_history(membershipType, membershipId, characterId, count=250, mode=None, page=page)
        try:
            res = res['Response']['activities']
        except:
            res = []
        # 熔炉 剧情
        for activity in res:
            modes = activity['activityDetails']['modes']
            seconds = activity['values']['timePlayedSeconds']['basic']['value']
            if 18 in modes:
                timeDict['strikes'] += seconds
            elif 4 in modes:
                timeDict['raid'] += seconds
            elif 5 in modes or 32 in modes:
                timeDict['crucible'] += seconds
            elif 64 in modes:
                timeDict['gambit'] += seconds
            else:
                timeDict['story'] += seconds

        if len(res) < 250:

            timeDict['total'] += timeDict['story'] + timeDict['strikes'] + \
                timeDict['raid'] + timeDict['crucible']+timeDict['gambit']
            print(timeDict)
            break
        page += 1
    return timeDict

seasonsAndYearsDict = {
    '年三': {1743682818: '不朽赛季', 1743682819: '黎明赛季', 2809059425: '英杰赛季', 2809059424: '影临赛季'},
    '年四': {2809059427: '狂猎赛季', 2809059426: '天选赛季', 2809059429: '永夜赛季'}
}

classDict = {3655393761: '泰坦', 671679327: '猎人', 2271682572: '术士',
             '泰坦': 3655393761, '猎人': 671679327, '术士': 2271682572}

activitiesDictUrl = 'https://api.wastedondestiny.com/activities?membershipType={}&membershipId={}&gameVersion=2'
timeDictUrl = 'https://api.wastedondestiny.com/breakdown?membershipType={}&membershipId={}&gameVersion=2&characterId={}&page={}'


basicDataNameToImgName = {'传承成就分': '账户banner',
                          '当前成就分': '账户banner',
                          '熔炉胜场': '熔炉banner',
                          '智谋胜场': '智谋banner',
                          '打击列表场次': '打击banner',
                          '公会经验值': '账户banner'}

# basicDataNameToImgColor = {'传承成就分': '#454545',
#                           '当前成就分': '#C6C6C6',
#                           '熔炉胜场': '#C9352E',
#                           '智谋胜场': '#4B997F',
#                           '打击列表场次': '#606DB2',
#                           '公会经验值': '账户banner'}


basicDataNameToImgColor = {'传承成就分': '#E7D1AC',
                           '当前成就分': '#DEA089',
                           '熔炉胜场': '#D46D68',
                           '智谋胜场': '#84A091',
                           '打击列表场次': '#4D809D',
                           '公会经验值': '账户banner'}


modeColorDict = {
    '熔炉': '#FF5D39',
    '智谋': '#239A72',
    '突袭': '#7F54A2',
    '打击': '#545F9C',
    '剧情': '#DCCE58', }


async def get_shengya_data(records: dict, profile: dict, charactersDict: dict, membershipType, membershipId, allCharactersList: list) -> tuple:
    """
    检索玩家的生涯数据，并返回一些处理好的dict数据类型

    Args:
        records (dict): 
                    getProfile - 900
        profile (dict): 
                    getProfile - 100
        characterDict (dict): 
                    getProfile - 200
        membershipType ([int,str]):
                    类型
        membershipId ([int,str]):
                    id

    Returns:
        返回玩家tuple数据，包含:
            basicDataToReturn (dict):
                            一些基本的生涯数据
            seasonsDictToReturn (dict):
                            玩家赛季历程(bool)
            activitiesTimeToReturn (dict):
                            最近15天每日活动时间(小时)
            characterTimeDictToReturn (dict):
                            每个职业每个模式的活动时长(小时)
    """

    profileRecordsData = records['data']
    userInfo = profile['data']
    传承成就分 = profileRecordsData['legacyScore']
    当前成就分 = profileRecordsData['activeScore']
    熔炉胜场 = profileRecordsData['records']['3561485187']['intervalObjectives'][0]['progress']
    智谋胜场 = profileRecordsData['records']['1676011372']['objectives'][0]['progress'] + \
        profileRecordsData['records']['2129704137']['objectives'][0]['progress'] + \
        profileRecordsData['records']['89114360']['objectives'][0]['progress']
    打击列表 = profileRecordsData['records']['2780814366']['objectives'][2]['progress']
    公会经验值 = profileRecordsData['records']['2505589392']['intervalObjectives'][0]['progress']

    basicDataToReturn = {
        '当前成就分': num2str(当前成就分),
        '传承成就分': num2str(传承成就分),
        '熔炉胜场': num2str(熔炉胜场),
        '智谋胜场': num2str(智谋胜场),
        '打击列表场次': num2str(打击列表),
        # '公会经验值': num2str(公会经验值),
    }

    seasonHashes = userInfo['seasonHashes']
    seasonsDictToReturn = {}
    for yearName in seasonsAndYearsDict:
        seasonsDictToReturn[yearName] = {}
        seasonsDict = seasonsAndYearsDict[yearName]
        for seasonHash in seasonsDict:
            seasonName = seasonsDict[seasonHash]
            if seasonHash in seasonHashes:
                seasonsDictToReturn[yearName][seasonName] = True
            else:
                seasonsDictToReturn[yearName][seasonName] = False

    activities = await get_dict_from_url(activitiesDictUrl.format(membershipType, membershipId))
    activitiesTimeToReturn = {'response': {},
                              'max': 0.0, 'min': 0.0, 'total': 0.0}

    for key in activities['response'].keys():
        # return Hour
        max = activitiesTimeToReturn['max']
        min = activitiesTimeToReturn['min']
        hours = seconds_to_hours(activities['response'][key])
        activitiesTimeToReturn['total'] += hours
        activitiesTimeToReturn['response'][key] = hours
        max = max if max > hours else hours
        min = min if min < hours else hours
        activitiesTimeToReturn['max'] = max
        activitiesTimeToReturn['min'] = min

    characterTimeDictToReturn = {}

    characterTimeDictToReturn['综合'] = {
        '熔炉': 0,
        '智谋': 0,
        '突袭': 0,
        '剧情': 0,
        '打击': 0,
        '总计': 0
    }
    for characterId in allCharactersList:
        try:
            className = classDict[charactersDict[characterId]['classHash']]
        except:
            className = '已删除角色'
        if className not in characterTimeDictToReturn:
            characterTimeDictToReturn[className] = {
                '熔炉': 0,
                '智谋': 0,
                '突袭': 0,
                '剧情': 0,
                '打击': 0,
                '总计': 0
            }

        timeDict = await get_activitiesModeTime_dict(membershipType, membershipId, characterId)
        print(timeDict)
        characterTimeDictToReturn[className]['熔炉'] += timeDict['crucible']
        characterTimeDictToReturn[className]['智谋'] += timeDict['gambit']
        characterTimeDictToReturn[className]['突袭'] += timeDict['raid']
        characterTimeDictToReturn[className]['剧情'] += timeDict['story']
        characterTimeDictToReturn[className]['打击'] += timeDict['strikes']
        characterTimeDictToReturn[className]['总计'] += timeDict['total']

    for value in characterTimeDictToReturn.values():
        for mode in value:
            seconds = value[mode]
            characterTimeDictToReturn['综合'][mode] += seconds
            value[mode] = seconds_to_hours(seconds)

    for mode in characterTimeDictToReturn['综合']:
        seconds = characterTimeDictToReturn['综合'][mode]
        characterTimeDictToReturn['综合'][mode] = seconds_to_hours(seconds)

    return basicDataToReturn, seasonsDictToReturn, activitiesTimeToReturn, characterTimeDictToReturn

currentActivityDataShowDict = {
    # 玻璃宝库
    3881495763:
    {
        'hash': [{'hash': '2506886274', 'banner': '突袭banner'}]
    },

    # 默认
    'default':
    {
        'hash': [{'hash': '3981543480', 'banner': '账户banner'}]
    }
}


def get_metric(hashid: str, metrics: dict):
    hashid = str(hashid)
    progress = metrics[hashid]['objectiveProgress']['progress']
    return num2str(progress)


def get_localtime_from_period(timeStr: str):
    localtime = datetime.datetime.strptime(timeStr, '%Y-%m-%dT%H:%M:%SZ')
    localtime += datetime.timedelta(hours=8)
    return localtime


def get_recent_play_characterId(characterActivities):
    characterIdPlayNow = ''
    for characterId, characterActivityInfo in characterActivities.items():
        localtime = get_localtime_from_period(
            characterActivityInfo['dateActivityStarted'])

        if characterIdPlayNow:
            diff = localtime - lastCharacterPlayTime
            if diff.seconds > 0 and diff.days >= 0:
                characterIdPlayNow = characterId
                lastCharacterPlayTime = localtime

        else:
            characterIdPlayNow = characterId
            lastCharacterPlayTime = localtime

    return characterIdPlayNow


async def get_partyMemberInfo(partyMembers: dict, currentActivityHash: int):
    currentActivityInfo = await destiny.decode_hash(currentActivityHash, 'DestinyActivityDefinition')
    currentActivityName = currentActivityInfo['displayProperties']['name']
    activityTypeHash = currentActivityInfo['activityTypeHash']
    activityTypeInfo = await destiny.decode_hash(activityTypeHash, 'DestinyActivityTypeDefinition')
    try:
        activityTypeName = activityTypeInfo['displayProperties']['name']
    except:
        activityTypeName = '轨道'

    if currentActivityHash in currentActivityDataShowDict:
        dataToShowName = currentActivityHash
    else:
        dataToShowName = 'default'
    dataToShowLen = len(currentActivityDataShowDict[dataToShowName]['hash'])
    try:
        pgcrImage = currentActivityInfo['pgcrImage']
        pgcrImageUrl = 'https://www.bungie.net' + pgcrImage
        pgcrFilePath = os.path.join(pgcrDirPath, f'{currentActivityHash}.png')
        await dowload_img(pgcrImageUrl, pgcrFilePath)
    except:
        pgcrFilePath = ''

    partyMembersLen = len(partyMembers)

    basicData = [currentActivityName, activityTypeName,
                 pgcrFilePath, partyMembersLen, dataToShowLen]

    partyMemberDataList = []
    for partyMemberInfo in partyMembers:
        membershipId = partyMemberInfo['membershipId']
        status = partyMemberInfo['status']
        status = '队长' if get_bitmask(status, 8) else '队员'

        for membershipType in [3, 1, 2]:
            try:
                membershipInfo = await destiny.api.get_profile(membershipType, membershipId,
                                                               [100, 104, 200, 204, 1100])
                membershipInfo = membershipInfo['Response']
                break
            except:
                continue

        profileName = membershipInfo['profile']['data']['userInfo']['displayName']
        seasonLevel = get_season_level_from_profile(membershipInfo)
        metrics = membershipInfo['metrics']['data']['metrics']

        characterIdPlayNow = get_recent_play_characterId(
            membershipInfo['characterActivities']['data'])

        # if characterActivityInfo['currentActivityHash']:
        #     characterIdPlayNow = characterId
        #     break
        characterDict = membershipInfo['characters']['data']

        try:
            titleRecordHash = characterDict[characterIdPlayNow]['titleRecordHash']
            titleRecord = await destiny.decode_hash(titleRecordHash, 'DestinyRecordDefinition')
            title = titleRecord['displayProperties']['name']
        except:
            title = ''
        className = classDict[characterDict[characterIdPlayNow]['classHash']]

        emblemBackgroundPath = characterDict[characterIdPlayNow]['emblemPath']
        emblemHash = characterDict[characterIdPlayNow]['emblemHash']
        emblemUrl = 'https://www.bungie.net' + emblemBackgroundPath
        emblemFilePath = os.path.join(emblemSmallDirPath, f'{emblemHash}.png')
        await dowload_img(emblemUrl, emblemFilePath)
        partyMemberTempData = {
            'name': profileName,
            'level': seasonLevel,
            'className': className,
            'title': title,
            'emblem': emblemFilePath,
            'status': status,
            'dataList': []
        }

        for metricHashInfo in currentActivityDataShowDict[dataToShowName]['hash']:
            metricHashId = metricHashInfo['hash']
            metricInfo = await destiny.decode_hash(metricHashId, 'DestinyMetricDefinition')
            metricName = metricInfo['displayProperties']['name']
            progress = get_metric(metricHashId, metrics)

            metricIconPath = os.path.join(
                destiny2DirPath, f"{metricHashInfo['banner']}.png")
            tempDict = {
                'name': metricName,
                'icon': metricIconPath,
                'progress': progress
            }

            partyMemberTempData['dataList'].append(tempDict)

        partyMemberDataList.append(partyMemberTempData)

    return partyMemberDataList, basicData


sealsList = read_json(os.path.join(recordSealsIconDirPath, 'sealsList.json'))
weaponSkinsDict = read_json(os.path.join(
    destiny2DirPath, 'weaponSkinsDict.json'))
print


def check_seals_completion(records):
    sealsDataToReturn = copy.deepcopy(sealsList)
    for i in range(len(sealsDataToReturn)):
        sealsDict = sealsDataToReturn[i]
        for recordHash, value in sealsDict.items():
            name = value['name']
            recordData = records[recordHash]
            progress = recordData['objectives'][0]['progress']
            completionValue = recordData['objectives'][0]['completionValue']
            if progress >= completionValue:
                value['icon'] = os.path.join(
                    recordSealsIconDirPath, f'{recordHash}_0.png')
            else:
                value['icon'] = os.path.join(
                    recordSealsIconDirPath, f'{recordHash}_1.png')
            value['progress'] = progress
            value['completionValue'] = completionValue
    return sealsDataToReturn


def check_weaponsskins_completion(profileCollectibles, characterCollectibles):
    weaponsDictToReturn = copy.deepcopy(weaponSkinsDict)
    for weaponType, weapons in weaponsDictToReturn.items():
        for weapon in weapons:
            weaponHash = weapon['hash']
            weaponname = weapon['name']
            weaponHighResIcon = weapon['highResIcon']
            weaponScreenShot = weapon['screenshot']
            weapon['acquired'] = get_collectible_acquired(
                weaponHash, profileCollectibles, characterCollectibles)

    return weaponsDictToReturn
