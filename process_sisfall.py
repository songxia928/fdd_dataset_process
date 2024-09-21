
import copy
import os


from utils.rw_txt import *
from utils.rw_json import *

from gen_train_dataset import process_one_action




def read_sisfall(folder):
    def read_one_file(file_path):
        lines = read_txt(file_path)

        action0 = { 'X_Axis':[], 'Y_Axis':[], 'Z_Axis':[], 'sensor_type': 'accelerometer', 'location': 'waist'}
        action1 = { 'X_Axis':[], 'Y_Axis':[], 'Z_Axis':[], 'sensor_type': 'accelerometer', 'location': 'waist'}

        for i, line in enumerate(lines):
            #print(' ---- i, line: ', i, line)
            line = line.replace(';', '').replace(' ', '')
            if len(line) == 0: continue

            tmp = line.split(',')
            
            x0, y0, z0 = tmp[0], tmp[1], tmp[2]   
            x1, y1, z1 = tmp[6], tmp[7], tmp[8]
            #print(' ---- x0, y0, z0,   x1, y1, z1: ', x0, y0, z0,   x1, y1, z1)

            action0['X_Axis'].append(float(x0))
            action0['Y_Axis'].append(float(y0))
            action0['Z_Axis'].append(float(z0))

            action1['X_Axis'].append(float(x1))
            action1['Y_Axis'].append(float(y1))
            action1['Z_Axis'].append(float(z1))

        return action0, action1

    

    actions = []
    actions_info = {'len': []}
    files0 = os.listdir(folder)
    for j, file0 in enumerate(files0):
        if file0[0] == '.': continue
        if file0[-4:] == '.txt' or file0[-4:] == '.pdf': continue

        folder1 = folder + '/' + file0
        files1 = os.listdir(folder1)
        for i, file1 in enumerate(files1):
            print(' ---- j, len(files0),  i, len(files1) file1: ', j, len(files0),  i, len(files1), file1)
            if file1[0] == '.': continue
            if file1[-4:] != '.txt': continue
        
            #if i < 392: continue
            #if file1 != 'UMAFall_Subject_13_ADL_Walking_3_2016-06-06_16-43-29.csv': continue
            tmp = file1.replace('.txt', '').split('_')

            Subject = tmp[1].replace('SA', '')
            Activity = tmp[0]
            class_name = tmp[0]
            ADL_Fall = 'Fall' if Activity[0] == 'F' else 'ADL'

            file_path = folder1 + '/' + file1
            action0, action1 = read_one_file(file_path)
            for action in [action0, action1]:
                if len(action['X_Axis']) ==0 : continue

                action['file_name'] = file1
                action['ADL_Fall'] = ADL_Fall
                action['class_name'] = class_name
                action['activity'] = Activity
                action['subject'] = Subject
                action['sample_rate'] = 200

                actions_info['len'].append(len(action['X_Axis']))
                actions.append(action)

    return actions, actions_info


def gen_sisfall_train_dataset(actions):
    out = []
    out_info = {'len': []}
    
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

    for action in actions:
        pos = action['location']
        s_max, s_min = pos_s_max[pos], pos_s_min[pos]

        res = process_one_action(action, s_max, s_min)
        out_info['len'].append(len(res['X_Axis']))
        out.append(res)
    return out, out_info


def process_sisfall_dataset(folder_in):
    folder = folder_in + '/sisfall/dataset'
    folder_save = folder_in + '/sisfall/dataset_processed'
    if not os.path.exists(folder_save): os.makedirs(folder_save)

    json_path_select = folder_save + '/select.json'
    json_path_select_info = folder_save + '/select_info.json'

    json_path_out = folder_save + '/out.json'
    json_path_out_info = folder_save + '/out_info.json'

    # ==== select acc
    if not os.path.exists(json_path_select):
        actions, actions_info = read_sisfall(folder)
        write_json(json_path_select, actions) 
        write_json(json_path_select_info, actions_info) 
    else: 
        actions = read_json(json_path_select) 
        actions_info = read_json(json_path_select_info) 
    print(' ---- len(actions), len(actions_info): ', len(actions), len(actions_info))


    # ==== gen_train_dataset
    out, out_info = gen_sisfall_train_dataset(actions)
    write_json(json_path_out, out) 
    write_json(json_path_out_info, out_info) 
    print(' ---- len(out), len(out_info): ', len(out), len(out_info))


    
if __name__ == '__main__':
    process_sisfall_dataset()



