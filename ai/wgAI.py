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
            self.memory_obj = {}
            self.main_city_occupied = False
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
                self.memory_obj[common.getBopIdentity(bop)] = bop.ObjPos

            # 堆叠检查
            wgruler.stackCheck(self.dic_metadata['l_obops'])
            wgruler.stackCheck(self.dic_metadata['l_ubops'])
            #同格检查
            wgruler.tonggeCheck(self.dic_metadata['l_obops'], self.dic_metadata['l_ubops'])
            wgruler.tonggeCheck(self.dic_metadata['l_ubops'], self.dic_metadata['l_obops'])

            #城市列表
            df_city = self.obj_interface.getCityData()
            df_city = df_city.sort_values(by='C1', ascending=True)
            self.dic_metadata['l_cities'] = []
            dic_color2flag = {'GREEN': -1, 'RED': 0, 'BLUE': 1}
            for index, row in df_city.iterrows():
                self.dic_metadata['l_cities'] += [row.MapID, dic_color2flag[row.UserFlag], row.C1]
            
            #检查主要目标点上是否有敌方棋子，如果主要目标地是敌方旗帜，先假设有敌方棋子
            main_city = wgsdata.mainCity(self.dic_metadata['l_cities'])
            if main_city in wgsdata.updateNotMyCityList(self.dic_metadata['l_cities'],self.flag_color):
                self.main_city_occupied = True
            for bop in self.dic_metadata['l_obops']:
                _,dis = self.obj_interface.getLOS(main_city,bop.ObjPos)
                if dis != None and dis >= 0:
                    self.main_city_occupied = main_city in self.memory_obj.values()

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
            score = self.obj_interface.getScore()
            not_my_city = wgsdata.updateNotMyCityList(self.dic_metadata['l_cities'],self.flag_color)
            if self.flag_color == 0:
                if score["RedObjScore"][0] == 0:
                    return True
                elif len(not_my_city) == 0:
                    return True;
            if self.flag_color == 1:
                if score["BlueObjScore"][0] == 0:
                    return True
                elif len(not_my_city) == 0:
                    return True;
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    def moveToSecondary(self):
        '''
        是否应该占领次要目标地
        '''
        try:
            score = self.obj_interface.getScore()
            not_my_city = wgsdata.updateNotMyCityList(self.dic_metadata['l_cities'],self.flag_color)
            if self.flag_color == 0:
                if score["BlueObjScore"][0] == 0 or score["RedObjScore"][0]-score["BlueObjScore"][0] > 60 and len(not_my_city) == 1:
                    return True
            if self.flag_color == 1:
                if score["RedObjScore"][0] == 0 or score["BlueObjScore"][0]-score["RedObjScore"][0] > 60 and len(not_my_city) == 1:
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

    def doAction(self):
        try:
            res = False 
            if wgstage.isMyMoveHuanJie(self.dic_metadata['l_stage'],self.flag_color):
                #return self.doMyMoveHuanJieAction()
                res = self.doMyMoveAction()
            if wgstage.isMyFinalShootHuanJie(self.dic_metadata['l_stage'],self.flag_color):
                res = self.doMyFinalShootingHuanJieAction()
            if wgstage.isOpMoveHuanJie(self.dic_metadata['l_stage'],self.flag_color):
                res = self.doOpMoveHuanJieAction()
            return res
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
            while wgstage.isOpMoveHuanJie(self.dic_metadata['l_stage'],self.flag_color):
                # 更新敌方棋子信息来进行可能的机会攻击
                self.updateSDData()
                # 射击动作
                for att_bop in self.dic_metadata['l_obops']:
                    for obj_bop in self.dic_metadata['l_ubops']:
                        flag,weaponID = self.genShootAction(att_bop, obj_bop) #判断是否可以射击,若可以射击，返回最佳射击武器
                        if flag:#可以射击
                            exe_success,_ = self.obj_interface.setFire(att_bop.ObjID,obj_bop.ObjID,(int)(weaponID)) #调用接口执行射击动作
                            if exe_success == 0: # 执行成功
                                att_bop.ObjAttack = 1
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
            # 更新敌方棋子信息来判断其是否处于同格从而避免攻击对方
            self.updateSDData()
            for att_bop in self.dic_metadata['l_obops']:
                for obj_bop in self.dic_metadata['l_ubops']:
                    flag,weaponID = self.genShootAction(att_bop, obj_bop) #判断是否可以射击,若可以射击，返回最佳射击武器
                    if flag:
                        exe_success,_ = self.obj_interface.setFire(att_bop.ObjID,obj_bop.ObjID,(int)(weaponID)) #调用接口执行射击动作
                        if exe_success == 0: # 执行成功
                            att_bop.ObjAttack = 1
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

    def doMyMoveAction(self):
        ''' 此时可能更新目标方位，默认目标为上次的目标位置'''
        try:
            res = False
            last_targets = self.dic_targets;
            self.dic_targets = {}

            for bop in self.dic_metadata['l_obops']:
                bopId = common.getBopIdentity(bop)
                if bopId in last_targets:
                    self.dic_targets[bopId] = last_targets[bopId]

            for bop in self.dic_metadata['l_obops']:
                if bop.ObjTypeX == 2:
                    res = self.doSoldierMoveAction(bop) or res 
            for bop in self.dic_metadata['l_obops']:
                if bop.ObjTypeX == 1:
                    res = self.doVehicleMoveAction(bop) or res
            for bop in self.dic_metadata['l_obops']:
                if bop.ObjTypeX == 0:
                    res = self.doTankMoveAction(bop) or res
            
            return res 
        except Exception as e:
            print('error in doMyMoveAction(): ' + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print('error in doMyMoveAction(): ' + str(k))
            self.__del__()
            raise
            
    def doTankMoveAction(self,tank_bop):
        ''' 坦克在机动环节动作为若当前主要争夺点没有我方旗子且没有我方旗子目标是它，则向其移动
        如果路途中遇到其它敌方棋子，则攻击对方'''
        try:
            res = False
            #print(common.getBopIdentity(tank_bop)," do some actions.")
            # 夺控动作
            if self.genOccupyAction(tank_bop): #判断是否可以夺控
                self.obj_interface.setOccupy(tank_bop.ObjID) #调用接口执行夺控动作
                res = True

            #  self.dic_metadata['l_ubops'] = self.dic_metadata['l_ubops'] #敌方棋子
            main_city = wgsdata.mainCity(self.dic_metadata['l_cities'])
            bopId = common.getBopIdentity(tank_bop)
            
            #设定目标
            _,dis_to_main = self.obj_interface.getMapDistance(tank_bop.ObjPos,main_city)
            self.updateSDData()
            
            if self.moveToSecondary(): #占领次要目标地扩大比分
                self.dic_targets[bopId] = wgsdata.secondaryCity(self.dic_metadata['l_cities'])
                res = self.doMove(tank_bop) or res
            elif dis_to_main == 0 or main_city not in self.dic_targets.values() and not self.main_city_occupied:
                self.dic_targets[bopId] = main_city
                #移动
                res = self.doMove(tank_bop) or res
            elif len(self.dic_metadata['l_ubops']) > 0:
                cur_ser = wgobject.bop2Ser(tank_bop)
                ubop_target = None
                min_dis = 10
                for ubop in self.dic_metadata['l_ubops']: #找个最近的非同格目标进行行进间射击,优先堆叠的对象
                    if ubop.ObjTongge == 0 and (ubop_target == None or self.obj_interface.getMapDistance(tank_bop.ObjPos,ubop.ObjPos)[1] <= min_dis):
                        if ubop.ObjBlood < 3 or len(common.getAllBopByPos(self.dic_metadata['l_ubops'],ubop.ObjPos)) >= 2:
                            min_dis = 0
                        else: 
                            _, min_dis = self.obj_interface.getMapDistance(tank_bop.ObjPos,ubop.ObjPos)
                        ubop_target = ubop

                # obj_ser = wgobject.bop2Ser(ubop_target)
                # _,flag_see = self.obj_interface.flagISU(cur_ser,obj_ser)
                if tank_bop.ObjAttack == 0 and ubop_target:
                    res = self.doMoveShootAction(tank_bop,ubop_target) or res
                #掩蔽
                score = self.obj_interface.getScore()
                if (self.flag_color == 0 and score["BlueScore"][0]+30<score["RedScore"][0] or self.flag_color == 1 and score["BlueScore"][0]>score["RedScore"][0]+30) and len(self.dic_metadata['l_ubops']) == 0:
                    self.obj_interface.setState(tank_bop.ObjID,2)
                self.updateSDData()

                if tank_bop.ObjAttack == 1:
                    res = self.doMove(tank_bop) or res 

            else:
                if self.flag_color == 0:
                    self.dic_targets[bopId] = main_city-1
                else:
                    self.dic_targets[bopId] = main_city+2
                #移动
                res = self.doMove(tank_bop) or res
            # else:
            #     self.dic_targets[bopId] = main_city
            #     res = self.doMove(tank_bop) or res
            return res

        except Exception as e:
            print('error in doTankMoveAction(): ' + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print('error in doTankMoveAction(): ' + str(k))
            self.__del__()
            raise

    def doVehicleMoveAction(self,vehicle_bop):
        ''' 战车在机动环节动作为若当前主要争夺点没有我方旗子且没有我方旗子目标是它，则向其移动'''
        try:
            res = False
            # 夺控动作
            #print(common.getBopIdentity(vehicle_bop)," do some actions.")
            if self.genOccupyAction(vehicle_bop): #判断是否可以夺控
                self.obj_interface.setOccupy(vehicle_bop.ObjID) #调用接口执行夺控动作
                res = True

            main_city = wgsdata.mainCity(self.dic_metadata['l_cities'])
            bopId = common.getBopIdentity(vehicle_bop)
            
            #设定目标
            self.dic_metadata['l_ubops'] = self.dic_metadata['l_ubops'] #敌方棋子
            cur_ser = wgobject.bop2Ser(vehicle_bop)
            flag_move = True
            for ubop in self.dic_metadata['l_ubops']:
                obj_ser = wgobject.bop2Ser(ubop)
                _,flag_see = self.obj_interface.flagISU(cur_ser,obj_ser)
                _,distance = self.obj_interface.getMapDistance(vehicle_bop.ObjPos,ubop.ObjPos)
                if flag_see and distance <= 4:
                    flag_move = False
                    break

            #是否帮助同格的己方棋子
            flag_help = False
            tonggeTarget = None
            for ubop in self.dic_metadata['l_ubops']:
                us = common.getAllBopByPos(self.dic_metadata['l_obops'],ubop.ObjPos)
                enemy = common.getAllBopByPos(self.dic_metadata['l_ubops'],ubop.ObjPos)
                if us != None and enemy != None and len(us) <= len(enemy):
                    flag_help = True
                    tonggeTarget = ubop.ObjPos

            if self.moveToSecondary(): #占领次要目标地扩大比分
                self.dic_targets[bopId] = wgsdata.secondaryCity(self.dic_metadata['l_cities'])
                res = self.doMove(vehicle_bop) or res
            elif flag_help:
                self.dic_targets[bopId] = tonggeTarget #帮助同格本方棋子
            elif main_city not in self.dic_targets.values() and flag_move:
                self.dic_targets[bopId] = main_city #设定目标为主要目标地
            else:
                if vehicle_bop.ObjSonNum == 1:
                    self.dic_targets[bopId] = main_city
                else:
                    if self.flag_color == 0:
                        self.dic_targets[bopId] = main_city +3
                    else:
                        self.dic_targets[bopId] = main_city

            _,dis_to_main = self.obj_interface.getMapDistance(vehicle_bop.ObjPos,main_city)
            if self.main_city_occupied:
                if self.flag_color == 0:
                    self.dic_targets[bopId] = main_city - 2
                else:
                    self.dic_targets[bopId] = main_city + 1

            #下车
            if vehicle_bop.ObjSonNum == 1:  # 载人车辆
                _, dis = self.obj_interface.getMapDistance(vehicle_bop.ObjPos, self.dic_targets[bopId]) # 距离夺控点的距离
                if dis <= 1 or not flag_move: # 距离目标<1
                    if self.genGetOffAction(vehicle_bop): #判断是否满足下车条件
                        self.obj_interface.setGetoff(vehicle_bop.ObjID) # 调用接口执行下车动作
                        res = True

            #移动
            if flag_move or flag_help:
                res = self.doMove(vehicle_bop) or res
            # #掩蔽
            # elif len(self.dic_metadata['l_ubops']) == 0:
            #     self.obj_interface.setState(att_bop.ObjID,2)
            return res

        except Exception as e:
            print('error in doVehicleMoveAction(): ' + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print('error in doVehicleMoveAction(): ' + str(k))
            self.__del__()
            raise

    def doSoldierMoveAction(self,soldier_bop):
        ''' 步兵在机动环节动作为若当前主要争夺点没有我方旗子且没有我方旗子目标是它，则向其移动一步'''
        try:
            res = False
            # 夺控动作
            #print(common.getBopIdentity(soldier_bop)," do some actions.")
            if self.genOccupyAction(soldier_bop): #判断是否可以夺控
                self.obj_interface.setOccupy(soldier_bop.ObjID) #调用接口执行夺控动作
                res = True

            main_city = wgsdata.mainCity(self.dic_metadata['l_cities'])
            bopId = common.getBopIdentity(soldier_bop)
            #设定目标
            self.dic_metadata['l_ubops'] = self.dic_metadata['l_ubops'] #敌方棋子
            cur_ser = wgobject.bop2Ser(soldier_bop)
            flag_move = True
            for ubop in self.dic_metadata['l_ubops']:
                obj_ser = wgobject.bop2Ser(ubop)
                _,flag_see = self.obj_interface.flagISU(cur_ser,obj_ser)
                _,distance = self.obj_interface.getMapDistance(soldier_bop.ObjPos,ubop.ObjPos)
                if flag_see and distance <= 2:
                    flag_move = False
                    break

            if main_city not in self.dic_targets.values() and flag_move:
                self.dic_targets[bopId] = main_city
            else:
                self.dic_targets[bopId] = soldier_bop.ObjPos
            #移动
            us = common.getAllBopByPos(self.dic_metadata['l_obops'],main_city)
            enemy = common.getAllBopByPos(self.dic_metadata['l_ubops'],main_city)
            flag_occupy = enemy == None or (us != None and enemy!=None and len(us) <= len(enemy)) 
            flag,l_path = self.genMoveAction(soldier_bop, self.dic_targets[bopId])
            if flag and l_path and flag_occupy and not wgruler.haveMoved(soldier_bop,self.dic_metadata['l_stage']):
                self.obj_interface.setMove(soldier_bop.ObjID,l_path[:]) #调用接口函数执行机动动作
                res = True
            return res 

        except Exception as e:
            print('error in doSoldierMoveAction(): ' + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print('error in doSoldierMoveAction(): ' + str(k))
            self.__del__()
            raise

    def doMoveShootAction(self,att_bop,obj_bop):
        ''' 只有坦克可以选择行进间射击'''
        try:
            print(att_bop.ObjID,"doMoveShootAction")
            res = False
            flag_help = False
            #移动到旁边然后攻击对方，攻击完之后后退
            self.genMoveShootTarget(att_bop,obj_bop)
            res = self.doMove(att_bop)
          
            flag,weaponID = self.genShootAction(att_bop, obj_bop) #判断是否可以射击,若可以射击，返回最佳射击武器
            if flag: #可以射击
                exe_success,_ = self.obj_interface.setFire(att_bop.ObjID,obj_bop.ObjID,(int)(weaponID)) #调用接口执行射击动作
                if exe_success == 0: # 执行成功
                    att_bop.ObjAttack = 1
                    res = True
                    #是否帮助同格的己方棋子
                    tonggeTarget = None
                    for ubop in self.dic_metadata['l_ubops']:
                        us = common.getAllBopByPos(self.dic_metadata['l_obops'],ubop.ObjPos)
                        enemy = common.getAllBopByPos(self.dic_metadata['l_ubops'],ubop.ObjPos)
                        if us != None and enemy != None and len(us) <= len(enemy):
                            flag_help = True
                            tonggeTarget = ubop.ObjPos

                    if flag_help:
                        self.dic_targets[common.getBopIdentity(att_bop)] = tonggeTarget
                    elif obj_bop.ObjTypeX == 2 and obj_bop.ObjBlood <= att_bop.ObjBlood:
                        self.dic_targets[common.getBopIdentity(att_bop)] = obj_bop.ObjPos
                    else:
                        self.genMoveShootBackTarget(att_bop,obj_bop) #后退三步

                    res = self.doMove(att_bop) or res
            else:
                print(att_bop.ObjStep, "jidongli ", att_bop.ObjStepMax)
                print("could not attack",common.getBopIdentity(obj_bop))

            #掩蔽
            if len(self.dic_metadata['l_ubops']) == 0:
                self.obj_interface.setState(att_bop.ObjID,2)
            return res

        except Exception as e:
            print('error in doTankMoveAction(): ' + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print('error in doTankMoveAction(): ' + str(k))
            self.__del__()
            raise

    def genMoveShootTarget(self,att_bop,obj_bop):
        #寻找行进间射击的目标位置，选取目标棋子周围最近的没有其它棋子的位置
        try:
            #around = common.getAroundPos(obj_bop.ObjPos)
            around = [80048,80049,80047,80045,70041,80050,att_bop.ObjPos+2,att_bop.ObjPos-2,att_bop.ObjPos+1,att_bop.ObjPos-1]
            target = None
            for pos in around:
                if pos == att_bop.ObjPos:
                    continue
                los = self.obj_interface.getLOS(pos,obj_bop.ObjPos)
                if los[0] == 0 and los[1]>=0 and common.getAllBopByPos(self.dic_metadata['l_ubops'],pos) == None:
                    if target == None or self.obj_interface.getMapDistance(pos,att_bop.ObjPos) <= self.obj_interface.getMapDistance(target,att_bop.ObjPos):
                        flag_set = True
                        flag,l_path = self.genMoveAction(att_bop,pos)
                        if l_path != None:
                            for p in l_path:
                                if common.getAllBopByPos(self.dic_metadata['l_ubops'],p) != None:
                                    flag_set = False 
                        if flag_set:
                            target = pos
            if target:
                self.dic_targets[common.getBopIdentity(att_bop)] = target

        except Exception as e:
            print('error in genMoveShootTarget(): ' + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print('error in genMoveShootTarget(): ' + str(k))
            self.__del__()
            raise

    def genMoveShootBackTarget(self,att_bop,obj_bop):
        #寻找行进间射击回退的位置
        try:
            around = [80047,80048,80045,70041,80050,80052,80049,80051,70051,70053,80054,80053]
            target = None
            for pos in around:
                if pos == att_bop.ObjPos:
                    continue
                flag_pos = True
                for bop in self.dic_metadata['l_ubops']:
                    los = self.obj_interface.getLOS(pos,bop.ObjPos)
                    if los[0] == 0 and los[1]<0:
                        flag_pos = True
                    else:
                        flag_pos = False
                        break
                if flag_pos and common.getAllBopByPos(self.dic_metadata['l_ubops'],pos) == None:
                    if target == None or self.obj_interface.getMapDistance(pos,att_bop.ObjPos) < self.obj_interface.getMapDistance(target,att_bop.ObjPos):
                        flag_set = True
                        flag,l_path = self.genMoveAction(att_bop,pos)
                        if l_path != None:
                            for p in l_path:
                                if common.getAllBopByPos(self.dic_metadata['l_ubops'],p) != None:
                                    flag_set = False 
                        if flag_set:
                            target = pos
            if target:
                self.dic_targets[common.getBopIdentity(att_bop)] = target

            print("go back to",target)

        except Exception as e:
            print('error in genMoveShootBackTarget(): ' + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print('error in genMoveShootBackTarget(): ' + str(k))
            self.__del__()
            raise

    def doMove(self, bop):
        #移动
        try:
            main_city = wgsdata.mainCity(self.dic_metadata['l_cities'])
            bopId = common.getBopIdentity(bop)
            flag,l_path = self.genMoveAction(bop, self.dic_targets[bopId])
            if flag and l_path:
                l = int(len(l_path)+1)//2 if len(l_path)>=4 else len(l_path)+1
                l_path = l_path[:l]
                if l_path[-1] == main_city and len(l_path)>=2:
                    l_path = l_path[:-1]
                self.obj_interface.setMove(bop.ObjID,l_path) #调用接口函数执行机动动作
                self.updateSDData()
                bop = common.getSpecifiedBopById(self.dic_metadata['l_obops'],common.getBopIdentity(bop))
                return True
            return False
        except Exception as e:
            common.echosentence_color("doMove error: " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color("doMove: " + str(k))
            self.__del__()
            raise

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
