import re

def process_gcode(input_path, output_path):
    """处理G-code文件，复制第一条G0指令到;TYPE:行后"""
    # 初始化变量
    last_x = 0.0
    last_y = 0.0
    last_z = 0.0
    result = []
    first_g1_found = False  # 用于标记是否已经找到第一条G0指令
    g1_first_line = None  # 用于存储第一条G0指令
    first_printhead = None  # 用于存储第一个打印头类型
    inserted_g1 = False  # 用于标记是否已插入G0指令到;TYPE:后面

    try:
        with open(input_path, 'r') as infile:
            for line in infile:
                line = line.strip()

                # 保留T0和T1指令
                if line == "T0" or line == "T1":
                    if first_printhead is None:
                        first_printhead = line  # 保存第一个打印头类型
                    result.append(line + "\n")
                    continue

                # 检测;TYPE:行，并在后面插入第一条G0指令（如果已找到）
                if ";TYPE:" in line and not inserted_g1:
                    result.append(line + "\n")
                    if g1_first_line:  # 插入第一条G0指令
                        result.append(g1_first_line)
                        inserted_g1 = True  # 标记已经插入
                    continue

                # 匹配G0或G1指令
                match = re.match(
                    r'(G0|G1)\s*(F\d+)?\s*(X[-+]?[0-9]*\.?[0-9]+)?\s*(Y[-+]?[0-9]*\.?[0-9]+)?\s*(Z[-+]?[0-9]*\.?[0-9]+)?\s*(E[-+]?[0-9]*\.?[0-9]+)?',
                    line)
                if match:
                    g_code = match.group(1)
                    x_value = match.group(3)
                    y_value = match.group(4)
                    z_value = match.group(5)

                    # 更新X, Y, Z坐标
                    if x_value:
                        last_x = round(float(x_value[1:]), 2)
                    if y_value:
                        last_y = round(float(y_value[1:]), 2)
                    if z_value:
                        last_z = round(float(z_value[1:]), 2)

                    # 复制第一条G0指令并跳过
                    if not first_g1_found and g_code == "G0":
                        g1_first_line = f"{g_code} X{last_x} Y{last_y} Z{last_z}\n"
                        first_g1_found = True
                        continue  # 跳过当前G0指令

                    # 保留G0指令
                    if g_code == "G0":
                        output_line = f"{g_code} X{last_x} Y{last_y} Z{last_z}\n"
                        result.append(output_line)
                        continue

                # 保留其他内容
                result.append(line + "\n")

        # 写入结果到输出文件
        with open(output_path, 'w') as outfile:
            for line in result:
                outfile.write(line)
        print("G-code 处理完成！")

    except Exception as e:
        raise Exception(f"处理 G-code 文件时出错: {e}")

# 命令行接口
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("用法: python GCodeProcessor.py <输入文件> <输出文件>")
    else:
        process_gcode(sys.argv[1], sys.argv[2])