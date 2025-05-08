import ast
import numpy as np
import os

def sort_contour_points(coords, z):
    # 将轮廓点排序，从第三象限 45 度角（X<0, Y<0，角度 -135°）开始，逆时针
    if not coords or len(coords) < 3:
        print(f"在 z={z:.3f} 处轮廓点不足，无法排序: {coords}")
        return coords

    # 转换为浮点数
    coords = [(float(x), float(y)) for x, y in coords]

    # 严格选择 X<0, Y<0 的点
    third_quadrant_points = [(i, x, y) for i, (x, y) in enumerate(coords) if x < 0 and y < 0]
    if not third_quadrant_points:
        print(f"在 z={z:.3f} 处无第三象限点（X<0, Y<0）: {coords}")
        raise ValueError(f"在 z={z:.3f} 处无第三象限点，无法排序")

    # 选择角度最接近 -135° 的点
    angles = [np.arctan2(y, x) for _, x, y in third_quadrant_points]
    target_angle = -2.356  # -135° in radians
    angle_diffs = [(abs(angle - target_angle), i) for i, angle in enumerate(angles)]
    min_diff, min_idx = min(angle_diffs, key=lambda x: x[0])
    start_idx = third_quadrant_points[min_idx][0]

    # 重新排序点，从 start_idx 开始
    sorted_coords = coords[start_idx:] + coords[:start_idx]

    # 确保逆时针方向（基于角度排序）
    center = np.mean(sorted_coords[:-1], axis=0)  # 计算中心点，排除闭合点
    sorted_coords[:-1] = sorted(
        sorted_coords[:-1],
        key=lambda p: np.arctan2(p[1] - center[1], p[0] - center[0])
    )

    # 确保闭合，添加第一个点
    if sorted_coords[0] != sorted_coords[-1]:
        sorted_coords.append(sorted_coords[0])

    # 验证点序唯一性
    unique_coords = list(dict.fromkeys([(x, y) for x, y in sorted_coords]))
    if len(unique_coords) < len(sorted_coords):
        print(f"在 z={z:.3f} 处检测到重复点，清理后: {unique_coords}")
        sorted_coords = unique_coords + [unique_coords[0]] if unique_coords[0] != unique_coords[-1] else unique_coords

    print(f"在 z={z:.3f} 处排序轮廓点，起点: {sorted_coords[0]}, 点数: {len(sorted_coords)}, 角度: {np.arctan2(sorted_coords[0][1], sorted_coords[0][0]):.3f} 弧度")
    return sorted_coords

def reorder_offset_contours(input_file, output_file):
    try:
        # 读取 contours.txt
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        original_contours = []
        offset_contours = []
        current_section = None

        # 解析 Original Contours 和 Offset Contours
        for line in lines:
            line = line.strip()
            if line == "Original Contours:":
                current_section = "original"
                continue
            if line == "Offset Contours:":
                current_section = "offset"
                continue
            if not line or current_section is None or not line.startswith('z='):
                continue
            z_part, coords_part = line.split(':', 1)
            z = float(z_part.split('=')[1])
            coords = ast.literal_eval(coords_part.strip())
            if current_section == "original":
                original_contours.append((z, coords))
            elif current_section == "offset":
                offset_contours.append((z, coords))

        print(f"读取 contours.txt: {len(original_contours)} 个原始轮廓, {len(offset_contours)} 个偏置轮廓")

        # 重新排序 Offset Contours
        reordered_offset_contours = []
        for z, coords in offset_contours:
            try:
                sorted_coords = sort_contour_points(coords, z)
                reordered_offset_contours.append((z, sorted_coords))
            except ValueError as e:
                print(f"在 z={z:.3f} 处排序失败: {e}")
                reordered_offset_contours.append((z, coords))  # 保留原始点序

        # 保存新的 contours.txt
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Original Contours:\n")
            for z, coords in original_contours:
                f.write(f"z={z:.3f}: {coords}\n")

            f.write("\nOffset Contours:\n")
            for z, coords in reordered_offset_contours:
                f.write(f"z={z:.3f}: {coords}\n")

        print(f"新的 contours.txt 已保存到: {output_file}")
        return True

    except Exception as e:
        print(f"处理 contours.txt 出错: {e}")
        return False

if __name__ == "__main__":
    input_file = "contours.txt"
    output_file = "contours_reordered.txt"
    if not os.path.exists(input_file):
        print(f"输入文件 {input_file} 不存在")
        sys.exit(1)

    success = reorder_offset_contours(input_file, output_file)
    if success:
        print("处理完成")
    else:
        print("处理失败")
        sys.exit(1)