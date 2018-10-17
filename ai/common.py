# coding:utf-8

# 全局变量
ji_neigh_offset = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, 0), (1, 1)]
ou_neigh_offset = [(0, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]
list_trans_neigh_edgeloc = [3, 4, 5, 0, 1, 2]
list_neighdir_offset_ji = ji_neigh_offset
list_neighdir_offset_ou = ou_neigh_offset

# 常用的坐标转换函数
def cvtInt4loc2Int6loc(int4loc):
    '''转换四位整形坐标int4loc到六位整形坐标int6loc'''
    try:
        assert isinstance(int4loc, int)
        tmp_row, tmp_col = int4loc // 100, int4loc % 100
        return cvtHexOffset2Int6loc(tmp_row, tmp_col)
    except Exception as e:
        echosentence_color('common > cvtInt4loc2Int6loc():{}'.format(str(e)))
        raise

def cvtInt6loc2Int4loc(int6loc):
    '''转换6位坐标int6loc到四位坐标int4loc'''
    try:
        assert isinstance(int6loc, int)
        y , x = cvtInt6loc2HexOffset ( int6loc )
        return y * 100 + x
    except Exception as e:
        echosentence_color('common cvtInt6loc2Int4loc():{}'.format(str(e)))
        raise

def cvtHexOffset2Int6loc(row, col):
    '''转换（row,col）到6位整型坐标'''
    try:
        if row % 2 == 1:
            tmpfirst = (row - 1) // 2
            tmplast = col * 2 + 1
        else:
            tmpfirst = row // 2
            tmplast = col * 2
        assert (tmpfirst >= 0 and tmplast >= 0)
        return int(tmpfirst * 10000 + tmplast)
    except Exception as e:
        echosentence_color('common > cvtHexOffset2Int6():{}'.format(str(e)))
        raise

def cvtInt6loc2HexOffset(int6loc):
    '''转换6位整形坐标int6loc转换为偏移坐标（y,x）2元组'''
    try:
        str6loc = str(int6loc)
        len_oristr6loc = len(str6loc)
        assert (len_oristr6loc <= 6)
        if len_oristr6loc < 6:
            str6loc = '0' * (6 - len_oristr6loc) + str6loc

        int_first_2, int_last_3 = int(str6loc[0:2]), int(str6loc[3:])
        if int_last_3 % 2 == 1:
            row , col = int_first_2 * 2 + 1 , (int_last_3 - 1) // 2
        else:
            row , col = int_first_2 * 2 , int_last_3 // 2
        return (row,col)
    except Exception as e:
        echosentence_color('comnon > cvtInt6loc2HexOffset():{}'.format(str(e)))
        raise

def tranlocInto4Str(y, x):
    '''将两个偏移整形坐标拼接成为四位字符串'''
    try:
        assert(x >=0 and x < 100 and y >=0 and y < 100)
        re = ''
        re += str(y) if y >= 10 else str(0) + str(y)
        re += str(x) if x >= 10 else str(0) + str(x)
        return re
    except Exception as e:
        echosentence_color(('error in common tranlocInto4str():{}'.format(str(e))))
        raise
def getAroundPos(pos):
    row,col = cvtInt6loc2HexOffset(pos);
    around = []
    around.append(cvtHexOffset2Int6loc(row-1,col))
    around.append(cvtHexOffset2Int6loc(row-1,col+1))
    around.append(cvtHexOffset2Int6loc(row,col+1))
    around.append(cvtHexOffset2Int6loc(row,col-1))
    around.append(cvtHexOffset2Int6loc(row+1,col))
    around.append(cvtHexOffset2Int6loc(row+1,col+1))
    return around

# 算子列表的筛选，查找，缩减工作: filter(function, list_bops)
def getSpecifiedBopById(list_bops, bop_id):
    '''给定算子ID，从当前敌我算子列表中找出对应的算子, 没有找到返回None；
        filter函数返回的是对象和原始列表中的对象的id相同'''
    try:
        # list_filtered_bops = filter(lambda cur_bop : cur_bop.ObjID == bop_id, list_bops)
        list_filtered_bops = [bop for bop in list_bops if bop_id == bop.ObjID]
        return list_filtered_bops[0] if len(list_filtered_bops) == 1 else None
    except Exception as e:
        echosentence_color('common > getSpecifiedBopById():{}'.format(str(e)))
        raise

def getSpecifiedBopByPos(list_bops, bop_pos, obj_type = -1):
    '''从指定的bop列表list_bops中找出位于指定位置bop_pos与类型obj_type的算子,没有返回None'''
    try:
        # list_filtered_bops = filter ( lambda cur_bop: cur_bop.ObjPos == bop_pos and cur_bop.ObjTypeX == obj_type , list_bops )
        if obj_type == -1: # all types
            list_filtered_bops = [bop for bop in list_bops if bop.ObjPos == bop_pos]
            return None if len(list_filtered_bops) == 0 else list_filtered_bops
        else:
            list_filtered_bops = [bop for bop in list_bops if bop.ObjPos == bop_pos and bop.ObjTypeX == obj_type]
            return list_filtered_bops[0] if len(list_filtered_bops) >= 1 else None
    except Exception as e:
        echosentence_color('common > getCorrespondingBopByPos():{}'.format(str(e)))
        raise

def getAllBopByPos(list_bops, bop_pos, obj_type = -1):
    '''从指定的bop列表list_bops中找出位于指定位置bop_pos与类型obj_type的所有算子,没有返回None'''
    try:
        # list_filtered_bops = filter ( lambda cur_bop: cur_bop.ObjPos == bop_pos and cur_bop.ObjTypeX == obj_type , list_bops )
        if obj_type == -1: # all types
            list_filtered_bops = [bop for bop in list_bops if bop.ObjPos == bop_pos]
            return None if len(list_filtered_bops) == 0 else list_filtered_bops
        else:
            list_filtered_bops = [bop for bop in list_bops if bop.ObjPos == bop_pos and bop.ObjTypeX == obj_type]
            return list_filtered_bops if len(list_filtered_bops) >= 1 else None
    except Exception as e:
        echosentence_color('common > getCorrespondingBopByPos():{}'.format(str(e)))
        raise

def getSpecifiedBopByIndex(list_bops, index):
    try:
        list_filtered = [bop for bop in list_bops if bop.ObjIndex == index]
        return list_filtered[0] if len(list_filtered) == 1 else None
    except Exception as e:
        echosentence_color('error in common.py > getSpecifiedBopByIndex():{}'.format(str(e)))
        raise

def getSpecifiedBopByIdentity(list_bops, identity):
    '''从输入列表中找出给定算子唯一标志的算子 GameColor + Army + ObjType, 没有找到返回None'''
    try:
        # list_filtered_bops = filter ( lambda cur_bop: '{}_{}_{}'.format ( cur_bop.GameColor , cur_bop.ObjArmy , cur_bop.ObjType ) == identity , list_bops )
        list_filtered_bops = [bop for bop in list_bops if '{}_{}_{}'.format ( bop.GameColor , bop.ObjArmy , bop.ObjType ) == identity]
        return list_filtered_bops [0] if len ( list_filtered_bops ) == 1 else None
    except Exception as e:
        echosentence_color('common > getSpecifiedBopByIdentity():{}'.format(str(e)))
        raise

def getBopIdentity(bop):
    return '{}_{}_{}'.format ( bop.GameColor , bop.ObjArmy , bop.ObjType )

def getValidTonggeBops(list_bops):
    '''处于同格状态并且能够还能继续射击的算子'''
    list_filtered_bops = [bop for bop in list_bops if bop.ObjTongge == 1 and bop.ObjTonggeShootCountLeft > 0 and bop.ObjBlood > 0]
    return list_filtered_bops

def getDiffSetForListBops(list_all_bops, list_bops):
    '''计算算子列表的补集'''
    try:
        list_diff_bops = []
        for cur_bop in list_all_bops:
            if not checkBopIsInList(list_bops, cur_bop):
                list_diff_bops.append(cur_bop)
        return list_diff_bops
    except Exception as e:
        echosentence_color('common > getDiffSetForListBops():{}'.format(str(e)))
        raise

def checkBopIsInList(list_bops, bop):
    '''利用算子ID检查算子bop 是否在给定的列表中list_bops中'''
    try:
        found_bop = getSpecifiedBopById(list_bops, bop.ObjID)
        return found_bop is not None
    except Exception as e:
        echosentence_color('common > checkBopIsInList():{}'.format(str(e)))
        raise

def getIndexInSpecifiedList(list_identities, bop):
    '''利用算子的identity找出算子在固定列表中的对应位置, 不存在返回-1'''
    try:
        identity =  '%d_%d_%d' % (bop.GameColor, bop.ObjArmy, bop.ObjType)
        return -1 if identity not in list_identities else list_identities.index(identity)
    except Exception as e:
        echosentence_color('common > getIndexInSpecifiedList():{}'.format(str(e)))
        raise

def removeZeorBloodBops (list_bops ):
    '''去掉算子列表中血量<=0的算子, 返回筛选后的算子列表'''
    try:
        # return filter(lambda bop: bop.ObjBlood > 0 , list_bops)
        return [bop for bop in list_bops if bop.ObjBlood > 0]
    except Exception as e:
        echosentence_color('common > removeZeorBops():{}'.format(str(e)))
        raise
    
def removeZeroShootCountBops(list_bops):
    return [bop for bop in list_bops if bop.ObjTonggeShootCountLeft > 0]
    
def getSpecifiedTaskFlag(cur_bop, dic_identity2flagmovings):
    '''算子identity ==> 算子的flag_moving'''
    try:
        str_identykey = '%d_%d_%d' % (cur_bop.GameColor, cur_bop.ObjArmy, cur_bop.ObjType)
        assert (str_identykey in dic_identity2flagmovings.keys())
        return dic_identity2flagmovings[str_identykey]
    except Exception as e:
        echosentence_color('common > getSpecifiedTaskFlag():{}'.format( str( e ) ))
        raise

# def getUniformTaskFlag(dic_identity2flagtasks):
#     '''检查并确认当前的任务'''
#     try:
#         list_taskflags = []
#         for key, value  in dic_identity2flagtasks.items():
#             list_taskflags.append(value)
#         assert  len(list_taskflags) > 0
#         if float(sum(list_taskflags)) / len(list_taskflags) == float(list_taskflags[0]):
#             return list_taskflags[0]
#         return -1
#     except Exception as e:
#         echosentence_color('PreKnow > getUniformTaskFlag():{}'.format(str(e)))
#         raise

# 取相对偏移量，输入参数为方向，距离 ==> 输出立方坐标系统下所有符合要求的偏移向量列表

list_dir2cubeoff = [[1,0,-1], [1,-1,0],[0,-1,1],[-1,0,1],[-1,1,0],[0,1,-1]]

def getDirOffVectorList(dir, dis):
    try:
        assert  dir in range(6) and dis > 0
        list_result = []
        sameloc = dir % 3
        varyloc = (sameloc + 1) % 3
        hastovaryloc = (sameloc + 2) % 3
        varyIncre = -1 if dir % 2 == 0  else 1
        for dis_index in range(1, dis+1):
            base_cur  = [x * dis_index for x in list_dir2cubeoff[dir]]
            # base_next = [x * dis_index for x in list_dir2cubeoff[(dir + 1) % 6]]
            list_result.append(base_cur)
            for i in range(1, dis_index):
                list_tmp_vec = [0] * 3
                list_tmp_vec[sameloc] = base_cur[sameloc]
                list_tmp_vec[varyloc] = base_cur[varyloc] + varyIncre * i
                list_tmp_vec[hastovaryloc] = 0 - list_tmp_vec[sameloc] - list_tmp_vec[varyloc]
                list_result.append(list_tmp_vec)
        return list_result
    except Exception as e:
        echosentence_color('common > getDirOffVectorList():{}'.format(str(e)))
        raise e

def writelist2(list2_eles, filename):
    with open(filename, 'w') as file:
        for list_eles in list2_eles:
            file.writelines(["{}\t".format(item)  for item in list_eles])
            # file.writelines(["{}\t".format(item)  for item in list_eles])
            file.write('\n')

def readlist( filename):
    list2_eles =  []
    with open(filename, 'r') as file:
        list2_streles = file.readlines()
        for str_list in list2_streles:
            list_ele = [float(ele) for ele in str_list.strip('\n').strip('\t').split('\t')]
            list2_eles.append(list_ele)
    return list2_eles

def echosentence_color(str_sentence = None, color = None, flag_newline = True):
    try:
        if color is not None:
            list_str_colors = ['darkbrown', 'red', 'green', 'yellow', 'blue', 'purple', 'yank', 'white']
            assert  str_sentence is not None and color in list_str_colors
            id_color = 30 + list_str_colors.index(color)
            print('\33[1;35;{}m'.format(id_color) + str_sentence + '\033[0m')
        else:
            if flag_newline :
                print(str_sentence)
            else:
                print(str_sentence,end=" ")
    except Exception as e:
        print('error in echosentence_color {}'.format(str(e)))
        raise

if __name__ == "__main__":
    # print getDirOffVectorList(dir= 3, dis= 3)
    pass