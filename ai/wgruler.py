# coding:utf-8

import common, hex, wgstage

def Shooting (list_g_stage , bop_attacker , bop_obj ):
    '''外部规则针对射击动作的判断(只关注射击动作)
        第一批: 'S' (射击) | 'N'(不允许射击) | 'MS' 移动射击组合动作(针对坦克) |  'TS' 测试射击能力(针对战车/人员在机动阶段可以射击,需要测试是否保留该射击能力到最终阶段的情况)
        给定参数: 攻击算子bop_attacker, 目标算子 bop_obj, 返回bop_attacker能够对bop_obj的射击动作类型
    '''
    try:
        # 处于同格状态的算子不能做射击动作
        if bop_attacker.ObjTongge == 1 or bop_obj.ObjTongge == 1: return 'N' #2018年10月24日添加：处于同格的算子不能被射击
        # 被压制的人员算子无法射击(同时也无法机动)
        if bop_attacker.ObjTypeX == 2 and bop_attacker.ObjKeep == 1: return 'N'
        #  处于行军状态的算子(车辆算子)无法射击
        if bop_attacker.ObjTypeX <= 1 and bop_attacker.ObjPass == 1: return 'N'
        #  分算子考虑, 只关注射击动作
        # if list_g_stage [1] % 2 == bop_attacker.GameColor: #我方阶段
        if wgstage.isMyStage(list_g_stage, bop_attacker.GameColor): #我方阶段
            # if list_g_stage[2] == 1: # 机动环节
            if wgstage.isMoveHuanJie(list_g_stage): # 机动环节
                if bop_attacker.ObjTypeX == 0:# 坦克
                    if bop_attacker.ObjAttack == 0:# 未射击过
                        if bop_attacker.ObjStep == bop_attacker.ObjStepMax: # 2018年10月24日添加：坦克未机动不能射击
                            return 'N'
                        return 'MS' if bop_attacker.ObjStep > 0  else 'S'
                    else: return 'N' # 已射击过
                if bop_attacker.ObjTypeX >= 1:# 战车与人员
                    if bop_attacker.ObjAttack == 0 and bop_attacker.ObjRound == 0 : # 未射击过+未机动过
                        if bop_obj.ObjAttack == 1 : return 'S'# 对方算子射击过,我方作掩护射击
                        else:
                            return 'TS' if bop_attacker.ObjFlagMoving == 1 else 'N' #保留机动能力,在最终阶段射击
                    else:
                        return 'N'
        else: # 对方阶段
            # if list_g_stage[2] == 1:# 机动环节, 我方算子作机会射击
            if wgstage.isMoveHuanJie(list_g_stage):# 机动环节, 我方算子作机会射击
                if bop_attacker.ObjAttack == 0 and bop_attacker.ObjRound == 0 and bop_obj.ObjRound == 1:return 'S'
                else:return 'N'

        # if list_g_stage[2] == 2:#最终射击环节
        if wgstage.isMyFinalShootHuanJie(list_g_stage, bop_attacker.GameColor):
            if bop_attacker.ObjAttack == 0 and bop_attacker.ObjRound == 0 :return 'S'
            else:return 'N'
        return 'N'
    except Exception as e:
        common.echosentence_color('wgruler > Shooting():{}'.format (str(e)))
        raise
        
def Moving( list_g_stage, cur_bop):
    ''' 外部规则针对机动动作的判断(只关注机动动作)
        第一批: 'M' 能够进行机动/ 'N' 不能进行机动
        BUG0: 隐蔽状态下，只有满格机动里才能机动，非满格机动力，无法切换到机动状态，不能机动
    '''
    try:
        # 特殊情况
        if cur_bop.ObjTongge == 1: return 'N' # 处于同格状态的算子不能做机动动作
        if cur_bop.ObjFlagMoving == 0: return 'N'  # ObjFlagMoving标志位==0
        if cur_bop.ObjHide == 1 and cur_bop.ObjStep != cur_bop.ObjStepMax: return 'N' # !修改
        if cur_bop.ObjTypeX == 2 and cur_bop.ObjKeep == 1: return 'N'  # 人员算子被压制
        if cur_bop.ObjTypeX == 2 and cur_bop.ObjPass == 2: return 'N'#  人员算子处于二级疲劳,不能机动
        if wgstage.isMyMoveHuanJie(list_g_stage, cur_bop.GameColor):
            if cur_bop.ObjStep > 0:
                return 'M'  # 机动条件:我方机动环节, 剩余机动力
            else: # cur_bop.ObjStep == 0:
                return 'O'
        return 'N'
    except Exception as e:
        common.echosentence_color('wgruler > Moving():{}'.format (str(e)))
        raise


def OccupyingRightNow(list_g_stage, cur_bop, list_loc_notmycity, list_ubops):
    '''判断当前算子是否能够进行原地夺控'''
    try:
        if cur_bop.ObjPos in list_loc_notmycity:
            c_row, c_col = common.cvtInt6loc2HexOffset(int(cur_bop.ObjPos))
            c_hex_off = hex.HEX_OFF(c_row, c_col)
            # 计算邻域坐标: 检查对方算子是否在夺控点1格以内防御
            list_neighbor_hexs = [c_hex_off]
            list_neighbor_tuples = c_hex_off.getSixNeighInOrder()
            list_neighbor_hexs += [hex.HEX_OFF(t[0], t[1]) for t in list_neighbor_tuples]
            list_neighbor_int6locs = [common.cvtHexOffset2Int6loc(n_hex_off.row, n_hex_off.col) for n_hex_off in  list_neighbor_hexs]
            for ubop in list_ubops:
                if ubop.ObjPos in list_neighbor_int6locs:
                    return 'N'
            return 'O'
    except Exception as e:
        common.echosentence_color('wgruler > OccupyingRightNow():{}'.format(str(e)))
        raise e


