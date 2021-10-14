import re
import os
import json
import requests
import random


root = os.getcwd()
root = os.path.join(root, 'res', 'destiny2', 'reply')
user_root = os.path.join(root, 'user')
group_root = os.path.join(root, 'group')
authorizedUserList = {}







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



authorizedUserListPath = os.path.join(root, '词库授权.json')
authorizedUserList = read_json(authorizedUserListPath)

def addAuthorizedUser(userId):
    if 'useAuthorized' not in authorizedUserList:
        authorizedUserList['useAuthorized'] = {}

    if userId in authorizedUserList['useAuthorized']:
        del authorizedUserList['useAuthorized'][userId]
        write_json(authorizedUserList,authorizedUserListPath)
        return 0
        
    authorizedUserList['useAuthorized'][userId] = {'count':0,'QA':[]}
    write_json(authorizedUserList,authorizedUserListPath)
    return 1


def addUsersAuthorized(userId):
    if 'addUsersAuthorized' not in authorizedUserList:
        authorizedUserList['addUsersAuthorized'] = []

    if userId in authorizedUserList['addUsersAuthorized']:
        authorizedUserList['addUsersAuthorized'].remove(userId)
        write_json(authorizedUserList,authorizedUserListPath)
        return 0
    else:
        authorizedUserList['addUsersAuthorized'].append(userId)
        write_json(authorizedUserList,authorizedUserListPath)
        return 1



def download_img(imgurl, name, mode):
    rsp = requests.get(imgurl)
    if rsp.status_code == 200:
        content = rsp.content
        # 注意下面open里面的mode是"wb+", 因为content的类型是bytes
        file_path = os.path.join(user_root, f'{name}.gif') if mode == 0 else os.path.join(
            group_root, f'{name}.gif')
        file_path = os.path.join(
            root, f'{name}.gif') if mode == 2 else file_path
        with open(file_path, "wb+") as f:
            f.write(content)
            return f'[CQ:image,file=file:///{file_path}]'
    return None


def add_reply(msg):
    raw_message = msg['raw_message']
    message = msg['message']
    user_id = msg['user_id']

    # if str(user_id) not in authorizedUserList['useAuthorized']:
    #     raise Exception('你还没有添加词库的权限，请加入小日向交流群联系开发者获得词库授权。')

    group_id = msg['group_id']
    raw_message = raw_message.replace('\r', r'\r')
    raw_message = raw_message.replace('\n', r'\n')
    res = re.match(
        r'添加(个人|群组) +[\(（【/](.+)[\)）】/] [\(（【/](.+)[\)）】/]', raw_message)
    if not res:
        raise Exception('格式错误，请输入词库帮助以查看相关教程')
    # 0是个人词库 1是群组词库
    file = os.path.join(user_root, f'{user_id}.json') if res.group(1) == '个人' else os.path.join(
        group_root, f'{group_id}.json')
    mode = 0 if res.group(1) == '个人' else 1
    dict_temp = {}
    if os.path.exists(file):  # 如果文件存在的话
        dict_temp = read_json(file)
    question = res.group(2)
    # [CQ:image,file=f46784e63445c8b7b62e06bbca04d608.image]
    answer = res.group(3)
    answer = answer.replace(r'\r', '\r')
    answer = answer.replace(r'\n', '\n')
    answer_res = re.match(r'.*\[CQ:image,file=(.+\.image)\].*', answer)
    # 返回的是f46784e63445c8b7b62e06bbca04d608.image
    if answer_res:  # 如果存在图片
        file_name = answer_res.group(1)
        for i in message:
            if i['type'] == 'image':
                file_name = i['data']['file']
                cqimg_file = download_img(
                    i['data']['url'], file_name, mode)
                if not cqimg_file:
                    raise Exception('保存图片时发生了错误，请重试')
                answer = answer.replace(
                    f'[CQ:image,file={file_name}]', cqimg_file)  # .img替换成了file:///
    if question in dict_temp:
        length = len(dict_temp[question]['msg'])
        dict_temp[question]['msg'].append(answer)
        length += 1
    else:
        dict_temp[question] = {'type': '自定义', 'msg': [answer]}
        length = 1
    write_json(dict_temp, file)
    # authorizedUserList['useAuthorized'][str(user_id)]['count'] += 1
    # authorizedUserList['useAuthorized'][str(user_id)]['QA'].append({'Q':question,'A':answer})
    # write_json(authorizedUserList,authorizedUserListPath)
    return(f'🎉词库添加成功，当前问题下有[{length}]个回答')


