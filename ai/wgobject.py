# coding:utf-8
from ctypes import *
import pandas

global MaxObjNum #最大班车数
MaxObjNum = 5


class BasicOperator(Structure):
    pass

arr_int5_type = c_int * 5

BasicOperator._fields_ = [('ObjID',c_int), # 算子自身ID
                          ('RoomID',c_int), # 房间号
                          ('UserID',c_int), # 用户ID
                          ('GameColor', c_int),  #游戏双方 红：0，蓝：1 =ObjFlag=ObjColor
                          
                          # ('ObjName',c_wchar_p), # 算子名称（汉语拼音：如战车棋子等）
                          ('ObjArmy',c_int), # 标志x营y排z班
                          # ('ObjIco', c_wchar_p),  #算子军标名称
                          ('ObjType', c_int),   # 算子类型 人：1，车：2
                          ('ObjTypeX', c_int),  # 算子类型的进一步细化：坦克 0/  战车1 / 人员2
                          
                          ('A1', c_int),  # 行进间射击能力 无：0 有：1
                          ('D1', c_int),  # 行军状态下消耗一个机动力单位可以移动的格子数目
                          ('D3', c_int),  # 当前行军的总格数目
                          ('B0', c_int),  # 装甲类型 无装甲：0，轻型装甲：1，中型装甲：2，重型装甲：3，复合装甲：4
                          ('S1', c_int),  # 对人观察距离
                          ('S2', c_int),  # 对车观察距离
                          
                          ('ObjPos', c_int),  #当前位置
                          ('ObjLastPos', c_int),  # 算子上一个时刻的位置，用于同格交战不胜之后的回退
                          ('ObjStep', c_float),  #剩余机动力
                          ('ObjStepMax', c_float),  #算子机动力上限
                          
                          ('ObjPass', c_int),  #车辆机动状态 机动：0 行军：非0  短停：2
                          ('ObjKeep', c_int),  #是否被压制 否：0 是：非0
                          ('ObjHide', c_int),  #是否遮蔽 否：0 是：非0
                          ('ObjRound', c_int),  #是否已机动 否：0 是：非0
                          ('ObjAttack', c_int),  #是否已射击 否：0 是：非0
                          ('ObjTire', c_int),  # 疲劳度 正常：0 一级疲劳：1 二级疲劳：2
                          ('ObjStack', c_int), # 算子是否发生了堆叠 0 未发生 1 发生
                          ('ObjTongge', c_int), # 算子当前是否处于同格状态，0否 1是
                          ('ObjTonggeOrder', c_int), # 先进入同格位置，被动同格，1 ； 后进入同格位置，主动同格 2
                          ('ObjTonggeShootCountLeft', c_int), # 在同格交战环节，剩余的射击次数
                          
                          
                          ('ObjBlood', c_int),  #当前车班数
                          ('C2', c_int),  # 剩余弹药数
                          ('C3', c_int),  # 剩余导弹数
                          
                          ('ObjWzNum', c_int),  # 关联武器数量
                          ('ObjMaxWzNum', c_int), # ObjArrWzIDs的长度，默认为5
                          ('ObjArrWzIDs', c_int * 5), # 算子挂载的武器编号列表 换成5个整形数据
                          
                          ('ObjSup', c_int),  # 算子是# self.updateBopsBecauseOfMoveing(bop_attacker, int_new_ObjPos)否乘车（在车上） 0 不乘车、1 乘车
                          ('ObjSpace', c_int),  # 运兵数量上限
                          ('ObjSonNum', c_int),  # 当前运兵数量
                          ('ObjSonID',c_int),   # 车上的人员算子的ID编号
                          ('ObjValue', c_float),  #算子分值
                          
                          ('ObjFlagTask', c_int), # 基于态势的任务分配 0 进攻 / 1 防御 / 2 撤退
                          ('ObjFlagMoving', c_int), # 针对无行射能力的算子, 用在机动环节检测到可以射击的情况下, 保留机动能力以便于在最终阶段可以射击
                          ('isVisible', c_int), # 该算子能够被对方看到(1) / 不能(0)
                          ('ObjActState', c_int) , # 当前算子是否处于激活态（处于激活态的算子可进入策略图中生成动作，0非激活态，1 激活态），注意阶段更新时需要重置标志位
                          ('ObjCanShoot', c_int),
                          ('ObjCanOccupy', c_int),
                          ('ObjCanSuicide', c_int),
                          ('ObjIndex', c_int), # sgr, 增加算子的索引信息

                        ]
l_pdfield = ['ID','Room','UserID','GameColor','Army','ObjType','A1','D1','B0','S1','S2','ObjPos','ObjStep','ObjStepMax',
             'ObjPass','ObjKeep','ObjHide','ObjRound','ObjAttack','ObjBlood','C2','A3','Wz','ObjSup','ObjSpace','ObjSonNum','ObjValue']
