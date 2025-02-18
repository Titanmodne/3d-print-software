import tkinter as tk
from tkinter import filedialog, messagebox


def process_data(content, first_layers, last_layers):
    """
    处理文件内容，要求：
      - 仅对处于前几层和后几层的层（由用户参数 first_layers 和 last_layers 指定）
        将 T1 替换为 T0。
      - 先扫描整个文件（逐行），收集所有出现的层号（以 ";LAYER:" 开头）。
      - 根据出现顺序，前 first_layers 个层和最后 last_layers 个层为目标层。
      - 再次扫描文件时，根据当前层状态决定是否替换 T1 为 T0。
    """
    # 将内容按行拆分
    lines = content.splitlines()

    # 第一遍扫描：收集独立层号列表（按首次出现的顺序，不重复）
    unique_layers = []
    for line in lines:
        if line.startswith(";LAYER:"):
            try:
                layer_number = int(line.split(":", 1)[1].strip())
            except ValueError:
                continue
            if layer_number not in unique_layers:
                unique_layers.append(layer_number)

    # 根据前几层和后几层参数确定目标层集合
    first_layers_set = set(unique_layers[:first_layers]) if first_layers > 0 else set()
    last_layers_set = set(unique_layers[-last_layers:]) if last_layers > 0 else set()
    target_layers = first_layers_set.union(last_layers_set)

    # 第二遍扫描：逐行处理，并维护当前层状态
    result_lines = []
    current_layer = None
    for line in lines:
        if line.startswith(";LAYER:"):
            try:
                current_layer = int(line.split(":", 1)[1].strip())
            except ValueError:
                current_layer = None
        # 如果当前层在目标层中，则将该行中所有 T1 替换为 T0
        if current_layer is not None and current_layer in target_layers:
            line = line.replace("T1", "T0")
        result_lines.append(line)

    return "\n".join(result_lines)


def browse_input_file():
    """选择输入文件"""
    filename = filedialog.askopenfilename(
        title="选择输入文件",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if filename:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, filename)


def browse_output_file():
    """选择输出文件"""
    filename = filedialog.asksaveasfilename(
        title="选择输出文件",
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if filename:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, filename)


def process_file():
    """读取输入文件，处理后写入输出文件"""
    input_path = input_entry.get().strip()
    output_path = output_entry.get().strip()
    first_layers_str = first_layers_entry.get().strip()
    last_layers_str = last_layers_entry.get().strip()

    if not input_path:
        messagebox.showerror("错误", "请输入输入文件路径")
        return
    if not output_path:
        messagebox.showerror("错误", "请输入输出文件路径")
        return
    if first_layers_str == "" or last_layers_str == "":
        messagebox.showerror("错误", "请输入前几层和后几层的参数")
        return

    try:
        first_layers = int(first_layers_str)
        last_layers = int(last_layers_str)
    except ValueError:
        messagebox.showerror("错误", "前几层和后几层的参数必须为整数")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        messagebox.showerror("错误", f"读取输入文件时出错:\n{e}")
        return

    processed_content = process_data(content, first_layers, last_layers)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
    except Exception as e:
        messagebox.showerror("错误", f"写入输出文件时出错:\n{e}")
        return

    messagebox.showinfo("完成", "文件处理完成！")


# ----------------- 创建 GUI 界面 -----------------
root = tk.Tk()
root.title("文件处理程序")

# 设置窗口大小及内边距
root.geometry("650x250")
padding_options = {'padx': 10, 'pady': 5}

# 输入文件选择
input_label = tk.Label(root, text="输入文件:")
input_label.grid(row=0, column=0, sticky="e", **padding_options)
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, **padding_options)
input_button = tk.Button(root, text="浏览", command=browse_input_file)
input_button.grid(row=0, column=2, **padding_options)

# 输出文件选择
output_label = tk.Label(root, text="输出文件:")
output_label.grid(row=1, column=0, sticky="e", **padding_options)
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, **padding_options)
output_button = tk.Button(root, text="浏览", command=browse_output_file)
output_button.grid(row=1, column=2, **padding_options)

# 前几层参数输入
first_layers_label = tk.Label(root, text="前几层:")
first_layers_label.grid(row=2, column=0, sticky="e", **padding_options)
first_layers_entry = tk.Entry(root, width=20)
first_layers_entry.grid(row=2, column=1, sticky="w", **padding_options)

# 后几层参数输入
last_layers_label = tk.Label(root, text="后几层:")
last_layers_label.grid(row=3, column=0, sticky="e", **padding_options)
last_layers_entry = tk.Entry(root, width=20)
last_layers_entry.grid(row=3, column=1, sticky="w", **padding_options)

# 开始处理按钮
process_button = tk.Button(root, text="开始处理", command=process_file, width=20)
process_button.grid(row=4, column=1, **padding_options)

root.mainloop()
