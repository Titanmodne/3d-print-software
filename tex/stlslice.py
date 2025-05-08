import sys
import numpy as np
import trimesh
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, \
    QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from shapely.geometry import Polygon
from shapely.ops import unary_union
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("STL轮廓提取器")
        self.resize(600, 400)
        print("MainWindow 初始化")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 控制面板
        self.load_button = QPushButton("加载STL文件")
        self.load_button.clicked.connect(self.load_stl)
        layout.addWidget(self.load_button)

        layout.addWidget(QLabel("层高 (h):"))
        self.layer_height_input = QLineEdit("1.0")
        layout.addWidget(self.layer_height_input)

        layout.addWidget(QLabel("偏置距离 (e):"))
        self.offset_distance_input = QLineEdit("0")
        layout.addWidget(self.offset_distance_input)

        self.apply_button = QPushButton("应用并保存轮廓")
        self.apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_button)

        layout.addStretch()

    def showEvent(self, event):
        print("MainWindow 显示")
        super().showEvent(event)

    def load_stl(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择STL文件", "", "STL文件 (*.stl)")
        if file_path:
            self.stl_path = file_path
            print(f"选择 STL 文件: {file_path}")

    def sort_contour_points(self, coords, z):
        # 将轮廓点排序，选择角度最接近 -135°（X<0, Y<0，-2.356 弧度）的点开始，逆时针
        if not coords or len(coords) < 3:
            print(f"在 z={z:.3f} 处轮廓点不足，无法排序: {coords}")
            return coords

        # 计算所有点的角度，选择最接近 -135° 的点
        target_angle = -2.356  # -135° in radians
        angles = [(abs(np.arctan2(y, x) - target_angle), i) for i, (x, y) in enumerate(coords)]
        min_diff, start_idx = min(angles, key=lambda x: x[0])

        # 重新排序点，从 start_idx 开始
        sorted_coords = coords[start_idx:] + coords[:start_idx]
        # 确保逆时针方向
        poly = Polygon(sorted_coords)
        if not poly.exterior.is_ccw:
            sorted_coords = sorted_coords[::-1]
            print(f"在 z={z:.3f} 处反转轮廓点为逆时针")

        # 确保闭合，添加第一个点
        if sorted_coords[0] != sorted_coords[-1]:
            sorted_coords.append(sorted_coords[0])

        print(f"在 z={z:.3f} 处排序轮廓点，起点: {sorted_coords[0]}, 点数: {len(sorted_coords)}, 角度: {np.arctan2(sorted_coords[0][1], sorted_coords[0][0]):.3f} 弧度")
        return sorted_coords

    def load_and_slice_stl(self, stl_path, layer_height, offset_distance):
        try:
            mesh = trimesh.load(stl_path, force='mesh')
            if not mesh.is_watertight:
                print("警告: STL网格非水密，尝试修复...")
                mesh.fill_holes()
                mesh.merge_vertices()
                mesh.fix_normals()
                if not mesh.is_watertight:
                    print("修复后仍非水密，处理可能不稳定。")
                else:
                    print("修复成功，STL网格现为水密。")
            else:
                print("STL网格是水密的，切片应生成闭合轮廓。")

            # 计算模型中心点（X, Y）
            bounds = mesh.bounds
            center_xy = [(bounds[0][0] + bounds[1][0]) / 2, (bounds[0][1] + bounds[1][1]) / 2]
            print(f"模型中心点 (X, Y): {center_xy}")

            z_min, z_max = mesh.bounds[:, 2]
            z_min += layer_height * 0.1
            z_max -= layer_height * 0.1
            layers = np.arange(z_min, z_max, layer_height)
            contours = []
            offset_contours = []

            for z in layers:
                print(f"处理层 z={z:.3f}")
                section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
                if section is None:
                    print(f"z={z:.3f} 无有效切片")
                    continue

                try:
                    path_2d, _ = section.to_2D()
                except Exception as e:
                    print(f"在z={z:.3f}处转换为2D出错: {e}")
                    continue

                polygons = []
                for entity in path_2d.entities:
                    coords = [(x, y) for x, y in path_2d.vertices[entity.points]]
                    print(f"处理实体 在 z={z:.3f}, 点数={len(coords)}, 坐标={coords}")

                    if len(coords) < 3:
                        print(f"点数不足，无法创建多边形 在 z={z:.3f}")
                        continue

                    try:
                        poly = Polygon(coords)
                        if poly.is_valid:
                            polygons.append(poly)
                            print(f"成功创建多边形 在 z={z:.3f}, 坐标={list(coords)}")
                        else:
                            print(f"在z={z:.3f}处多边形无效，尝试修复")
                            poly = poly.buffer(0)
                            if poly.is_valid:
                                polygons.append(poly)
                                print(f"修复成功，创建多边形 在 z={z:.3f}")
                            else:
                                print(f"在z={z:.3f}处多边形仍无效")
                    except Exception as e:
                        print(f"在z={z:.3f}处创建多边形出错: {e}")
                        continue

                if not polygons:
                    print(f"在z={z:.3f}处无有效多边形")
                    continue

                try:
                    merged = unary_union(polygons)
                except Exception as e:
                    print(f"在z={z:.3f}处合并多边形出错: {e}")
                    continue

                if merged.geom_type == 'Polygon':
                    coords = [(x, y) for x, y in merged.exterior.coords[:-1]]
                    sorted_coords = self.sort_contour_points(coords, z)
                    contours.append((Polygon(sorted_coords), z))
                    try:
                        offset_poly = merged.buffer(-offset_distance, resolution=16)
                        if offset_poly.geom_type == 'Polygon' and not offset_poly.is_empty:
                            offset_coords = [(x, y) for x, y in offset_poly.exterior.coords[:-1]]
                            sorted_offset_coords = self.sort_contour_points(offset_coords, z)
                            offset_contours.append((Polygon(sorted_offset_coords), z))
                        else:
                            print(f"在z={z:.3f}处偏置多边形无效或为空")
                            offset_contours.append((Polygon(sorted_coords), z))  # 回退到原始轮廓
                    except Exception as e:
                        print(f"在z={z:.3f}处偏置多边形出错: {e}")
                        offset_contours.append((Polygon(sorted_coords), z))  # 回退到原始轮廓
                elif merged.geom_type == 'MultiPolygon':
                    # 选择面积最大的多边形，并验证是否包含第三象限点
                    valid_polys = [p for p in merged.geoms if any(x < 0 and y < 0 for x, y in p.exterior.coords)]
                    if not valid_polys:
                        print(f"在 z={z:.3f} 处 MultiPolygon 无第三象限点，尝试最大面积多边形")
                        largest_poly = max(merged.geoms, key=lambda p: p.area)
                    else:
                        largest_poly = max(valid_polys, key=lambda p: p.area)
                    coords = [(x, y) for x, y in largest_poly.exterior.coords[:-1]]
                    sorted_coords = self.sort_contour_points(coords, z)
                    contours.append((Polygon(sorted_coords), z))
                    try:
                        offset_poly = largest_poly.buffer(-offset_distance, resolution=16)
                        if offset_poly.geom_type == 'Polygon' and not offset_poly.is_empty:
                            offset_coords = [(x, y) for x, y in offset_poly.exterior.coords[:-1]]
                            sorted_offset_coords = self.sort_contour_points(offset_coords, z)
                            offset_contours.append((Polygon(sorted_offset_coords), z))
                        else:
                            print(f"在z={z:.3f}处偏置多边形无效或为空")
                            offset_contours.append((Polygon(sorted_coords), z))  # 回退到原始轮廓
                    except Exception as e:
                        print(f"在z={z:.3f}处偏置多边形出错: {e}")
                        offset_contours.append((Polygon(sorted_coords), z))  # 回退到原始轮廓

            print(f"处理完成: {len(contours)} 个原始轮廓, {len(offset_contours)} 个偏置轮廓")
            return contours, offset_contours, center_xy

        except Exception as e:
            print(f"处理STL文件出错: {e}")
            return [], [], None

    def save_contours_to_file(self, contours, offset_contours, center_xy, output_file):
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Original Contours:\n")
                for contour, z in contours:
                    if contour.geom_type == 'Polygon':
                        coords = [(round(x, 3), round(y, 3)) for x, y in contour.exterior.coords]
                        f.write(f"z={z:.3f}: {coords}\n")
                    elif contour.geom_type == 'MultiPolygon':
                        for i, poly in enumerate(contour.geoms):
                            coords = [(round(x, 3), round(y, 3)) for x, y in poly.exterior.coords]
                            f.write(f"z={z:.3f} (MultiPolygon {i + 1}): {coords}\n")

                f.write("\nOffset Contours:\n")
                for contour, z in offset_contours:
                    if contour.geom_type == 'Polygon':
                        coords = [(round(x, 3), round(y, 3)) for x, y in contour.exterior.coords]
                        f.write(f"z={z:.3f}: {coords}\n")
                    elif contour.geom_type == 'MultiPolygon':
                        for i, poly in enumerate(contour.geoms):
                            coords = [(round(x, 3), round(y, 3)) for x, y in poly.exterior.coords]
                            f.write(f"z={z:.3f} (MultiPolygon {i + 1}): {coords}\n")

                # 写入中心点
                if center_xy:
                    f.write(f"\nCenter Point: ({round(center_xy[0], 3)}, {round(center_xy[1], 3)})\n")
                else:
                    f.write("\nCenter Point: Not calculated\n")

            print(f"轮廓和中心点已保存到: {output_file}")
        except Exception as e:
            print(f"保存轮廓到文件出错: {e}")
            QMessageBox.warning(self, "错误", f"无法保存轮廓到文件: {e}")

    def apply_settings(self):
        if hasattr(self, 'stl_path'):
            try:
                layer_height = float(self.layer_height_input.text())
                offset_distance = float(self.offset_distance_input.text())
                if layer_height <= 0 or offset_distance < 0:
                    raise ValueError("层高必须为正数，偏置距离必须为非负数。")

                print("开始处理 STL 文件")
                contours, offset_contours, center_xy = self.load_and_slice_stl(self.stl_path, layer_height, offset_distance)
                if not contours:
                    QMessageBox.warning(self, "错误", "无法处理STL文件或未找到有效轮廓。")
                else:
                    # 保存轮廓和中心点到文件
                    output_file = os.path.join(os.path.dirname(__file__), "contours.txt")
                    self.save_contours_to_file(contours, offset_contours, center_xy, output_file)
                    QMessageBox.information(self, "成功", f"轮廓和中心点已保存到 {output_file}")
            except ValueError as e:
                QMessageBox.warning(self, "无效输入", str(e))
            except Exception as e:
                print(f"应用设置出错: {e}")
                QMessageBox.warning(self, "错误", f"意外错误: {e}")
        else:
            QMessageBox.warning(self, "错误", "请先选择STL文件")


if __name__ == '__main__':
    print("启动 QApplication")
    app = QApplication(sys.argv)
    window = MainWindow()
    print("显示 MainWindow")
    window.show()
    print("进入事件循环")
    sys.exit(app.exec_())