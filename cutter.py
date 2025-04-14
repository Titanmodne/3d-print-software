import re
import math
import argparse

def parse_gcode(content):
    """
    解析 G-code，将每个块内的所有行按顺序存入 commands，
    同时提取所有以 G0 和 G1 开头的命令，并记录其在 commands 列表中的行号。
    每个命令保存格式：(行号, command_type, x, y, z, j, f)
    其中 command_type 为 'G0' 或 'G1'
    """
    blocks = content.strip().split("\n\n")
    all_data = []
    for block in blocks:
        commands = block.strip().split('\n')
        positions = []
        for idx, command in enumerate(commands):
            if command.startswith("G0") or command.startswith("G1"):
                command_type = command.split()[0]
                parts = command.split()
                try:
                    # 提取 X, Y, Z
                    x = next(float(p[1:]) for p in parts if p.startswith("X"))
                    y = next(float(p[1:]) for p in parts if p.startswith("Y"))
                    z = next(float(p[1:]) for p in parts if p.startswith("Z"))
                except StopIteration:
                    continue  # 缺少 X, Y, Z 时跳过
                # 提取 J 和 F
                j = next((float(p[1:]) for p in parts if p.startswith("J")), None)
                f = next((float(p[1:]) for p in parts if p.startswith("F")), None)
                positions.append((idx, command_type, x, y, z, j, f))
        all_data.append((commands, positions))
    return all_data

def calculate_length(positions):
    """
    计算由 positions 中 G1 命令构成的路径总长度
    """
    total_length = 0
    g1_positions = [p for p in positions if p[1] == 'G1']
    if len(g1_positions) < 2:
        return 0
    for i in range(1, len(g1_positions)):
        _, _, x1, y1, z1, _, _ = g1_positions[i - 1]
        _, _, x2, y2, z2, _, _ = g1_positions[i]
        total_length += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
    return total_length

def insert_cut_points(all_data, d, insert_f, connection_f, j_offset):
    """
    对于每个文本块：
      - 如果该块的前三行中包含 "T1"，则认为该块需要剪断，
        否则原样输出该块。
      - 对需要剪断的块：
          1. 计算 G1 命令的路径总长度 L，设剪切点累计长度 C = L - d
          2. 遍历 G1 命令，累计距离，当累计距离首次超过 C 时，
             在该段内线性插值得到剪切点坐标及 J 值，并记录插入位置。
          3. 在该位置插入新的剪切指令（使用 insert_f 进给和 j_offset 调整后的 J 值），
             紧跟插入附加指令，然后更新剪切点后所有 G0 和 G1 命令的 J 和 F 值。
    """
    results = []
    for commands, positions in all_data:
        # 仅检查文本块的前三行是否含有 "T1"
        found_T1 = any("T1" in line for line in commands[:3])

        if not found_T1:
            results.append("\n".join(commands))
            continue

        if len(positions) < 2:
            results.append("\n".join(commands))
            continue

        # 只考虑 G1 命令计算路径长度
        g1_positions = [p for p in positions if p[1] == 'G1']
        L = calculate_length(g1_positions)
        C = L - d
        cumulative_distance = 0
        new_j_value = None
        insertion_index = None
        additional_commands = [
            "M400",
            "M280 P1.0000 S95",
            "M280 P1.0000 S2",
            "M400",
            "; fiber_basic cut 0"
        ]

        # 遍历 G1 命令，计算累计距离
        for i in range(1, len(g1_positions)):
            idx_prev, _, x1, y1, z1, j1, f1 = g1_positions[i - 1]
            idx_curr, _, x2, y2, z2, j2, f2 = g1_positions[i]
            seg = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
            if seg == 0:
                continue
            if cumulative_distance + seg >= C:
                ratio = (C - cumulative_distance) / seg
                x_new = x1 + ratio * (x2 - x1)
                y_new = y1 + ratio * (y2 - y1)
                z_new = z1 + ratio * (z2 - z1)
                if j1 is not None and j2 is not None:
                    new_j_value = j1 + ratio * (j2 - j1)
                else:
                    new_j_value = 0
                # 插入位置为当前 G1 命令的行号
                insertion_index = idx_curr
                new_command = f"G1 X{x_new:.2f} Y{y_new:.2f} Z{z_new:.2f} J{new_j_value + j_offset:.2f} F{insert_f}"
                commands.insert(insertion_index, new_command)
                for cmd in reversed(additional_commands):
                    commands.insert(insertion_index + 1, cmd)
                break
            cumulative_distance += seg

        # 更新剪切点之后所有 G0 和 G1 命令的 J 和 F 值
        if new_j_value is not None and insertion_index is not None:
            # 找到插入点之后的命令行
            start_index = insertion_index + len(additional_commands) + 1
            for idx in range(start_index, len(commands)):
                if commands[idx].startswith("G0") or commands[idx].startswith("G1"):
                    parts = commands[idx].split()
                    command_type = parts[0]
                    # 保留 X, Y, Z 参数不变
                    x_val = next((p for p in parts if p.startswith("X")), None)
                    y_val = next((p for p in parts if p.startswith("Y")), None)
                    z_val = next((p for p in parts if p.startswith("Z")), None)
                    # 更新 J 和 F 值
                    if x_val and y_val and z_val:
                        commands[idx] = f"{command_type} {x_val} {y_val} {z_val} J{new_j_value + j_offset:.2f} F{connection_f}"
                    else:
                        # 如果缺少 X, Y, Z，则不进行修改
                        continue

        results.append("\n".join(commands))
    return "\n\n".join(results)

def process_gcode_file(input_file, output_file, distance, insert_f, connection_f, j_offset):
    """处理 G-code 文件的核心函数"""
    with open(input_file, 'r') as file:
        content = file.read()

    all_data = parse_gcode(content)
    updated_gcode = insert_cut_points(all_data, distance, insert_f, connection_f, j_offset)

    with open(output_file, 'w') as file:
        file.write(updated_gcode)

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="处理 G-code 文件以插入剪切点并调整参数")
    parser.add_argument('--input', required=True, help='输入 G-code 文件路径')
    parser.add_argument('--output', required=True, help='输出 G-code 文件路径')
    parser.add_argument('--distance', type=float, required=True, help='剪断距离（mm）')
    parser.add_argument('--insert_f', type=float, required=True, help='插入的 G1 命令的进给速度')
    parser.add_argument('--connection_f', type=float, required=True, help='剪切点后 G0 和 G1 命令的进给速度')
    parser.add_argument('--j_offset', type=float, required=True, help='J 参数的偏移值')

    # 解析命令行参数
    args = parser.parse_args()

    try:
        # 调用处理函数
        process_gcode_file(args.input, args.output, args.distance, args.insert_f, args.connection_f, args.j_offset)
        print("处理完成！")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()