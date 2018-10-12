#coding:utf-8
import wgobject,wgruler,wgsdata,common,wgstage
import random,time,sys,pandas
sys.path.append('../interface/')

'''AI类 调用接口读取态势数据，生成动作以及动作执行'''
class AI:
    def __init__(self,obj_interface,flag_color):
        '''
        初始化
        :param obj_interface: 接口类
        :param flag_color: 'RED'/红色 'BLUE'/蓝色
        '''
        try:
            self.obj_interface = obj_interface
            self.flag_color = 0 if flag_color == 'RED' else 1
            # l_obops:我方算子列表; l_ubops:敌方算子列表; l_cities:夺控点信息列表; l_stage:阶段信息
            self.dic_metadata = {'l_obops': [], 'l_ubops': [], 'l_cities': [], 'l_stage': []}
            self.dic_targets = {}
            self.updateSDData() # 更新态势数据
            
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def run(self):
        '''
        主循环
        :return:
        '''
        try:
            #主循环
            while ((not self.timeIsout()) and (not self.oneWin())): # 游戏是否结束或一方胜利
                self.updateSDData() #更新态势数据
                if self.dic_metadata['l_stage'][1] % 2 == self.flag_color:
                    common.echosentence_color('-' * 20 ) #打印信息
                flag_validAction = self.doAction() #执行动作
                if( not flag_validAction): #没有有效动作
                    self.wait(self.dic_metadata,self.flag_color) #等待下个有效动作，打印等待信息
                time.sleep(0.1)
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def updateSDData(self):
        '''
        更新态势数据，放在成员变量dic_metadata中
        :return:
        '''
        try:
            # 时间信息
            self.dic_metadata['l_stage'] = self.obj_interface.getSimTime()

            # 我方算子
            self.dic_metadata['l_obops'] = []
            df_myOp = self.obj_interface.getSideOperatorsData()
            for index, row in df_myOp.iterrows():
                bop = wgobject.Gen_Op(row)
                bop = wgruler.cvtMapBop2AIBop(bop,self.dic_metadata['l_stage'])
                self.dic_metadata['l_obops'].append(bop)

            # 敌方算子
            self.dic_metadata['l_ubops'] = []
            df_enemyOp = self.obj_interface.getEnemyOperatorsData()
            for index,row in df_enemyOp.iterrows(): #敌方算子不包括血量为0的算子
                bop = wgobject.Gen_Op(row)
                bop = wgruler.cvtMapBop2AIBop(bop, self.dic_metadata['l_stage'])
                self.dic_metadata['l_ubops'].append(bop)

            # 堆叠检查
            wgruler.stackCheck(self.dic_metadata['l_obops'])
            wgruler.stackCheck(self.dic_metadata['l_ubops'])
            #同格检查
            wgruler.tonggeCheck(self.dic_metadata['l_obops'], self.dic_metadata['l_ubops'])
            wgruler.tonggeCheck(self.dic_metadata['l_obops'], self.dic_metadata['l_ubops'])

            #城市列表
            df_city = self.obj_interface.getCityData()
            df_city = df_city.sort_values(by='C1', ascending=True)
            self.dic_metadata['l_cities'] = []
            dic_color2flag = {'GREEN': -1, 'RED': 0, 'BLUE': 1}
            for index, row in df_city.iterrows():
                self.dic_metadata['l_cities'] += [row.MapID, dic_color2flag[row.UserFlag], row.C1]
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def timeIsout(self):
        '''
        游戏时间是否结束
        :return: True/是 False/否
        '''
        try:
            return self.obj_interface.flagTimeOut()
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def oneWin(self):
        '''
        是否一方胜利
        :return: True/是 False/否
        '''
        try:
            num_obops, num_ubops = len(self.dic_metadata['l_obops']), len(self.dic_metadata['l_ubops'])
            return num_obops == 0
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def doAction(self):
        try:
            if wgstage.isMyMoveHuanJie(self.dic_metadata['l_stage'],self.flag_color):
                return self.doMyMoveHuanJieAction()
            if wgstage.isMyFinalShootHuanJie(self.dic_metadata['l_stage'],self.flag_color):
                return self.doMyFinalShootingHuanJieAction()
            if wgstage.isOpMoveHuanJie(self.dic_metadata['l_stage'],self.flag_color):
                return self.doOpMoveHuanJieAction()
            return False
        except Exception as e:
            print('error in run_onestep(): ' + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print('error in run_onestep(): ' + str(k))
            self.__del__()
            raise

    def doOpMoveHuanJieAction(self):
        try:
            res = False
            l_ourbops = self.dic_metadata['l_obops'] #我方算子
            l_enemybops = self.dic_metadata['l_ubops'] #敌方算子
            while wgstage.isOpMoveHuanJie(self.dic_metadata['l_stage'],self.flag_color):
                # 射击动作
                # 选择最大伤害的敌人
                for att_bop in l_ourbops:
                    Flag = False
                    Obj = None
                    Maxf = 0
                    weapon = -1
                    for obj_bop in l_enemybops:
                        flag,weaponID = self.genShootAction(att_bop, obj_bop) #判断是否可以射击,若可以射击，返回最佳射击武器
                        if flag:
                            Flag = True
                            computeFlag, f = self.obj_interface.getAttackLevel(wgobject.bop2Ser(att_bop),wgobject.bop2Ser(obj_bop),int(weaponID))
                            if computeFlag == 0 and f > Maxf:
                                Maxf = f
                                Obj = obj_bop
                                weapon = weaponID
                        if Flag and Obj is not None: #可以射击
                            exe_success,_ = self.obj_interface.setFire(att_bop.ObjID,Obj.ObjID,(int)(weapon)) #调用接口执行射击动作
                            if exe_success == 0: # 执行成功
                                res = True
                self.dic_metadata['l_stage'] = self.obj_interface.getSimTime()
            return res
        except Exception as e:
            print('error in doOpMoveHuanJieAction(): ' + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print('error in doOpMoveHuanJieAction(): ' + str(k))
            self.__del__()
            raise

    def doMyFinalShootingHuanJieAction(self):

        try:
            res = False
            l_ourbops = self.dic_metadata['l_obops'] #我方算子
            l_enemybops = self.dic_metadata['l_ubops'] #敌方算子
            # 射击动作
            # 选择最大伤害的敌人
            for att_bop in l_ourbops:
                Flag = False
                Obj = None
                Maxf = 0
                weapon = -1
                for obj_bop in l_enemybops:
                    flag,weaponID = self.genShootAction(att_bop, obj_bop) #判断是否可以射击,若可以射击，返回最佳射击武器
                    if flag:
                        Flag = True
                        computeFlag, f = self.obj_interface.getAttackLevel(wgobject.bop2Ser(att_bop),wgobject.bop2Ser(obj_bop),int(weaponID))
                        if computeFlag == 0 and f > Maxf:
                            Maxf = f
                            Obj = obj_bop
                            weapon = weaponID
                    if Flag and Obj is not None: #可以射击
                        exe_success,_ = self.obj_interface.setFire(att_bop.ObjID,Obj.ObjID,(int)(weapon)) #调用接口执行射击动作
                        if exe_success == 0: # 执行成功
                            res = True
                return res
        except Exception as e:
            print('error in doMyFinalShootingHuanJieAction(): ' + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print('error in doMyFinalShootingHuanJieAction(): ' + str(k))
            self.__del__()
            raise


    def doMyMoveHuanJieAction(self):
        try:
            res = False
            l_ourbops = self.dic_metadata['l_obops'] #我方算子
            l_enemybops = self.dic_metadata['l_ubops'] #敌方算子
            l_cities = self.dic_metadata['l_cities'] #夺控点列表

            # 夺控动作
            for cur_bop in l_ourbops:
                if self.genOccupyAction(cur_bop): #判断是否可以夺控
                    self.obj_interface.setOccupy(cur_bop.ObjID) #调用接口执行夺控动作
                    res = True
            
            city_loc = wgsdata.mainCity(l_cities,self.flag_color)
            if city_loc in wgsdata.updateNotMyCityList(l_cities,self.flag_color) and common.getSpecifiedBopByPos(l_enemybops, city_loc):
                city_loc = wgsdata.secondaryCity(l_cities,self.flag_color)
            # 机动动作
            for cur_bop in l_ourbops:
                flag_move = True
                if cur_bop.ObjTypeX in [1,2]:
                    '''，人和战车能观察到敌方算子且距离小于6，放弃机动机会'''
                    cur_ser = wgobject.bop2Ser(cur_bop)
                    for ubop in l_enemybops:
                        obj_ser = wgobject.bop2Ser(ubop)
                        _,flag_see = self.obj_interface.flagISU(cur_ser,obj_ser)
                        _,distance = self.obj_interface.getMapDistance(cur_bop.ObjPos,ubop.ObjPos)
                        if flag_see and distance <= 6:
                            flag_move = False
                            break
                if flag_move:
                    if cur_bop.ObjPos != city_loc:
                        if cur_bop.ObjTypeX == 0:
                            flag,l_path = self.genMoveAction(cur_bop, city_loc+2)  # 判断能否执行机动动作，如果能，返回机动路径
                        else:
                            flag,l_path = self.genMoveAction(cur_bop, city_loc)
                        if flag and l_path:
                            self.obj_interface.setMove(cur_bop.ObjID,l_path) #调用接口函数执行机动动作
                            res = True

            # 人员下车
            for cur_bop in l_ourbops:
                if cur_bop.ObjTypeX == 1 and cur_bop.ObjSonNum == 1:  # 载人车辆
                    _, dis = self.obj_interface.getMapDistance(cur_bop.ObjPos, city_loc) # 距离夺控点的距离
                    if dis <= 3 or (dis < 6 and common.getSpecifiedBopByPos(l_enemybops, city_loc)): # 距离目标<3 或者目标被占且<10 下车
                        if self.genGetOffAction(cur_bop): #判断是否满足下车条件
                            self.obj_interface.setGetoff(cur_bop.ObjID) # 调用接口执行下车动作
                            res = True

            # 射击动作
            for att_bop in l_ourbops:
                if att_bop.ObjTypeX == 0:
                    res = res or self.doMoveShootAction(att_bop)

            return res 
        except Exception as e:
            print('error in doMyMoveHuanJieAction(): ' + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print('error in doMyMoveHuanJieAction(): ' + str(k))
            self.__del__()
            raise
            
    # def doTankMoveAction(self,tank_bop):

    # def doVehicleMoveAction(slef,vehicle_bop):
    #     ''' 战车在机动环节动作为若当前主要争夺点没有我方旗子且没有我方旗子目标是它，则向其移动'''
    #     res = False
    #     # 夺控动作
    #     if self.genOccupyAction(vehicle_bop): #判断是否可以夺控
    #         self.obj_interface.setOccupy(vehicle_bop.ObjID) #调用接口执行夺控动作
    #         res = True

    #     main_city = wgsdata.mainCity(self.dic_metadata['l_cities'],self.flag_color)
    #     bopId = common.getBopIdentity(vehicle_bop)

    #     #设定目标
    #     cur_ser = wgobject.bop2Ser(vehicle_bop)
    #     for ubop in l_enemybops:
    #         obj_ser = wgobject.bop2Ser(ubop)
    #         _,flag_see = self.obj_interface.flagISU(cur_ser,obj_ser)
    #         _,distance = self.obj_interface.getMapDistance(cur_bop.ObjPos,ubop.ObjPos)
    #         if flag_see and distance <= 6:
    #             flag_move = False
    #             break

    #     if main_city not in self.dic_targets.values():
    #         self.dic_targets[bopId] = main_city
    #     else:
    #         self.dic_targets[bopId] = vehicle_bop.ObjPos
    #     #移动
    #     flag,l_path = self.genMoveAction(vechicle_bop, main_city)
    #     if flag and l_path:
    #         self.obj_interface.setMove(vehicle_bop.ObjID,l_path) #调用接口函数执行机动动作
    #         return True

    # def doSoldierMoveAction(self,soldier_bop):
    #     ''' 步兵在机动环节动作为若当前主要争夺点没有我方旗子且没有我方旗子目标是它，则向其移动一步'''
    #     res = False
    #     # 夺控动作
    #     if self.genOccupyAction(soldier_bop): #判断是否可以夺控
    #         self.obj_interface.setOccupy(soldier_bop.ObjID) #调用接口执行夺控动作
    #         res = True

    #     main_city = wgsdata.mainCity(self.dic_metadata['l_cities'],self.flag_color)
    #     bopId = common.getBopIdentity(soldier_bop)
    #     #设定目标
    #     if main_city not in self.dic_targets.values():
    #         self.dic_targets[bopId] = main_city
    #     else:
    #         self.dic_targets[bopId] = soldier_bop.ObjPos
    #     #移动
    #     flag,l_path = self.genMoveAction(soldier_bop, main_city)
    #     if flag and l_path:
    #         self.obj_interface.setMove(soldier_bop.ObjID,l_path[0:1]) #调用接口函数执行机动动作
    #         return True

    def doMoveShootAction(self,att_bop):
        ''' 只有坦克可以选择行进间射击'''

        # 选择最大伤害的敌人
        l_enemybops = self.dic_metadata['l_ubops'] #敌方列表
        Flag = False
        Obj = None
        Maxf = 0
        weapon = -1
        res = False
        for obj_bop in l_enemybops:
            flag,weaponID = self.genShootAction(att_bop, obj_bop) #判断是否可以射击,若可以射击，返回最佳射击武器
            if flag:
                Flag = True
                computeFlag, f = self.obj_interface.getAttackLevel(wgobject.bop2Ser(att_bop),wgobject.bop2Ser(obj_bop),int(weaponID))
                if computeFlag == 0 and f > Maxf:
                    Maxf = f
                    Obj = obj_bop
                    weapon = weaponID
            if Flag and Obj is not None: #可以射击
                exe_success,_ = self.obj_interface.setFire(att_bop.ObjID,Obj.ObjID,(int)(weapon)) #调用接口执行射击动作
                if exe_success == 0: # 执行成功
                    res = True
        return res

    def genShootAction(self, bop_attacker, bop_obj):
        '''
        判断能否射击
        :param bop_attacker:
        :param bop_obj:
        :return: (True,wp_index)/(能射击,武器编号),(False,None)/(不能射击，None)
        '''
        try:
            list_g_stage = self.dic_metadata['l_stage']
            flag_str_shooting = wgruler.Shooting(list_g_stage, bop_attacker, bop_obj)

            if flag_str_shooting != 'N' and flag_str_shooting != 'TS':
                ser_att = wgobject.bop2Ser(bop_attacker)
                ser_obj = wgobject.bop2Ser(bop_obj)
                flag_success, wp_index = self.obj_interface.chooseWeaponIndex(ser_att,ser_obj) # 获取武器编号
                if flag_success == 0:
                    return (True,wp_index)
            return (False,None)
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def genOccupyAction(self, cur_bop):
        '''
        判断是否可以夺控
        :param cur_bop:
        :return: True/可以夺控,False/不能夺控
        '''
        try:
            list_g_stage = self.dic_metadata['l_stage']
            list_loc_notmycity = wgsdata.updateNotMyCityList(self.dic_metadata['l_cities'], cur_bop.GameColor)
            list_ubops = self.dic_metadata['l_ubops']

            if wgruler.OccupyingRightNow(list_g_stage, cur_bop, list_loc_notmycity, list_ubops) == 'O':
                return True
            return False
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def genGetOffAction(self, cur_bop):
        '''
        判断能否下车
        :param cur_bop:
        :return: True/可以下车 Flase/不能下车
        '''
        try:
            list_g_stage = self.dic_metadata['l_stage']
            # 下车模型首先保证能够机动
            flag_str_moving = wgruler.Moving(list_g_stage, cur_bop=cur_bop)
            if flag_str_moving == 'M' and cur_bop.ObjTypeX == 1 and cur_bop.ObjSonNum == 1 and \
                    cur_bop.ObjStep >= cur_bop.ObjStepMax // 2 and cur_bop.ObjKeep == 0:  # 没有被压制
                # and cur_bop.ObjSonNum == 1 and cur_bop.ObjStep >= 3 and cur_bop.ObjKeep == 0:  # 没有被压制  ???3
                return  True

            return False
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def genGetOnAction(self, car_bop, peo_bop):
        '''
        生成上车动作
        :param car_bop:
        :param peo_bop:
        :return: True/能上车 False/不能上车
        '''
        try:

            list_g_stage = self.dic_metadata['l_stage']
            flag_car_moving = wgruler.Moving(list_g_stage, cur_bop=car_bop)
            flag_peo_moving = wgruler.Moving(list_g_stage, cur_bop=peo_bop)

            flag_car_geton = car_bop.ObjTypeX == 1 and car_bop.ObjSonNum == 0 and car_bop.ObjStep >= car_bop.ObjStepMax // 2 and car_bop.ObjKeep == 0
            flag_peo_geton = peo_bop.ObjTypeX == 2 and peo_bop.ObjStep == peo_bop.ObjStepMax and peo_bop.ObjKeep == 0
            if flag_car_moving == 'M'and flag_peo_moving == 'M'  and flag_car_geton and flag_peo_geton:
                return  True
            return False
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def genMoveAction(self, cur_bop, obj_pos):
        '''
        判断是否机动,若机动，返回机动路线
        :param cur_bop: 机动算子
        :param obj_pos: 目标位置
        :return: (True,list)/(需要机动，机动路线),(False,None)/(不机动，None)
        '''
        try:
            list_g_stage = self.dic_metadata['l_stage']
            flag_str_moving = wgruler.Moving(list_g_stage, cur_bop)
            assert flag_str_moving in ['N', 'M', 'O']
            if flag_str_moving == 'M':
                series = wgobject.bop2Ser(cur_bop)
                flag_result, list_movepath = self.obj_interface.getMovePath(series,obj_pos)
                if(flag_result == 0):
                    return True,list_movepath
            return False,None
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def wait(self, dic_metadata, flag_color):
        '''信息打印'''
        try:
            list_g_stage_now = self.obj_interface.getSimTime()
            dic_metadata['l_stage'] = list_g_stage_now
            if dic_metadata['l_stage'][0:3] == list_g_stage_now[0:3]:
                # if list_g_stage_now[1] % 2 == self.flag_color:
                if list_g_stage_now[1] % 2 == flag_color:
                    print(u'AI 当前阶段({})，无动作输出，等待中...'.format(self.showStage(list_g_stage_now)))
                    while (dic_metadata['l_stage'][0:3] == list_g_stage_now[0:3]):
                        time.sleep(0.5)
                        list_g_stage_now = self.obj_interface.getSimTime()
                else:  # 对方阶段
                    if list_g_stage_now[2] != 1: #对间瞄，最终射击
                        print(u'AI 当前阶段({})，无动作输出，等待中...'.format(self.showStage(list_g_stage_now)))
                        while (dic_metadata['l_stage'][0:3] == list_g_stage_now[0:3]):
                            time.sleep(0.5)
                            list_g_stage_now = self.obj_interface.getSimTime()
                    else:  # 对方机动环节(刷新数据库,重新迭代)
                        time.sleep(0.05)
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def showStage(self,list_g_stage):
        '''打印当前环节信息'''
        try:
            str_redcolor, str_bluecolor = '红方', '蓝方'
            list_huanjie_strs = ['间瞄', '机动', '最终射击', '最终射击', '同格交战']
            str_hoststagecolor, str_gueststagecolor = (str_redcolor, str_bluecolor) if list_g_stage[1] % 2 == 0 \
                else (str_bluecolor, str_redcolor)
            str_prefix = str_hoststagecolor if list_g_stage[2] == 2 else str_gueststagecolor if list_g_stage[2] == 3 else ''
            # str_prefix = str_hoststagecolor if list_g_stage[2] == 2 else str_gueststagecolor
            return '{} 第{}回合 第{}阶段 {}环节 剩余{}秒'.format(
                str_hoststagecolor, list_g_stage[0] + 1, list_g_stage[1] + 1,
                                    str_prefix + list_huanjie_strs[list_g_stage[2]], list_g_stage[3])
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def __del__(self):
        if self.obj_interface is not None:
            self.obj_interface.__del__()
