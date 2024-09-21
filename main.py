import copy
import os
import random

from utils.rw_json import *


from process_umafall import process_umafall_dataset
from process_upfall import process_upfall_dataset
from process_sisfall import process_sisfall_dataset

def dataset_split_train_and_test(folder_in, folder_out, dataset_name):
    def process_one(json_path, folder_out, dataset_name):
        actions = read_json(json_path)

        location_cnt = {}
        location_g5_filename = {}
        g5_filename = {0:[], 1:[], 2:[], 3:[], 4:[]}
        for i, action in enumerate(actions):
            #print(' ---- json_path, i: ', json_path, i)

            location = action['location']
            if 'pocket' in location:
                location = 'pocket'

            ADL_Fall = action['ADL_Fall']
            action['label'] = 1 if ADL_Fall == 'Fall' else 0
            action.pop('class_name')
           
            if location not in location_cnt: 
                location_cnt[location] = 0
                location_g5_filename[location] = copy.deepcopy(g5_filename)
            else:  
                location_cnt[location] += 1
            

            folder_save = folder_out + '/' + dataset_name + '/' + location
            if not os.path.exists(folder_save): os.makedirs(folder_save)
            file_path = folder_save + '/{:05d}.json'.format(location_cnt[location])
            write_json(file_path, action)

            ii = location_cnt[location]%5
            filename = location + '/{:05d}.json'.format(location_cnt[location])
            location_g5_filename[location][ii].append(filename)

        

        file_path = folder_out + '/' + dataset_name + '_5groups.json'
        write_json(file_path, location_g5_filename)

    if not os.path.exists(folder_out): os.makedirs(folder_out)

    json_path = '{}/{}/dataset_processed/out.json'.format(folder_in, dataset_name)
    process_one(json_path, folder_out, dataset_name)


def process():

    datasets_name = ['sisfall', 'umafall', 'upfall']

    folder_in =  './dataset'
    folder_out = './output'

    # ==== process dataset
    for dataset_name in datasets_name:
        if dataset_name == 'umafall':   process_umafall_dataset(folder_in)     
        if dataset_name == 'upfall':    process_upfall_dataset(folder_in)     
        if dataset_name == 'sisfall':   process_sisfall_dataset(folder_in)     

    # ==== split train and test
    for dataset_name in datasets_name:
        dataset_split_train_and_test(folder_in, folder_out, dataset_name)


if __name__ == '__main__':
    process()






