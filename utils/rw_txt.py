
# -*- coding: utf-8 -*-

# ============================================= READ TXT ==============================================================
def read_txt(path_file, spt=None):
    # ==== get_lines
    def read_lines(path_file, fg_first=False):
        with open(path_file, 'r', encoding='utf-8') as fr:
            lines = fr.readlines()

        res = []
        for i, line in enumerate(lines):
            line = line.strip('\n').strip('\r')
            res.append(line)
        return res

    # ==== mult_list
    lines = read_lines(path_file)
    if spt is None :
        return lines
    else:
        out = []
        min_nSpt = len(lines[0].split(spt))
        max_nSpt = min_nSpt
        for i, line in enumerate(lines):
            line_spt = line.split(spt)
            min_nSpt, max_nSpt = min(min_nSpt, len(line_spt)), max(max_nSpt, len(line_spt))
            out.append(line_spt)
        print('#### read_txt, len(out): ', len(out))
        print('## len(out[0]), min_nSpt, max_nSpt: ', len(out[0]), min_nSpt, max_nSpt)
        if min_nSpt != max_nSpt: print('############  WARNING  ############ min_Spt != maxSpt,   read_txt, path_file:', path_file)
        return out

# ============================================= WRITE TXT ==============================================================
def write_txt(path_file, input_data, spt=None, mode='w'):
    def write_lines(path_file, lines, mode='w'):
        with open(path_file, mode=mode, encoding='utf-8') as fw:
            for line in lines:
                fw.write(line + '\n')

    if spt is None:
        lines = input_data
    else:
        lines = [spt.join(d) for d in input_data]
    write_lines(path_file, lines, mode=mode)



