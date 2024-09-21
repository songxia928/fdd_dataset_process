
import numpy as np

import json

def read_json(path_file):
    with open(path_file, 'rb') as fr:
        out = json.load(fr)
    print('#### read_json, len(out): ', len(out))
    return out


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif type(obj) is np.float32:
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, set):
            return list(obj)
        else:
            return super(NpEncoder, self).default(obj)


    
def write_json(path_file, input_data, indent=4):
    json_str = json.dumps(input_data, indent=indent, ensure_ascii=False, cls=NpEncoder)
    #json_str = json.dumps(input_data, indent=indent, ensure_ascii=False)
    json_utf8 = json_str.encode('utf8')
    with open(path_file, 'wb') as fw:
        fw.write(json_utf8)




if __name__ == '__main__':
    dic = {'22': 22, 'a': 'xyz'}

    path_file = './tp.json'
    write_json(path_file, dic)

    json_path = 'C:/Users/admin/Downloads/zh.val.json'
    dic = read_json(json_path)
    
    file_path = json_path.replace('.json', '_2.json')
    write_json(file_path, dic)