def Gen_Op(Objects):
    op=BasicOperator()
    
    op.ObjID = Objects.ID
    op.RoomID = Objects.Room
    op.UserID = Objects.UserID
    op.GameColor = 0 if Objects.GameColor == 'RED' else 1
    # op.ObjName = Objects.ObjName # 汉语步兵棋子转码的问题？
    op.ObjArmy = int(Objects.Army) # GameColor + Amy + ObjType 三者可以作为算子的唯一标识
    # op.ObjIco=Objects.ObjIco
    op.ObjType = Objects.ObjType
    
    op.A1 = Objects.A1
    if op.A1 == 1:
        op.ObjTypeX = 0  # 坦克
    elif op.ObjType == 2:
        op.ObjTypeX = 1# 战车
    else:
        op.ObjTypeX = 2  # 人员
    
    op.D1 = Objects.D1 # 出现/0错误
    op.B0 = Objects.B0
    op.S1 = Objects.S1
    op.S2 = Objects.S2
    
    op.ObjPos = Objects.ObjPos
    op.ObjLastPos = Objects.ObjPos
    op.ObjStep = Objects.ObjStepMax
    op.ObjStepMax = Objects.ObjStep

    # 状态标志位置
    op.ObjPass = Objects.ObjPass
    op.ObjKeep = Objects.ObjKeep
    op.ObjHide = Objects.ObjHide
    op.ObjRound = Objects.ObjRound
    op.ObjAttack = Objects.ObjAttack
    op.ObjTire = 0
    op.ObjStack = 0
    op.ObjTongge = 0
    op.ObjTonggeOrder = 0
    op.ObjTonggeShootCountLeft = 0
    
    op.ObjBlood = Objects.ObjBlood
    op.C2 = int(Objects.C2) #用于武器的弹药数
    op.C3 = int(Objects.A3) # 用于武器的导弹数

    #  武器部分
    wzlist = Objects.Wz.split( ',' )
    op.ObjWzNum =len(wzlist)
    op.ObjMaxWzNum = 5
    assert (op.ObjWzNum < op.ObjMaxWzNum)
    
    my_wzids = arr_int5_type()
    for i in range(op.ObjWzNum):
        my_wzids[i] = c_int(int(wzlist[i]))
    op.ObjArrWzIDs = my_wzids

    op.ObjSup = Objects.ObjSup  # 标记算子是否在车上
    op.ObjSpace = Objects.ObjSpace
    op.ObjSonID = Objects.ObjSup  #乘车算子的ObjID编号
    op.ObjSonNum =Objects.ObjSonNum #乘车人员的数量（班数）
    op.ObjValue = Objects.ObjValue
    
    #  算子模型标记
    op.ObjFlagTask = 0
    op.ObjFlagMoving = 1
    op.isVisible = 1

    # 策略AI的标记
    op.ObjActState = 1
    op.ObjCanShoot = 0
    op.ObjCanOccupy = 0
    op.ObjCanSuicide = 0
    
    op.ObjIndex = 0

    return op

def bop2Ser(bop):
    try:
        ser = pandas.Series(l_pdfield)
        ser.ID = bop.ObjID
        ser.Room = bop.RoomID
        ser.UserID = bop.UserID
        ser.GameColor = 'RED' if bop.GameColor == 0 else 'BLUE'
        # op.ObjName = Objects.ObjName # 汉语步兵棋子转码的问题？
        ser.Army = int(bop.ObjArmy)  # GameColor + Amy + ObjType 三者可以作为算子的唯一标识
        # op.ObjIco=Objects.ObjIco
        ser.ObjType = bop.ObjType

        ser.A1 = bop.A1
        ser.D1 = bop.D1  # 出现/0错误
        ser.B0 = bop.B0
        ser.S1 = bop.S1
        ser.S2 = bop.S2

        ser.ObjPos = bop.ObjPos
        ser.ObjLastPos = bop.ObjPos
        ser.ObjStep = bop.ObjStepMax
        ser.ObjStepMax = bop.ObjStep

        # 状态标志位置
        ser.ObjPass = bop.ObjPass
        ser.ObjKeep = bop.ObjKeep
        ser.ObjHide = bop.ObjHide
        ser.ObjRound = bop.ObjRound
        ser.ObjAttack = bop.ObjAttack
        ser.ObjBlood = bop.ObjBlood
        ser.C2 = bop.C2  # 用于武器的弹药数
        ser.A3 = bop.C3  # 用于武器的导弹数

        #  武器部分
        l_wz = []
        for wz in bop.ObjArrWzIDs:
            l_wz.append(int(wz))
        str_wz =''
        if len(l_wz) > 0:
            str_wz = str(l_wz[0])
            for i in range(1,len(l_wz)):
                if l_wz[i] == 0:
                    break
                str_wz = str_wz + ',' + str(l_wz[i])
        ser.Wz = str_wz

        ser.ObjSup = bop.ObjSup  # 标记算子是否在车上
        ser.ObjSpace = bop.ObjSpace
        # ser.ObjSonID = bop.ObjSup  # 乘车算子的ObjID编号
        ser.ObjSonNum = bop.ObjSonNum  # 乘车人员的数量（班数）
        ser.ObjValue = bop.ObjValue
        return ser
    except Exception as e:
        print(e)
        raise

if __name__ == '__main__':
    pass