def add_all(msg):
    raw_message = msg['raw_message']
    message = msg['message']
    user_id = msg['user_id']
    if user_id not in [614867321,2181656404]:
        raise Exception('需要小日向的管理权限才可以修改全局词库')
    raw_message = raw_message.replace('\r', r'\r')
    raw_message = raw_message.replace('\n', r'\n')
    res = re.match(
        r'添加全局.*[\(（【/](.+)[\)）】/] [\(（【/](.+)[\)）】/] [\(（【/](.+)[\)）】/]', raw_message)
    if not res:
        raise Exception('格式错误，请输入词库帮助以查看相关教程')
    file = os.path.join(root, 'All.json')
    dict_temp = {}
    if os.path.exists(file):  # 如果文件存在的话
        dict_temp = read_json(file)
    question = res.group(1)
    # [CQ:image,file=f46784e63445c8b7b62e06bbca04d608.image]
    answer = res.group(2)
    answer = answer.replace(r'\r', '\r')
    answer = answer.replace(r'\n', '\n')
    if res.group(3) == '重定向':
        if answer in dict_temp:
            if 'alias' in dict_temp[answer]:
                dict_temp[answer]['alias'].append(question)
                write_json(dict_temp, file)
                return (f'重定向成功，已将{question}定向到{answer}\n{question}->{answer} Flag=0')
            else:
                dict_temp[answer]['alias'] = [question]
                write_json(dict_temp, file)
                return (f'重定向成功，已将{question}定向到{answer}\n{question}->{answer} Flag=1')
        else:
            raise Exception(f'重定向失败，请检查{answer}是否在词库中')

    answer_res = re.match(r'.*\[CQ:image,file=(.+\.image)\].*', answer)
    # 返回的是f46784e63445c8b7b62e06bbca04d608.image
    if answer_res:  # 如果存在图片
        file_name = answer_res.group(1)
        for i in message:
            if i['type'] == 'image':
                file_name = i['data']['file']
                cqimg_file = download_img(
                    i['data']['url'], file_name, 2)  # 2为全局
                if not cqimg_file:
                    return None
                answer = answer.replace(
                    f'[CQ:image,file={file_name}]', cqimg_file)  # .img替换成了file:///
    if question in dict_temp:
        length = len(dict_temp[question]['msg'])
        dict_temp[question]['msg'].append(answer)
        length += 1
    else:
        dict_temp[question] = {'type': res.group(3), 'msg': [answer]}
        length = 1
    write_json(dict_temp, file)
    return(f'🎉全局词库添加成功，当前问题下有[{length}]个回答')


def get_msg_from_msgdict(msg: list):
    length = len(msg)
    # keys = list(msg.keys())
    # key = keys[random.randint(0,length-1)]
    key = random.randint(0, length-1)
    return msg[key]


def get_msg(msg):
    user_id = msg['user_id']
    group_id = msg['group_id']
    checkmsg = msg['raw_message']
    file_all = os.path.join(root, 'All.json')
    file_group = os.path.join(group_root, f'{group_id}.json')
    file_user = os.path.join(user_root, f'{user_id}.json')
    dict_temp = {}
    if os.path.exists(file_all):  # 如果文件存在的话
        dict_temp = read_json(file_all)
        if checkmsg in dict_temp and dict_temp[checkmsg]['type'] != '绑定' :
            print(dict_temp[checkmsg]['msg'])
            return get_msg_from_msgdict(dict_temp[checkmsg]['msg'])
        for i in dict_temp:
            if 'alias' in dict_temp[i] and checkmsg in dict_temp[i]['alias']:
                return get_msg_from_msgdict(dict_temp[i]['msg'])
    # if os.path.exists(file_group):  # 如果文件存在的话
    #     dict_temp = read_json(file_group)
    #     if checkmsg in dict_temp and dict_temp[checkmsg]['type'] != '绑定' :
    #         print(dict_temp[checkmsg]['msg'])
    #         return get_msg_from_msgdict(dict_temp[checkmsg]['msg'])
    # if os.path.exists(file_user):  # 如果文件存在的话
    #     dict_temp = read_json(file_user)
    #     if checkmsg in dict_temp and dict_temp[checkmsg]['type'] != '绑定' :
    #         return get_msg_from_msgdict(dict_temp[checkmsg]['msg'])
    return None


def lookup_user(msg):
    user_id = msg['user_id']
    file_user = os.path.join(user_root, f'{user_id}.json')
    if os.path.exists(file_user):  # 如果文件存在的话
        dict_temp = read_json(file_user)
        msg = '你的问答和绑定数据如下：\n'
        绑定 = ''
        问答 = ''
        for i in dict_temp:
            if dict_temp[i]['type'] == '绑定':
                name = i
                id = dict_temp[i]['msg']
                绑定 += f'{name}:{id}\n'
            else:
                if 'CQ:image' in i:
                    问答 += '图片：'
                else:
                    问答 += f'{i}：'
                length = len(dict_temp[i]['msg'])
                问答 += f'{length}条回答\n'
        msg = f'\n【个人绑定】\n{绑定}【个人词库】\n{问答}'
        msg += '\n🎈群组词库/全局词库也可以查查看哦'
        return msg
    raise Exception('你还没有数据，请先尝试添加问答和绑定')


