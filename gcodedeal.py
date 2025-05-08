import tkinter as tk
from tkinter import filedialog, messagebox
import os


class GCodeProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("G-code 文件处理器")
        self.root.geometry("600x300")

        # 输入文件
        self.input_label = tk.Label(root, text="输入 G-code 文件:")
        self.input_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.input_path = tk.StringVar()
        self.input_entry = tk.Entry(root, textvariable=self.input_path, width=50)
        self.input_entry.grid(row=0, column=1, padx=10, pady=5)

        self.input_button = tk.Button(root, text="选择", command=self.select_input_file)
        self.input_button.grid(row=0, column=2, padx=10, pady=5)

        # 输出文件
        self.output_label = tk.Label(root, text="输出 G-code 文件:")
        self.output_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.output_path = tk.StringVar()
        self.output_entry = tk.Entry(root, textvariable=self.output_path, width=50)
        self.output_entry.grid(row=1, column=1, padx=10, pady=5)

        self.output_button = tk.Button(root, text="选择", command=self.select_output_file)
        self.output_button.grid(row=1, column=2, padx=10, pady=5)

        # 处理按钮
        self.process_button = tk.Button(root, text="处理 G-code", command=self.process_gcode)
        self.process_button.grid(row=2, column=1, padx=10, pady=20)

        # 状态标签
        self.status_label = tk.Label(root, text="状态: 等待选择文件", wraplength=500)
        self.status_label.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

    def select_input_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("G-code 文件", "*.gcode"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_path.set(file_path)
            self.status_label.config(text=f"状态: 已选择输入文件 {os.path.basename(file_path)}")

    def select_output_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".gcode",
            filetypes=[("G-code 文件", "*.gcode"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.output_path.set(file_path)
            self.status_label.config(text=f"状态: 已选择输出文件 {os.path.basename(file_path)}")

    def process_gcode(self):
        input_file = self.input_path.get()
        output_file = self.output_path.get()

        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("错误", "请选择有效的输入 G-code 文件")
            self.status_label.config(text="状态: 输入文件无效")
            return
        if not output_file:
            messagebox.showerror("错误", "请选择输出 G-code 文件路径")
            self.status_label.config(text="状态: 输出文件路径未指定")
            return

        self.status_label.config(text="状态: 正在处理...")
        self.root.update()

        try:
            # 读取输入文件
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            output_lines = []
            current_segment = []
            in_segment = False

            for line in lines:
                line = line.strip()
                if not line:
                    # 空行，结束当前分段
                    if in_segment and current_segment:
                        # 处理分段
                        if current_segment[0].startswith('G1'):
                            # 提取第一个 G1 行的 X, Y, Z, F
                            parts = current_segment[0].split()
                            x = next((part[1:] for part in parts if part.startswith('X')), None)
                            y = next((part[1:] for part in parts if part.startswith('Y')), None)
                            z = next((part[1:] for part in parts if part.startswith('Z')), None)
                            f = next((part[1:] for part in parts if part.startswith('F')), None)
                            if x and y and z and f:
                                g0_line = f"G0 X{x} Y{y} Z{z} F{f}"
                                output_lines.append("T0")
                                output_lines.append(g0_line)
                                output_lines.extend(current_segment)
                                output_lines.append("")
                            else:
                                # 格式错误，直接输出
                                output_lines.append("T0")
                                output_lines.extend(current_segment)
                                output_lines.append("")
                        else:
                            # 非 G1 开头，直接输出
                            output_lines.append("T0")
                            output_lines.extend(current_segment)
                            output_lines.append("")
                        current_segment = []
                        in_segment = False
                    else:
                        output_lines.append("")
                    continue

                if line.startswith('T0'):
                    # 新分段开始
                    if in_segment and current_segment:
                        # 处理上一个分段
                        if current_segment[0].startswith('G1'):
                            parts = current_segment[0].split()
                            x = next((part[1:] for part in parts if part.startswith('X')), None)
                            y = next((part[1:] for part in parts if part.startswith('Y')), None)
                            z = next((part[1:] for part in parts if part.startswith('Z')), None)
                            f = next((part[1:] for part in parts if part.startswith('F')), None)
                            if x and y and z and f:
                                g0_line = f"G0 X{x} Y{y} Z{z} F{f}"
                                output_lines.append("T0")
                                output_lines.append(g0_line)
                                output_lines.extend(current_segment)
                                output_lines.append("")
                            else:
                                output_lines.append("T0")
                                output_lines.extend(current_segment)
                                output_lines.append("")
                    current_segment = []
                    in_segment = True
                    continue

                if in_segment:
                    current_segment.append(line)

            # 处理最后一个分段
            if in_segment and current_segment:
                if current_segment[0].startswith('G1'):
                    parts = current_segment[0].split()
                    x = next((part[1:] for part in parts if part.startswith('X')), None)
                    y = next((part[1:] for part in parts if part.startswith('Y')), None)
                    z = next((part[1:] for part in parts if part.startswith('Z')), None)
                    f = next((part[1:] for part in parts if part.startswith('F')), None)
                    if x and y and z and f:
                        g0_line = f"G0 X{x} Y{y} Z{z} F{f}"
                        output_lines.append("T0")
                        output_lines.append(g0_line)
                        output_lines.extend(current_segment)
                        output_lines.append("")
                    else:
                        output_lines.append("T0")
                        output_lines.extend(current_segment)
                        output_lines.append("")
                else:
                    output_lines.append("T0")
                    output_lines.extend(current_segment)
                    output_lines.append("")

            # 保存输出文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines))

            self.status_label.config(text=f"状态: 处理完成，输出到 {os.path.basename(output_file)}")
            messagebox.showinfo("成功", f"G-code 文件处理完成，保存到 {output_file}")

        except Exception as e:
            self.status_label.config(text=f"状态: 处理失败 - {str(e)}")
            messagebox.showerror("错误", f"处理 G-code 文件失败: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GCodeProcessorApp(root)
    root.mainloop()