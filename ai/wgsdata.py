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




if __name__ == '__main__':
    pass