import tkinter as tk
from tkinter import filedialog, scrolledtext
import math


def parse_gcode(content):
    # 分块解析G-code，每个块代表一条路径
    blocks = content.strip().split("\n\n")
    all_data = []
    for block in blocks:
        commands = block.split('\n')
        positions = []
        for command in commands:
            if command.startswith("G1"):
                parts = command.split()
                x = float(parts[1][1:])
                y = float(parts[2][1:])
                z = float(parts[3][1:])
                j = float(parts[4][1:])
                positions.append((x, y, z, j))
        all_data.append((commands, positions))
    return all_data


def calculate_length(positions):
    # 计算路径总长度
    total_length = 0
    for i in range(1, len(positions)):
        x1, y1, z1, _ = positions[i - 1]
        x2, y2, z2, _ = positions[i]
        total_length += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
    return total_length


def insert_point(all_data, d):
    # 插入新点及切断命令
    results = []
    for commands, positions in all_data:
        L = calculate_length(positions)
        C = L - d
        cumulative_distance = 0
        new_j_value = None

        for i in range(1, len(positions)):
            x1, y1, z1, j1 = positions[i - 1]
            x2, y2, z2, j2 = positions[i]
            dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
            cumulative_distance += dist

            if cumulative_distance >= C and new_j_value is None:
                # 计算插入点
                ratio = (dist - (cumulative_distance - C)) / dist
                x_new = x1 + ratio * (x2 - x1)
                y_new = y1 + ratio * (y2 - y1)
                z_new = z1 + ratio * (z2 - z1)

                # 使用比例计算新的J值
                new_j_value = j1 + ratio * (j2 - j1)

                # 创建新命令并插入
                f = commands[i].split()[-1]
                new_command = f"G1 X{x_new:.2f} Y{y_new:.2f} Z{z_new:.2f} J{new_j_value:.2f} {f}"
                commands.insert(i, new_command)

                # 插入额外的切断命令
                additional_commands = ["M400", "M280 P1.0000 S2", "M280 P1.0000 S95", "M400", "; fiber_basic cut 0"]
                for cmd in reversed(additional_commands):
                    commands.insert(i + 1, cmd)

                # 保持新计算的J值直到文本块的末尾
                for j in range(i + len(additional_commands) + 1, len(commands)):
                    parts = commands[j].split()
                    if parts[0] == "G1":
                        x, y, z = parts[1][1:], parts[2][1:], parts[3][1:]
                        f = parts[-1] if len(parts) > 5 else ""
                        commands[j] = f"G1 X{x} Y{y} Z{z} J{new_j_value:.2f} {f}"

                break  # 插入点找到后退出循环

        # 修改前2条数据的F值为100
        for i in range(min(2, len(commands))):
            parts = commands[i].split()
            if parts[0] == "G1":
                x, y, z, j = parts[1][1:], parts[2][1:], parts[3][1:], parts[4][1:]
                commands[i] = f"G1 X{x} Y{y} Z{z} J{j} F100"

        results.append("\n".join(commands))
    return "\n\n".join(results)


def insert_connection_points(content, d):
    # 在每两个文本块之间插入连接数据
    blocks = content.strip().split("\n\n")
    updated_blocks = [blocks[0]]  # 初始化为第一个块

    for i in range(1, len(blocks)):
        # 获取上一块的最后一条命令和下一块的第一条命令
        prev_commands = blocks[i - 1].strip().split("\n")
        next_commands = blocks[i].strip().split("\n")
        last_command = prev_commands[-1]
        first_command = next_commands[0]

        # 修改上一块的最后一条数据
        last_command_parts = last_command.split()
        if last_command_parts[0] == "G1":
            z = float(last_command_parts[3][1:]) + 5
            j = float(last_command_parts[4][1:]) + d + 3
            f = "F1000"
            last_command = f"{last_command_parts[0]} {last_command_parts[1]} {last_command_parts[2]} Z{z:.2f} J{j:.2f} {f}"

        # 修改下一块的第一条数据
        first_command_parts = first_command.split()
        if first_command_parts[0] == "G1":
            x = float(first_command_parts[1][1:]) - 5
            y = float(first_command_parts[2][1:]) - 5
            z = float(first_command_parts[3][1:]) + 5
            f = "F1000"
            first_command = f"G1 X{x:.2f} Y{y:.2f} Z{z:.2f} J0.00 {f}"

        # 插入连接命令和 G92 J0
        updated_blocks.append(last_command)
        updated_blocks.append("G92 J0")
        updated_blocks.append(first_command)
        updated_blocks.append(blocks[i])

    return "\n\n".join(updated_blocks)


def main_app():
    app = tk.Tk()
    app.title("G-code Processor")
    file_entry = tk.Entry(app, width=50)
    file_entry.pack()
    d_entry = tk.Entry(app, width=20)
    d_entry.pack()
    output_text = scrolledtext.ScrolledText(app, width=80, height=20)
    output_text.pack()

    def load_file():
        file_path = filedialog.askopenfilename()
        if file_path:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)

    def process_file():
        file_path = file_entry.get()
        d_value = float(d_entry.get())
        output_text.delete('1.0', tk.END)
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            all_data = parse_gcode(content)
            updated_gcode = insert_point(all_data, d_value)
            final_gcode = insert_connection_points(updated_gcode, d_value)
            final_gcode = final_gcode.replace("\n\nG92 J0\n\n", "\nG92 J0\n")
            output_text.insert(tk.END, final_gcode)
        except Exception as e:
            output_text.insert(tk.END, str(e))

    def save_file():
        result = output_text.get("1.0", tk.END)
        if result:
            save_path = filedialog.asksaveasfilename(defaultextension=".txt")
            if save_path:
                with open(save_path, 'w') as file:
                    file.write(result)

    tk.Button(app, text="浏览", command=load_file).pack()
    tk.Button(app, text="处理", command=process_file).pack()
    tk.Button(app, text="保存为TXT", command=save_file).pack()

    app.mainloop()


if __name__ == "__main__":
    main_app()