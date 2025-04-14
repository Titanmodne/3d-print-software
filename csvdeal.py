import csv
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox


def select_file_count():
    """ 弹出对话框让用户输入要处理的文件数量 """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    count = simpledialog.askinteger("输入", "请输入要处理的文件数量：", minvalue=1, parent=root)
    return count


def choose_files(file_count):
    """ 根据用户指定的文件数量，依次选择文件 """
    files = []
    for _ in range(file_count):
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        file_path = filedialog.askopenfilename(title="选择 CSV 文件", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            files.append(file_path)
        else:
            messagebox.showwarning("警告", "未选择文件，操作将被取消！")
            break
    return files


def choose_save_location():
    """ 弹出文件保存窗口让用户选择输出 TXT 文件的位置 """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    file_path = filedialog.asksaveasfilename(title="保存为", filetypes=[("Text Files", "*.txt")],
                                             defaultextension=".txt")
    return file_path


def extract_and_combine_coordinates(csv_files, output_txt_file):
    """
    从一系列 CSV 文件中提取 XYZ 坐标，将结果合并并保存到一个 TXT 文件中。
    每个文件的坐标之间用空行隔开。

    参数:
    csv_files (list): CSV 文件路径列表。
    output_txt_file (str): 输出的 TXT 文件路径。
    """
    with open(output_txt_file, 'w') as txtfile:
        for i, csv_file in enumerate(csv_files):
            if i > 0:
                txtfile.write("\n")  # 在文件内容之间添加空行
            with open(csv_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    x = float(row['X'])
                    y = float(row['Y'])
                    z = float(row['Z'])
                    # 精度控制为小数点后三位
                    txtfile.write(f"G1 X: {x:.3f}, Y: {y:.3f}, Z: {z:.3f}\n")


def main():
    file_count = select_file_count()
    if not file_count:
        messagebox.showinfo("提示", "操作已取消或未输入有效数量！")
        return

    csv_files = choose_files(file_count)
    if len(csv_files) != file_count:
        return  # 如果用户取消了选择，则不继续执行

    output_txt_file = choose_save_location()
    if not output_txt_file:
        messagebox.showinfo("提示", "没有指定输出文件！")
        return

    extract_and_combine_coordinates(csv_files, output_txt_file)
    messagebox.showinfo("完成", "坐标已成功提取并保存！")


if __name__ == "__main__":
    main()
