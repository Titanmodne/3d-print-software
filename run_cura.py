import subprocess
import os
import tkinter as tk
from tkinter import filedialog

def select_file():
    # 创建并返回文件选择对话框
    root = tk.Tk()
    root.withdraw()  # 不显示根窗口
    file_path = filedialog.askopenfilename(
        title="选择STL文件",
        filetypes=[("STL files", "*.stl")]
    )
    return file_path

def run_cura_engine(stl_file_path):
    if not stl_file_path:
        print("没有选择文件。")
        return

    # 要切换到的目录
    target_directory = r"C:\Program Files\UltiMaker Cura 5.8.1"
    os.chdir(target_directory)

    # 指定CuraEngine.exe的路径
    cura_engine_path = "CuraEngine.exe"

    # 设置Cura的配置文件路径
    config_path = r"share\cura\resources\definitions\fdmprinter.def.json"

    # 桌面路径
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_folder = os.path.join(desktop_path, "input_gcode")

    # 如果输出文件夹不存在，则创建它
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 根据输入的STL文件名称设置输出的G-code文件路径
    output_gcode_path = os.path.join(output_folder, os.path.basename(stl_file_path).replace('.stl', '.gcode'))

    # 构建命令
    command = [
        cura_engine_path,
        "slice",
        "-j", config_path,
        "-s", "roofing_layer_count=0",
        "-l", stl_file_path,
        "-o", output_gcode_path
    ]

    # 执行命令
    try:
        subprocess.run(command, check=True)
        print("切片成功！输出文件位于：" + output_gcode_path)
    except subprocess.CalledProcessError as e:
        print("切片失败：", e)

# 主函数
if __name__ == "__main__":
    stl_file = select_file()
    run_cura_engine(stl_file)