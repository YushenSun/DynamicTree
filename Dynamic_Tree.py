import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
import re
from matplotlib import font_manager

# Manually load the font for English
matplotlib.rcParams['font.family'] = 'Arial'  # Using Arial font
matplotlib.rcParams['axes.unicode_minus'] = False  # To display negative signs
# 使用Arial字体，并确保负号能够正确显示

class Node:
    def __init__(self, id, player, actions, branches=None, payoffs=None):
        """
        Initialize a node in the game tree.
        初始化博弈树中的一个节点
        """
        self.id = id  # Node identifier
        self.player = player  # Decision maker (A or B)
        self.actions = actions  # Possible actions for the player
        self.branches = branches or {}  # The branches leading to the next nodes
        self.payoffs = payoffs  # For leaf nodes, contains (A payoff, B payoff)
        # 对象属性：节点ID，决策者，行动，分支（后续节点），收益

class GameTree:
    def __init__(self):
        """
        Initialize the game tree.
        初始化博弈树
        """
        self.nodes = {}  # Dictionary to store all nodes in the game tree
        # 存储所有节点的字典

    def add_node(self, node):
        """
        Add a node to the game tree.
        将节点添加到博弈树中
        """
        self.nodes[node.id] = node  # Add node using its ID as the key
        # 使用节点ID作为键，将节点添加到字典中

    def solve_nash_equilibrium(self):
        """
        Use backward induction to solve the Nash equilibrium in the game tree.
        使用逆向归纳法求解博弈树中的纳什均衡
        """
        for node_id in sorted(self.nodes.keys(), reverse=True):  # Sort nodes in reverse order (from leaf to root)
            node = self.nodes[node_id]  # Get the current node
            if node.payoffs:
                continue  # Skip leaf nodes, which already have payoffs
            # 跳过叶子节点，因为它们已经有收益数据

            if node.player == 'A':
                # If it's A's turn, A will maximize their payoff
                best_action = max(node.branches, key=lambda action: self.nodes[node.branches[action]].payoffs[0])
                node.best_action = best_action
                # A选择最大化收益的行动
            elif node.player == 'B':
                # If it's B's turn, B will maximize their payoff
                best_action = max(node.branches, key=lambda action: self.nodes[node.branches[action]].payoffs[1])
                node.best_action = best_action
                # B选择最大化收益的行动

    def visualize(self):
        """
        Visualize the game tree.
        可视化博弈树
        """
        G = nx.DiGraph()  # Create a directed graph to represent the game tree
        
        for node_id, node in self.nodes.items():
            G.add_node(node.id, label=node.id)  # Add each node to the graph with its ID as label
            if node.payoffs:
                G.nodes[node.id]['payoffs'] = node.payoffs  # Store the payoffs at the node
            
            # Add edges based on branches to represent the transitions between nodes
            for action, next_node_id in node.branches.items():
                G.add_edge(node.id, next_node_id, label=action)  # Add edges for the actions

        pos = nx.spring_layout(G)  # Using spring layout to position the nodes in a visually appealing way
        labels = nx.get_edge_attributes(G, 'label')  # Get the edge labels (actions)
        
        # Draw the game tree with nodes and labels
        nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", font_size=10, font_weight='bold', arrows=True)
        # 绘制节点，设置节点大小、颜色、字体等属性
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)  # Draw edge labels (actions)

        # Add payoff information at node positions
        for node_id, node in self.nodes.items():
            if node.payoffs:
                x, y = pos[node_id]
                # Adjust the payoff label slightly downwards to create space between terminal node and payoff
                plt.text(x, y - 0.1, f"A: {node.payoffs[0]}, B: {node.payoffs[1]}", fontsize=9, ha='center')
                # 在节点位置显示收益信息，位移量是0.1，避免和节点标签重叠

        plt.title("Game Tree Visualization")  # Set the title of the plot
        # 设置图形标题
        plt.show()

# Parse function assuming you have the correct parsing logic
def parse_game_tree_from_file(filename):
    """
    Parse the game tree from a text file.
    从文本文件中解析博弈树
    """
    game_tree = GameTree()  # Create an empty game tree
    node_map = {}  # A map to store nodes for easy reference
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()  # Read all lines in the file
    
    i = 0  # Index for line traversal
    while i < len(lines):
        line = lines[i].strip()  # Strip whitespace from the current line
        if line.startswith("Node"):  # Process node lines
            node_id = line.split(":")[0].strip()  # Extract node ID
            player = None
            actions = []
            branches = {}
            payoffs = None
            
            player_line = lines[i + 1].strip()  # Get the line indicating the player (A or B)
            if "A" in player_line:
                player = "A"
            elif "B" in player_line:
                player = "B"
            # 解析决策者（A或B）
            
            actions_line = lines[i + 2].strip()  # Get the line with actions
            actions = actions_line.split(":")[1].strip().strip("[]").split(", ")
            # 解析节点的行动
            
            branches_line = lines[i + 3].strip()  # Get the line with subsequent branches
            branches = {}
            if "Subsequent" in branches_line:
                j = i + 4
                while j < len(lines) and not lines[j].startswith("Terminal Node") and lines[j].strip() != "":
                    branch_line = lines[j].strip()
                    if "->" in branch_line:
                        action, next_node = branch_line.split("->")
                        branches[action.strip()] = next_node.strip()
                    j += 1
                i = j - 1
            # 解析后续节点
            
            node = Node(node_id, player, actions, branches, payoffs)
            game_tree.add_node(node)  # Add the node to the game tree
            node_map[node_id] = node  # Store the node for easy reference
        
        if line.startswith("Terminal Node"):  # Process terminal nodes
            node_id = line.split(":")[0].strip()  # Extract terminal node ID
            try:
                payoffs_line = lines[i + 1].strip().split(":")  # Get the line with payoffs
                if len(payoffs_line) > 1:
                    payoffs_values = re.findall(r'\d+', payoffs_line[1])  # Extract the payoff values using regex
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
            
            node = Node(node_id, "None", [], None, payoffs)  # Create a terminal node
            game_tree.add_node(node)  # Add the terminal node to the game tree
            node_map[node_id] = node  # Store the terminal node for easy reference
        
        i += 1  # Move to the next line in the file
    
    return game_tree

def print_game_tree(game_tree):
    """
    Print the structured content of the game tree for debugging purposes.
    输出博弈树的结构化内容，便于调试
    """
    for node_id, node in game_tree.nodes.items():
        if node.payoffs:
            print(f"{node_id}:")
            print(f"  Payoff: {node.payoffs}")
        else:
            print(f"{node_id}:")
            print(f"  Decision Maker: {node.player}")
            print(f"  Actions: {node.actions}")
            if node.branches:
                print(f"  Subsequent:")
                for action, next_node in node.branches.items():
                    print(f"    {action} -> {next_node}")
    # 输出博弈树的结构，包含每个节点的信息

# Example code: How to parse, solve, and visualize the game tree
filename = 'game_tree.txt'  # Assuming the file name is game_tree.txt
game_tree = parse_game_tree_from_file(filename)

# Print the game tree content
print_game_tree(game_tree)

# Visualize the game tree
game_tree.visualize()

# Solve the Nash equilibrium of the game tree
#game_tree.solve_nash_equilibrium()
