import json
import os
import re
root = os.getcwd()
root = os.path.join(root, 'res', 'destiny2', 'reply')
user_root = os.path.join(root, 'user')
group_root = os.path.join(root,  'group')


class Untie(Exception):
    '''当没有绑定时，抛出此异常'''
    # 自定义异常类型的初始化


class Untie_friend(Exception):
    '''当没有绑定时，抛出此异常'''
    # 自定义异常类型的初始化

    # def __init__(self, value, msg):
    # 返回异常类对象的说明信息

    def __str__(self):
        return f"你似乎想通过快捷方式查询朋友的数据，但你并没有绑定该朋友的队伍码。\n请输入绑定 【昵称】【队伍码】以绑定你朋友的队伍码"


def read_json(file):
    dict_temp = {}
    try:
        with open(file, 'r', encoding='utf-8') as f:
            dict_temp = json.load(f)
            return dict_temp
    except:
        return dict_temp


def get_tie_urself(path):
    dict_temp = {}
    if not os.path.exists(path):
        raise Exception(
            '通过这种方式查询需要先绑定自己的队伍码哦，或者使用队伍码/用户名来查询。\n对我说👉绑定 7656xxx👈来绑定吧')
    dict_temp = read_json(path)
    if '_self_' in dict_temp and dict_temp['_self_']['type'] == '绑定':
        return dict_temp['_self_']['msg']
    else:
        raise Exception(
            '通过这种方式查询需要先绑定自己的队伍码哦，或者使用队伍码/用户名来查询。\n对我说👉绑定 7656xxx👈来绑定吧')


def get_tie_from_file(path, name):
    dict_temp = {}
    if os.path.exists(path):
        dict_temp = read_json(path)
    if name in dict_temp and dict_temp[name]['type'] == '绑定':
        return dict_temp[name]['msg']


def gethardlink(session):
    msg = session.ctx
    user_id = msg['user_id']
    group_id = msg['group_id']
    file_all = os.path.join(root, 'All.json')
    file_group = os.path.join(group_root, f'{group_id}.json')
    file_user = os.path.join(user_root, f'{user_id}.json')
    checkmsg = session.current_arg
    dict_temp = {}

    if checkmsg:  # 如果文本不为空
        res = re.match(r'(\w*) *(术士|猎人|泰坦) *', checkmsg)

        if res:
            print(res.groups())
            if res.group(1):  # 有名字
                id = get_tie_from_file(file_user, res.group(1))
                if id:
                    return f'{id} {res.group(2)}'
                id = get_tie_from_file(file_group, res.group(1))
                if id:
                    return f'{id} {res.group(2)}'
                id = get_tie_from_file(file_all, res.group(1))
                if id:
                    return f'{id} {res.group(2)}'
                return None

            else:  # 没有名字，查询自己的
                id = get_tie_urself(file_user)
                return f'{id} {res.group(2)}'
        else:
            id = get_tie_from_file(file_user, checkmsg)
            if id:
                return f'{id}'
            id = get_tie_from_file(file_group, checkmsg)
            if id:
                return f'{id}'
            id = get_tie_from_file(file_all, checkmsg)
            if id:
                return f'{id}'
            return None

    else:  # 文本为空
        return get_tie_urself(file_user)
