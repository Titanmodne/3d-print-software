import sys
import ast
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from shapely.geometry import Polygon, Point, LineString

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("绿色线过滤器")
        self.resize(600, 400)
        print("MainWindow 初始化")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 控制面板
        self.load_button = QPushButton("加载绿色线文件")
        self.load_button.clicked.connect(self.load_polyline)
        layout.addWidget(self.load_button)

        layout.addStretch()

        # 边框范围（Z=0.100，XYZ 坐标，3 位小数）
        self.boundary_coords = [
            (-13.024, -13.025, 0.100),
            (-13.024, 22.975, 0.100),
            (22.974, 22.975, 0.100),
            (22.974, -13.025, 0.100)
        ]
        self.boundary_z = 0.100
        # 提取 XY 坐标用于 shapely Polygon
        self.boundary_xy = [(x, y) for x, y, z in self.boundary_coords]
        self.boundary_polygon = Polygon(self.boundary_xy)
        # 计算边框中心点
        boundary_points = np.array(self.boundary_xy)
        self.boundary_center = np.mean(boundary_points, axis=0).tolist()  # [x, y]
        print(f"边框中心点: ({self.boundary_center[0]:.3f}, {self.boundary_center[1]:.3f})")

    def showEvent(self, event):
        print("MainWindow 显示")
        super().showEvent(event)

    def load_polyline(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择绿色线文件", "", "文本文件 (*.txt)")
        if file_path:
            try:
                # 读取绿色线文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    points = ast.literal_eval(content)  # 解析为 [(x, y, z), ...]

                # 筛选 Z=0.100 的点（允许小误差）
                points = [(x, y, z) for x, y, z in points if abs(z - self.boundary_z) < 1e-6]
                if not points:
                    raise ValueError("文件中未找到 Z=0.100 的点")

                # 计算绿色线中心点并平移
                green_points_xy = [(x, y) for x, y, z in points]
                green_center = np.mean(green_points_xy, axis=0).tolist()  # [x, y]
                print(f"绿色线中心点: ({green_center[0]:.3f}, {green_center[1]:.3f})")
                dx = self.boundary_center[0] - green_center[0]
                dy = self.boundary_center[1] - green_center[1]
                print(f"平移量: (dx={dx:.3f}, dy={dy:.3f})")
                # 平移绿色线点
                shifted_points = [(x + dx, y + dy, z) for x, y, z in points]

                # 处理绿色线
                filtered_points, entry_exit_points = self.filter_points_in_boundary(shifted_points)

                # 保存结果
                output_file = os.path.join(os.path.dirname(__file__), "filtered_polyline.txt")
                self.save_filtered_polyline(filtered_points, output_file)

                QMessageBox.information(
                    self,
                    "成功",
                    f"绿色线中心: ({green_center[0]:.3f}, {green_center[1]:.3f})\n"
                    f"边框中心: ({self.boundary_center[0]:.3f}, {self.boundary_center[1]:.3f})\n"
                    f"平移量: (dx={dx:.3f}, dy={dy:.3f})\n"
                    f"已处理 {len(filtered_points)} 个点，保存到 {output_file}\n"
                    f"进入/离开点: {entry_exit_points}"
                )
                print(f"过滤点: {len(filtered_points)} 个, 保存到: {output_file}")
                print(f"进入/离开点: {entry_exit_points}")

            except Exception as e:
                print(f"加载或处理文件出错: {e}")
                QMessageBox.warning(self, "错误", f"无法处理绿色线文件: {e}")

    def filter_points_in_boundary(self, points):
        filtered_points = []
        entry_exit_points = []

        # 检查每个点是否在边框内
        for i in range(len(points)):
            x, y, z = points[i]
            point = Point(x, y)
            if self.boundary_polygon.contains(point) or self.boundary_polygon.touches(point):
                filtered_points.append((round(x, 3), round(y, 3), 0.100))

        # 查找线段与边框的交点
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            line = LineString([(p1[0], p1[1]), (p2[0], p2[1])])
            if line.intersects(self.boundary_polygon):
                intersection = line.intersection(self.boundary_polygon)
                if intersection.geom_type == 'Point':
                    x, y = intersection.x, intersection.y
                    z = 0.100
                    filtered_points.append((round(x, 3), round(y, 3), z))
                elif intersection.geom_type == 'MultiPoint':
                    for pt in intersection.geoms:
                        x, y = pt.x, pt.y
                        z = 0.100
                        filtered_points.append((round(x, 3), round(y, 3), z))

        # 按线段顺序重新连接
        connected_points = []
        current_segment = []
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            line = LineString([(p1[0], p1[1]), (p2[0], p2[1])])
            p1_inside = self.boundary_polygon.contains(Point(p1[0], p1[1])) or self.boundary_polygon.touches(Point(p1[0], p1[1]))
            p2_inside = self.boundary_polygon.contains(Point(p2[0], p2[1])) or self.boundary_polygon.touches(Point(p2[0], p2[1]))

            if p1_inside:
                current_segment.append((round(p1[0], 3), round(p1[1], 3), 0.100))
            if line.intersects(self.boundary_polygon):
                intersection = line.intersection(self.boundary_polygon)
                if intersection.geom_type == 'Point':
                    x, y = intersection.x, intersection.y
                    z = 0.100
                    intersection_point = (round(x, 3), round(y, 3), z)
                    if not p1_inside:
                        current_segment.append(intersection_point)
                        entry_exit_points.append(('entry', intersection_point))
                    elif not p2_inside:
                        current_segment.append(intersection_point)
                        entry_exit_points.append(('exit', intersection_point))
                elif intersection.geom_type == 'MultiPoint':
                    for pt in intersection.geoms:
                        x, y = pt.x, pt.y
                        z = 0.100
                        intersection_point = (round(x, 3), round(y, 3), z)
                        if not p1_inside:
                            current_segment.append(intersection_point)
                            entry_exit_points.append(('entry', intersection_point))
                        elif not p2_inside:
                            current_segment.append(intersection_point)
                            entry_exit_points.append(('exit', intersection_point))

            if p2_inside:
                current_segment.append((round(p2[0], 3), round(p2[1], 3), 0.100))
            elif current_segment:
                connected_points.extend(current_segment)
                current_segment = []

        if current_segment:
            connected_points.extend(current_segment)

        return connected_points, entry_exit_points

    def save_filtered_polyline(self, points, output_file):
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('[')
                for i, (x, y, z) in enumerate(points):
                    f.write(f'({x:.3f}, {y:.3f}, {z:.3f})')
                    if i < len(points) - 1:
                        f.write(', ')
                f.write(']')
            print(f"已保存过滤后的轮廓到: {output_file}")
        except Exception as e:
            print(f"保存文件出错: {e}")
            raise

if __name__ == '__main__':
    print("启动 QApplication")
    app = QApplication(sys.argv)
    window = MainWindow()
    print("显示 MainWindow")
    window.show()
    print("进入事件循环")
    sys.exit(app.exec_())