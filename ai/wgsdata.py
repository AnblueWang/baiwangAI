# coding:utf-8

import common

def updateNotMyCityList(l_cities, flag_color):
    '''更新非我方城市列表'''
    try:
        assert len(l_cities) % 3 == 0
        list_valid_indexs = [i for i in range(len(l_cities) // 3) if l_cities[i * 3 + 1] != flag_color]
        return [l_cities[i * 3] for i in list_valid_indexs]
    except Exception as e:
        common.echosentence_color('wgsdata > updateNotMyCityList():{}'.format(str(e)))
        raise

def mainCity(l_cities, flag_color):
    '''返回主要目标地'''
    try:
        assert len(l_cities) % 3 == 0
        return [l_cities[i] for i in range(len(l_cities)) if i % 3 == 0 and l_cities[i+2] == 80][0] # 主要夺控点坐标
    except Exception as e:
        common.echosentence_color('wgsdata > mainCity():{}'.format(str(e)))
        raise

def secondaryCity(l_cities, flag_color):
    '''返回次要目标地'''
    try:
        assert len(l_cities) % 3 == 0
        return [l_cities[i] for i in range(len(l_cities)) if i % 3 == 0 and l_cities[i+2] == 50][0] # 主要夺控点坐标
    except Exception as e:
        common.echosentence_color('wgsdata > secondaryCity():{}'.format(str(e)))
        raise



if __name__ == '__main__':
    pass