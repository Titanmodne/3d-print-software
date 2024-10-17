import re
import tkinter as tk
from tkinter import filedialog, simpledialog
import math

def extract_coordinates(input_file):
    coordinates = []
    original_lines = []

    with open(input_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = re.findall(r'X: ([+-]?\d*\.?\d+), Y: ([+-]?\d*\.?\d+), Z: ([+-]?\d*\.?\d+)', line)
                if parts:
                    x, y, z = map(float, parts[0])
                    coordinates.append((x, y, z))
                    original_lines.append(line)

    return coordinates, original_lines

def calculate_distances(coordinates, original_lines, c, f):
    output_lines = []
    previous_z = None
    accumulated_j = 0  # 初始化累加的J值
    line_count_after_empty = 0  # 记录每个空行后的行数

    for i in range(len(coordinates)):
        x, y, z = coordinates[i]
        modified_line = original_lines[i].replace("G0", "G1")

        # Calculate distance if not the first entry
        if i > 0:
            x1, y1, z1 = coordinates[i - 1]
            j = math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
            j_c = j * c
            if z != previous_z:  # Check for Z value changes
                if line_count_after_empty < 4:
                    # Remove the last few lines if line count after the last empty line is less than 4
                    output_lines = output_lines[:-line_count_after_empty]
                output_lines.append("")  # Add an empty line before the line with new Z
                accumulated_j = 0  # Reset J value for the new Z
                line_count_after_empty = 0  # Reset line count after empty line
            accumulated_j += j_c  # Accumulate J value
            modified_line = f"{modified_line} J: {accumulated_j:.2f} F: {f}"
        else:
            modified_line = f"{modified_line} J: {accumulated_j:.2f} F: 100"

        output_lines.append(modified_line)
        previous_z = z  # Update the previous Z value for the next iteration
        line_count_after_empty += 1  # Increment line count after empty line

    # Remove the last few lines if line count after the last empty line is less than 4
    if line_count_after_empty < 4:
        output_lines = output_lines[:-line_count_after_empty]

    return output_lines

def main():
    root = tk.Tk()
    root.withdraw()

    k = simpledialog.askfloat("Input Parameter K", "Please enter the multiplier K:", minvalue=0.0)
    if k is None:
        print("No K parameter entered.")
        return

    f = simpledialog.askfloat("Input Parameter F", "Please enter the value for F:", minvalue=0.0)
    if f is None:
        print("No F parameter entered.")
        return

    input_file_path = filedialog.askopenfilename(title='Select Input File', filetypes=[('Text Files', '*.txt')])
    if not input_file_path:
        print("No input file selected.")
        return

    coordinates, original_lines = extract_coordinates(input_file_path)
    if not coordinates:
        print("No coordinates extracted.")
        return

    output_lines = calculate_distances(coordinates, original_lines, k, f)

    output_file_path = filedialog.asksaveasfilename(defaultextension='.txt', title='Save Output File',
                                                    filetypes=[('Text Files', '*.txt')])
    if not output_file_path:
        print("No output file selected.")
        return

    with open(output_file_path, 'w') as file:
        # Write the processed output lines
        for line in output_lines:
            file.write(line + "\n")

    print(f"Processed data saved to {output_file_path}")

if __name__ == "__main__":
    main()