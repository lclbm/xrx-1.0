import nonebot
from nonebot import RequestSession, on_request, on_command, CommandSession, on_notice, NoticeSession, MessageSegment
from hoshino import Service, priv
import aiocqhttp
import re
from hoshino.service import sucmd
import hoshino
import asyncio
import os
import json
from ..test.query import write_json

购买记录 = {}
购买记录_path = os.path.join(os.getcwd(), 'res', 'destiny2', '购买记录.json')

one = 2287326985
two = 2933986918
three = 3555747646
four = 2117336792
five = 3542782278
six = 3635409731
seven = 3566266406
night = 3563627090
ten = 1306821650
botDict = {
    1: one,
    2: two,
    3: three,
    4: four,
    5: five,
    6: six,
    7: seven,
    9: night,
    10: ten
}
botQQList = [one, two, three, four, five, six, seven, night, ten]
messageGroupList = [827529117, 666126096]
messageGroup = 827529117
messageGroup2 = 666126096

# one = 1281357456
# two = 2933986918
# messageGroup = 766202127


def 购买记录write_json():
    global 购买记录
    with open(购买记录_path, 'w', encoding='utf-8') as f:
        # 设置不转换成ascii  json字符串首缩进
        f.write(json.dumps(购买记录, ensure_ascii=False, indent=2))


def 购买记录read_json():
    global 购买记录
    try:
        if os.path.exists(购买记录_path):
            with open(购买记录_path, 'r', encoding='utf-8') as f:
                购买记录 = json.load(f)
        else:
            购买记录write_json()
    except:
        pass


购买记录read_json()

sv = Service('群组')

#
# @sv.on_message('group')
# async def handle_group_message(bot, event: aiocqhttp.Event):
#     print(event)
#     if event.raw_message == '测试测试':
#         await bot.send_group_msg(self_id=event.self_id, group_id=messageGroup, message=绑定帮助)

group_list = {}
group_add = {}

# @on_notice('group_decrease')
# async def group_member_decrease(session:NoticeSession):
#     ev=session.event
#     user_id = ev.user_id
#     try:
#         await session.send(f'（{user_id}）走了...')
#     except:
#         pass


@on_request('group.add')
async def handle_group_add(session: RequestSession):
    ev = session.event
    if ev.self_id != night:
        return None
    if ev.group_id not in messageGroupList:
        return None
    user_id = ev.user_id
    try:
        user_info = await session.bot.get_stranger_info(user_id=user_id,
                                                        self_id=ev.self_id)
        nickname = user_info['nickname']
    except Exception as e:
        nickname = f'{e}'
    at = MessageSegment.at(614867321)
    await session.send(
        f'{at}\n👉收到1条加群请求\nQQ：{user_id}\n昵称：{nickname}\n{ev.comment}')


# @on_notice('group_increase')
# async def group_member_add(session: NoticeSession):
#     ev = session.event
#     print(ev)
#     user_id = ev.user_id
#     self_id = ev.self_id
#     at = MessageSegment.at(user_id)
#     try:
#         #1号机进了2号机的群
#         if self_id == two and user_id == one:
#             await session.bot.set_group_leave(self_id=one,group_id=ev.group_id)
#         #2号机进了1号机的群
#         if self_id == one and user_id == two:
#             await session.bot.set_group_leave(self_id=two,group_id=ev.group_id)

#     except:
#         pass


