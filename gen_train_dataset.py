import os
import copy
import numpy as np
from scipy.signal import resample_poly

def resample_sequence(sequence, old_rate, new_rate):
    if old_rate == new_rate: return sequence

    # 将新旧采样率都乘以一个足够大的数，使得它们变为整数
    old_rate *= 10
    new_rate *= 10
    
    # 计算新旧采样率的最大公约数
    gcd = np.gcd(int(old_rate), int(new_rate))
    
    # 计算重采样的比例因子
    up = int(new_rate) // gcd
    down = int(old_rate) // gcd
    
    # 使用 resample_poly 函数进行重采样
    #print(' ---- sequence, up, down: ', sequence, up, down)
    new_sequence = resample_poly(sequence, up, down)
    
    return new_sequence


def resample(action):
    action_cp = copy.deepcopy(action)
    action_cp['X_Axis'] = resample_sequence(action['X_Axis'], old_rate=action['sample_rate'], new_rate=18.4)
    action_cp['Y_Axis'] = resample_sequence(action['Y_Axis'], old_rate=action['sample_rate'], new_rate=18.4)
    action_cp['Z_Axis'] = resample_sequence(action['Z_Axis'], old_rate=action['sample_rate'], new_rate=18.4)
    return action_cp 


def norm_xyz(action):
    xyzs = []
    for x, y, z in zip(action['X_Axis'], action['Y_Axis'], action['Z_Axis']):
        xyz = np.sqrt(x**2 + y**2 + z**2)  
        xyzs.append(xyz) 
    xyzs = np.array(xyzs)
    idx_max = np.argmax(xyzs)
    return idx_max


def windows(action, idx_max):
    win_st = idx_max - 37
    win_ed = idx_max + 28 +1
    n = len(action['X_Axis'])

    if win_st < 0:
        #print(' ---- win_st < 0. idx_max,  win_st, win_ed: ', idx_max, win_st, win_ed) 
        win_st = 0
        win_ed = 66
    elif win_ed > n-1:
        #print(' ---- win_ed > n-1. idx_max, n, win_st, win_ed: ', idx_max, n,  win_st, win_ed) 
        win_st = n-66
        win_ed = n

    if win_ed - win_st != 66:
        print(' ---- win_ed - win_st != 66.  win_ed, win_st: ', win_ed, win_st)

    action_cp = copy.deepcopy(action)
    action_cp['X_Axis'] = action['X_Axis'][win_st:win_ed]
    action_cp['Y_Axis'] = action['Y_Axis'][win_st:win_ed]
    action_cp['Z_Axis'] = action['Z_Axis'][win_st:win_ed]
    return action_cp


def normal(action, s_max, s_min):
    def normal_one_data(sequence, s_max, s_min):
        sequence_new = []
        for s in sequence: 
            s_new = (s-s_min)/(s_max-s_min)
            sequence_new.append(s_new)
        return sequence_new

    action_cp = copy.deepcopy(action)

   
    action_cp['X_Axis'] = normal_one_data(action['X_Axis'], s_max, s_min)
    action_cp['Y_Axis'] = normal_one_data(action['Y_Axis'], s_max, s_min)
    action_cp['Z_Axis'] = normal_one_data(action['Z_Axis'], s_max, s_min)
    return action_cp 


def process_one_action(action, s_max, s_min):
    res_sample = resample(action)
    idx_max = norm_xyz(res_sample)
    res_windows = windows(res_sample, idx_max)
    res = normal(res_windows, s_max, s_min)
    return res



