import copy
import os

from utils.rw_txt import *
from utils.rw_json import *

from gen_train_dataset import process_one_action


def read_umafall(folder):
    def read_one_file(file_path):
        def delete_points_in_string(s):
            num = s.count(".")
            if num <= 1: return s, 0
            
            idx = s.index('.')
            s_out = s[:idx+1] + s[idx+1:].replace('.', '')
            #return s_out, True   
            return s, 1   

        def repair_610E10(s, ss_forward, ss_back):
            if s != "-6,10E+10": return s, 0

            idx = -1
            not_610E10 = True
            while not_610E10:
                s_pre = ss_forward[idx]
                if s_pre != "-6,10E+10":
                    not_610E10 = False
                idx -= 1

            idx = 0
            not_610E10 = True
            while not_610E10:
                s_next = ss_back[idx]
                if s_next != "-6,10E+10":
                    not_610E10 = False
                idx += 1

            s_out = str( (float(s_pre) + float(s_next))/2 )
            #return s_out, True
            return s, 1


        lines = read_txt(file_path)
        for i, line in enumerate(lines):
            if len(line) == 0: continue
            elif line[:4] == '    ': continue
            elif line[0] != '%':
               idx_st = i
               break

        info = { 'TimeStamp':[], 'Sample_No':[], 
                'X_Axis':[], 'Y_Axis':[], 'Z_Axis':[], 
                'Sensor_Type':[], 'Sensor_ID':[],
                'flag_point':[], 'flag_610E10':[]}

        X_Axis_list, Y_Axis_list, Z_Axis_list = [], [], []
        for i, line in enumerate(lines[idx_st:]):
            ii = idx_st + i
            #print(' ---- idx_st, line: ', idx_st, line)
            TimeStamp, Sample_No, X_Axis, Y_Axis, Z_Axis, Sensor_Type, Sensor_ID = line.split(';')[:7]
            X_Axis, flag_X = delete_points_in_string(X_Axis)
            Y_Axis, flag_Y = delete_points_in_string(Y_Axis)
            Z_Axis, flag_Z = delete_points_in_string(Z_Axis)

            flag_point = 1 if flag_X or flag_Y or flag_Z else 0

            #if flag_X or flag_Y or flag_Z: print(' ---- delete_points_in_string. file_path, i, line:', file_path, i, line, X_Axis, Y_Axis, Z_Axis)

            TimeStamp, Sample_No, Sensor_Type, Sensor_ID = int(TimeStamp), int(Sample_No),  int(Sensor_Type), int(Sensor_ID) 

            X_Axis_list.append(X_Axis)
            Y_Axis_list.append(Y_Axis)
            Z_Axis_list.append(Z_Axis)

            info['TimeStamp'].append(TimeStamp)
            info['Sample_No'].append(Sample_No)
            info['Sensor_Type'].append(Sensor_Type)
            info['Sensor_ID'].append(Sensor_ID)
            info['flag_point'].append(flag_point)

        for i, (X_Axis, Y_Axis, Z_Axis) in enumerate(zip(X_Axis_list, Y_Axis_list, Z_Axis_list)):
            X_Axis, flag_X = repair_610E10(X_Axis, X_Axis_list[i-5:i], X_Axis_list[i+1:i+5])
            Y_Axis, flag_Y = repair_610E10(Y_Axis, Y_Axis_list[i-5:i], Y_Axis_list[i+1:i+5])
            Z_Axis, flag_Z = repair_610E10(Z_Axis, Z_Axis_list[i-5:i], Z_Axis_list[i+1:i+5])

            flag_610E10 = 1 if flag_X or flag_Y or flag_Z else 0

            #if flag_X or flag_Y or flag_Z: print(' ---- repair_610E10. after. file_path, i, line, X_Axis, Y_Axis, Z_Axis:', file_path, i, X_Axis_list[i], Y_Axis_list[i], Z_Axis_list[i],  X_Axis, Y_Axis, Z_Axis)

            #X_Axis, Y_Axis, Z_Axis = float(X_Axis), float(Y_Axis), float(Z_Axis)

            info['flag_610E10'].append(flag_610E10)
            info['X_Axis'].append(X_Axis)
            info['Y_Axis'].append(Y_Axis)
            info['Z_Axis'].append(Z_Axis)

        return info
   
    res = []
    files1 = os.listdir(folder)
    for i, file1 in enumerate(files1):
        print(' ---- i, len(files1) file1: ', i, len(files1), file1)
        if file1[0] == '.': continue
        
        #if i < 392: continue
        #if file1 != 'UMAFall_Subject_13_ADL_Walking_3_2016-06-06_16-43-29.csv': continue

        file_path = folder + '/' + file1
        info = read_one_file(file_path)

        tmp = file1.replace('.csv', '').split('_')
        info['Subject'] = tmp[2]
        info['ADL_Fall'] = tmp[3]
        info['class_name'] = tmp[4]
        info['filename'] = file1

        res.append(info)

   

    return res


