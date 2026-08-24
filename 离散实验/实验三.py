import itertools

class DisjointSet:
    """并查集：用于判断连通性和环"""
    def __init__(self, n):
        self.parent = list(range(n))
        self.count = n

    def find(self, i):
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j
            self.count -= 1
            return True
        return False

def get_path_nodes(u, target, adj, path, visited):
    """DFS找树中两点间的唯一节点路径序列，用于构建基本回路"""
    visited[u] = True
    path.append(u)
    if u == target:
        return True
    for v in adj[u]:
        if not visited[v]:
            if get_path_nodes(v, target, adj, path, visited):
                return True
    path.pop()
    return False

def get_ordered_cycle_string(edge_set, edge_map):
    """
    核心修改：将无序的边集合转换为按物理路径顺序（顺时针/逆时针）排列的字符串 
    """
    if not edge_set:
        return "Φ"
    
    # 1. 构建该回路的局部邻接表
    local_adj = {}
    for edge_name in edge_set:
        u, v = edge_map[edge_name]
        local_adj.setdefault(u, []).append((v, edge_name))
        local_adj.setdefault(v, []).append((u, edge_name))
    
    # 2. 从回路中的任意一个点出发进行遍历
    start_node = next(iter(local_adj))
    current_node = start_node
    ordered_edges = []
    visited_edges = set()
    
    # 3. 沿着边寻找路径，直到找完集合中所有的边
    while len(ordered_edges) < len(edge_set):
        found_next = False
        for neighbor, ename in local_adj[current_node]:
            if ename not in visited_edges:
                ordered_edges.append(ename)
                visited_edges.add(ename)
                current_node = neighbor
                found_next = True
                break
        if not found_next: break # 防止非连通情况

    return "".join(ordered_edges)

def main():
    # --- 1. 新示例数据：5x5 邻接矩阵 (来自图片) ---
    n = 5
    adj_matrix = [
        [0, 1, 1, 0, 1],
        [1, 0, 1, 0, 0],
        [1, 1, 0, 1, 1],
        [0, 0, 1, 0, 1],
        [1, 0, 1, 1, 0]
    ]

    # --- 2. 边标定 (严格按行由上到下、由左到右)  ---
    all_edges = []
    edge_map = {}      # 用于快速查询：边名 -> (u, v)
    name_lookup = {}   # 用于快速查询：(u, v) -> 边名
    cnt = 1
    for i in range(n):
        for j in range(i + 1, n):
            if adj_matrix[i][j] == 1:
                name = f"e{cnt}"
                all_edges.append({'u': i, 'v': j, 'id': cnt, 'name': name})
                edge_map[name] = (i, j)
                name_lookup[tuple(sorted((i, j)))] = name
                cnt += 1
    
    print("--- 边的标定结果 ---")
    edge_desc = [f"{e['name']}:({e['u']+1},{e['v']+1})" for e in all_edges]
    print(" ".join(edge_desc))

    # --- 3. 求解所有生成树 [cite: 14, 19] ---
    spanning_trees = []
    for subset in itertools.combinations(all_edges, n - 1):
        ds = DisjointSet(n)
        valid_tree = True
        for e in subset:
            if not ds.union(e['u'], e['v']):
                valid_tree = False
                break
        if valid_tree and ds.count == 1:
            spanning_trees.append(subset)

    print("\n--- 输出1：图G的所有生成树及总个数 ---")
    print(f"生成树总个数: {len(spanning_trees)}")
    for i, tree in enumerate(spanning_trees):
        # 生成树内部的边仍按编号排序输出以示整洁
        names = sorted([e['name'] for e in tree], key=lambda x: int(x[1:]))
        print(f"T{i+1}: {{ {', '.join(names)} }}")

    # --- 4. 选取第一棵生成树 T1 及基本回路系统 [cite: 13, 20] ---
    T1 = spanning_trees[0]
    T1_ids = set(e['id'] for e in T1)
    T1_names = set(e['name'] for e in T1)
    
    t1_adj = [[] for _ in range(n)]
    t1_matrix = [[0]*n for _ in range(n)]
    for e in T1:
        t1_adj[e['u']].append(e['v'])
        t1_adj[e['v']].append(e['u'])
        t1_matrix[e['u']][e['v']] = 1
        t1_matrix[e['v']][e['u']] = 1

    print("\n--- 输出2：生成树T1的相邻矩阵 ---")
    for row in t1_matrix:
        print(" ".join(map(str, row)))

    fundamental_cycles = []
    chords = [e for e in all_edges if e['id'] not in T1_ids]
    
    # 求解基本回路并存储为边集合
    for chord in chords:
        path_nodes = []
        visited = [False] * n
        get_path_nodes(chord['u'], chord['v'], t1_adj, path_nodes, visited)
        
        cycle_set = {chord['name']}
        for k in range(len(path_nodes) - 1):
            u, v = path_nodes[k], path_nodes[k+1]
            ename = name_lookup[tuple(sorted((u, v)))]
            cycle_set.add(ename)
        fundamental_cycles.append(cycle_set)

    print("\n--- 输出2(续)：基本回路系统 (按路径顺序) ---")
    # 修改：调用路径排序函数输出
    f_cycles_str = [get_ordered_cycle_string(c, edge_map) for c in fundamental_cycles]
    print(f"{{ {', '.join(f_cycles_str)} }}")

    # --- 5. 环路空间  ---
    print("\n--- 输出3：环路空间 (按路径顺序) ---")
    cycle_space = []
    num_cycles = len(fundamental_cycles)
    for i in range(1 << num_cycles):
        current_xor_sum = set()
        for j in range(num_cycles):
            if (i >> j) & 1:
                current_xor_sum ^= fundamental_cycles[j] # 集合对称差即异或运算
        
        # 修改：即使是合成的环路，也按路径顺序输出
        cycle_space.append(get_ordered_cycle_string(current_xor_sum, edge_map))

    print(f"{{ {', '.join(cycle_space)} }}")

if __name__ == "__main__":
    main()