@on_request('group.invite')
async def handle_group_invite(session: RequestSession):
    print('收到邀请收到邀请收到邀请收到邀请收到邀请')
    ev = session.event
    # if ev.self_id == one:
    #     return None
    print(ev)
    try:
        try:
            group_info = await session.bot.get_group_info(group_id=ev.group_id,
                                                          self_id=ev.self_id)
            group_name = group_info["group_name"]
        except Exception as err:
            group_name = f'[获取失败]'

        group_id = ev.group_id
        at = MessageSegment.at(614867321)
        at2 = MessageSegment.at(ev.user_id)

        # if ev.self_id !=six:
        #     await session.bot.send_group_msg(self_id=ev.self_id, group_id=messageGroup,
        #                                      message=f'群号：{ev.group_id}\n群名：{group_name}\n方式：{ev.sub_type}\n邀请人：{at2}\n❗请不要拉小日向1/2/3/4/5/6号机，请邀请9号机')
        #     await session.bot.send_group_msg(self_id=ev.self_id, group_id=messageGroup2,
        #                                      message=f'群号：{ev.group_id}\n群名：{group_name}\n方式：{ev.sub_type}\n邀请人：{at2}\n❗请不要拉小日向1/2/3/4/5/6号机，请邀请9号机')
        #     return None

        group_list[ev.group_id] = {
            'flag': f'{ev.flag}',
            'sub_type': f'{ev.sub_type}',
            'group_name': f'{group_name}',
            'user_id': f'{ev.user_id}',
            'self_id': f'{ev.self_id}'
        }
        # comment = ev.comment
        length = len(group_list)
        print(ev)

        # if ev.self_id == one:
        #     print('enterif')
        #     await session.bot.send_group_msg(self_id=ev.self_id, group_id=messageGroup,
        #                                     message=f'{at2}目前1号机已经满额啦，请尝试拉2号机哈\n❗群号：{group_id}\n❗群名：{group_name}\n')
        #     print('通知发送成功')

        #     await session.bot.set_group_add_request(flag=ev.flag, sub_type=ev.sub_type, approve=False, reason='请邀请小日向2号机')
        #     print('拒绝成功')

        #     del group_list[int(group_id)]
        #     return None
        # else:
        try:
            await session.bot.send_group_msg(
                self_id=ev.self_id,
                group_id=messageGroup,
                message=
                f'{at}\n👉收到1条群组请求\n群号：{ev.group_id}\n群名：{group_name}\n方式：{ev.sub_type}\n邀请人：{at2}\n目前剩余{length}条请求未处理\n如果该请求未自动同意请联系群主'
            )
            await session.bot.send_group_msg(
                self_id=ev.self_id,
                group_id=messageGroup2,
                message=
                f'{at}\n👉收到1条群组请求\n群号：{ev.group_id}\n群名：{group_name}\n方式：{ev.sub_type}\n邀请人：{at2}\n目前剩余{length}条请求未处理\n如果该请求未自动同意请联系群主'
            )
        except:
            ...

        group_id = str(ev.group_id)
        if group_id in 购买记录 and 购买记录[group_id]['days'] >= 0:
            print('Test')

            try:

                await session.bot.set_group_add_request(self_id=ev.self_id,
                                                        flag=ev.flag,
                                                        sub_type=ev.sub_type,
                                                        approve=True)
                await asyncio.sleep(1)
                print('邀请成功邀请成功邀请成功邀请成功邀请成功邀请成功')
                await session.bot.send_group_msg(
                    self_id=ev.self_id,
                    group_id=messageGroup,
                    message=
                    f'{at2}该群已授权，已自动同意\n✅群号：{group_id}\n✅群名：{group_name}')
                await session.bot.send_group_msg(
                    self_id=ev.self_id,
                    group_id=messageGroup2,
                    message=
                    f'{at2}该群已授权，已自动同意\n✅群号：{group_id}\n✅群名：{group_name}')

            except Exception as err:
                await session.bot.send_group_msg(
                    self_id=ev.self_id,
                    group_id=messageGroup,
                    message=
                    f'{at2}\n❗群号：{group_id}\n❗群名：{group_name}\n小日向为你处理失败了呢，邀请一次后请等待10分钟左右哦。'
                )
                await session.bot.send_group_msg(
                    self_id=ev.self_id,
                    group_id=messageGroup2,
                    message=
                    f'{at2}\n❗群号：{group_id}\n❗群名：{group_name}\n小日向为你处理失败了呢，邀请一次后请等待10分钟左右哦。'
                )
            finally:
                del group_list[int(group_id)]

        # await session.bot.send_private_msg(self_id=ev.self_id, user_id=614867321,
        #                                    message=f'收到group_request\n{comment}\n剩余{length}条请求未处理')

        # user_id = ev.user_id
        # user_info = await session.bot.get_stranger_info(user_id=user_id)
        # nickname = user_info['nickname']

    except Exception as e:
        await session.bot.send_group_msg(
            self_id=ev.self_id,
            group_id=messageGroup,
            message=f'{at}\n👉收到1条群组请求\n❗异常：{e}\n群号：{ev.group_id}\n')
        await session.bot.send_group_msg(
            self_id=ev.self_id,
            group_id=messageGroup2,
            message=f'{at}\n👉收到1条群组请求\n❗异常：{e}\n群号：{ev.group_id}\n')


