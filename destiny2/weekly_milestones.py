import asyncio
import pydest
import copy

API_KEY = '19a8efe4509a4570bee47bd9883f7d93'
destiny = pydest.Pydest(API_KEY)

weekly_milestones = {
    '巅峰周常': {
        '1684722553': {
            'name': '超控',
            'completion': False
        },
        # review
        'temp1': {
            'name': '帝国猎杀大师',
            'completion': False
        },
        '2029743966': {
            'name': '日落10w分',
            'completion': False
        },
        "825965416": {
            'name': '预言',
            'completion': False
        },
        '3341030123': {
            'name': '大魔眼周常',
            'completion': [8, 0]
        },
        # review
        '1713200903': {
            'name': 'Exo挑战',
            'completion': False
        },
        '1086730368': {
            'name': '先知',
            'completion': False
        },
        # review
        '3603098564': {
            'name': '公会周常',
            'completion': [5000, 0]
        },
        '3312774044': {
            'name': '熔炉周常',
            'completion': [3, 0]
        },
        '3448738070': {
            'name': '智谋周常',
            'completion': [3, 0]
        },
        '1437935813': {
            'name': '先锋打击',
            'completion': [3, 0]
        },
    },
    '光尘周常': {
        '2594202463': {
            'name': '沙克斯周常',
            'completion': [8, 0]
        },
        '3802603984': {
            'name': '浪客周常',
            'completion': [8, 0]
        },
        '2709491520': {
            'name': '萨瓦拉周常',
            'completion': [8, 0]
        },
    },
    '其他周常': {
        '3899487295': {
            'name': '枪匠周常',
            'completion': [8, 0]
        },
        '2540726600': {
            'name': '瓦里克斯周常',
            'completion': [8, 0]
        },
        '1424672028': {
            'name': '陌客周常',
            'completion': [100, 0]
        },
        'temp2': {
            'name': '异端深渊',
            'completion': False
        },
        '541780856': {
            'name': '深岩墓室',
            'completion': False
        },
    }
}

帝国猎杀大师ActivityHashIdList = [2205920677, 4173217513, 5517242]
# 暗影女祭司,勇士,技术专家
异端深渊ActivityHashIdList = [2582501063]


def check_milestions_completion(characterMilestones: dict,
                                characterActivities: dict):
    milestonesDictToReturn = copy.deepcopy(weekly_milestones)
    for milestoneTypeName in milestonesDictToReturn:
        milestonesDict = milestonesDictToReturn[milestoneTypeName]
        for milestoneHashId in milestonesDict:
            if 'temp' not in milestoneHashId:
                # milestoneInfo = await destiny.decode_hash(
                #     milestoneHashId, 'DestinyMilestoneDefinition')
                # milestoneDescription = milestoneInfo['displayProperties'][
                #     'description']
                if milestoneHashId in characterMilestones:
                    milestone = characterMilestones[milestoneHashId]
                    if 'availableQuests' in milestone and isinstance(
                            milestonesDict[milestoneHashId]['completion'],
                            list):
                        progress = milestone['availableQuests'][0]['status'][
                            'stepObjectives'][0]['progress']
                        if milestone['availableQuests'][0]['status'][
                                'stepObjectives'][0]['objectiveHash'] == 1001409310:
                            progress = 5000
                            milestonesDict[milestoneHashId]['completion'][
                                1] = progress
                            continue

                    if 'activities' in milestone and isinstance(
                            milestonesDict[milestoneHashId]['completion'],
                            list):
                        progress = milestone['activities'][0]['challenges'][
                            0]['objective']['progress']
                        milestonesDict[milestoneHashId]['completion'][
                            1] = progress
                        continue

                    if 'rewards' in milestone:
                        completion = milestone['rewards'][0]['entries'][0][
                            'earned']
                        milestonesDict[milestoneHashId]['completion'] = completion

                else:
                    if isinstance(
                            milestonesDict[milestoneHashId]['completion'],
                            list):
                        milestonesDict[milestoneHashId]['completion'][
                            1] = milestonesDict[milestoneHashId][
                                'completion'][0]
                    else:
                        milestonesDict[milestoneHashId]['completion'] = True

    for milestoneActivity in characterActivities:
        if milestoneActivity['activityHash'] in 帝国猎杀大师ActivityHashIdList:
            completion = True
            if 'challenges' not in milestoneActivity:
                completion = True
            else:
                for challenge in milestoneActivity['challenges']:
                    challenge = challenge['objective']
                    if challenge['objectiveHash'] == 1980717736:
                        completion = False
                        break

            milestonesDictToReturn['巅峰周常']['temp1']['completion'] = completion

        if milestoneActivity['activityHash'] in 异端深渊ActivityHashIdList:
            completion = milestoneActivity['isCompleted']
            milestonesDictToReturn['其他周常']['temp2']['completion'] = completion

    return milestonesDictToReturn