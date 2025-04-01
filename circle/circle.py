# code from Mwen

import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import sys

def fit_line(points):
    """使用最小二乘法拟合直线 y = mx + c"""
    if len(points) < 2:
        return None
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    A = np.vstack([x, np.ones(len(x))]).T  # 构造线性方程
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]  # 最小二乘法拟合 y = mx + c
    return m, c

def get_intersection(line1, line2):
    """
    计算两条直线的交点
    
    参数:
    line1: (m1, c1) 第一条直线的斜率和截距
    line2: (m2, c2) 第二条直线的斜率和截距
    
    返回:
    (x, y) 交点坐标, 若平行返回 None
    """
    m1, c1 = line1
    m2, c2 = line2
    
    # 处理平行的情况（斜率相同）
    if abs(m1 - m2) < 1e-6:
        return None  # 平行，无交点
    
    # 计算交点
    x = (c2 - c1) / (m1 - m2)
    y = m1 * x + c1
    return (int(x), int(y))  # 返回整数坐标

def get_color_at_point(image, point):
    """获取图像中某个点的颜色"""
    x, y = point

    # 转换为 HSV 色彩空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 获取点的 HSV 值
    h, s, v = hsv[y, x]

    # 颜色范围（针对红色和紫色）
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    lower_purple = np.array([110, 50, 50])  # 紫色范围: 110° ~ 160°
    upper_purple = np.array([160, 255, 255])

    # 判断是否为红色范围
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = mask_red1 | mask_red2

    # 判断是否为紫色范围
    mask_purple = cv2.inRange(hsv, lower_purple, upper_purple)

    # 判断颜色并返回
    if mask_red[y, x] > 0:
        return (0, 0, 255)  # 红色
    elif mask_purple[y, x] > 0:
        return (128, 0, 128)  # 紫色
    else:
        return (255, 255, 255)  # 白色（如果不符合红/紫）

if __name__ == "__main__":
    # 读取图像
    image = cv2.imread(sys.argv[1])
    output = image.copy()

    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    # 使用 HoughCircles 进行圆检测
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                            param1=50, param2=30, minRadius=10, maxRadius=30)

    detected_centers = []  # 存储圆心坐标
    radii = []  # 存储圆半径
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            detected_centers.append(center)
            #cv2.circle(output, center, i[2], (0, 255, 0), 2)  # 画出圆圈
            #cv2.circle(output, center, 2, (0, 0, 255), 3)  # 画出圆心
            radii.append(i[2])
    radii_aavg = np.mean(radii)

    if detected_centers:
        detected_centers = np.array(detected_centers)

        # 获取全局最小/最大值
        x_min = min(detected_centers[:, 0])-10
        x_max = max(detected_centers[:, 0])+10
        y_min = min(detected_centers[:, 1])-10
        y_max = max(detected_centers[:, 1])+10

        # 使用 KMeans 聚类
        kmeans_y = KMeans(n_clusters=8, n_init='auto', random_state=42).fit(detected_centers[:, 1].reshape(-1, 1))
        row_labels = kmeans_y.labels_

        kmeans_x = KMeans(n_clusters=12, n_init='auto', random_state=42).fit(detected_centers[:, 0].reshape(-1, 1))
        col_labels = kmeans_x.labels_

        # 组织分组数据
        rows = [[] for _ in range(8)]
        cols = [[] for _ in range(12)]
        
        for i, center in enumerate(detected_centers):
            rows[row_labels[i]].append(center)
            cols[col_labels[i]].append(center)

    

        # 拟合 8 条横向直线（蓝色）
        for row in rows:
            if len(row) > 1:
                m, c = fit_line(row)
                y_start = int(m * x_min + c)
                y_end = int(m * x_max + c)
                cv2.line(output, (x_min, y_start), (x_max, y_end), (255, 0, 0), 2)  # 画出蓝色横线

        # 拟合 12 条纵向直线（黄色）
        for col in cols:
            if len(col) > 1:
                m, c = fit_line([(p[1], p[0]) for p in col])  # 交换 x, y 拟合 x = my + c
                x_start = int(m * y_min + c)
                x_end = int(m * y_max + c)
                cv2.line(output, (x_start, y_min), (x_end, y_max), (0, 255, 255), 2)  # 画出黄色纵线

        h_mc = []
        v_mc = []
        for row in rows:
            if len(row) > 1:  # 确保至少有两个点
                m, c = fit_line(row)
                h_mc.append((m, c))
        for col in cols:
            if len(col) > 1:
                m, c = fit_line(col)
                v_mc.append((m, c))
        intersection = []
        for hmc in h_mc:
            for vmc in v_mc:
                intersection.append(get_intersection(hmc, vmc))
        for i in intersection:
            rgb = get_color_at_point(image, i)
            cv2.circle(output, i, int(radii_aavg), rgb, 2)  # 画出圆圈
            cv2.circle(output, i, 2, (255, 255, 255), 3)  # 画出圆心

    # 显示结果
    plt.figure(figsize=(10, 6))
    plt.imshow(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))
    plt.title("Hough circle detection and grid fitting")
    plt.axis("off")
    plt.show()