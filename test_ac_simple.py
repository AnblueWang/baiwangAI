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




if __name__ == '__main__':
    ip = sys.argv[1] # ip address
    roomid = int(sys.argv[2]) + 0 # roomid
    flag_ai_color = int(sys.argv[3]) # 0-red 1-blue
    flag_ai_color = 'RED' if flag_ai_color == 0 else 'BLUE'
    num_xd = dic_xd2aixd[int(sys.argv[4])] # Scenario 想定

    obj_interface = None
    obj_ai = None
    try:
        obj_interface = wginterface.AI_InterFace(ipaddress = ip,roomID = roomid,gameColor = flag_ai_color,num_xd = num_xd)
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