@sucmd('quit', aliases=('退群', ), force_private=False)
async def quit_group(session: CommandSession):
    args = session.current_arg
    if (res := re.match(r'([1234567]) (\d+)', args)):
        try:
            await session.bot.set_group_leave(self_id=botDict[int(
                res.group(1))],
                                              group_id=int(res.group(2)))
            msg = '退出成功'
        except:
            msg = '退出失败'
    else:
        msg = '格式错误，退群 [1234567] <\d+>'

    await session.send(msg, at_sender=True)


@sucmd('处理加群', force_private=False)
async def chuli(session: CommandSession):
    try:
        ev = session.event
        if ev.self_id != night:
            return None
        if ev.user_id != 614867321:
            raise Exception('只有管理员才有权限处理加群')
        if session.current_arg:
            res = re.match(r'(\d+) *([01]) *(.+)?', session.current_arg)
            group_id = int(res.group(1))
            approve = True if int(res.group(2)) == 1 else False
            flag = group_list[group_id]['flag']
            sub_type = group_list[group_id]['sub_type']
            group_name = group_list[group_id]['group_name']
            self_id = group_list[group_id]['self_id']
            comment = res.group(3)
            at2 = MessageSegment.at(group_list[group_id]['user_id'])
            del group_list[group_id]
            try:
                if approve:
                    await session.bot.set_group_add_request(self_id=self_id,
                                                            flag=flag,
                                                            sub_type=sub_type,
                                                            approve=approve)
                    await session.send(
                        f'{at2}已同意\n✅群号：{group_id}\n✅群名：{group_name}')
                else:
                    await session.bot.set_group_add_request(self_id=self_id,
                                                            flag=flag,
                                                            sub_type=sub_type,
                                                            approve=approve,
                                                            reason=comment)
                    await session.send(
                        f'{at2}已拒绝\n❌群号：{group_id}\n❌群名：{group_name}\n拒绝理由：{comment}'
                    )

            except Exception as e:
                await session.bot.send_group_msg(
                    group_id=messageGroup,
                    message=f'处理失败\n❗群号：{group_id}\n❗群名：{group_name}\n{e}',
                    self_id=self_id)
        else:
            group_list.clear()
    except Exception as e:
        await session.send(f'{e}')


@sucmd('查询加群', force_private=False)
async def chaxun(session: CommandSession):
    try:
        print(group_list)
        ev = session.event
        if ev.self_id != night:
            return None
        num = 0
        msg = ''
        for key, value in group_list.items():
            group_name = value['group_name']
            sub_type = value['sub_type']
            user_id = value['user_id']
            msg += f'👉{key}\n{group_name}\n邀请人：{user_id}\n'
            num += 1
        await session.send(message=f'{msg}处理加群 [群号] [01]')
    except Exception as e:
        await session.send(f'{e}')


#
#
# @on_request('group.add')
# async def handle_group_invite(session: RequestSession):
#     if session.ctx['user_id'] in nonebot.get_bot().config.SUPERUSERS:
#         await session.approve()
#     else:
#         await session.reject(reason='邀请入群请联系维护组')


@on_notice('notify.poke')
async def group_poke_me(session: NoticeSession):
    ev = session.event
    print(ev)
    try:
        if ev.target_id == ev.self_id:
            msg = f'[CQ:poke,qq={ev.user_id}]'
            await session.send(msg)
    except:
        pass


@sucmd('删除授权', force_private=False)
async def del_shouquan(session: CommandSession):
    try:
        ev = session.event
        if ev.self_id != night:
            return None
        if session.current_arg:
            if (res := re.match(r'(\d+)', session.current_arg)):
                group_id = str(res.group(1))
                if group_id in 购买记录:
                    del 购买记录[group_id]
                    购买记录write_json()
                    await session.send(f'删除成功', at_sender=True)
                else:
                    raise Exception('需要删除授权的群号不在授权记录内')

            else:
                raise Exception('请输入删除授权的群号')

        else:
            raise Exception('请输入删除授权的群号')

    except Exception as e:
        await session.send(f'\n{e}', at_sender=True)


