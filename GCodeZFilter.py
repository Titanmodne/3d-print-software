import re

def process_gcode(input_path, output_path):
    """处理G-code文件，删除Z值不符合条件的G0/G1指令"""
    try:
        with open(input_path, 'r') as infile:
            lines = infile.readlines()

        result_lines = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 处理G0/G1指令的块
            if line.startswith(('G0', 'G1')):
                # 获取当前行和下一行的Z值进行比较
                if i + 1 < len(lines):  # 确保有第二行
                    match1 = re.search(r'Z([+-]?[0-9]*\.?[0-9]+)', lines[i])
                    match2 = re.search(r'Z([+-]?[0-9]*\.?[0-9]+)', lines[i + 1])

                    if match1 and match2:
                        z1 = float(match1.group(1))
                        z2 = float(match2.group(1))

                        # 如果当前行的 Z 值大于下一行的 Z 值，则删除当前行
                        if z1 > z2:
                            i += 1  # 跳过当前行
                            continue  # 跳过当前行并处理下一行

                # 将有效行加入结果
                result_lines.append(line)

                # 检查是否下一行不是G0/G1指令，如果是，则添加一个空行
                if i + 1 < len(lines) and not lines[i + 1].strip().startswith(('G0', 'G1')):
                    result_lines.append("")  # 添加空行

            else:
                result_lines.append(line)

            i += 1

        # 写入处理后的文本到输出文件
        with open(output_path, 'w') as outfile:
            outfile.write('\n'.join(result_lines))
        print("G-code 处理完成！")

    except Exception as e:
        raise Exception(f"处理 G-code 文件时出错: {e}")

# 命令行接口
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("用法: python GCodeZFilter.py <输入文件> <输出文件>")
    else:
        process_gcode(sys.argv[1], sys.argv[2])