import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
import re

# 使用系统字体路径手动设置中文字体（适用于 Windows）
matplotlib.rcParams['font.family'] = 'STHeiti'  # 指定字体为微软雅黑
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 如果你希望使用其他字体，可以设置其路径
# matplotlib.font_manager.fontManager.addfont('C:/Windows/Fonts/msyh.ttc')

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

        pos = nx.spring_layout(G)  # 使用spring_layout布局
        labels = nx.get_edge_attributes(G, 'label')
        
        # 绘制博弈树
        nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", font_size=10, font_weight='bold', arrows=True)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

        # 在节点位置添加支付信息
        for node_id, node in self.nodes.items():
            if node.payoffs:
                x, y = pos[node_id]
                plt.text(x, y, f"A: {node.payoffs[0]}, B: {node.payoffs[1]}", fontsize=9, ha='center')

        plt.title("Game Tree Visualization 博弈树可视化")
        plt.show()

# 解析函数，假设你已经有了正确的解析逻辑
def parse_game_tree_from_file(filename):
    game_tree = GameTree()
    node_map = {}  # 用来存储节点，方便引用
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0  # 用于遍历行的索引
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("节点"):
            node_id = line.split(":")[0].strip()
            player = None
            actions = []
            branches = {}
            payoffs = None
            
            player_line = lines[i + 1].strip()
            if "A" in player_line:
                player = "A"
            elif "B" in player_line:
                player = "B"
            
            actions_line = lines[i + 2].strip()
            actions = actions_line.split(":")[1].strip().strip("[]").split(", ")
            
            branches_line = lines[i + 3].strip()
            branches = {}
            if "后续" in branches_line:
                j = i + 4
                while j < len(lines) and not lines[j].startswith("终点节点") and lines[j].strip() != "":
                    branch_line = lines[j].strip()
                    if "->" in branch_line:
                        action, next_node = branch_line.split("->")
                        branches[action.strip()] = next_node.strip()
                    j += 1
                i = j - 1

            node = Node(node_id, player, actions, branches, payoffs)
            game_tree.add_node(node)
            node_map[node_id] = node
        
        if line.startswith("终点节点"):
            node_id = line.split(":")[0].strip()
            try:
                payoffs_line = lines[i + 1].strip().split(":")
                if len(payoffs_line) > 1:
                    payoffs_values = re.findall(r'\d+', payoffs_line[1])
                    if len(payoffs_values) == 2:
                        a_payoff = int(payoffs_values[0])
                        b_payoff = int(payoffs_values[1])
                        payoffs = (a_payoff, b_payoff)
                    else:
                        payoffs = (0, 0)
                else:
                    payoffs = (0, 0)
            except IndexError:
                payoffs = (0, 0)
            
            node = Node(node_id, "None", [], None, payoffs)
            game_tree.add_node(node)
            node_map[node_id] = node
        
        i += 1  # Move to next line
    
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

# 示例代码：如何使用解析、求解博弈树和可视化功能
filename = 'game_tree.txt'  # 假设文件名为 game_tree.txt
game_tree = parse_game_tree_from_file(filename)

# 输出博弈树内容
print_game_tree(game_tree)

# 可视化博弈树
game_tree.visualize()

# 求解博弈树的纳什均衡
#game_tree.solve_nash_equilibrium()
