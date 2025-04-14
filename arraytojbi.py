import numpy as np
import os

def process_array_to_jbi(input_file, output_folder, user=2, tool=0):
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

    # 定义JBI文件的格式字符串，包含 user 和 tool 占位符
    Jformat = '/JOB\n//NAME {name}\n//POS\n///NPOS {npos1},0,{npos2},0,0,0\n///USER {user}\n///TOOL {tool}\n///POSTYPE USER\n///RECTAN\n///RCONF 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0\n'
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
            # 使用动态的 user 和 tool 参数格式化 Jformat
            fid.write(Jformat.format(name=i + 1, npos1=filen, npos2=2 * filen, user=user, tool=tool))
            for j in range(filen * i, filen * (i + 1)):
                cR = (j % filen)
                fid.write(Cformat.format(cR, F[j, 0], F[j, 1], F[j, 2]))

            fid.write('///POSTYPE PULSE\n///PULSE\n')
            for j in range(filen * i, filen * (i + 1)):
                eR1 = 2 * (j % filen)
                eR2 = eR1 + 1
                fid.write(Eformat.format(eR1, int(F[j, 3]), eR2, int(F[j, 4])))

            # 在 INST 部分也使用动态 user 参数
            fid.write(f'//INST\n///DATE 2019/10/30 19:46\n///ATTR SC,RW,RJ\n////FRAME USER {user}\n///GROUP1 RB1\n///GROUP2 ST2\n///GROUP3 ST3\nNOP\n')
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
            # 使用动态的 user 和 tool 参数格式化 Jformat
            fid.write(Jformat.format(name=num_files + 1, npos1=lm, npos2=2 * lm, user=user, tool=tool))
            for i in range(num_files * filen, num_files * filen + lm):
                cR = (i % filen)
                fid.write(Cformat.format(cR, F[i, 0], F[i, 1], F[i, 2]))
            fid.write('///POSTYPE PULSE\n///PULSE\n')
            for j in range(filen * num_files, filen * num_files + lm):
                eR1 = 2 * (j % filen)
                eR2 = eR1 + 1
                fid.write(Eformat.format(eR1, int(F[j, 3]), eR2, int(F[j, 4])))
            # 在 INST 部分也使用动态 user 参数
            fid.write(f'//INST\n///DATE 2019/10/30 19:46\n///ATTR SC,RW,RJ\n////FRAME USER {user}\n///GROUP1 RB1\n///GROUP2 ST2\n///GROUP3 ST3\nNOP\n')
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