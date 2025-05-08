import sys
import ast
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox, QOpenGLWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.setMinimumSize(800, 600)
        self.contours = []  # 列表：[(coords, z), ...]，coords 为 [(x, y), ...]
        self.offset_contours = []
        self.bounds = None  # XY 边界
        self.z_range = None  # Z 范围
        self.rotation = [0, 0]
        self.translation = [0, 0, 0]
        self.scale = 1.0
        self.last_pos = None
        print("GLWidget 初始化")

    def initializeGL(self):
        print("初始化 OpenGL")
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glLineWidth(2.0)

    def resizeGL(self, w, h):
        print(f"调整窗口大小: {w}x{h}")
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h != 0 else 1, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        print("执行 paintGL")
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # 自适应视口
        if self.bounds is not None and self.z_range is not None:
            xy_extent = np.max(self.bounds[1] - self.bounds[0])
            z_extent = self.z_range[1] - self.z_range[0]
            max_extent = max(xy_extent, z_extent)
            if max_extent > 0:
                scale_factor = 20.0 / max_extent
                glScalef(scale_factor, scale_factor, scale_factor)
                center_xy = (self.bounds[0] + self.bounds[1]) / 2
                center_z = (self.z_range[0] + self.z_range[1]) / 2
                glTranslatef(-center_xy[0], -center_xy[1], -center_z - max_extent * 2)
            else:
                glTranslatef(0, 0, -50)
        else:
            glTranslatef(0, 0, -50)

        glTranslatef(self.translation[0], self.translation[1], self.translation[2])
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glScalef(self.scale, self.scale, self.scale)

        # 绘制原始轮廓（蓝色）
        glColor3f(0, 0, 1)
        print(f"渲染原始轮廓: {len(self.contours)} 个")
        for coords, z in self.contours:
            glBegin(GL_LINE_LOOP)
            for x, y in coords:
                glVertex3f(float(x), float(y), float(z))
            glEnd()
            print(f"绘制原始轮廓: z={z:.3f}, 点数={len(coords)}, 坐标={coords}")

        # 绘制偏置轮廓（红色）
        glColor3f(1, 0, 0)
        print(f"渲染偏置轮廓: {len(self.offset_contours)} 个")
        for coords, z in self.offset_contours:
            glBegin(GL_LINE_LOOP)
            for x, y in coords:
                glVertex3f(float(x), float(y), float(z))
            glEnd()
            print(f"绘制偏置轮廓: z={z:.3f}, 点数={len(coords)}, 坐标={coords}")

        glFlush()

    def mousePressEvent(self, event):
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_pos:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()
            if event.buttons() == Qt.LeftButton:
                self.rotation[0] += dy * 0.5
                self.rotation[1] += dx * 0.5
            elif event.buttons() == Qt.RightButton:
                self.translation[0] += dx * 0.01
                self.translation[1] -= dy * 0.01
            self.last_pos = event.pos()
            self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.scale *= 1.1 if delta > 0 else 0.9
        self.update()

    def set_contours(self, contours, offset_contours):
        self.contours = contours
        self.offset_contours = offset_contours
        # 计算边界和 Z 范围
        all_points = []
        all_z = []
        for coords, z in contours + offset_contours:
            all_points.extend(coords)
            all_z.append(z)
        if all_points:
            points_np = np.array(all_points)
            self.bounds = np.array([points_np.min(axis=0), points_np.max(axis=0)])
            self.z_range = [min(all_z), max(all_z)] if all_z else [0, 0]
        else:
            self.bounds = None
            self.z_range = None
        print(f"设置轮廓: {len(contours)} 个原始, {len(offset_contours)} 个偏置, 边界={self.bounds}, Z范围={self.z_range}")
        self.repaint()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("轮廓查看器")
        self.resize(1000, 700)
        print("MainWindow 初始化")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        self.gl_widget = GLWidget()
        layout.addWidget(self.gl_widget, stretch=3)

        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        layout.addWidget(control_panel, stretch=1)

        self.load_button = QPushButton("加载轮廓文件")
        self.load_button.clicked.connect(self.load_contours)
        control_layout.addWidget(self.load_button)

        control_layout.addStretch()

        glutInit()
        print("GLUT 初始化完成")

    def showEvent(self, event):
        print("MainWindow 显示")
        super().showEvent(event)

    def load_contours(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择轮廓文件", "", "文本文件 (*.txt)")
        if file_path:
            try:
                contours = []
                offset_contours = []
                current_section = None

                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line == "Original Contours:":
                            current_section = "original"
                            continue
                        elif line == "Offset Contours:":
                            current_section = "offset"
                            continue
                        if not line or current_section is None:
                            continue

                        # 解析 z 和 coords
                        if ':' in line:
                            z_part, coords_part = line.split(':', 1)
                            z = float(z_part.split('=')[1].split()[0])
                            # 使用 ast.literal_eval 解析坐标列表
                            coords = ast.literal_eval(coords_part.strip())
                            if current_section == "original":
                                contours.append((coords, z))
                            else:
                                offset_contours.append((coords, z))

                if not contours and not offset_contours:
                    raise ValueError("文件中未找到有效轮廓数据")

                print(f"加载轮廓: {len(contours)} 个原始, {len(offset_contours)} 个偏置")
                self.gl_widget.set_contours(contours, offset_contours)
                QMessageBox.information(self, "成功", f"已加载 {len(contours)} 个原始轮廓和 {len(offset_contours)} 个偏置轮廓")
            except Exception as e:
                print(f"加载轮廓文件出错: {e}")
                QMessageBox.warning(self, "错误", f"无法加载轮廓文件: {e}")

if __name__ == '__main__':
    print("启动 QApplication")
    app = QApplication(sys.argv)
    window = MainWindow()
    print("显示 MainWindow")
    window.show()
    print("进入事件循环")
    sys.exit(app.exec_())