import copy
import os

from utils.rw_txt import *
from utils.rw_json import *

from gen_train_dataset import process_one_action


def read_upfall(folder):
    def read_one_file(file_path):
        lines = read_txt(file_path)

        action0 = { 'X_Axis':[], 'Y_Axis':[], 'Z_Axis':[], 'sensor_type': 'accelerometer', 'location': 'ankle'}
        action1 = { 'X_Axis':[], 'Y_Axis':[], 'Z_Axis':[], 'sensor_type': 'accelerometer', 'location': 'right pocket'}
        action2 = { 'X_Axis':[], 'Y_Axis':[], 'Z_Axis':[], 'sensor_type': 'accelerometer', 'location': 'waist'}
        action3 = { 'X_Axis':[], 'Y_Axis':[], 'Z_Axis':[], 'sensor_type': 'accelerometer', 'location': 'neck'}
        action4 = { 'X_Axis':[], 'Y_Axis':[], 'Z_Axis':[], 'sensor_type': 'accelerometer', 'location': 'wrist'}

        flag0 = 0
        flag1 = 0
        flag2 = 0
        flag3 = 0
        flag4 = 0

        for i, line in enumerate(lines[2:]):
            #print(' ---- i, line: ', i, line)
            tmp = line.split(',')
            x0, y0, z0 = tmp[1:4]   
            x1, y1, z1 = tmp[8:11]   
            x2, y2, z2 = tmp[15:18]     
            x3, y3, z3 = tmp[22:25]     
            x4, y4, z4 = tmp[29:32]  

            if x0 != '': 
                action0['X_Axis'].append(float(x0))
                action0['Y_Axis'].append(float(y0))
                action0['Z_Axis'].append(float(z0))
            else:
                flag0 = 1

            if x1 != '': 
                action1['X_Axis'].append(float(x1))
                action1['Y_Axis'].append(float(y1))
                action1['Z_Axis'].append(float(z1))
            else:
                flag1 = 1

            if x2 != '': 
                action2['X_Axis'].append(float(x2))
                action2['Y_Axis'].append(float(y2))
                action2['Z_Axis'].append(float(z2))
            else:
                flag2 = 1

            if x3 != '': 
                action3['X_Axis'].append(float(x3))
                action3['Y_Axis'].append(float(y3))
                action3['Z_Axis'].append(float(z3))
            else:
                flag3 = 1

            if x4 != '': 
                action4['X_Axis'].append(float(x4))
                action4['Y_Axis'].append(float(y4))
                action4['Z_Axis'].append(float(z4))
            else:
                flag4 = 1

        action0_tp = None if flag0 == 1 else action0
        action1_tp = None if flag1 == 1 else action1
        action2_tp = None if flag2 == 1 else action2
        action3_tp = None if flag3 == 1 else action3
        action4_tp = None if flag4 == 1 else action4

        #return action0, action1, action2, action3, action4
        return action0_tp, action1_tp, action2_tp, action3_tp, action4_tp

    Activity_to_classname = {
        1: 'Falling forward using hands',
        2: 'Falling forward using knees',
        3: 'Falling backwards',
        4: 'Falling sideward',
        5: 'Falling sitting in empty chair',
        6: 'Walking',
        7: 'Standing',
        8: 'Sitting',
        9: 'Picking up an object',
        10: 'Jumping',
        11: 'Laying',
    }

    actions = []
    actions_info = {'len': []}
    files1 = os.listdir(folder)
    for i, file1 in enumerate(files1):
        print(' ---- i, len(files1) file1: ', i, len(files1), file1)
        if file1[0] == '.': continue
        
        #if i < 392: continue
        #if file1 != 'UMAFall_Subject_13_ADL_Walking_3_2016-06-06_16-43-29.csv': continue

        Subject = file1.split('Activity')[0].replace('Subject', '')
        Activity = int(file1.split('Activity')[1].split('Trial')[0])
        class_name = Activity_to_classname[Activity]
        ADL_Fall = 'Fall' if Activity < 6 else 'ADL'

        file_path = folder + '/' + file1
        action0, action1, action2, action3, action4 = read_one_file(file_path)
        for action in [action0, action1, action2, action3, action4]:
            if action is None : continue
            if len(action['X_Axis']) ==0 : continue

            action['file_name'] = file1
            action['ADL_Fall'] = ADL_Fall
            action['class_name'] = class_name
            action['activity'] = Activity
            action['subject'] = Subject
            action['sample_rate'] = 18.4

            actions_info['len'].append(len(action['X_Axis']))
            actions.append(action)

    return actions, actions_info


def gen_upfall_train_dataset(actions):
    pos_ss_max_list, pos_ss_min_list = {}, {}
    for action in actions:
        ss = action['X_Axis'] + action['Y_Axis'] + action['Z_Axis']
        ss_max, ss_min = max(ss), min(ss)

        pos = action['location'] 
        if pos not in pos_ss_max_list: pos_ss_max_list[pos] = []
        if pos not in pos_ss_min_list: pos_ss_min_list[pos] = []

        pos_ss_max_list[pos].append(ss_max)
        pos_ss_min_list[pos].append(ss_min)

    pos_s_max, pos_s_min = {}, {}
    for pos, ss_max_list in pos_ss_max_list.items():
        s_max = max(ss_max_list)
        pos_s_max[pos] = s_max
    for pos, ss_min_list in pos_ss_min_list.items():
        s_min = min(ss_min_list)
        pos_s_min[pos] = s_min


    out = []
    out_info = {'len': []}
    for action in actions:
        pos = action['location']
        s_max, s_min = pos_s_max[pos], pos_s_min[pos]

        res = process_one_action(action, s_max, s_min)
        out_info['len'].append(len(res['X_Axis']))
        out.append(res)
    return out, out_info


def process_upfall_dataset(folder_in):
    folder = folder_in + '/upfall/dataset'
    folder_save = folder_in + '/upfall/dataset_processed'
    if not os.path.exists(folder_save): os.makedirs(folder_save)

    json_path_select = folder_save + '/select.json'
    json_path_select_info = folder_save + '/select_info.json'

    json_path_out = folder_save + '/out.json'
    json_path_out_info = folder_save + '/out_info.json'

    # ==== select acc
    if not os.path.exists(json_path_select):
        actions, actions_info = read_upfall(folder)
        write_json(json_path_select, actions) 
        write_json(json_path_select_info, actions_info) 
    else: 
        actions = read_json(json_path_select) 
        actions_info = read_json(json_path_select_info) 
    print(' ---- len(actions), len(actions_info): ', len(actions), len(actions_info))


    # ==== gen_train_dataset
    out, out_info = gen_upfall_train_dataset(actions)
    write_json(json_path_out, out) 
    write_json(json_path_out_info, out_info) 
    print(' ---- len(out), len(out_info): ', len(out), len(out_info))


    
if __name__ == '__main__':
    process_upfall_dataset()



