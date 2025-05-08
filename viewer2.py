import sys
import numpy as np
import ast
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog, QLabel, QMessageBox, QOpenGLWidget, QLineEdit
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.setMinimumSize(800, 600)
        self.layers = []  # [(z, points, color), ...]
        self.bounds = None
        self.z_range = None
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

        if self.bounds is not None and self.z_range is not None:
            xy_extent = np.max(self.bounds[1] - self.bounds[0])
            z_extent = self.z_range[1] - self.z_range[0] if self.z_range[0] != self.z_range[1] else 1.0
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

        for z, points, color in self.layers:
            # 绘制路径
            glColor3f(*color)
            print(f"渲染路径 z={z:.3f}: {len(points)} 个点, 颜色={color}")
            glBegin(GL_LINE_STRIP)
            for x, y in points:
                glVertex3f(float(x), float(y), float(z))
            glEnd()

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
        self.scale = max(0.1, min(self.scale, 10.0))
        self.update()

    def set_layers(self, layers):
        self.layers = layers
        all_points = []
        all_z = []
        for z, points, _ in layers:
            all_points.extend(points)
            all_z.append(z)
        if all_points:
            points_np = np.array(all_points)
            self.bounds = np.array([points_np.min(axis=0), points_np.max(axis=0)])
            self.z_range = [min(all_z), max(all_z)] if all_z else [0.1, 0.3]
        else:
            self.bounds = None
            self.z_range = None
        print(f"设置层: {len(layers)} 层, 边界={self.bounds}, Z范围={self.z_range}")
        self.repaint()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("三层旋转蜂窝网格展示")
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

        self.load_button = QPushButton("加载绿色蜂窝网格文件")
        self.load_button.clicked.connect(self.load_polyline)
        control_layout.addWidget(self.load_button)

        self.input_label = QLabel("输入文件: 未选择")
        control_layout.addWidget(self.input_label)

        # 添加 X 和 Y 输入框
        control_layout.addWidget(QLabel("第一个六边形中心点 X 距离 (负值，第三象限):"))
        self.x_input = QLineEdit("-2.598")  # 默认值，假设 s=1
        control_layout.addWidget(self.x_input)

        control_layout.addWidget(QLabel("第一个六边形中心点 Y 距离 (负值，第三象限):"))
        self.y_input = QLineEdit("-1.5")  # 默认值，假设 s=1
        control_layout.addWidget(self.y_input)

        self.center_label = QLabel("中心点: 未计算")
        control_layout.addWidget(self.center_label)

        self.process_button = QPushButton("处理并展示")
        self.process_button.clicked.connect(self.process_and_display)
        control_layout.addWidget(self.process_button)

        self.output_label = QLabel("输出文件: 未生成")
        control_layout.addWidget(self.output_label)

        control_layout.addStretch()

        glutInit()
        print("GLUT 初始化完成")

        self.polyline_points = None

    def showEvent(self, event):
        print("MainWindow 显示")
        super().showEvent(event)

    def load_polyline(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择绿色蜂窝网格文件", "", "文本文件 (*.txt)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    self.polyline_points = ast.literal_eval(content)
                points_np = np.array(self.polyline_points)
                print(f"加载绿色蜂窝网格点: {len(self.polyline_points)} 个, 范围: {np.min(points_np, axis=0)}, {np.max(points_np, axis=0)}")
                self.input_label.setText(f"输入文件: {file_path}")
                # 暂时不计算中心点，直到处理时使用 X 和 Y 参数
                self.center_label.setText("中心点: 未计算")
                QMessageBox.information(self, "成功", f"已加载绿色蜂窝网格文件: {file_path}, {len(self.polyline_points)} 个点")
            except Exception as e:
                print(f"加载绿色蜂窝网格文件出错: {e}")
                QMessageBox.warning(self, "错误", f"无法加载绿色蜂窝网格文件: {e}")
                self.polyline_points = None
                self.input_label.setText("输入文件: 未选择")
                self.center_label.setText("中心点: 未计算")

    def shift_to_origin(self, points, x_first, y_first):
        # 计算几何中心
        geometric_center = np.mean(points, axis=0)
        print(f"原始几何中心: ({geometric_center[0]:.3f}, {geometric_center[1]:.3f})")

        # 验证 X 和 Y 参数
        try:
            x_first = float(x_first)
            y_first = float(y_first)
        except ValueError:
            raise ValueError("X 和 Y 必须为数字")

        if x_first >= 0 or y_first >= 0:
            raise ValueError("X 和 Y 必须为负值（第三象限）")

        # 验证 X/Y 比例是否符合六边形几何
        expected_ratio = -np.sqrt(3)  # X/Y = -√3
        if abs(x_first / y_first - expected_ratio) > 0.01:
            raise ValueError(f"X/Y 比例应为 -√3 ≈ -1.732，当前为 {x_first / y_first:.3f}")

        # 计算边长 s
        s = -y_first / 1.5
        print(f"根据 Y={y_first} 计算边长 s: {s:.3f}")

        # 平移网格，使几何中心位于 (0, 0)
        shifted_points = [(x - geometric_center[0], y - geometric_center[1]) for x, y in points]

        # 计算第一个六边形中心在平移后的位置
        first_hex_center = (-np.sqrt(3) * 1.5 * s, -1.5 * s)  # (i=-1, j=-1)
        print(f"平移后第一个六边形中心（理论）: ({first_hex_center[0]:.3f}, {first_hex_center[1]:.3f})")

        # 调整网格，使第一个六边形中心位于用户指定的 (X, Y)
        dx = x_first - first_hex_center[0]
        dy = y_first - first_hex_center[1]
        final_points = [(x + dx, y + dy) for x, y in shifted_points]
        print(f"额外平移 (dx={dx:.3f}, dy={dy:.3f}) 使第一个六边形中心位于 ({x_first}, {y_first})")

        # 验证中心点是否为 (0, 0)
        new_center = np.mean(final_points, axis=0)
        print(f"调整后几何中心: ({new_center[0]:.3f}, {new_center[1]:.3f})")

        return final_points

    def rotate_points(self, points, center, angle):
        # 以中心点旋转点，角度为弧度
        cos_theta = np.cos(angle)
        sin_theta = np.sin(angle)
        rotated_points = []
        for x, y in points:
            x_rel = x - center[0]
            y_rel = y - center[1]
            x_new = center[0] + x_rel * cos_theta - y_rel * sin_theta
            y_new = center[1] + x_rel * sin_theta + y_rel * cos_theta
            rotated_points.append((round(x_new, 3), round(y_new, 3)))
        return rotated_points

    def process_and_display(self):
        if self.polyline_points is None:
            QMessageBox.warning(self, "错误", "请先加载绿色蜂窝网格文件")
            return

        try:
            # 获取用户输入的 X 和 Y
            x_first = self.x_input.text()
            y_first = self.y_input.text()

            # 平移网格，使中心位于 (0, 0)，第一个六边形中心位于 (X, Y)
            points_np = np.array(self.polyline_points)
            shifted_points = self.shift_to_origin(points_np, x_first, y_first)

            # 中心点固定为 (0, 0)
            center = (0.0, 0.0)
            self.center_label.setText(f"中心点: ({center[0]:.3f}, {center[1]:.3f})")

            # 旋转角度和渲染参数
            rotations = [
                (0, 0.1, (1.0, 0.0, 0.0)),  # 0°, Z=0.1, 红色
                (2 * np.pi / 3, 0.2, (0.0, 1.0, 0.0)),  # 120°, Z=0.2, 绿色
                (4 * np.pi / 3, 0.3, (0.0, 0.0, 1.0))  # 240°, Z=0.3, 蓝色
            ]
            output_files = [
                "green_polyline_rot0.txt",
                "green_polyline_rot120.txt",
                "green_polyline_rot240.txt"
            ]

            layers = []
            for (angle, z, color), output_file in zip(rotations, output_files):
                # 旋转点
                rotated_points = self.rotate_points(shifted_points, center, angle)
                # 保存到文件
                output_path = os.path.join(os.path.dirname(__file__), output_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(str(rotated_points))
                print(f"保存旋转 {angle * 180 / np.pi:.0f}° 网格到: {output_path}")
                # 添加到渲染层
                layers.append((z, rotated_points, color))

            # 设置渲染层
            self.gl_widget.set_layers(layers)

            self.output_label.setText(f"输出文件: {', '.join(output_files)}")
            QMessageBox.information(self, "成功", f"已渲染三层路径并保存文件: {', '.join(output_files)}")

        except Exception as e:
            print(f"处理旋转和渲染出错: {e}")
            QMessageBox.warning(self, "错误", f"处理失败: {e}")

if __name__ == '__main__':
    print("启动 QApplication")
    app = QApplication(sys.argv)
    window = MainWindow()
    print("显示 MainWindow")
    window.show()
    print("进入事件循环")
    sys.exit(app.exec_())