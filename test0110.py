import numpy as np
import os
import tkinter as tk
from tkinter import filedialog

def process_array_to_jbi(input_file, output_folder):
    # 读取输入数据
    try:
        F = np.loadtxt(input_file)  # 假设输入文件是TXT格式，每行包含多个值
    except Exception as e:
        print(f"读取输入文件时发生错误: {str(e)}")
        return

    m, n = F.shape  # 获取数据的行数和列数
    if n < 7:
        print("输入数据的列数不足7列，请确保每行包含7个值。")
        return

    # 设置每个JBI文件的最大数据点数量
    filen = 9500
    num_files = m // filen

    # 定义JBI文件的格式字符串
    Jformat = '/JOB\n//NAME {}\n//POS\n///NPOS {},0,{},0,0,0\n///USER 2\n///TOOL 0\n///POSTYPE USER\n///RECTAN\n///RCONF 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0\n'
    Cformat = 'C{:05d}={:.3f},{:.3f},{:.3f},180,0,0\n'
    Eformat = 'EC{:05d}={}\nEC{:05d}={}\n'
    Mformat = 'MOVL C{:05d} V={:.1f} +MOVJ EC{:05d} +MOVJ EC{:05d}\n'

    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 生成JBI文件
    for i in range(num_files):
        filename = os.path.join(output_folder, f'{i + 1}.JBI')
        with open(filename, 'w') as fid:
            fid.write(Jformat.format(i + 1, filen, 2 * filen))
            for j in range(filen * i, filen * (i + 1)):
                cR = (j % filen)
                fid.write(Cformat.format(cR, F[j, 0], F[j, 1], F[j, 2]))

            fid.write('///POSTYPE PULSE\n///PULSE\n')
            for j in range(filen * i, filen * (i + 1)):
                eR1 = 2 * (j % filen)
                eR2 = eR1 + 1
                fid.write(Eformat.format(eR1, int(F[j, 3]), eR2, int(F[j, 4])))

            fid.write('//INST\n///DATE 2019/10/30 19:46\n///ATTR SC,RW,RJ\n////FRAME USER 2\n///GROUP1 RB1\n///GROUP2 ST2\n///GROUP3 ST3\nNOP\n')
            for j in range(filen * i, filen * (i + 1)):
                cR = (j % filen)
                eR1 = 2 * (j % filen)
                eR2 = eR1 + 1
                v = F[j, 5]
                fid.write(Mformat.format(cR, v, eR1, eR2))
                if F[j, 6] == 1:
                    fid.write('HAND HNO: 1 ON\n')
                elif F[j, 6] == 2:
                    fid.write('HAND HNO: 2 ON\nTIMER T=1.00\nHAND HNO: 2 OFF\n')
                elif F[j, 6] == 3:
                    fid.write('HAND HNO: 1 OFF\n')
            fid.write('END\n')

    # 处理剩余的数据点
    lm = m % filen  # 剩余的数据点数
    if lm > 0:
        filename = os.path.join(output_folder, f'{num_files + 1}.JBI')
        with open(filename, 'w') as fid:
            fid.write(Jformat.format(num_files + 1, lm, 2 * lm))
            for i in range(num_files * filen, num_files * filen + lm):
                cR = (i % filen)
                fid.write(Cformat.format(cR, F[i, 0], F[i, 1], F[i, 2]))
            fid.write('///POSTYPE PULSE\n///PULSE\n')
            for j in range(filen * num_files, filen * num_files + lm):
                eR1 = 2 * (j % filen)
                eR2 = eR1 + 1
                fid.write(Eformat.format(eR1, int(F[j, 3]), eR2, int(F[j, 4])))
            fid.write('//INST\n///DATE 2019/10/30 19:46\n///ATTR SC,RW,RJ\n////FRAME USER 2\n///GROUP1 RB1\n///GROUP2 ST2\n///GROUP3 ST3\nNOP\n')
            for j in range(filen * num_files, filen * num_files + lm):
                cR = (j % filen)
                eR1 = 2 * (j % filen)
                eR2 = eR1 + 1
                v = F[j, 5]
                fid.write(Mformat.format(cR, v, eR1, eR2))
                if F[j, 6] == 1:
                    fid.write('HAND HNO: 1 ON\n')
                elif F[j, 6] == 2:
                    fid.write('HAND HNO: 2 ON\nTIMER T=1.00\nHAND HNO: 2 OFF\n')
                elif F[j, 6] == 3:
                    fid.write('HAND HNO: 1 OFF\n')
            fid.write('END\n')

    print('JBI conversion completed successfully for all files.')

def select_input_output():
    # 创建Tkinter窗口
    root = tk.Tk()
    root.withdraw()  # 不显示主窗口

    # 选择输入文件
    input_file = filedialog.askopenfilename(title="选择输入文件", filetypes=[("Text files", "*.txt")])
    if not input_file:
        print("没有选择输入文件。")
        return

    # 获取输入文件的文件夹路径和文件名
    input_folder, input_filename = os.path.split(input_file)
    output_folder = os.path.join(input_folder, os.path.splitext(input_filename)[0])  # 输出文件夹与输入文件同名

    # 调用处理函数
    process_array_to_jbi(input_file, output_folder)
    print(f"所有JBI文件已保存至：{output_folder}")

# 启动文件选择和处理流程
select_input_output()
