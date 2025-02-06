import argparse
import re


# 处理G-code文件，默认处理所有打印头（T0 和 T1）
def process_gcode(input_file, output_file):
    # 默认打印头类型为 Both（即 T0 和 T1 均处理）
    printhead_type = 'Both'

    # 初始化变量
    current_printhead = None
    last_x = 0.0
    last_y = 0.0
    last_z = 0.0
    result = []
    skip_next_lines = 0  # 用于跳过下一行数据
    prev_line = None  # 用于存储上一次的行
    prev_g0_line = None  # 用于存储上一次的G0行

    with open(input_file, 'r') as infile:
        for line in infile:
            line = line.strip()

            # 如果要跳过这一行，直接跳过
            if skip_next_lines > 0:
                skip_next_lines -= 1
                continue

            # 保留所有含有 ;TYPE: 或 ;LAYER: 的行
            if ";TYPE:" in line or ";LAYER:" in line:
                # 检测是否为 WALL-OUTER 类型且存在上一条G0行
                if ";TYPE:WALL-OUTER" in line and prev_g0_line:
                    # 将 WALL-OUTER 行放前面，G0 行放后面
                    result.append(line + "\n")
                    result.append(prev_g0_line)
                    prev_g0_line = None  # 重置上一条G0行
                    continue
                else:
                    result.append(line + "\n")
                    continue

            # 严格检查 T0 和 T1 打印头
            if line == "T0" and (printhead_type == 'T0' or printhead_type == 'Both'):
                current_printhead = "T0"
                result.append("T0\n")  # 单独添加 T0 行
                continue
            elif line == "T1" and (printhead_type == 'T1' or printhead_type == 'Both'):
                current_printhead = "T1"
                result.append("T1\n")  # 单独添加 T1 行
                continue

            # 检测 G0 或 G1 指令
            match = re.match(
                r'(G0|G1)\s*(F\d+)?\s*(X[-+]?[0-9]*\.?[0-9]+)?\s*(Y[-+]?[0-9]*\.?[0-9]+)?\s*(Z[-+]?[0-9]*\.?[0-9]+)?\s*(E[-+]?[0-9]*\.?[0-9]+)?',
                line)
            if match:
                g_code = match.group(1)
                x_value = match.group(3)
                y_value = match.group(4)
                z_value = match.group(5)

                # 更新 X, Y, Z 值
                if x_value:
                    last_x = round(float(x_value[1:]), 2)
                if y_value:
                    last_y = round(float(y_value[1:]), 2)
                if z_value:
                    last_z = round(float(z_value[1:]), 2)

                # 将 G0 指令存储到 prev_g0_line 中，用于后续交换
                if g_code == "G0":
                    prev_g0_line = f"{g_code} X{last_x} Y{last_y} Z{last_z}\n"
                    continue  # 跳过当前 G0 行，等待后续交换

                # 处理 G1 指令，并保存到结果
                if current_printhead in ["T0", "T1"]:
                    output_line = f"{g_code} X{last_x} Y{last_y} Z{last_z}\n"
                    result.append(output_line)

    # 写入结果到输出文件
    with open(output_file, 'w') as outfile:
        for line in result:
            outfile.write(line)


def main():
    # 使用 argparse 解析命令行参数（只包含输入和输出文件路径）
    parser = argparse.ArgumentParser(description="处理G-code文件并修改T0/T1（仅需指定输入和输出文件）")
    parser.add_argument('input_file', type=str, help="输入G-code文件路径")
    parser.add_argument('output_file', type=str, help="输出文件路径")

    args = parser.parse_args()

    # 调用处理函数
    process_gcode(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
