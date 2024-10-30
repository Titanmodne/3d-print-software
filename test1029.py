import re
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

def extract_coordinates(gcode_file):
    """
    提取G-code文件中的坐标，并处理Z值的缺失情况。
    如果之前没有有效的X、Y、Z值，则将其设置为0。
    """
    coordinates = []
    current_x = 0  # 当前的X值，初始为0
    current_y = 0  # 当前的Y值，初始为0
    current_z = 0  # 当前的Z值，初始为0
    current_e = 0  # 当前的E值，初始为0

    gcode_pattern = re.compile(
        r'^(G[01])\s*(F[+-]?\d*\.?\d+)?\s*(X[+-]?\d*\.?\d+)?\s*(Y[+-]?\d*\.?\d+)?\s*(Z[+-]?\d*\.?\d+)?\s*(E[+-]?\d*\.?\d+)?', re.MULTILINE)

    with open(gcode_file, 'r') as file:
        for line in file:
            line = line.strip()
            gcode_match = gcode_pattern.match(line)
            if gcode_match:
                g_code, f_value, x, y, z, e = gcode_match.groups()
                x = x[1:] if x else current_x
                y = y[1:] if y else current_y
                z = z[1:] if z else current_z
                e = e[1:] if e else None  # 移除 E 前缀，只保留数值部分或保留 None
                current_x, current_y, current_z = x, y, z
                coordinates.append((g_code, x, y, z, e))

    return coordinates

def replace_none_z_values(coordinates):
    """
    遍历坐标列表，替换其中Z为None的值为最后的有效Z值。
    如果之前没有有效的Z值，则将其设置为0。
    删除所有E值为None的行。
    """
    current_z = 0
    current_e = 0
    updated_coordinates = []
    for g_code, x, y, z, e in coordinates:
        if e is None:
            continue  # 跳过E值为空的行
        e_float = float(e)  # 将 E 转换为浮点数
        z = z or current_z
        current_z = z
        if e_float < current_e:  # 检测E值是否小于前一个值
            updated_coordinates.append(None)  # 插入空行
        current_e = e_float  # 更新当前E值
        updated_coordinates.append((g_code, x, y, z, e))
    return updated_coordinates

def save_to_txt(coordinates, output_file):
    """
    将处理后的坐标数据保存为TXT文件。
    """
    with open(output_file, 'w') as file:
        for line in coordinates:
            if line is None:
                file.write("\n")  # 写入空行
            else:
                g_code, x, y, z, e = line
                e_value = f", E: {e}"
                file.write(f"{g_code} X: {x}, Y: {y}, Z: {z}{e_value}\n")

def process_gcode(gcode_file_path, output_file_path, output_box):
    """
    处理G-code文件的坐标提取、Z值替换和保存，并在输出框中显示结果。
    """
    coordinates = extract_coordinates(gcode_file_path)
    updated_coordinates = replace_none_z_values(coordinates)
    save_to_txt(updated_coordinates, output_file_path)
    output_box.delete(1.0, tk.END)  # 清空输出框内容
    for line in updated_coordinates:
        if line is None:
            output_box.insert(tk.END, "\n")  # 输出空行
        else:
            g_code, x, y, z, e = line
            e_value = f", E: {e}"
            output_box.insert(tk.END, f"{g_code} X: {x}, Y: {y}, Z: {z}{e_value}\n")
    messagebox.showinfo("完成", f"处理后的数据已保存至 {output_file_path}")

def select_gcode_file(entry):
    """
    选择G-code文件并在输入框中显示路径。
    """
    file_path = filedialog.askopenfilename(filetypes=[("G-code Files", "*.gcode")])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def main():
    root = tk.Tk()
    root.title("G-code 处理程序")

    # 输入文件选择
    tk.Label(root, text="选择G-code文件：").grid(row=0, column=0, padx=5, pady=5)
    input_entry = tk.Entry(root, width=50)
    input_entry.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(root, text="浏览", command=lambda: select_gcode_file(input_entry)).grid(row=0, column=2, padx=5, pady=5)

    # 输出文件名输入
    tk.Label(root, text="输出TXT文件名：").grid(row=1, column=0, padx=5, pady=5)
    output_entry = tk.Entry(root, width=50)
    output_entry.insert(0, r"C:\Users\zhong\Desktop\1.txt")
    output_entry.grid(row=1, column=1, padx=5, pady=5)

    # 输出框
    tk.Label(root, text="输出内容：").grid(row=2, column=0, padx=5, pady=5)
    output_box = scrolledtext.ScrolledText(root, width=60, height=20)
    output_box.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

    # 处理按钮
    tk.Button(root, text="开始处理", command=lambda: process_gcode(input_entry.get(), output_entry.get(), output_box)).grid(row=4, column=1, padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()