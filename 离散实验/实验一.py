import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# ==========================================
# 核心功能函数实现
# ==========================================

def get_adjacency_from_incidence(inc_matrix):
    """
    功能：根据关联矩阵，输出该图的邻接矩阵 A
    """
    rows, cols = inc_matrix.shape
    # 初始化邻接矩阵 (n x n)
    adj_matrix = np.zeros((rows, rows), dtype=int)
    
    # 遍历每一列（每一条边）
    for j in range(cols):
        # 找到该列中非0的行索引（兼容 1 或 -1）
        nodes = np.where(inc_matrix[:, j] != 0)[0]
        
        if len(nodes) == 2:
            # 普通边：连接两个不同顶点 u, v
            u, v = nodes
            adj_matrix[u][v] += 1
            adj_matrix[v][u] += 1
        elif len(nodes) == 1:
            # 自环：连接顶点 u 和 u
            u = nodes[0]
            adj_matrix[u][u] += 1 
            
    return adj_matrix

def analyze_vertex_elements(inc_matrix, adj_matrix):
    """
    功能：输出每个顶点的度数、邻域
    """
    num_nodes = inc_matrix.shape[0]
    print("\n--- 顶点要素分析 (度数与邻域) ---")
    for i in range(num_nodes):
        # 计算度数：统计关联矩阵该行非0元素的个数 (对于简单无向图，通常每条边贡献1度)
        # 注意：如果有自环，在关联矩阵中通常占1列。
        degree = np.sum(np.abs(inc_matrix[i, :]))
        
        # 邻域：邻接矩阵中非0元素的索引
        neighbors = np.where(adj_matrix[i, :] > 0)[0]
        neighbor_labels = [f"v{n+1}" for n in neighbors]
        print(f"顶点 v{i+1}: 度数 = {degree}, 邻域 = {neighbor_labels}")

def check_simple_graph(adj_matrix):
    """
    功能：判断是否为简单图
    条件：无自环 (对角线为0) 且 无多重边 (元素值<=1)
    """
    # 检查自环
    has_loops = np.any(np.diagonal(adj_matrix) > 0)
    # 检查多重边
    has_parallel_edges = np.any(adj_matrix > 1)
    
    is_simple = not (has_loops or has_parallel_edges)
    
    print("\n--- 简单图判断 ---")
    print(f"是否存在自环: {has_loops}")
    print(f"是否存在多重边: {has_parallel_edges}")
    print(f"结论: 该图{'是' if is_simple else '不是'}简单图")
    return is_simple

def analyze_connectivity(adj_matrix):
    """
    功能：判断连通分支数及每个分支包含的顶点
    """
    G = nx.from_numpy_array(adj_matrix)
    components = list(nx.connected_components(G))
    
    print("\n--- 连通性分析 ---")
    print(f"连通分支数量: {len(components)}")
    for idx, comp in enumerate(components):
        # 将索引转换为 v1, v2 标签并排序
        # 使用 key=lambda x: int(x[1:]) 确保 v1, v2, v10 排序正确
        nodes = sorted([f"v{n+1}" for n in comp], key=lambda x: int(x[1:]))
        print(f"分支 {idx+1}: 包含顶点 {nodes}")

