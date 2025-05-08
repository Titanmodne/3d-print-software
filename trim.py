from shapely.geometry import LineString, Polygon
import numpy as np
import sys
import ast
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog, \
    QMessageBox, QOpenGLWidget
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def find_internal_intersections(line_points, polygon_points):
    line = LineString(line_points)
    polygon = Polygon(polygon_points)
    intersection = line.intersection(polygon)
    if not intersection.is_empty:
        if intersection.geom_type == 'LineString' and polygon.contains(intersection):
            return intersection
        elif intersection.geom_type == 'MultiLineString':
            internal_segments = [segment for segment in intersection.geoms if polygon.contains(segment)]
            return internal_segments
    return None

def connect_segments(intersection):
    if intersection is None:
        return []
    if isinstance(intersection, LineString):
        return [(round(x, 3), round(y, 3)) for x, y in intersection.coords]

    segments = [list(segment.coords) for segment in intersection]
    if not segments:
        return []

    connected_points = segments[0]
    for i in range(1, len(segments)):
        next_segment = segments[i]
        last_point = connected_points[-1]
        first_point = next_segment[0]
        dist = np.linalg.norm(np.array(last_point) - np.array(first_point))
        if dist < 1e-3:
            connected_points.extend(next_segment[1:])
        else:
            connected_points.extend(next_segment)

    cleaned_points = [connected_points[0]]
    for i in range(1, len(connected_points)):
        if connected_points[i] != connected_points[i - 1]:
            cleaned_points.append(connected_points[i])

    return [(round(x, 3), round(y, 3)) for x, y in cleaned_points]

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.setMinimumSize(800, 600)
        self.layers = []  # [(z, path_points, boundary_points), ...]
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

        for z, path_points, boundary_points in self.layers:
            # 绘制多边形（蓝色）
            glColor3f(0, 0, 1)
            print(f"渲染多边形 z={z:.3f}: {len(boundary_points)} 个点")
            glBegin(GL_LINE_LOOP)
            for x, y in boundary_points:
                glVertex3f(float(x), float(y), float(z))
            glEnd()

            # 绘制折线（绿色）
            glColor3f(0, 1, 0)
            print(f"渲染折线 z={z:.3f}: {len(path_points)} 个点")
            glBegin(GL_LINE_STRIP)
            for x, y in path_points:
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
        for z, path_points, boundary_points in layers:
            all_points.extend(path_points + boundary_points)
            all_z.append(z)
        if all_points:
            points_np = np.array(all_points)
            self.bounds = np.array([points_np.min(axis=0), points_np.max(axis=0)])
            self.z_range = [min(all_z), max(all_z)] if all_z else [0.1, 0.1]
        else:
            self.bounds = None
            self.z_range = None
        print(f"设置层: {len(layers)} 层, 边界={self.bounds}, Z范围={self.z_range}")
        self.repaint()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("多层折线与多边形交点查看器")
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

        self.load_polyline_button = QPushButton("加载绿色折线文件")
        self.load_polyline_button.clicked.connect(self.load_polyline)
        control_layout.addWidget(self.load_polyline_button)

        self.load_contours_button = QPushButton("加载轮廓文件")
        self.load_contours_button.clicked.connect(self.load_contours)
        control_layout.addWidget(self.load_contours_button)

        self.process_button = QPushButton("处理并显示交点")
        self.process_button.clicked.connect(self.process_and_display)
        control_layout.addWidget(self.process_button)

        control_layout.addStretch()

        glutInit()
        print("GLUT 初始化完成")

        self.line_points = None
        self.contours = None
        self.stl_center = None

    def showEvent(self, event):
        print("MainWindow 显示")
        super().showEvent(event)

    def load_polyline(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择绿色折线文件", "", "文本文件 (*.txt)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    self.line_points = ast.literal_eval(content)
                print(f"加载绿色折线点: {len(self.line_points)} 个")
                QMessageBox.information(self, "成功", f"已加载绿色折线文件: {file_path}, {len(self.line_points)} 个点")
            except Exception as e:
                print(f"加载绿色折线文件出错: {e}")
                QMessageBox.warning(self, "错误", f"无法加载绿色折线文件: {e}")

    def load_contours(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择轮廓文件", "", "文本文件 (*.txt)")
        if file_path:
            try:
                self.contours = []
                self.stl_center = None
                current_section = None
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line == "Offset Contours:":
                            current_section = "offset"
                            continue
                        if line == "Original Contours:":
                            current_section = "original"
                            continue
                        if not line:
                            continue
                        if line.startswith('Center Point:'):
                            try:
                                center_str = line.split(':', 1)[1].strip()
                                center_xy = ast.literal_eval(center_str)
                                self.stl_center = (float(center_xy[0]), float(center_xy[1]))
                                print(f"加载 STL 模型中心点: {self.stl_center}")
                            except Exception as e:
                                print(f"解析中心点出错: {e}")
                            continue
                        if not line.startswith('z=') or current_section != "offset":
                            continue
                        z_part, coords_part = line.split(':', 1)
                        z = float(z_part.split('=')[1])
                        coords = ast.literal_eval(coords_part.strip())
                        self.contours.append((z, coords))
                if not self.contours:
                    raise ValueError("文件中未找到有效轮廓数据")
                print(f"加载轮廓层: {len(self.contours)} 层")
                self.contours.sort(key=lambda x: x[0])  # 按 Z 升序排序
                if self.stl_center is None:
                    print("警告: 未找到 STL 模型中心点")
                QMessageBox.information(self, "成功", f"已加载轮廓文件: {file_path}, {len(self.contours)} 层")
            except Exception as e:
                print(f"加载轮廓文件出错: {e}")
                QMessageBox.warning(self, "错误", f"无法加载轮廓文件: {e}")

    def process_and_display(self):
        if self.line_points is None or self.contours is None:
            QMessageBox.warning(self, "错误", "请先加载绿色折线文件和轮廓文件")
            return
        if self.stl_center is None:
            QMessageBox.warning(self, "错误", "轮廓文件中未找到 STL 模型中心点")
            return

        try:
            # 计算绿色折线中心点
            line_points_np = np.array(self.line_points)
            line_center = np.mean(line_points_np, axis=0)
            print(f"绿色折线中心点: ({line_center[0]:.3f}, {line_center[1]:.3f})")

            layers = []
            output_lines = []
            total_points = 0
            for z, boundary_points in self.contours:
                # 使用 STL 模型中心点
                stl_center = np.array(self.stl_center)
                print(f"STL 模型中心点 z={z:.3f}: ({stl_center[0]:.3f}, {stl_center[1]:.3f})")

                # 平移折线，使其中心与 STL 模型中心对齐
                dx = stl_center[0] - line_center[0]
                dy = stl_center[1] - line_center[1]
                print(f"平移量 z={z:.3f}: (dx={dx:.3f}, dy={dy:.3f})")
                shifted_points = [(round(x + dx, 3), round(y + dy, 3)) for x, y in self.line_points]

                # 计算交点
                intersection = find_internal_intersections(shifted_points, boundary_points)

                # 连接线段
                connected_points = connect_segments(intersection)

                # 添加到输出
                output_lines.append(f"T1")
                # 输出轮廓点并强制闭合
                for x, y in boundary_points:
                    output_lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f}")
                # 添加第一个点以闭合路径
                if boundary_points:
                    x, y = boundary_points[0]
                    output_lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f}")
                # 输出绿色折线点
                output_lines.append("")
                if connected_points:
                    output_lines.append(f"T2")
                    for x, y in connected_points:
                        output_lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f}")
                    total_points += len(connected_points)
                output_lines.append("")
                print(f"z={z:.3f}: 轮廓点 {len(boundary_points)} 个, 交点 {len(connected_points)} 个")

                # 添加到渲染层
                layers.append((z, connected_points, boundary_points))

            # 保存单一输出文件
            output_file = os.path.join(os.path.dirname(__file__), "connected_polyline_all.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines))
            print(f"总交点: {total_points} 个, 保存到: {output_file}")

            # 显示结果
            self.gl_widget.set_layers(layers)

            QMessageBox.information(
                self,
                "成功",
                f"已处理 {len(layers)} 层，总交点 {total_points} 个，保存到 {output_file}"
            )

        except Exception as e:
            print(f"处理交点出错: {e}")
            QMessageBox.warning(self, "错误", f"处理交点失败: {e}")

if __name__ == '__main__':
    print("启动 QApplication")
    app = QApplication(sys.argv)
    window = MainWindow()
    print("显示 MainWindow")
    window.show()
    print("进入事件循环")
    sys.exit(app.exec_())