def lookup_group(msg):
    group_id = msg['group_id']
    file_group = os.path.join(group_root, f'{group_id}.json')
    if os.path.exists(file_group):  # 如果文件存在的话
        dict_temp = read_json(file_group)
        msg = '本群问答和绑定数据如下：\n'
        绑定 = ''
        问答 = ''
        for i in dict_temp:
            if dict_temp[i]['type'] == '绑定':
                name = i
                id = dict_temp[i]['msg']
                绑定 += f'{name}:{id} | '
            else:
                if 'CQ:image' in i:
                    问答 += '图片：'
                else:
                    问答 += f'{i}：'
                length = len(dict_temp[i]['msg'])
                问答 += f'{length}回答 | '
        msg = f'\n【群组绑定】\n{绑定}\n【群组词库】\n{问答}'
        msg += '\n🎈个人词库/全局词库也可以看看哦'
        return msg
    raise Exception('该群还没有数据，请先尝试添加问答和绑定')


def lookup_all(msg):
    path = os.path.join(root, f'All.json')
    notShowList = ['perk']
    if os.path.exists(path):  # 如果文件存在的话
        dict_temp = read_json(path)
        msg = '全局问答和绑定数据如下：\n'
        绑定 = ''
        问答 = ''
        for i in dict_temp:
            if dict_temp[i]['type'] == '绑定':
                name = i
                id = dict_temp[i]['msg']
                绑定 += f'{name} | '
            else:
                if dict_temp[i]['type'] != '自定义':
                    continue
                if 'CQ:image' in i:
                    问答 += '[图片]:'
                else:
                    问答 += f'{i}:'
                length = len(dict_temp[i]['msg'])
                问答 += f'{length} | '
        msg = f'\n【全局绑定】\n{绑定}\n【全局问答】\n{问答}'
        msg += '\n🎈个人词库/群组词库也可以看看哦'
        return msg
    raise Exception('全局还没有数据，请先尝试添加问答和绑定')


def delimg(msg):
    for i in msg:
        res = re.match(r'.*file:///(.*gif).*', i)
        if res:
            path = res.group(1)
            if os.path.exists(path):
                os.remove(path)


def roll(mode, role):
    if mode == '群组':
        if role == 'owner':
            return 0
        if role == 'admin':
            num = random.randint(3, 10)
            if num < 5:
                num=str(num).zfill(2)
                raise Exception(f'/random 3-10 : {num}\n删除失败了，可以再试试嗷')
        else:
            num = random.randint(1, 10)
            if num < 6:
                num=str(num).zfill(2)
                raise Exception(f'/random 1-10 : {num}\n删除失败了，可以再试试嗷')
                

def del_reply(msg):
    user_id = msg['user_id']
    group_id = msg['group_id']
    checkmsg = msg['raw_message']
    role = msg['sender']['role']
    file_group = os.path.join(group_root, f'{group_id}.json')
    file_user = os.path.join(user_root, f'{user_id}.json')
    res = re.match(r'删除(个人|群组).*[/【（(](.+)[/】）)].*', checkmsg)
    if not res:
        raise Exception('删除格式错误，请输入词库帮助以查看相关教程')
    path = file_user if res.group(1) == '个人' else file_group
    checkmsg = res.group(2)
    if os.path.exists(path):  # 如果文件存在的话
        dict_temp = read_json(path)
        if checkmsg in dict_temp:
            roll(res.group(1), role)
            delimg(dict_temp[checkmsg]['msg'])
            del dict_temp[checkmsg]
            write_json(dict_temp, path)
            return f'[{checkmsg}]删除成功'
        else:
            raise Exception(f'删除的问题[{checkmsg}]不在词库内')
    else:
        raise Exception(f'要删除的词库不存在，请先创建词库')


def del_all(msg):
    checkmsg = msg['raw_message']
    user_id = msg['user_id']
    if user_id not in [614867321,2181656404]:
        raise Exception('需要小日向的管理权限才可以修改全局词库')
    path = os.path.join(root, 'All.json')
    res = re.match(r'删除全局.*[/【（(](.+)[/】）)].*', checkmsg)
    if not res:
        raise Exception('删除格式错误，请输入词库帮助以查看相关教程')
    checkmsg = res.group(1)
    if os.path.exists(path):  # 如果文件存在的话
        dict_temp = read_json(path)
        for i in dict_temp:
            if i == checkmsg:
                delimg(dict_temp[i]['msg'])
                del dict_temp[i]
                write_json(dict_temp, path)
                return f'全局词库[{checkmsg}]删除成功'
            if 'alias' in dict_temp[i] and checkmsg in dict_temp[i]['alias']:
                dict_temp[i]['alias'].remove(checkmsg)
                write_json(dict_temp, path)
                return f'全局词库重定向[{checkmsg}]删除成功\nx{checkmsg}x->{i}'
        else:
            raise Exception(f'[{checkmsg}]不在全局词库内')
    else:
        raise Exception(f'要删除的词库不存在，请先创建词库')