@sucmd('checkcheck', force_private=False)
async def _(session: CommandSession):
    try:
        ev = session.event
        if ev.self_id != night:
            return None

        GROUP_DICT = {}
        for botqq in botDict.values():
            try:
                groupDict = await session.bot.get_group_list(self_id=botqq)
            except:
                continue
            for groupInfo in groupDict:
                group_id = groupInfo['group_id']
                if group_id in GROUP_DICT:
                    GROUP_DICT[group_id].add(botqq)
                else:
                    GROUP_DICT[group_id] = set([botqq])
        
        open('testtest.txt','w').write(str(GROUP_DICT))
        for group_id, value in GROUP_DICT.items():
            if len(value) > 1:
                print(group_id, value)

    except Exception as e:
        await session.send(f'\n{e}', at_sender=True)


@sucmd('comecome', force_private=False)
async def _(session: CommandSession):
    try:
        ev = session.event
        if ev.self_id != night:
            return None

        GROUP_DICT = {}
        for botqq in botDict.values():
            try:
                groupDict = await session.bot.get_group_list(self_id=botqq)
            except:
                continue
            
            for groupInfo in groupDict:
                group_id = groupInfo['group_id']
                if group_id in GROUP_DICT:
                    GROUP_DICT[group_id].add(botqq)
                else:
                    GROUP_DICT[group_id] = set([botqq])
        open('testtest.txt','w').write(str(GROUP_DICT))

        for group_id, value in GROUP_DICT.items():
            if group_id in [827529117,666126096,924371658]:
                continue
            if len(value) > 1:
                for botqq in list(value)[1:]:
                    await session.bot.set_group_leave(self_id=botqq,
                                                      group_id=group_id)
                    await asyncio.sleep(3)

    except Exception as e:
        await session.send(f'\n{e}', at_sender=True)


