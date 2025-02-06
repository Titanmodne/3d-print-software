import sys
import math
import tkinter as tk
from tkinter import filedialog

def parse_gcode(content):
    blocks = content.strip().split("\n\n")
    all_data = []
    for block in blocks:
        commands = block.strip().split('\n')
        positions = []
        for command in commands:
            if command.startswith("G1"):
                parts = command.split()
                x = float(parts[1][1:])
                y = float(parts[2][1:])
                z = float(parts[3][1:])
                f = float(parts[-1][1:])
                j = None
                if len(parts) > 4 and parts[4][0] == 'J':
                    j = float(parts[4][1:])
                positions.append((x, y, z, j, f))
        all_data.append((commands, positions))
    return all_data

def calculate_length(positions):
    total_length = 0
    for i in range(1, len(positions)):
        x1, y1, z1, _, _ = positions[i - 1]
        x2, y2, z2, _, _ = positions[i]
        total_length += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
    return total_length

def insert_cut_points(all_data, d, insert_f, j_offset):
    results = []
    for commands, positions in all_data:
        L = calculate_length(positions)
        C = L - d  # 计算剪断点的距离
        cumulative_distance = 0
        new_j_value = None

        for i in range(1, len(positions)):
            x1, y1, z1, j1, f1 = positions[i - 1]
            x2, y2, z2, j2, f2 = positions[i]
            dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

            # 跳过零距离段
            if dist == 0:
                continue

            cumulative_distance += dist

            # 只在 J 类型的挤出时进行剪断
            if j1 is not None and cumulative_distance >= C and new_j_value is None:
                ratio = (dist - (cumulative_distance - C)) / dist
                x_new = x1 + ratio * (x2 - x1)
                y_new = y1 + ratio * (y2 - y1)
                z_new = z1 + ratio * (z2 - z1)
                new_j_value = j1 + ratio * (j2 - j1)

                # 插入新的 G1 指令，修改 F 和 J 值
                new_command = f"G1 X{x_new:.2f} Y{y_new:.2f} Z{z_new:.2f} J{new_j_value + j_offset:.2f} F{insert_f}"
                commands.insert(i, new_command)

                # 添加剪断后的相关 G-code 指令
                additional_commands = ["M400", "M280 P1.0000 S2", "M280 P1.0000 S95", "M400", "; fiber_basic cut 0"]
                for cmd in reversed(additional_commands):
                    commands.insert(i + 1, cmd)

                # 更新后续的 G1 指令
                for j in range(i + len(additional_commands) + 1, len(commands)):
                    parts = commands[j].split()
                    if parts[0] == "G1":
                        x, y, z = parts[1][1:], parts[2][1:], parts[3][1:]
                        commands[j] = f"G1 X{x} Y{y} Z{z} J{new_j_value + j_offset:.2f} F{f1}"

                break

        # 更新 F 参数
        for i in range(min(2, len(commands))):
            parts = commands[i].split()
            if parts[0] == "G1":
                x, y, z, j, f = parts[1][1:], parts[2][1:], parts[3][1:], parts[4][1:], parts[-1][1:]
                commands[i] = f"G1 X{x} Y{y} Z{z} J{j} F{insert_f}"

        results.append("\n".join(commands))
    return "\n\n".join(results)

def process_gcode_file(input_file, output_file, distance, insert_f, connection_f, j_offset):
    with open(input_file, 'r') as file:
        content = file.read()

    all_data = parse_gcode(content)
    updated_gcode = insert_cut_points(all_data, distance, insert_f, j_offset)

    with open(output_file, 'w') as file:
        file.write(updated_gcode)

def browse_file(entry):
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    entry.delete(0, tk.END)
    entry.insert(0, file_path)

def save_file(entry):
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    entry.delete(0, tk.END)
    entry.insert(0, file_path)

def run():
    input_file = input_entry.get()
    output_file = output_entry.get()
    distance = float(distance_entry.get())
    insert_f = float(insert_f_entry.get())
    connection_f = float(connection_f_entry.get())
    j_offset = float(j_offset_entry.get())

    process_gcode_file(input_file, output_file, distance, insert_f, connection_f, j_offset)

# 创建界面
root = tk.Tk()
root.title("G-code Cutter")

tk.Label(root, text="输入文件:").grid(row=0, column=0)
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1)
input_button = tk.Button(root, text="浏览", command=lambda: browse_file(input_entry))
input_button.grid(row=0, column=2)

tk.Label(root, text="输出文件:").grid(row=1, column=0)
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1)
output_button = tk.Button(root, text="保存", command=lambda: save_file(output_entry))
output_button.grid(row=1, column=2)

tk.Label(root, text="剪断距离 (mm):").grid(row=2, column=0)
distance_entry = tk.Entry(root)
distance_entry.grid(row=2, column=1)

tk.Label(root, text="插入F值:").grid(row=3, column=0)
insert_f_entry = tk.Entry(root)
insert_f_entry.grid(row=3, column=1)

tk.Label(root, text="连接F值:").grid(row=4, column=0)
connection_f_entry = tk.Entry(root)
connection_f_entry.grid(row=4, column=1)

tk.Label(root, text="J偏移值:").grid(row=5, column=0)
j_offset_entry = tk.Entry(root)
j_offset_entry.grid(row=5, column=1)

run_button = tk.Button(root, text="运行", command=run)
run_button.grid(row=6, column=1)

root.mainloop()