def tie_all(msg):
    raw_message = msg['raw_message']
    user_id = msg['user_id']
    if user_id not in [614867321,2181656404]:
        raise Exception('需要小日向的管理权限才可以修改全局绑定')
    res = re.match(
        r'绑定全局.*[\(（【/](.+)[\)）】/].*[\(（【/](7656\d{13})[\)）】/].*', raw_message)
    if not res:
        raise Exception('格式错误，请输入绑定帮助以查看相关教程')
    file = os.path.join(root, 'All.json')
    dict_temp = {}
    if os.path.exists(file):  # 如果文件存在的话
        dict_temp = read_json(file)
    question = res.group(1)
    # [CQ:image,file=f46784e63445c8b7b62e06bbca04d608.image]
    answer = res.group(2)
    if question in dict_temp and dict_temp[question]['type'] != '绑定':
        raise Exception('已经有自定义回复占据了这个位置啦，小日向建议你换一个关键词哦')
    else:
        dict_temp[question] = {'type': '绑定' , 'msg': answer}
        write_json(dict_temp, file)
        return (f'🎉全局绑定成功，{question}已被指定\n输入👉智谋 {question}👈试试吧')
        
def tie_group(msg):
    raw_message = msg['raw_message']
    group_id = msg['group_id']
    res = re.match(
        r'绑定群组.*[\(（【/](.+)[\)）】/].*[\(（【/](7656\d{13})[\)）】/].*', raw_message)
    if not res:
        raise Exception('格式错误，请输入绑定帮助以查看相关教程')
    file = os.path.join(group_root, f'{group_id}.json')
    dict_temp = {}
    if os.path.exists(file):  # 如果文件存在的话
        dict_temp = read_json(file)
    question = res.group(1)
    # [CQ:image,file=f46784e63445c8b7b62e06bbca04d608.image]
    answer = res.group(2)
    if question in dict_temp and dict_temp[question]['type'] != '绑定':
        raise Exception('已经有自定义回复占据了这个位置啦，小日向建议你换一个关键词哦')
    else:
        dict_temp[question] = {'type': '绑定' , 'msg': answer}
        write_json(dict_temp, file)
        return (f'🎉群组绑定成功，{question}已被指定\n输入👉智谋 {question}👈试试吧\n❗该绑定仅在本群有效')
        
def tie_user(msg):
    raw_message = msg['raw_message']
    user_id = msg['user_id']
    res = re.match(
        r'绑定个人.*[\(（【/](.+)[\)）】/].*[\(（【/](7656\d{13})[\)）】/].*', raw_message)
    if not res:
        raise Exception('格式错误，请输入绑定帮助以查看相关教程')
    file = os.path.join(user_root, f'{user_id}.json')
    dict_temp = {}
    if os.path.exists(file):  # 如果文件存在的话
        dict_temp = read_json(file)
    question = res.group(1)
    # [CQ:image,file=f46784e63445c8b7b62e06bbca04d608.image]
    answer = res.group(2)
    if question in dict_temp and dict_temp[question]['type'] != '绑定':
        raise Exception('已经有自定义回复占据了这个位置啦，小日向建议你换一个关键词哦')
    else:
        dict_temp[question] = {'type': '绑定' , 'msg': answer}
        write_json(dict_temp, file)
        return (f'🎉个人绑定成功，{question}已被指定\n输入👉智谋 {question}👈试试吧')
        
def tie_urself(msg):
    raw_message = msg['raw_message']
    user_id = msg['user_id']
    res = re.match(
        r'绑定 *(7656\d{13}).*', raw_message)
    if not res:
        raise Exception('格式错误，队伍码格式为以7656开头的17位纯数字')
    file = os.path.join(user_root, f'{user_id}.json')
    dict_temp = {}
    if os.path.exists(file):  # 如果文件存在的话
        dict_temp = read_json(file)
    question = '_self_'
    # [CQ:image,file=f46784e63445c8b7b62e06bbca04d608.image]
    answer = res.group(1)
    if question in dict_temp and dict_temp[question]['type'] != '绑定':
        raise Exception('已经有自定义回复占据了这个位置啦，小日向建议你换一个关键词哦')
    else:
        dict_temp[question] = {'type': '绑定' , 'msg': answer}
        write_json(dict_temp, file)
        return (f'🎉绑定成功啦，以后你只需要输入指令头就可以查询自己的数据啦！\n输入👉智谋👈试试吧\n❗该绑定仅对你有效')
        

