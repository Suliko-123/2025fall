import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from itertools import permutations

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False 

# 1. 优化后的精确解算法：复杂度 O((n-1)! / 2)
def solve_exact_optimized(matrix):
    n = len(matrix)
    if n < 3: return list(range(1, n + 1)) + [1], 0
    
    nodes_to_permute = list(range(1, n)) # 排除起点 0
    best_path = None
    min_dist = float('inf')
    
    # 遍历排列
    for p in permutations(nodes_to_permute):
        # 核心优化：只保留顺时针，消除逆时针重复
        # 约束条件：路径中第一个移动到的点 p[0] 必须小于 最后一个点 p[-1]
        if p[0] < p[-1]:
            path_indices = [0] + list(p) + [0]
            dist = sum(matrix[path_indices[i]][path_indices[i+1]] for i in range(n))
            if dist < min_dist:
                min_dist = dist
                best_path = [idx + 1 for idx in path_indices] # 转为1-based
                
    return best_path, min_dist

# 2. 近似解算法：最近邻 (O(n^2))
def solve_approximate(matrix):
    n = len(matrix)
    path = [0]
    unvisited = set(range(1, n))
    curr = 0
    while unvisited:
        next_node = min(unvisited, key=lambda x: matrix[curr][x])
        path.append(next_node)
        unvisited.remove(next_node)
        curr = next_node
    path.append(0)
    dist = sum(matrix[path[i]][path[i+1]] for i in range(n))
    return [idx + 1 for idx in path], dist

# 3. 绘图函数：显示所有边权并以 1 为起点
def draw_tsp_complete(matrix, path, dist, title):
    n = len(matrix)
    G = nx.Graph()
    for i in range(n):
        for j in range(i + 1, n):
            G.add_edge(i + 1, j + 1, weight=matrix[i][j])
    
    pos = nx.circular_layout(G)
    plt.figure(figsize=(10, 8))
    
    # 绘制背景：所有边及其权重
    nx.draw_networkx_edges(G, pos, alpha=0.1, edge_color='gray', style='--')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color='gray')
    
    # 绘制巡检路径
    DG = nx.DiGraph()
    path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
    DG.add_edges_from(path_edges)
    nx.draw_networkx_edges(DG, pos, edgelist=path_edges, width=3, edge_color='red', 
                           arrowstyle='->', arrowsize=20, connectionstyle='arc3,rad=0.1')
    
    # 绘制节点
    node_colors = ['#2ecc71' if node == 1 else '#3498db' for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color=node_colors, edgecolors='white')
    nx.draw_networkx_labels(G, pos, font_size=12, font_color='white', font_weight='bold')
    
    plt.title(f"{title}\n路径: {'->'.join(map(str, path))}\n总长: {dist}", fontsize=13)
    plt.axis('off')
    plt.show()

# --- 实验数据 (来自用户图片) ---
A1 = [[0, 2, 3, 5], [2, 0, 1, 4], [3, 1, 0, 3], [5, 4, 3, 0]]
A2 = [[0, 3, 5, 8, 10, 13, 15], [3, 0, 2, 5, 7, 10, 12], [5, 2, 0, 3, 5, 8, 10], 
      [8, 5, 3, 0, 2, 5, 7], [10, 7, 5, 2, 0, 3, 5], [13, 10, 8, 5, 3, 0, 2], [15, 12, 10, 7, 5, 2, 0]]

# 执行实验
p1, d1 = solve_exact_optimized(A1)
print(f"A1 精确解 (优化后): {p1}, 距离: {d1}")
draw_tsp_complete(A1, p1, d1, "实验 A1: 优化后的精确解 (n=4)")

p2, d2 = solve_approximate(A2)
print(f"A2 近似解: {p2}, 距离: {d2}")
draw_tsp_complete(A2, p2, d2, "实验 A2: 近似解 (n=7)")