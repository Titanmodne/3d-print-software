import re
import sys

def process_gcode(input_path, output_path):
    """处理G-code文件并写入输出文件"""
    # 初始化变量
    current_printhead = None
    last_x = 0.0
    last_y = 0.0
    last_z = 0.0
    result = []
    skip_next_lines = 0  # 用于跳过下一行数据
    first_g1_line = True  # 用于标记是否是第一条G1指令
    skip_first_g1 = False  # 用于跳过第一条G1指令的标志

    try:
        with open(input_path, 'r') as infile:
            for line in infile:
                line = line.strip()

                # 检查是否为G91指令，如果是，停止提取
                if line.startswith("G91"):
                    break

                # 如果要跳过这一行，直接跳过
                if skip_next_lines > 0:
                    skip_next_lines -= 1
                    continue

                # 保留所有含有;TYPE:或;LAYER:的行
                if ";TYPE:" in line or ";LAYER:" in line:
                    if skip_first_g1:  # 如果已经跳过第一条G1，则将下一条G1指令合并到;TYPE:后
                        skip_first_g1 = False
                        result.append(line + "\n")
                        continue
                    else:
                        result.append(line + "\n")
                        continue

                # 严格检查T0和T1打印头
                if line == "T0":
                    current_printhead = "T0"
                    result.append("T0\n")
                    continue
                elif line == "T1":
                    current_printhead = "T1"
                    result.append("T1\n")
                    continue

                # 检测G0或G1指令
                match = re.match(
                    r'(G0|G1)\s*(F\d+)?\s*(X[-+]?[0-9]*\.?[0-9]+)?\s*(Y[-+]?[0-9]*\.?[0-9]+)?\s*(Z[-+]?[0-9]*\.?[0-9]+)?\s*(E[-+]?[0-9]*\.?[0-9]+)?',
                    line)
                if match:
                    g_code = match.group(1)
                    x_value = match.group(3)
                    y_value = match.group(4)
                    z_value = match.group(5)

                    # 更新X, Y, Z值
                    if x_value:
                        last_x = round(float(x_value[1:]), 2)
                    if y_value:
                        last_y = round(float(y_value[1:]), 2)
                    if z_value:
                        last_z = round(float(z_value[1:]), 2)

                    # 如果是第一条G1指令，跳过它
                    if first_g1_line:
                        first_g1_line = False
                        skip_first_g1 = True
                        continue

                    # 保留G0指令
                    if g_code == "G0":
                        output_line = f"{g_code} X{last_x} Y{last_y} Z{last_z}\n"
                        result.append(output_line)
                        continue

                    # 处理G1指令
                    if current_printhead in ["T0", "T1"]:
                        output_line = f"{g_code} X{last_x} Y{last_y} Z{last_z}\n"
                        result.append(output_line)

        # 写入结果到文件
        with open(output_path, 'w') as outfile:
            for line in result:
                outfile.write(line)
        print("G-code 处理完成！")

    except Exception as e:
        raise Exception(f"处理 G-code 文件时出错: {e}")

# 命令行接口
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python GCodeProcessor.py <输入文件> <输出文件>")
    else:
        process_gcode(sys.argv[1], sys.argv[2])