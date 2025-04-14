import tkinter as tk
from tkinter import filedialog, messagebox
import trimesh
import numpy as np
from stl import mesh
import os

class STLProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STL File Processor")

        # 输入文件路径
        tk.Label(root, text="输入 STL 文件:").grid(row=0, column=0, padx=5, pady=5)
        self.input_path = tk.Entry(root, width=50)
        self.input_path.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="浏览", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)

        # 输出目录
        tk.Label(root, text="输出目录:").grid(row=1, column=0, padx=5, pady=5)
        self.output_dir = tk.Entry(root, width=50)
        self.output_dir.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(root, text="浏览", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)

        # 外壳厚度
        tk.Label(root, text="外壳厚度 (mm):").grid(row=2, column=0, padx=5, pady=5)
        self.thickness = tk.Entry(root, width=10)
        self.thickness.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # 处理按钮
        tk.Button(root, text="处理 STL", command=self.process_stl).grid(row=3, column=0, columnspan=3, pady=10)

    def browse_input(self):
        file_path = filedialog.askopenfilename(filetypes=[("STL files", "*.stl")])
        if file_path:
            self.input_path.delete(0, tk.END)
            self.input_path.insert(0, file_path)

    def browse_output(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir.delete(0, tk.END)
            self.output_dir.insert(0, dir_path)

    def vertex_offset(self, mesh, distance):
        """沿法向内移顶点以模拟内缩"""
        # 计算顶点法向量
        vertex_normals = mesh.vertex_normals
        # 内移顶点
        new_vertices = mesh.vertices - distance * vertex_normals
        # 创建新网格
        new_mesh = trimesh.Trimesh(vertices=new_vertices, faces=mesh.faces, process=False)
        return new_mesh

    def process_stl(self):
        input_file = self.input_path.get()
        output_dir = self.output_dir.get()
        try:
            thickness = float(self.thickness.get())
            if thickness <= 0:
                raise ValueError("厚度必须为正数。")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的厚度值（正数）。")
            return

        if not input_file or not output_dir:
            messagebox.showerror("错误", "请指定输入文件和输出目录。")
            return

        try:
            # 加载 STL 文件
            model = trimesh.load(input_file)

            # 检查是否封闭
            if not model.is_watertight:
                messagebox.showwarning("警告", "输入的 STL 文件不是封闭的，结果可能不准确。建议使用 MeshLab 或 Blender 修复文件。")

            # 创建外壳（原始模型）
            shell_mesh = model.copy()

            # 创建内部（通过顶点法向内移）
            inner_mesh = self.vertex_offset(model, thickness)

            # 检查内部网格有效性
            if len(inner_mesh.faces) == 0:
                messagebox.showerror("错误", "无法创建内部模型，请尝试更小的厚度。")
                return

            # 保存外壳和内部 STL 文件
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            shell_path = os.path.join(output_dir, f"{base_name}_shell.stl")
            inner_path = os.path.join(output_dir, f"{base_name}_inner.stl")

            shell_mesh.export(shell_path)
            inner_mesh.export(inner_path)

            messagebox.showinfo("成功", f"文件已保存：\n{shell_path}\n{inner_path}")

        except Exception as e:
            messagebox.showerror("错误", f"发生错误：{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = STLProcessorApp(root)
    root.mainloop()