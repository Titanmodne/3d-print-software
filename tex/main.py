import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import tkinter as tk
import numpy as np
from math import cos, sin, pi, sqrt
import platform as std_platform  # 使用别名导入标准 platform 模块

class HexagonGridApp:
    def __init__(self):
        # 初始化参数
        self.center_x = 0  # 固定为 0
        self.center_y = 0  # 固定为 0
        self.side_length = 4
        self.offset_c = 0.2
        self.x_range = 10  # 网格 X 范围的一半
        self.y_range = 10  # 网格 Y 范围的一半
        self.z_offset = 0  # 仅存储，不影响 Z 值
        self.scale = 1.0
        self.translate_x = 0
        self.translate_y = 0
        self.camera_z = 100
        self.rotate_x = 0
        self.rotate_y = 0
        self.dragging = False
        self.rotating = False
        self.last_mouse_pos = (0, 0)

        # 初始化 Tkinter 窗口
        self.root = tk.Tk()
        self.root.title("蜂窝网格生成")

        self.show_original = tk.BooleanVar(self.root, value=True)
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        tk.Label(self.frame, text="边长 l:").grid(row=0, column=0, padx=5)
        self.entry_l = tk.Entry(self.frame, width=10)
        self.entry_l.grid(row=0, column=1)
        self.entry_l.insert(0, "4")

        tk.Label(self.frame, text="Z 偏移:").grid(row=0, column=2, padx=5)
        self.entry_z_offset = tk.Entry(self.frame, width=10)
        self.entry_z_offset.grid(row=0, column=3)
        self.entry_z_offset.insert(0, "0")

        tk.Label(self.frame, text="偏置 c:").grid(row=0, column=4, padx=5)
        self.entry_c = tk.Entry(self.frame, width=10)
        self.entry_c.grid(row=0, column=5)
        self.entry_c.insert(0, "0.2")

        tk.Label(self.frame, text="网格范围 X 一半:").grid(row=0, column=6, padx=5)
        self.entry_x_range = tk.Entry(self.frame, width=10)
        self.entry_x_range.grid(row=0, column=7)
        self.entry_x_range.insert(0, "10")

        tk.Label(self.frame, text="网格范围 Y 一半:").grid(row=0, column=8, padx=5)
        self.entry_y_range = tk.Entry(self.frame, width=10)
        self.entry_y_range.grid(row=0, column=9)
        self.entry_y_range.insert(0, "10")

        tk.Checkbutton(self.frame, text="显示原路径", variable=self.show_original).grid(row=0, column=10, padx=10)
        tk.Button(self.frame, text="更新", command=self.update_params).grid(row=0, column=11, padx=10)

        # 初始化 Pygame 和 OpenGL
        pygame.init()
        self.display = (600, 600)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("蜂窝网格生成")
        self.setup_opengl()

        self.running = True
        self.main_loop()

    def setup_opengl(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.display[0] / self.display[1], 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)

    def update_params(self):
        try:
            self.side_length = float(self.entry_l.get())
            self.z_offset = float(self.entry_z_offset.get())  # 仅存储，不影响 Z 值
            self.offset_c = float(self.entry_c.get())
            self.offset_c = min(self.offset_c, self.side_length * 0.5)
            self.x_range = float(self.entry_x_range.get())
            self.y_range = float(self.entry_y_range.get())
            if self.x_range <= 0 or self.y_range <= 0:
                raise ValueError("X 和 Y 范围必须为正值")
        except ValueError:
            print("请输入有效的数字！")

    def save_polyline(self, points, filename="green_polyline.txt"):
        with open(filename, 'w') as f:
            f.write('[')
            for i, point in enumerate(points):
                x = round(point[0], 3)
                y = round(point[1], 3)
                f.write(f'({x:.3f}, {y:.3f})')  # 仅保存 XY 坐标
                if i < len(points) - 1:
                    f.write(', ')
            f.write(']')

    def save_points_set(self, points, filename="points_set.txt"):
        with open(filename, 'w') as f:
            for i, point in enumerate(points):
                x = round(point[0], 3)
                y = round(point[1], 3)
                f.write(f"{i}: ({x:.3f}, {y:.3f})\n")  # 仅保存 XY 坐标

    def draw_grid(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # 绘制背景网格
        glColor3f(0.8, 0.8, 0.8)
        glBegin(GL_LINES)
        grid_spacing = 50
        width, height = self.display
        for y in range(0, height + grid_spacing, grid_spacing):
            glVertex3f(0, y, 0.1)
            glVertex3f(width, y, 0.1)
        for x in range(0, width + grid_spacing, grid_spacing):
            glVertex3f(x, 0, 0.1)
            glVertex3f(x, height, 0.1)
        glEnd()

        # 绘制坐标系（黑色 X 和 Y 轴）
        glColor3f(0.0, 0.0, 0.0)  # 黑色
        glLineWidth(2.0)

        # 绘制 X 轴
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0.1)
        glVertex3f(width, 0, 0.1)
        glEnd()

        # 绘制 Y 轴
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0.1)
        glVertex3f(0, height, 0.1)
        glEnd()

        # 添加单位距离标记
        unit_spacing = 50  # 每 50 像素一个单位
        for x in range(0, width + unit_spacing, unit_spacing):
            glBegin(GL_LINES)
            glVertex3f(x, 0, 0.1)
            glVertex3f(x, 10, 0.1)  # 刻度线长度 10 像素
            glEnd()
        for y in range(0, height + unit_spacing, unit_spacing):
            glBegin(GL_LINES)
            glVertex3f(0, y, 0.1)
            glVertex3f(10, y, 0.1)  # 刻度线长度 10 像素
            glEnd()

        glPopMatrix()

    def get_hexagon_points(self, center_x, center_y, center_z):
        vertices = []
        for i in range(6):
            angle = pi / 3 * i + pi / 2
            x = center_x + self.side_length * cos(angle)
            y = center_y + self.side_length * sin(angle)
            z = center_z  # 使用传入的 Z 值
            vertices.append((round(x, 3), round(y, 3), round(z, 3)))

        original_points = vertices[:4]

        new_points = []
        start = vertices[0]
        end = vertices[1]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dz = 0
        length = sqrt(dx**2 + dy**2 + dz**2)
        if length != 0:
            ux = dx / length
            uy = dy / length
            uz = 0
            x1 = start[0] + ux * self.offset_c
            y1 = start[1] + uy * self.offset_c
            z1 = center_z
            new_points.append((round(x1, 3), round(y1, 3), round(z1, 3)))
            x2 = start[0] + ux * (length - self.offset_c)
            y2 = start[1] + uy * (length - self.offset_c)
            z2 = center_z
            new_points.append((round(x2, 3), round(y2, 3), round(z2, 3)))

        start = vertices[2]
        end = vertices[3]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dz = 0
        length = sqrt(dx**2 + dy**2 + dz**2)
        if length != 0:
            ux = dx / length
            uy = dy / length
            uz = 0
            x3 = start[0] + ux * self.offset_c
            y3 = start[1] + uy * self.offset_c
            z3 = center_z
            new_points.append((round(x3, 3), round(y3, 3), round(z3, 3)))
            x4 = end[0] - ux * self.offset_c
            y4 = end[1] - uy * self.offset_c
            z4 = center_z
            new_points.append((round(x4, 3), round(y4, 3), round(z4, 3)))

        return original_points, new_points

    def draw_hexagon(self, center_x, center_y, center_z):
        original_points, new_points = self.get_hexagon_points(center_x, center_y, center_z)

        if self.show_original.get():
            glColor3f(1.0, 0.0, 0.0)
            glBegin(GL_LINE_STRIP)
            for x, y, z in original_points:
                glVertex3f(x, y, z)
            glEnd()

            glColor3f(1.0, 0.0, 0.0)
            glPointSize(6.0)
            glBegin(GL_POINTS)
            for x, y, z in original_points:
                glVertex3f(x, y, z)
            glEnd()

        return new_points

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.dragging = True
                        self.last_mouse_pos = event.pos
                    elif event.button == 3:
                        self.rotating = True
                        self.last_mouse_pos = event.pos
                    elif event.button == 4:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        world_x = self.center_x + self.translate_x + (mouse_x - self.display[0]/2) * (self.camera_z / 300) / self.scale
                        world_y = self.center_y + self.translate_y + (self.display[1]/2 - mouse_y) * (self.camera_z / 300) / self.scale
                        self.scale *= 1.1
                        self.scale = min(self.scale, 10.0)
                        self.translate_x = world_x - self.center_x - (mouse_x - self.display[0]/2) * (self.camera_z / 300) / self.scale
                        self.translate_y = world_y - self.center_y - (self.display[1]/2 - mouse_y) * (self.camera_z / 300) / self.scale
                    elif event.button == 5:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        world_x = self.center_x + self.translate_x + (mouse_x - self.display[0]/2) * (self.camera_z / 300) / self.scale
                        world_y = self.center_y + self.translate_y + (self.display[1]/2 - mouse_y) * (self.camera_z / 300) / self.scale
                        self.scale /= 1.1
                        self.scale = max(self.scale, 0.1)
                        self.translate_x = world_x - self.center_x - (mouse_x - self.display[0]/2) * (self.camera_z / 300) / self.scale
                        self.translate_y = world_y - self.center_y - (self.display[1]/2 - mouse_y) * (self.camera_z / 300) / self.scale
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False
                    elif event.button == 3:
                        self.rotating = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        dx = event.pos[0] - self.last_mouse_pos[0]
                        dy = event.pos[1] - self.last_mouse_pos[1]
                        self.translate_x -= dx * 0.5 / self.scale
                        self.translate_y += dy * 0.5 / self.scale
                        self.last_mouse_pos = event.pos
                    elif self.rotating:
                        dx = event.pos[0] - self.last_mouse_pos[0]
                        dy = event.pos[1] - self.last_mouse_pos[1]
                        self.rotate_y -= dx * 0.2
                        self.rotate_x += dy * 0.2
                        self.last_mouse_pos = event.pos

            try:
                self.root.update()
            except tk.TclError:
                self.running = False

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            gluLookAt(
                self.center_x + self.translate_x, self.center_y + self.translate_y, self.camera_z,
                self.center_x + self.translate_x, self.center_y + self.translate_y, 0.1,
                0, 1, 0
            )
            glRotatef(self.rotate_x, 1, 0, 0)
            glRotatef(self.rotate_y, 0, 1, 0)
            glScalef(self.scale, self.scale, self.scale)

            # 计算复制次数
            copies_a = int(2 * self.y_range / 3)
            copies_b = int(2 * self.x_range / (sin(2 * pi / 3) * 2))
            print(f"Y 轴复制次数 (2y/3): {copies_a}")
            print(f"X 轴复制次数 (2x/(sin(120°)*2)): {copies_b}")

            # 生成绿色路径并收集折线点
            all_points = []
            polyline_points = []
            for j in range(copies_b + 1):
                offset_x = j * 2 * self.side_length * (sqrt(3) / 2)
                group_points = []
                all_new_points = []
                for i in range(copies_a + 1):
                    offset_y = i * 3 * self.side_length
                    new_points = self.get_hexagon_points(
                        self.center_x + offset_x,
                        self.center_y - offset_y,
                        0.1
                    )[1]
                    all_new_points.extend(new_points)
                symmetric_center_x = self.center_x + offset_x
                symmetric_points = [(2 * symmetric_center_x - x, y, z) for x, y, z in all_new_points]
                combined_points = all_new_points + [symmetric_points[-1]] + symmetric_points[::-1]
                group_points = combined_points
                all_points.extend(group_points)
                polyline_points.extend(group_points)

                if j < copies_b:
                    current_tail = group_points[-1]
                    next_head = self.get_hexagon_points(
                        self.center_x + (j+1) * 2 * self.side_length * (sqrt(3) / 2),
                        self.center_y,
                        0.1
                    )[1][0]
                    polyline_points.append(current_tail)
                    polyline_points.append(next_head)

            # 渲染绿色路径
            glColor3f(0.0, 1.0, 0.0)
            glBegin(GL_LINE_STRIP)
            for x, y, z in polyline_points:
                glVertex3f(x, y, z)
            glEnd()

            glColor3f(0.0, 1.0, 0.0)
            glPointSize(4.0)
            glBegin(GL_POINTS)
            for x, y, z in polyline_points:
                glVertex3f(x, y, z)
            glEnd()

            # 生成红色路径
            for i in range(copies_a + 1):
                offset_y = i * 3 * self.side_length
                self.draw_hexagon(self.center_x, self.center_y - offset_y, 0.1)

            self.draw_grid()

            # 保存原始折线和点集文件
            self.save_polyline(polyline_points, "green_polyline.txt")
            self.save_points_set(polyline_points, "points_set.txt")

            error = glGetError()
            if error != GL_NO_ERROR:
                print(f"OpenGL 错误: {error}")

            pygame.display.flip()
            pygame.time.wait(10)

        pygame.quit()
        self.root.destroy()

if __name__ == "__main__":
    if std_platform.system() == "Emscripten":  # 使用 std_platform
        print("Running in Emscripten environment (e.g., Pyodide)")
        # 在 Pyodide 环境下运行的代码
    else:
        print(f"Running on {std_platform.system()} (e.g., Windows)")
        app = HexagonGridApp()