@sucmd('授权检查', force_private=False)
async def check_shouquan(session: CommandSession):
    try:
        ev = session.event
        if ev.self_id != night:
            return None
        msgFlag = 1 if '通知' in ev.raw_message else 0
        quitFlag = 1 if '退群' in ev.raw_message else 0
        msgCount = 0
        quitCount = 0
        msgFailCount = 0
        quitFailCount = 0
        购买记录read_json()
        groupSumDict = {}
        for botqq in botDict.values():
            groupDict = await session.bot.get_group_list(self_id=botqq)
            groupSumDict[botqq] = groupDict
        write_json(groupSumDict, '群列表数据.json')

        quitCountDict = {
            one: 0,
            two: 0,
            three: 0,
            four: 0,
            five: 0,
            six: 0,
            seven: 0
        }

        with open('群操作日志.txt', 'w') as 日志:
            for botqq, groupDict in groupSumDict.items():
                for groupInfo in groupDict:
                    group_id = str(groupInfo['group_id'])
                    if str(group_id) not in 购买记录:
                        print(botqq, '退群', group_id)
                        quitCountDict[botqq] += 1

                        if msgFlag:
                            try:
                                await session.bot.send_group_msg(
                                    group_id=group_id,
                                    message=
                                    f'该群{group_id}的小日向授权已过期，如果需要续费请在小日向交流群内联系小日向开发者何志武223。',
                                    self_id=botqq)
                                # await session.bot.set_group_card(group_id=group_id,user_id=botqq,self_id=botqq,card='小日向授权已过期')
                                日志.write(f'[{botqq}] 退群 {group_id}\n')
                                await asyncio.sleep(2)
                            except:
                                msgFailCount += 1

                            msgCount += 1
                        if quitFlag:
                            try:
                                await session.bot.set_group_leave(
                                    self_id=botqq, group_id=group_id)
                                await asyncio.sleep(2)
                                quitCount += 1
                            except:
                                quitFailCount += 1

                    else:
                        daysLeft = 购买记录[group_id]['days']
                        groupType = 购买记录[group_id]['groupType']
                        if daysLeft <= 0 and groupType != 3:

                            quitCountDict[botqq] += 1
                            日志.write(f'[{botqq}] 退群 {group_id}\n')
                            if msgFlag:
                                try:
                                    await session.bot.send_group_msg(
                                        group_id=group_id,
                                        message=
                                        f'该群{group_id}的小日向授权已过期，如果需要续费请在小日向交流群内联系小日向开发者何志武223。',
                                        self_id=botqq)
                                    print(botqq, '退群', group_id)
                                    # await session.bot.set_group_card(group_id=group_id,user_id=botqq,self_id=botqq,card='小日向授权已过期')
                                    await asyncio.sleep(2)
                                except:
                                    msgFailCount += 1
                                msgCount += 1

                            if quitFlag:
                                try:
                                    await session.bot.set_group_leave(
                                        self_id=botqq, group_id=group_id)
                                    await asyncio.sleep(2)
                                    quitCount += 1
                                except:
                                    quitFailCount += 1
                        elif daysLeft <= 3 and groupType != 3:
                            print(botqq, '通知', group_id)
                            quitCountDict[botqq] += 1
                            日志.write(f'[{botqq}] 通知 {group_id} {daysLeft}天\n')
                            if msgFlag:
                                try:
                                    await session.bot.send_group_msg(
                                        group_id=group_id,
                                        message=
                                        f'该群{group_id}的小日向授权还有{daysLeft}天过期，如果需要续费请在小日向交流群内联系小日向开发者何志武223。',
                                        self_id=botqq)
                                    # await session.bot.set_group_card(group_id=group_id,user_id=botqq,self_id=botqq,card=f'小日向授权{daysLeft}天后过期')
                                    await asyncio.sleep(2)
                                except:
                                    msgFailCount += 1
                                msgCount += 1
                        # else:
                        #     # await session.bot.set_group_card()
                        #     await session.bot.call_action(action='set_group_card',group_id=group_id,user_id=botqq,self_id=botqq)
            groupDictToList = list(groupSumDict.values())
            botlen = len(botDict)
            for i in range(botlen):
                for j in range(i + 1, botlen):
                    for groupInfo in groupDictToList[i]:
                        groupId = groupInfo['group_id']
                        for groupInfoCheck in groupDictToList[j]:
                            groupIdToBeChecked = groupInfoCheck['group_id']
                            if groupId == groupIdToBeChecked:
                                日志.write(
                                    f'{i+1}{j+1}相同 {groupIdToBeChecked}\n')

        bot1GroupNum = len(groupSumDict[one])
        bot2GroupNum = len(groupSumDict[two])
        bot3GroupNum = len(groupSumDict[three])
        bot4GroupNum = len(groupSumDict[four])
        bot5GroupNum = len(groupSumDict[five])
        bot6GroupNum = len(groupSumDict[six])
        #bot7GroupNum = len(groupSumDict[seven])

        groupNumSum = bot1GroupNum+bot2GroupNum + \
            bot3GroupNum+bot4GroupNum+bot5GroupNum+bot6GroupNum
        groupNoticeNumSum = quitCountDict[one]+quitCountDict[two] + \
            quitCountDict[three]+quitCountDict[four] + \
            quitCountDict[five]+quitCountDict[six]
        msg = f'''
小日向1号机：{quitCountDict[one]}/{bot1GroupNum}
小日向2号机：{quitCountDict[two]}/{bot2GroupNum}
小日向3号机：{quitCountDict[three]}/{bot3GroupNum}
小日向4号机：{quitCountDict[four]}/{bot4GroupNum}
小日向5号机：{quitCountDict[five]}/{bot5GroupNum}
小日向6号机：{quitCountDict[six]}/{bot6GroupNum}
总计：{groupNoticeNumSum}/{groupNumSum}'''
        msg += f'\n通知：❌{msgFailCount}🔰{msgCount}' if msgFlag else ''
        msg += f'\n退群：❌{quitFailCount}🔰{quitCount}' if quitFlag else ''
        await session.send(msg, at_sender=True)
    except Exception as e:
        await session.send(f'\n{e}', at_sender=True)


