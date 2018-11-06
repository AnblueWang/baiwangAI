#coding:utf-8

import sys

sys.path.append('./ai/')
sys.path.append('./interface/')
import __wginterface as wginterface
import wgAI


''' 将输入想定转化为接口想定'''
dic_xd2aixd = {
    0: 0,
    9:9,
    15:15,
}


def usage():
    print('argv[0] = test_ac.simple.py 脚本名称')
    print('argv[1] = ipaddress  ip地址')
    print('argv[2] = roomid  推演室编号')
    print('argv[3] = flag_color  所选颜色：0或1 ，0== RED 1== BLUE' )
    print('argv[4] = num_xd  想定编号 0 == 城镇居民地')
    print('argv[5] = user  用户名')
    print('argv[6] = pwd  密码')

if __name__ == '__main__':
    try:
        ip = sys.argv[1] # ip address
        roomid = int(sys.argv[2]) + 0 # roomid
        flag_ai_color = int(sys.argv[3]) # 0-red 1-blue
        assert flag_ai_color in [0,1]
        flag_ai_color = 'RED' if flag_ai_color == 0 else 'BLUE'
        num_xd = dic_xd2aixd[int(sys.argv[4])] # Scenario 想定
        user =sys.argv[5]
        pwd = sys.argv[6]
    except Exception as e:
        print('命令行参数错误')
        print('---------------')
        usage()
        print('---------------')
        raise

    obj_interface = None
    obj_ai = None
    try:
        obj_interface = wginterface.AI_InterFace(user = user,pwd = pwd,ipaddress = ip,roomID = roomid,gameColor = flag_ai_color,num_xd = num_xd)
        print('='*20+'\n'+'u成功启动AI'+'\n'+'='*20 + '\n' + '-'*20)
        obj_ai = wgAI.AI(obj_interface,flag_ai_color)
        obj_ai.run()
    except Exception as e:
        print(" " + str(e))
        if obj_interface is not None:
            obj_interface.__del__()
        if obj_ai is not None:
            obj_ai.__del__()
        raise
    except KeyboardInterrupt as k:
            print(" " + str(k))
            if obj_interface is not None:
                obj_interface.__del__()
            if obj_ai is not None:
                obj_ai.__del__()
            raise