def cvtMapBop2AIBop ( map_bop , list_g_stage ):
    '''地图算子 -> AI算子的映射函数 （将算子的阶段标志换成0_1标志）
        BUG0: 2018/08/06 - 08:23 加入隐蔽状态的判断
    '''
    try:
        # map_bop.ObjStep , map_bop.ObjStepMax = map_bop.ObjStepMax , map_bop.ObjStep  # step / stepmax 交换
        map_bop.ObjAttack = 1 if haveShooted ( map_bop , list_g_stage ) else 0
        map_bop.ObjRound = 1 if haveMoved ( map_bop , list_g_stage ) else 0
        map_bop.ObjRound = 1 if map_bop.ObjStep != map_bop.ObjStepMax else map_bop.ObjRound # 特殊设置
        map_bop.ObjKeep = 1 if hasBeenKept ( map_bop , list_g_stage ) else 0
        map_bop.ObjHide = 1 if hasHiden(map_bop) else 0
        # if map_bop.ObjKeep == 1:
        #     print '{} is kept'.format(map_bop.ObjID)

        map_bop.ObjTire = 1 if hasBeenTired ( map_bop ) else 0
        # 人员算子的ObjPass出现了3?
        map_bop.ObjPass = 2 if map_bop.ObjTypeX == 2 and map_bop.ObjPass > 2 else map_bop.ObjPass
        if map_bop.ObjPass >=  1 and map_bop.ObjType == 1: # 人员算子处于疲劳状态
            map_bop.ObjStep = 0  if (2 - map_bop.ObjPass) < 0 else 2 - map_bop.ObjPass
        return map_bop
    except Exception as e:
        common.echosentence_color('wgruler > cvtMapBop2AIBop():{}'.format (str(e)))
        raise

def haveShooted( bop, list_g_stage):
    '''判断算子在当前阶段是否已经射击过
       射击只判断当前阶段（算子在每个阶段开始时候射击标志清零/ 算子在每个阶段（无论敌我）都可以进行射击）
    '''
    try:
        round_num = wgstage.getStageId(list_g_stage)
        return True if bop.ObjAttack == round_num else False
    except Exception as e:
        common.echosentence_color('wgruler > haveShooted():{}'.format(str(e)))
        raise

def haveMoved(bop, list_g_stage):
    ''' 判断算子在当前阶段是否已经机动过
        机动要分我方/敌方两个阶段（算子只能在属于自己的机动阶段进行机动）
        BUG: 该函数目前只能用于我方算子
    '''
    try:
        if bop.ObjRound == 0: return False
        round_num = wgstage.getStageId(list_g_stage)
        # if list_g_stage[1] % 2 ==  bop.GameColor :
        if wgstage.isMyStage(list_g_stage, bop.GameColor):
            return True if bop.ObjRound == round_num else False
        else:
            return True if bop.ObjRound == round_num - 1 else False
    except Exception as e:
        common.echosentence_color('wgruler > haveMoved():{}'.format ( str ( e ) ))
        raise

def hasBeenKept( bop, list_g_stage):
    '''判断算子是否被压制在当前阶段是否被压制
       在每个回合地第1个阶段移除红方标志; 在每个回合的第3个阶段移除蓝方标志
    '''
    try:
        round_num = wgstage.getStageId(list_g_stage)
        if bop.ObjKeep == 0 : return False
        if bop.ObjKeep == round_num: return True
        else:
            if bop.GameColor == 0:
                expected_num = round_num - (round_num % 4 + 1) if round_num % 4 < 3 else round_num
            else:
                expected_num = (round_num - 1) // 4 * 4 + 1
            return False if expected_num > bop.ObjKeep else True
    except Exception as e:
        common.echosentence_color('wgruler > hasBeenKept():{}'.format ( str ( e ) ))
        raise

def hasBeenTired(bop_attacker):
    '''判断算子是否已经疲劳:(只关注人)'''
    try:
        return bop_attacker.ObjType == 1 and bop_attacker.ObjPass >= 1
    except Exception as e:
        common.echosentence_color('wgruler > hasBeenTired():{}'.format (str(e)))
        raise

def hasHiden(bop):
    try:
        assert bop.ObjHide in [0, 2]
        return True if bop.ObjHide > 0 else False
    except Exception as e:
        common.echosentence_color('error in wgruler.py> hasHiden():{}'.format(str(e)))
        raise

def stackCheck (list_bops ):
    '''算子的堆叠检查'''
    try:
        for cur_index , cur_bop in enumerate ( list_bops ):
            flag_stack = False
            for inter_index , inter_bop in enumerate ( list_bops ):
                if cur_index != inter_index and cur_bop.ObjPos == inter_bop.ObjPos:
                    flag_stack = True
                    break
            cur_bop.ObjStack = 1 if flag_stack else 0
    except Exception as e:
        common.echosentence_color('wgruler > stackCheck():{}'.format ( str ( e ) ))
        raise

def tonggeCheck(list_obops, list_ubops):
    '''算子是否处于同格交战状态,'''
    try:
        for obop in list_obops:
            list_result_bops = common.getSpecifiedBopByPos(list_ubops, obop.ObjPos, obj_type = -1)
            obop.ObjTongge = 1 if list_result_bops is not None else 0
            if obop.ObjTongge == 0:
                obop.ObjTonggeOrder = obop.ObjTonggeShootCountLeft = 0

    except Exception as e:
        common.echosentence_color('wgruler > tonggeCheck():{}'.format(str(e)))
        raise e



if __name__ == '__main__':
    pass