@sucmd('添加授权', aliases=('授权添加'), force_private=False)
async def shouquan(session: CommandSession):
    try:
        ev = session.event
        if ev.self_id != night:
            return None
        if session.current_arg:
            if (res := re.match(r'(\d+) (\d+) ([01234])',
                                session.current_arg)):
                group_id = str(res.group(1))
                days = int(res.group(2))
                groupType = int(res.group(3))
                if group_id in 购买记录:
                    群信息 = 购买记录[group_id]
                    群信息['days'] += days
                    if groupType != 0:
                        群信息['groupType'] = groupType
                else:
                    购买记录[group_id] = {'days': days, 'groupType': groupType}
                    群信息 = 购买记录[group_id]
                购买记录write_json()
                await session.send(
                    f"\n添加成功\n群号: {group_id}\n天数: {群信息['days']}\n类型: {群信息['groupType']}",
                    at_sender=True)
                readyToDelete = []
                for group_id, value in group_list.items():
                    group_id = str(group_id)
                    if group_id in 购买记录 and 购买记录[group_id]['days'] >= 0:
                        flag = value['flag']
                        sub_type = value['sub_type']
                        self_id = value['self_id']
                        group_name = value['group_name']
                        at2 = MessageSegment.at(value['user_id'])
                        try:
                            await session.bot.set_group_add_request(
                                self_id=self_id,
                                flag=flag,
                                sub_type=sub_type,
                                approve=True)
                            await session.bot.send_group_msg(
                                self_id=self_id,
                                group_id=messageGroup,
                                message=
                                f'{at2}\n检测到该群的授权，已自动同意\n✅群号：{group_id}\n✅群名：{group_name}'
                            )
                            await session.bot.send_group_msg(
                                self_id=self_id,
                                group_id=messageGroup2,
                                message=
                                f'{at2}\n检测到该群的授权，已自动同意\n✅群号：{group_id}\n✅群名：{group_name}'
                            )

                        except Exception as e:
                            await session.bot.send_group_msg(
                                self_id=self_id,
                                group_id=messageGroup,
                                message=
                                f'{at2}\n检测到该群的授权，自动同意失败\n❗群号：{group_id}\n❗群名：{group_name}\n{e}'
                            )
                            await session.bot.send_group_msg(
                                self_id=self_id,
                                group_id=messageGroup2,
                                message=
                                f'{at2}\n检测到该群的授权，自动同意失败\n❗群号：{group_id}\n❗群名：{group_name}\n{e}'
                            )
                        readyToDelete.append(int(group_id))
                for group_id in readyToDelete:
                    del group_list[int(group_id)]

            else:
                raise Exception('添加授权 <群号> <天数> [类型]\n[类型]: 0无 1原 2半 3略 4测')

        else:
            raise Exception('添加授权 <群号> <天数> [类型]\n[类型]: 0无 1原 2半 3略 4测')

    except Exception as e:
        await session.send(f'\n{e}', at_sender=True)


@on_command('查询授权', aliases=('授权查询'), only_to_me=False)
async def cxsq(session: CommandSession):
    try:
        ev = session.event
        if session.current_arg:
            if (res := re.match(r'(\d+)', session.current_arg)):
                group_id = str(res.group(1))

            else:
                raise Exception('格式错误')
        else:
            group_id = ev.group_id

        print(group_id)
        if group_id == messageGroup:
            raise Exception('请回到自己的群内发送授权查询，或者在这里发送授权查询 群号进行查询')
        group_id = str(group_id)
        if group_id in 购买记录:
            群信息 = 购买记录[group_id]
            await session.send(
                f"\n群号: {group_id}\n天数: {群信息['days']}\n类型: {群信息['groupType']}",
                at_sender=True)
        else:
            raise Exception(f'未找到群号{group_id}的授权记录')

    except Exception as e:
        await session.send(f'\n{e}', at_sender=True)


@sucmd('摸鱼', force_private=False)
async def moyu(session: CommandSession):
    try:
        ev = session.event
        if ev.self_id != night:
            return None
        if session.current_arg:
            购买记录read_json()
            day = int(session.current_arg)
            for group_id in 购买记录:
                购买记录[group_id]['days'] -= day
            购买记录write_json()
            await session.send(f'已经为所有群摸了{day}天', at_sender=True)

    except Exception as e:
        await session.send(f'\n{e}', at_sender=True)


@sucmd('#reload', force_private=False)
async def reload(session: CommandSession):

    ev = session.event
    if ev.self_id != night:
        return None
    for qq in botQQList:
        try:
            await session.bot.call_action(action='reload_event_filter',
                                          self_id=qq)
        except:
            ...
    await session.send(f'事件过滤器已经重载', at_sender=True)
