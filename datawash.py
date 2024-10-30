import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def remove_e_values_and_manage_lines(file_path, output_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        new_lines = []
        last_z_value = None
        last_line_was_empty = False  # 追踪最后一行是否是空行

        for line in lines:
            parts = line.split(',')
            new_parts = [part for part in parts if not part.strip().startswith('E')]
            # 查找当前行的Z值
            z_part = [part for part in parts if part.strip().startswith('Z')]
            current_z_value = z_part[0] if z_part else None

            # 如果Z值改变了，并且上一行不是空行，添加一个空行
            if last_z_value is not None and current_z_value != last_z_value and not last_line_was_empty:
                new_lines.append('\n')
                last_line_was_empty = True

            new_line = ','.join(new_parts).strip()
            if new_line:  # 只添加非空行
                new_lines.append(new_line + '\n')
                last_line_was_empty = False

            last_z_value = current_z_value

        with open(output_path, 'w') as file:
            file.writelines(new_lines)
        messagebox.showinfo("成功", "文件处理完成！")
    except Exception as e:
        messagebox.showerror("错误", str(e))


def select_input_file():
    input_path = filedialog.askopenfilename(title="选择文件", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if input_path:
        output_path = filedialog.asksaveasfilename(title="保存文件为",
                                                   filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if output_path:
            remove_e_values_and_manage_lines(input_path, output_path)


root = tk.Tk()
root.title("删除E值并优化空行")
root.geometry("300x150")

btn_select_file = tk.Button(root, text="选择文件", command=select_input_file)
btn_select_file.pack(expand=True)

root.mainloop()
