import sys
import numpy as np
import re
import os
import pandas as pd

Gfile = input('输入需转换的Gcode文件名：')

# *********读取切片软件生成的Gcode文件，

jt = 8279/100
et = 12300/100

with open(Gfile,"r") as f:
    data = f.readlines()
n = len(data)


# *********并将其中两个喷嘴的路径，剪断指令，和纯材料喷嘴的升降指令，保存到一个数组中。
# *********其中纯材料喷嘴上升指令为1，预浸丝剪断指令为2，纯材料喷嘴下降指令为3。

 #定义一个初始m行，7列的二维数组，m表示m个点。
m = 0
for i in range(n):
    data1 = data[i]
    if "G1" in data1:
       m = m + 1
print(m)
arr = [[0 for j in range(7)] for i in range(m)]           # m行7列。

# 定义初始值
x_value = 0
y_value = 0
z_value = 0       #第一个点的高度。
e_value = 0       #
exp  = 0            #绝对值
j_value = 0       #相对前一个的差值
jxp = 0             #绝对值
f_value = 0



# 正则表达式提取数据，
pax = r"X(\d+\.\d+|\d+|\-\d+\.\d+|\-\d+)"
pay = r"Y(\d+\.\d+|\d+|\-\d+\.\d+|\-\d+)"
paz = r"Z(\d+\.\d+|\d+|\-\d+\.\d+|\-\d+)"
pae = r"E(\d+\.\d+|\d+|\-\d+\.\d+|\-\d+)"
paj = r"J(\d+\.\d+|\d+|\-\d+\.\d+|\-\d+)"
paf = r"F(\d+\.\d+|\d+|\-\d+\.\d+|\-\d+)"



# n = 14

p = 0 #第p个点

for i in range(1,n):
    data2 = data[i]
    if "G92" in data2:
        e_value = 0
        j_value = 0

    if "G1" in data2:
        p = p + 1
        x = re.search(pax,data2)
        if x:
            x_value = float(x.group(1))
        arr[p-1][0] = x_value
        y = re.search(pay,data2)
        if y:
            y_value = float(y.group(1))
        arr[p-1][1] = y_value
        z = re.search(paz,data2)
        if z:
            z_value = float(z.group(1))
        arr[p-1][2] = z_value
        e = re.search(pae,data2)
        if e:
            ex = e_value
            e_value = float(e.group(1))
            exp = e_value - ex + exp
        arr[p-1][3] = int(exp*et)
        j = re.search(paj,data2)
        if j:
            jx = j_value
            j_value = float(j.group(1))
            jxp = j_value - jx + jxp
        arr[p-1][4] = int(jxp*jt)
        f = re.search(paf,data2)
        if f:
            f_value = float(f.group(1))
        arr[p-1][5] = f_value/60
    if "M280 P0 S95" in data2:
        arr[p-1][6] = 3
    if "M280 P0 S2" in data2:
        arr[p-1][6] = 1
    if "cut" in data2:
        arr[p-1][6] = 2

v = arr[1][5]
# print(arr)

# 写入多行
with open("array.txt", "w") as f:
    # 遍历数组的每一行
    for row in arr:
        # 将每一行转换成字符串，用制表符分隔各个元素
        row_str = "\t".join(str(x) for x in row)
        # 将每一行字符串写入文件，并加上换行符
        f.write(row_str + "\n")



