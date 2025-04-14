import re

def convert_gcode_format(input_file_path, output_file_path):
    """转换 G-code 文件的格式从旧格式到新格式"""
    try:
        with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
            for line in infile:
                # 匹配并解析原始格式中的数据
                match = re.search(r'G[01] X: ([\d\.-]+), Y: ([\d\.-]+), Z: ([\d\.-]+) J: ([\d\.-]+) F: (\d+)', line)
                if match:
                    x, y, z, j, f = match.groups()
                    # 转换为新的格式并写入文件
                    new_line = f'G1 X{x} Y{y} Z{z} J{j} F{f}\n'
                    outfile.write(new_line)
                else:
                    # 如果不匹配，原样写入
                    outfile.write(line)
        print(f"文件已转换并保存到 {output_file_path}")
    except Exception as e:
        print(f"处理文件时出错: {e}")

# 这个模块现在可以被其他Python脚本作为库调用
