import networkx as nx
import matplotlib.pyplot as plt
import re

class Node:
    def __init__(self, id, player, actions, branches=None, payoffs=None):
        self.id = id
        self.player = player
        self.actions = actions
        self.branches = branches or {}
        self.payoffs = payoffs  # For leaf nodes, contains (A payoff, B payoff)

class GameTree:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node):
        self.nodes[node.id] = node

    def solve_nash_equilibrium(self):
        """
        使用逆向归纳法求解博弈树中的纳什均衡。
        """
        # 从叶子节点开始逆向归纳
        for node_id in sorted(self.nodes.keys(), reverse=True):  # 假设节点ID为数字，逆序处理
            node = self.nodes[node_id]
            if node.payoffs:
                continue  # 如果是叶子节点，直接跳过
            # 根据后续节点的收益来计算最优选择
            if node.player == 'A':
                # A选择最大化收益
                best_action = max(node.branches, key=lambda action: self.nodes[node.branches[action]].payoffs[0])
                node.best_action = best_action
            elif node.player == 'B':
                # B选择最大化收益
                best_action = max(node.branches, key=lambda action: self.nodes[node.branches[action]].payoffs[1])
                node.best_action = best_action

    def visualize(self):
        """
        可视化博弈树
        """
        G = nx.DiGraph()
        
        for node_id, node in self.nodes.items():
            G.add_node(node.id, label=node.id)
            if node.payoffs:
                G.nodes[node.id]['payoffs'] = node.payoffs

            for action, next_node_id in node.branches.items():
                G.add_edge(node.id, next_node_id, label=action)

        pos = nx.spring_layout(G)
        labels = nx.get_edge_attributes(G, 'label')

        nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", font_size=10)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

        for node_id, node in self.nodes.items():
            if node.payoffs:
                x, y = pos[node_id]
                plt.text(x, y, f"A: {node.payoffs[0]}, B: {node.payoffs[1]}", fontsize=9, ha='center')

        plt.show()
import re

def parse_game_tree_from_file(filename):
    """
    从txt文件读取博弈树，返回一个GameTree对象
    """
    game_tree = GameTree()
    node_map = {}  # 用来存储节点，方便引用
    
    with open(filename, 'r', encoding='utf-8') as f:  # 使用utf-8编码打开文件
        lines = f.readlines()
    
    i = 0  # 用于遍历行的索引
    while i < len(lines):
        line = lines[i].strip()  # 去掉每行的首尾空格
        print(f"Processing line: {line}")  # 调试信息
        
        if line.startswith("节点"):
            node_id = line.split(":")[0].strip()
            player = None
            actions = []
            branches = {}
            payoffs = None
            
            # 获取决策者
            player_line = lines[i + 1].strip()  # 获取决策者这一行
            if "A" in player_line:
                player = "A"
            elif "B" in player_line:
                player = "B"
            
            # 获取行动列表
            actions_line = lines[i + 2].strip()  # 获取行动这一行
            actions = actions_line.split(":")[1].strip().strip("[]").split(", ")  # 解析行动
            
            # 获取后续节点
            branches_line = lines[i + 3].strip()  # 获取后续这一行
            branches = {}
            if "后续" in branches_line:
                j = i + 4
                while j < len(lines) and not lines[j].startswith("终点节点") and lines[j].strip() != "":
                    branch_line = lines[j].strip()
                    if "->" in branch_line:  # 只处理包含 "->" 的分支
                        action, next_node = branch_line.split("->")
                        branches[action.strip()] = next_node.strip()
                    j += 1
                i = j - 1  # 更新索引，跳过已处理的后续节点

            # 创建节点
            node = Node(node_id, player, actions, branches, payoffs)
            game_tree.add_node(node)
            node_map[node_id] = node
        
        if line.startswith("终点节点"):
            node_id = line.split(":")[0].strip()
            try:
                # 获取终点节点的收益
                payoffs_line = lines[i + 1].strip().split(":")
                print(f"Payoff line: {payoffs_line}")  # 调试信息
                if len(payoffs_line) > 1:  # 确保收益格式正确
                    # 使用正则表达式提取数字部分 (x, y)
                    payoffs_values = re.findall(r'\d+', payoffs_line[1])  # 提取所有数字
                    
                    if len(payoffs_values) == 2:
                        a_payoff = int(payoffs_values[0])  # 获取 A 收益的数字
                        b_payoff = int(payoffs_values[1])  # 获取 B 收益的数字
                        payoffs = (a_payoff, b_payoff)
                    else:
                        payoffs = (0, 0)  # 如果没有找到两个数字，设置为默认值
                        print(f"Warning: Invalid payoff data for {node_id}, using default (0, 0).")
                else:
                    payoffs = (0, 0)  # 默认收益为0
            except IndexError:
                payoffs = (0, 0)  # 默认收益为0
                print(f"Warning: Missing or malformed payoff data for {node_id}")
            
            node = Node(node_id, "None", [], None, payoffs)
            game_tree.add_node(node)
            node_map[node_id] = node
        
        i += 1  # 移动到下一行
    
    return game_tree


def print_game_tree(game_tree):
    """
    输出博弈树的结构化内容，便于调试。
    """
    for node_id, node in game_tree.nodes.items():
        if node.payoffs:
            print(f"{node_id}:")
            print(f"  收益: {node.payoffs}")
        else:
            print(f"{node_id}:")
            print(f"  决策者: {node.player}")
            print(f"  行动: {node.actions}")
            if node.branches:
                print(f"  后续:")
                for action, next_node in node.branches.items():
                    print(f"    {action} -> {next_node}")



# 使用示例
filename = 'game_tree.txt'  # 假设文件中有博弈树的文本数据
game_tree = parse_game_tree_from_file(filename)

# 读取博弈树
game_tree = parse_game_tree_from_file('game_tree.txt')

# 输出博弈树内容
print_game_tree(game_tree)


# 求解博弈树的纳什均衡
#game_tree.solve_nash_equilibrium()

# 可视化博弈树
#game_tree.visualize()