def select_acc_and_split_action(res):
    actions = []
    actions_info = []


    sensor_id_to_position = {
                            0: 'right pocket',
                            1: 'wrist',
                            2: 'ankle',
                            3: 'waist',
                            4: 'chest',
                          }

    for info in res:
        TimeStamp, Sample_No, X_Axis, Y_Axis, Z_Axis, Sensor_Type, Sensor_ID, Flag_point, Flag_610E10 = info['TimeStamp'], info['Sample_No'], info['X_Axis'], info['Y_Axis'], info['Z_Axis'], info['Sensor_Type'], info['Sensor_ID'], info['flag_point'], info['flag_610E10']
        Subject, ADL_Fall, class_name, filename = info['Subject'], info['ADL_Fall'], info['class_name'], info['filename'] 

        action = {'X_Axis':[], 'Y_Axis':[], 'Z_Axis':[], 
                'sensor_type':'accelerometer'}
        flag = 0
        action_info = { }

        sensor_type_old, sensor_id_old = Sensor_Type[0], Sensor_ID[0]
        for timestamp, sample_no, x_axis, y_axis, z_axis, sensor_type, sensor_id, flag_point, flag_610E10 in zip(TimeStamp, Sample_No, X_Axis, Y_Axis, Z_Axis, Sensor_Type, Sensor_ID, Flag_point, Flag_610E10):

            if flag_point or flag_610E10:
                flag = 1

            if sensor_type_old != sensor_type or sensor_id_old != sensor_id: # split action      
                if len(action['X_Axis']) > 0 and flag == 0:
                    X_Axis = [float(d) for d in action['X_Axis']]
                    Y_Axis = [float(d) for d in action['Y_Axis']]
                    Z_Axis = [float(d) for d in action['Z_Axis']]
                    action['X_Axis'] = X_Axis
                    action['Y_Axis'] = Y_Axis
                    action['Z_Axis'] = Z_Axis
                    actions.append(action)
                    actions_info.append(action_info)
                action = { 'X_Axis':[], 'Y_Axis':[], 'Z_Axis':[], 
                        'sensor_type':'accelerometer'}
            
                action_info = {}

            sensor_type, sensor_id_old = sensor_type, sensor_id 

            if sensor_type != 0: continue   # not acc
 
            action['location'] = sensor_id_to_position[sensor_id]
            action['sample_rate'] = 200 if sensor_id==0 else 20
            action['subject'] = Subject
            action['ADL_Fall'] = ADL_Fall
            action['class_name'] = class_name
            action['file_name'] = filename

            action['X_Axis'].append(x_axis)
            action['Y_Axis'].append(y_axis)
            action['Z_Axis'].append(z_axis)

            action_info['len'] = len(action['X_Axis'])

        if len(action['X_Axis']) > 0 and flag == 0:
            X_Axis = [float(d) for d in action['X_Axis']]
            Y_Axis = [float(d) for d in action['Y_Axis']]
            Z_Axis = [float(d) for d in action['Z_Axis']]
            action['X_Axis'] = X_Axis
            action['Y_Axis'] = Y_Axis
            action['Z_Axis'] = Z_Axis
            actions.append(action)
            actions_info.append(action_info)
    return actions, actions_info


def gen_umafall_train_dataset(actions):


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


def process_umafall_dataset(folder_in):
    folder = folder_in + '/umafall/dataset'
    folder_save = folder_in + '/umafall/dataset_processed'
    if not os.path.exists(folder_save): os.makedirs(folder_save)

    json_path_all = folder_save + '/all.json'
    json_path_select = folder_save + '/select.json'
    json_path_select_info = folder_save + '/select_info.json'

    json_path_out = folder_save + '/out.json'
    json_path_out_info = folder_save + '/out_info.json'

    # ==== read file
    if not os.path.exists(json_path_all):
        res = read_umafall(folder)
        write_json(json_path_all, res) 
    else: 
        res = read_json(json_path_all) 
    print(' ---- len(res): ', len(res))


    # ==== select acc
    #if 1:
    if not os.path.exists(json_path_select):
        actions, actions_info = select_acc_and_split_action(res)
        write_json(json_path_select, actions) 
        write_json(json_path_select_info, actions_info) 
    else: 
        actions = read_json(json_path_select) 
        actions_info = read_json(json_path_select_info) 
    print(' ---- len(actions), len(actions_info): ', len(actions), len(actions_info))


    # ==== gen_train_dataset
    out, out_info = gen_umafall_train_dataset(actions)
    write_json(json_path_out, out) 
    write_json(json_path_out_info, out_info) 
    print(' ---- len(out), len(out_info): ', len(out), len(out_info))


    
if __name__ == '__main__':
    process_umafall_dataset()



