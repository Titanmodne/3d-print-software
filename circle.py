import sys
import numpy as np
import ast
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QMessageBox
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("绿色蜂窝网格旋转器")
        self.resize(600, 400)
        print("MainWindow 初始化")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 控制面板
        self.load_button = QPushButton("加载绿色蜂窝网格文件")
        self.load_button.clicked.connect(self.load_polyline)
        layout.addWidget(self.load_button)

        self.input_label = QLabel("输入文件: 未选择")
        layout.addWidget(self.input_label)

        self.center_label = QLabel("中心点: 未计算")
        layout.addWidget(self.center_label)

        self.process_button = QPushButton("旋转并保存")
        self.process_button.clicked.connect(self.process_and_save)
        layout.addWidget(self.process_button)

        self.output_label = QLabel("输出文件: 未生成")
        layout.addWidget(self.output_label)

        layout.addStretch()

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
                # 计算中心点
                center = np.mean(points_np, axis=0)
                self.center_label.setText(f"中心点: ({center[0]:.3f}, {center[1]:.3f})")
                QMessageBox.information(self, "成功", f"已加载绿色蜂窝网格文件: {file_path}, {len(self.polyline_points)} 个点")
            except Exception as e:
                print(f"加载绿色蜂窝网格文件出错: {e}")
                QMessageBox.warning(self, "错误", f"无法加载绿色蜂窝网格文件: {e}")
                self.polyline_points = None
                self.input_label.setText("输入文件: 未选择")
                self.center_label.setText("中心点: 未计算")

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

    def process_and_save(self):
        if self.polyline_points is None:
            QMessageBox.warning(self, "错误", "请先加载绿色蜂窝网格文件")
            return

        try:
            # 计算中心点
            points_np = np.array(self.polyline_points)
            center = np.mean(points_np, axis=0)
            print(f"绿色蜂窝网格中心点: ({center[0]:.3f}, {center[1]:.3f})")

            # 旋转角度（弧度）
            angles = [0, 2 * np.pi / 3, 4 * np.pi / 3]  # 0°, 120°, 240°
            output_files = [
                "green_polyline_rot0.txt",
                "green_polyline_rot120.txt",
                "green_polyline_rot240.txt"
            ]

            for angle, output_file in zip(angles, output_files):
                # 旋转点
                rotated_points = self.rotate_points(self.polyline_points, center, angle)
                # 保存到文件
                output_path = os.path.join(os.path.dirname(__file__), output_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(str(rotated_points))
                print(f"保存旋转 {angle * 180 / np.pi:.0f}° 网格到: {output_path}")

            self.output_label.setText(f"输出文件: {', '.join(output_files)}")
            QMessageBox.information(self, "成功", f"已生成旋转网格文件: {', '.join(output_files)}")

        except Exception as e:
            print(f"处理旋转出错: {e}")
            QMessageBox.warning(self, "错误", f"处理旋转失败: {e}")

if __name__ == '__main__':
    print("启动 QApplication")
    app = QApplication(sys.argv)
    window = MainWindow()
    print("显示 MainWindow")
    window.show()
    print("进入事件循环")
    sys.exit(app.exec_())