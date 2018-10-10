# coding:utf-8
import common

def getStageId(list_g_stage):
    return list_g_stage[0] * 4 + list_g_stage[1] + 1

def getValidTimeID( list_g_stage ):
    '''根据list_g_stage反推处合适的剩余时间'''
    dic_huanjie2timeid = { 0: 89, 1:79 , 2: 39, 3:24, 4:9 }
    return dic_huanjie2timeid[list_g_stage[2]]

'''当前是否是我方flag_mycolor阶段'''
def isMyStage(list_g_stage, flag_mycolor):
    try:
        assert flag_mycolor in [0,1]
        return list_g_stage[1] % 2 == flag_mycolor
    except Exception as e:
        common.echosentence_color('error in wgstage.py > isRStage():{}'.format(str(e)))
        raise
'''是否是我方间瞄环节'''
def isMyJMHuanJie(list_g_stage, flag_mycolor):
    return isMyStage(list_g_stage, flag_mycolor) and isJMHuanJie(list_g_stage)
'''是否是我方机动环节 '''
def isMyMoveHuanJie(list_g_stage, flag_mycolor):
    return isMyStage(list_g_stage, flag_mycolor) and isMoveHuanJie(list_g_stage)
'''是否是我方最终射击环节'''
def isMyFinalShootHuanJie(list_g_stage, flag_mycolor):
    f = isRFinalShootHuanJie if flag_mycolor == 0 else isBFinalShootHuanJie
    return f(list_g_stage)
'''当前是否是红方阶段'''
def isRStage(list_g_stage):
    return isMyStage(list_g_stage=list_g_stage, flag_mycolor=0)
'''当前是否是蓝方阶段'''
def isBStage(list_g_stage):
    return isMyStage(list_g_stage=list_g_stage, flag_mycolor=1)
'''当前阶段的颜色：红0蓝1'''
def getStageColorFlag(list_g_stage):
    return list_g_stage[1] % 2
'''当前是否是间瞄环节'''
def isJMHuanJie(list_g_stage):
    return list_g_stage[2] == 0
'''当前是否是机动环节'''
def isMoveHuanJie(list_g_stage):
    return list_g_stage[2] == 1
'''当前是否是红方最终射击环节'''
def isRFinalShootHuanJie(list_g_stage):
    return  (isRStage(list_g_stage) and list_g_stage[2] == 2 ) or (isBStage(list_g_stage) and list_g_stage[2] == 3 )
'''当前是否是蓝方最终射击环节'''
def isBFinalShootHuanJie(list_g_stage):
    return  (isRStage(list_g_stage) and list_g_stage[2] == 3 ) or (isBStage(list_g_stage) and list_g_stage[2] == 2 )
'''当前是否是最终射击环节'''
def isFinalShootHuanJie(list_g_stage):
    return isBFinalShootHuanJie(list_g_stage) or isRFinalShootHuanJie(list_g_stage)
'''当前是否是同格交战环节'''
def isTongGeHuanJie(list_g_stage):
    return list_g_stage[2] == 4
'''当前是否为移除红方算子压制标志的阶段'''
def isRemoveKeepFlag4R(list_g_stage):
    return list_g_stage[1] == 2
'''当前是否为移除蓝方算子压制标志的阶段'''
def isRemoveKeepFlag4B(list_g_stage):
    return list_g_stage[1] == 0

if __name__ == '__main__':
    pass
    