def visualize_graph(inc_matrix):
    """
    功能：可视化表示（高级优化版）
    特点：支持多重边弯曲绘制，支持自环显示，优化标签防遮挡
    """
    rows, cols = inc_matrix.shape
    G = nx.MultiGraph() # 使用 MultiGraph 以支持多重边
    
    # 1. 添加节点
    node_labels = {i: f"v{i+1}" for i in range(rows)}
    for i in range(rows):
        G.add_node(i)
    
    # 2. 添加边并记录标签
    # edge_map 结构: key=(u, v, key_index), value=edge_label (e1, e2...)
    edge_map = {} 
    
    for j in range(cols):
        nodes = np.where(inc_matrix[:, j] != 0)[0]
        label = f"e{j+1}"
        
        if len(nodes) == 2:
            u, v = nodes
            key = G.add_edge(u, v) # key用于区分多重边
            edge_map[(u, v, key)] = label
        elif len(nodes) == 1:
            u = nodes[0]
            key = G.add_edge(u, u)
            edge_map[(u, u, key)] = label

    # 3. 开始绘图
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(G, seed=42, k=0.9) # k调整节点间距
    
    # 画节点
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color='#87CEFA', edgecolors='black')
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=12, font_weight='bold')

    # 画边（关键优化：处理多重边的弯曲）
    ax = plt.gca()
    
    # 对边进行分组，判断两点之间有几条边
    edge_groups = {}
    for u, v, k in G.edges(keys=True):
        pair = tuple(sorted((u, v)))
        if pair not in edge_groups:
            edge_groups[pair] = []
        edge_groups[pair].append((u, v, k))
    
    # 遍历每一组边进行绘制
    for pair, edges in edge_groups.items():
        count = len(edges)
        for i, (u, v, k) in enumerate(edges):
            # 计算弧度 rad
            # 如果只有一条边且不是自环，画直线 (rad=0)
            # 如果有多条边，按顺序赋予不同的弧度
            if count == 1 and u != v:
                rad = 0
            else:
                # 自环或多重边需要弯曲
                # 弧度序列示例: 0.1, -0.1, 0.2, -0.2 ...
                if u == v: # 自环
                    rad = 0.2 + i * 0.1 # 自环弧度大一点
                else: 
                    # 多重边，交替正负弧度
                    sign = 1 if i % 2 == 0 else -1
                    rad = 0.15 * (1 + i // 2) * sign
            
            # 绘制边
            # connectionstyle='arc3, rad=...' 用于画曲线
            nx.draw_networkx_edges(
                G, pos, 
                edgelist=[(u, v)], 
                connectionstyle=f'arc3, rad={rad}', 
                width=2, alpha=0.7, edge_color='#555555'
            )
            
            # 绘制边标签 (计算标签位置)
            # 获取节点坐标
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            label_text = edge_map.get((u, v, k), edge_map.get((v, u, k), ""))
            
            # 标签位置估算 (简单的中点 + 弧度偏移)
            if u != v:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                # 根据弧度做一点简单的法向偏移，避免标签都在一条线上
                # 这是一个简单的视觉优化
                offset_x = (y1 - y2) * rad * 0.5
                offset_y = (x2 - x1) * rad * 0.5
                lx, ly = mx + offset_x, my + offset_y
            else:
                # 自环标签位置，放在节点上方
                lx, ly = x1, y1 + 0.1 + (i * 0.05)
            
            # 绘制带白色背景框的标签
            plt.text(
                lx, ly, label_text, 
                size=10, color='red', weight='bold',
                horizontalalignment='center', verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8)
            )

    plt.title("Graph Visualization (Optimized for Multi-edges & Self-loops)", fontsize=15)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# ==========================================
# 主程序入口
# ==========================================

if __name__ == "__main__":
    # ================= 数据定义区域 =================
    # 1. 定义 M1 
    M1 = np.array([
        [1,1,0,0,0,1,0],
        [1,0,1,1,0,0,0],
        [0,1,1,0,1,0,0],
        [0,0,0,1,1,0,1],
        [0,0,0,0,0,1,1] 
    ])

    # 2. 定义 M2 
    M2 = np.array([
        [1,1,0,0,0,0,0],
        [0,1,1,0,1,0,0],
        [0,0,0,1,1,0,0],
        [1,0,1,1,0,0,0],
        [0,0,0,0,0,1,1],
        [0,0,0,0,0,1,0],
        [0,0,0,0,0,0,1]
    ])

    # 3. 定义 M3 
    M3 = np.array([
        [1,1,1,0,0],
        [1,1,0,1,1],
        [0,0,0,1,0],
        [0,0,1,0,1]
    ])

    # 4. 定义 M4 
   
    M4 = np.array([
        [1,1,1,0,0],
        [1,-1,0,1,1],
        [0,1,0,1,0],
        [0,0,1,0,1]
    ])

  
    M_example = M3
  

    # ================= 执行区域 =================
    print(f"--- 当前正在分析矩阵 ---")
    print(M_example)

    # 1. 转换为邻接矩阵
    adj_matrix = get_adjacency_from_incidence(M_example)
    print("\n--- 计算得到的邻接矩阵 A ---")
    print(adj_matrix)

    # 2. 分析度数和邻域
    analyze_vertex_elements(M_example, adj_matrix)

    # 3. 判断简单图
    check_simple_graph(adj_matrix)

    # 4. 连通性判断
    analyze_connectivity(adj_matrix)

    # 5. 可视化
    print("\n正在生成优化后的可视化图像...")
    visualize_graph(M_example)