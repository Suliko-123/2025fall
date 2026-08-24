import numpy as np
import sympy as sp

class GraphAnalyzer:
    def __init__(self, adj_matrix):
        self.adj = np.array(adj_matrix)
        self.n = len(adj_matrix)
        self.k_sym = sp.Symbol('k')

    def get_max_degree(self):
        """计算图的最大度 Δ(G)"""
        return int(max(np.sum(self.adj, axis=1)))

    def is_complete_graph(self):
        """判断是否为完全图 Kn"""
        for i in range(self.n):
            for j in range(self.n):
                if i != j and self.adj[i][j] == 0:
                    return False
        return True

    def is_bipartite(self):
        """判定二部图：使用 BFS 染色，若无奇圈则为二部图"""
        color = [-1] * self.n
        for start_node in range(self.n):
            if color[start_node] == -1:
                color[start_node] = 0
                queue = [start_node]
                while queue:
                    u = queue.pop(0)
                    for v in range(self.n):
                        if self.adj[u][v] == 1:
                            if color[v] == -1:
                                color[v] = 1 - color[u]
                                queue.append(v)
                            elif color[v] == color[u]:
                                return False # 发现奇圈
        return True

    def get_chromatic_polynomial(self, matrix=None):
        """
        根据定理 12.9 递归求解色多项式:
        P(G, k) = P(G - e, k) - P(G · e, k)
        """
        if matrix is None:
            matrix = self.adj.copy()
        
        n = len(matrix)
        # 寻找第一条边
        edge = None
        for i in range(n):
            for j in range(i + 1, n):
                if matrix[i][j] == 1:
                    edge = (i, j)
                    break
            if edge: break
        
        # 基础情况：零图（无边图），色多项式为 k^n
        if edge is None:
            return self.k_sym**n
        
        u, v = edge
        # 1. 计算 P(G - e, k): 删边
        m_minus_e = matrix.copy()
        m_minus_e[u][v] = m_minus_e[v][u] = 0
        p_minus_e = self.get_chromatic_polynomial(m_minus_e)
        
        # 2. 计算 P(G · e, k): 收缩边
        # 将 v 合并到 u
        m_contract_e = matrix.copy()
        for i in range(n):
            if m_contract_e[v][i] == 1:
                m_contract_e[u][i] = m_contract_e[i][u] = 1
        # 删除节点 v
        m_contract_e = np.delete(m_contract_e, v, axis=0)
        m_contract_e = np.delete(m_contract_e, v, axis=1)
        # 消除合并可能产生的自环
        for i in range(len(m_contract_e)):
            m_contract_e[i][i] = 0
            
        p_contract_e = self.get_chromatic_polynomial(m_contract_e)
        
        return sp.expand(p_minus_e - p_contract_e)

    def get_chromatic_number(self):
        """确定点色数 χ(G)"""
        poly = self.get_chromatic_polynomial()
        for k_val in range(1, self.n + 2):
            if poly.subs(self.k_sym, k_val) > 0:
                return k_val
        return self.n

def run_experiment(name, matrix, test_ks):
    print(f"--- 实验分析: {name} ---")
    ga = GraphAnalyzer(matrix)
    
    # 1. 理论界限分析
    delta = ga.get_max_degree()
    is_kn = ga.is_complete_graph()
    is_bip = ga.is_bipartite()
    
    print(f"最大度 Δ(G) = {delta}")
    print(f"上界分析: 根据最大度定理，χ(G) ≤ {delta + 1}")
    if not is_kn:
        print(f"Brooks定理: 该图不是完全图，χ(G) ≤ {delta}")
        
    print(f"下界分析: ", end="")
    if is_bip:
        print("该图是二部图，不含奇圈，下界 χ(G) = 2")
    else:
        print("该图含有奇圈，不是二部图，下界 χ(G) ≥ 3")
    
    # 2. 色多项式与点色数
    poly = ga.get_chromatic_polynomial()
    chi = ga.get_chromatic_number()
    
    print(f"色多项式 P(G, k) = {poly}")
    print(f"点色数 χ(G) = {chi}")
    
    # 3. 实验要求输出
    for k in test_ks:
        ways = poly.subs(ga.k_sym, k)
        res = "能" if ways > 0 else "不能"
        print(f"当 k={k} 时: {res}完成分配, 合法方案数 = {ways}")
    print("\n")

# 测试数据
A1 = [[0,1,1,1,1],[1,0,1,0,0],[1,1,0,1,0],[1,0,1,0,1],[1,0,0,1,0]]
A2 = [[0,1,1,1],[1,0,1,1],[1,1,0,1],[1,1,1,0]]
A3 = [[0,1,0,1,0,0],[1,0,1,0,0,0],[0,1,0,0,0,1],[1,0,0,0,1,0],[0,0,0,1,0,0],[0,0,1,0,0,0]]

if __name__ == "__main__":
    run_experiment("无线基站 A1", A1, [2, 3, 4])
    run_experiment("无线基站 A2", A2, [3, 4])
    run_experiment("无线基站 A3", A3, [2, 3])