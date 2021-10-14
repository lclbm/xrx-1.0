
import re
import hoshino
from hoshino import Service, R
import asyncio
from nonebot import *
import sys
import os
import json
print(os.getcwd())
sys.path.append(os.getcwd())
sys.path.append('C:/HoshinoBot/hoshino/modules/add_info')
from a import *
from hoshino.service import sucmd


sv = hoshino.Service('add')
_bot = get_bot()


# @sv.on_command('绑定帮助')
# async def Help(session):
#     msg = '''待更新'''
#     await session.send(msg)

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


@sv.on_message('group')
async def check(*params):
    bot, ctx = (_bot, params[0]) if len(params) == 1 else params
    msg = get_msg(ctx)
    if msg:
        print(msg)
        await bot.send(ctx, msg)


@sv.on_command('添加全局')
async def add_info_all(session):
    try:
        msg = add_all(session.ctx)
        await session.send(msg, at_sender=True)
    except Exception as e:
        await session.send(f'{e}', at_sender=True)


# addReplyError = '小日向词库功能停用2周，请等待新版词库功能上线。'
# @sv.on_command('添加个人')
# async def add_info_user(session):
#     try:
#         msg = add_reply(session.ctx)
#         await session.send(msg, at_sender=True)
#     except Exception as e:
#         await session.send(f'{e}', at_sender=True)


# @sv.on_command('添加群组')
# async def add_info_group(session):
#     try:
#         msg = add_reply(session.ctx)
#         await session.send(msg, at_sender=True)
#     except Exception as e:
#         await session.send(f'{e}', at_sender=True)


# @sv.on_command('个人词库',)
# async def look_user(session):
#     try:
#         msg = lookup_user(session.ctx)
#         await session.send(msg, at_sender=True)
#     except Exception as e:
#         await session.send(f'{e}', at_sender=True)


# @sv.on_command('群组词库')
# async def look_group(session):
#     try:
#         msg = lookup_group(session.ctx)
#         await session.send(msg, at_sender=True)
#     except Exception as e:
#         await session.send(f'{e}', at_sender=True)


# @sv.on_command('全局词库')
# async def look_all(session):
#     try:
#         msg = lookup_all(session.ctx)
#         await session.send(msg, at_sender=True)
#     except Exception as e:
#         await session.send(f'{e}', at_sender=True)


# @sv.on_command('删除个人')
# async def delete_tie_user(session):
#     try:
#         msg = del_reply(session.ctx)
#         await session.send(msg, at_sender=True)
#     except Exception as e:
#         await session.send(f'{e}', at_sender=True)


# @sv.on_command('删除群组')
# async def delete_tie_group(session):
#     try:
#         msg = del_reply(session.ctx)
#         await session.send(msg, at_sender=True)
#     except Exception as e:
#         await session.send(f'{e}', at_sender=True)


@sv.on_command('删除全局')
async def delete_tie_all(session):
    try:
        msg = del_all(session.ctx)
        await session.send(msg, at_sender=True)
    except Exception as e:
        await session.send(f'{e}', at_sender=True)


@sv.on_command('绑定全局')
async def tieall(session):
    try:
        msg = tie_all(session.ctx)
        await session.send(msg, at_sender=True)
    except Exception as e:
        await session.send(f'{e}', at_sender=True)


@sv.on_command('绑定群组')
async def tiegroup(session):
    try:
        msg = tie_group(session.ctx)
        await session.send(msg, at_sender=True)
    except Exception as e:
        await session.send(f'{e}', at_sender=True)


@sv.on_command('绑定个人')
async def tieuser(session):
    try:
        msg = tie_user(session.ctx)
        await session.send(msg, at_sender=True)
    except Exception as e:
        await session.send(f'{e}', at_sender=True)


@sv.on_command('绑定')
async def tieurself(session):
    try:
        msg = tie_urself(session.ctx)
        await session.send(msg, at_sender=True)
    except Exception as e:
        await session.send(f'{e}', at_sender=True)




# @on_notice('notify.poke')
async def group_poke(session: NoticeSession):
    ev = session.event
    try:
        if str(ev.sender_id) in authorizedUserList['addUsersAuthorized'] :
            userId = str(ev.target_id)
            flag = addAuthorizedUser(userId)
            at = MessageSegment.at(userId)
            source = MessageSegment.at(ev.sender_id)
            if flag:
                await session.send(f'🎉词库管理员{source}已授予{at}添加词库的权限，请合理使用词库功能。')
            else:
                await session.send(f'词库管理员{source}已删除{at}添加词库的权限。')
    except Exception as e:
        await session.send(f'{e}')



@sucmd('词库授权', force_private=False)
async def addUsersAuthorized_async(session:CommandSession):
    try:
        ev = session.event
        userId = session.current_arg
        if (res := re.match(r' *\[CQ:at,qq=(\d+)\] *',userId)):
            userId = res.group(1)
        flag = addUsersAuthorized(str(userId))
        at = MessageSegment.at(userId)
        if flag:
            await session.send(f'{at}\n🎉已经允许你添加用户词库授权，你现在有权限增加/删除别人的词库授权，请勿滥用\n🎉戳戳别人试试吧')
        else:
            await session.send(f'{at}\n已经取消你添加词库授权的权限。')
    except Exception as e:
        await session.send(f'{e}', at_sender=True)


one = 2287326985
two = 2933986918
messageGroup = 827529117


@sucmd('#群列表获取', force_private=False)
async def grouplist_async(session:CommandSession):
    
    try:
        ev = session.event
        if ev.self_id == two:
            return None
        groupDictOne = await session.bot.get_group_list(self_id=one)
        groupDictTwo = await session.bot.get_group_list(self_id=two)
        groupList = []
        for i in groupDictTwo:
            group_id = i['group_id']
            groupList.append(group_id)
        print(groupDictTwo)
        购买记录 = read_json('购买记录.json')
        write_json(groupDictOne,'群列表1.json')
        write_json(groupDictTwo,'群列表2.json')
        print('success')
        count=0
        for i in groupDictOne:
            group_id = i['group_id']
            if str(group_id) not in 购买记录:
                await session.bot.set_group_leave(group_id=group_id,self_id=ev.self_id)
        
                count+=1
                print(count,'未找到购买记录')
            else:
                if group_id in groupList:
                    await session.bot.set_group_leave(group_id=group_id,self_id=one)
                count+=1
                print(count,'12号机重合退群')


    except Exception as e:
        await session.send(f'{e}', at_sender=True)
