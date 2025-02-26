import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
import re

# Manually load the font for English
matplotlib.rcParams['font.family'] = 'Arial'  # Using Arial font
matplotlib.rcParams['axes.unicode_minus'] = False  # To display negative signs

# Node class definition
class Node:
    def __init__(self, id, player, actions, branches=None, payoffs=None, is_leaf=False):
        """
        Initialize a node in the game tree.
        初始化博弈树中的一个节点
        """
        self.id = id  # Node identifier
        self.player = player  # Decision maker (A or B)
        self.actions = actions  # Possible actions for the player
        self.branches = branches or {}  # The branches leading to the next nodes
        self.payoffs = payoffs  # For leaf nodes, contains (A payoff, B payoff)
        self.status = "undecided"  # Node status: "undecided" or "decided"
        self.best_action = None  # The best action for the node once it's decided
        self.is_leaf = is_leaf  # Flag to indicate if it's a leaf node

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
        optimal_nodes = set()  # Store optimal nodes
        optimal_edges = set()  # Store optimal edges (as (start_node, end_node))

        # Start backward induction
        while True:
            decided_this_round = set()

            for node_id, node in self.nodes.items():
                if node.status == "undecided":
                    all_decided = True
                    for actions, next_node_id in node.branches.items():
                        next_node = self.nodes[next_node_id]
                        if next_node.status == "undecided":
                            all_decided = False
                            break

                    print(f"Processing Node {node_id}: Status: {node.status}, Actions: {node.actions}, Branches: {node.branches}")

                    if all_decided:
                        best_action = None
                        if node.player == "A":
                            # For player A, choose the action that maximizes their payoff
                            best_action = max(
                                node.branches,
                                key=lambda action: self.nodes[node.branches[action]].payoffs[0]
                                if self.nodes[node.branches[action]].payoffs else float('-inf')
                            )
                        elif node.player == "B":
                            # For player B, choose the action that maximizes their payoff
                            best_action = max(
                                node.branches,
                                key=lambda action: self.nodes[node.branches[action]].payoffs[1]
                                if self.nodes[node.branches[action]].payoffs else float('-inf')
                            )

                        # Ensure the best action was actually selected
                        if best_action is not None:
                            node.best_action = best_action
                            node.status = "decided"
                            optimal_nodes.add(node.id)
                            decided_this_round.add(node.id)

                            # Propagate the best action's payoff back to the current node
                            next_node_id = node.branches[best_action]
                            next_node = self.nodes[next_node_id]
                            if next_node.payoffs:
                                node.payoffs = next_node.payoffs
                                print(f"Node {node_id} decided, Next node: {next_node_id}, Payoff: {node.payoffs}")
                            else:
                                print(f"Warning: Next node {next_node_id} has no payoffs")

            if not decided_this_round:
                break  # If no node was decided in this round, we are done

        # After all nodes are decided, compute the optimal edges
        for node_id, node in self.nodes.items():
            if node.status == "decided" and node.best_action is not None:  # Ensure best_action exists
                next_node_id = node.branches[node.best_action]
                optimal_edges.add((node.id, next_node_id))

        print("Optimal nodes:", optimal_nodes)
        print("Optimal edges:", optimal_edges)
        return optimal_nodes, optimal_edges

    def visualize(self, ultimate_nodes, ultimate_actions):
        """
        Visualize the game tree, highlighting the ultimate path.
        可视化博弈树，并突出显示最终最优路径（仅高亮输出路径中的节点和边）。
        """
        G = nx.DiGraph()  # 创建有向图来表示博弈树
        
        # 将所有节点和边加入图中
        for node_id, node in self.nodes.items():
            # 如果是决策节点，在标签中显示玩家信息
            label = node.id
            if not node.is_leaf:
                label += f" ({node.player})"
            G.add_node(node.id, label=label)
            if node.payoffs:
                G.nodes[node.id]['payoffs'] = node.payoffs
            
            for action, next_node_id in node.branches.items():
                G.add_edge(node.id, next_node_id, label=action)
        
        pos = nx.spring_layout(G)  # 使用 spring 布局
        edge_labels = nx.get_edge_attributes(G, 'label')
        node_labels = nx.get_node_attributes(G, 'label')
        
        # 绘制全部图
        nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=3000,
                node_color="lightblue", font_size=10, font_weight='bold', arrows=True)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        
        # 高亮最终路径的节点（使用 ultimate_nodes 列表）
        for node_id in ultimate_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=[node_id], node_color="pink", node_size=3000)
        
        # 高亮最终路径的边：使用 ultimate_nodes 列表的相邻节点构造边
        for i in range(len(ultimate_nodes) - 1):
            edge = (ultimate_nodes[i], ultimate_nodes[i+1])
            nx.draw_networkx_edges(G, pos, edgelist=[edge], width=2, edge_color="black")
        
        # 显示每个节点的收益信息
        for node_id, node in self.nodes.items():
            if node.payoffs: # 在所有节点显示收益信息
            #if node.is_leaf: # 仅在叶子节点显示收益信息
                x, y = pos[node_id]
                plt.text(x, y - 0.1, f"A: {node.payoffs[0]}, B: {node.payoffs[1]}", fontsize=9, ha='center')
        
        plt.title("Game Tree Visualization with Ultimate Path Highlighted")
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
            
            node = Node(node_id, "None", [], None, payoffs, is_leaf=True)  # Mark as leaf node
            node.status = "decided"  # Set the terminal node's status to "decided"
            game_tree.add_node(node)  # Add the terminal node to the game tree
            node_map[node_id] = node  # Store the terminal node for easy reference
        
        i += 1  # Move to the next line in the file
    
    return game_tree

def output_game_tree_solution(game_tree, start_node_id):
    """
    Output the solution of the game tree in a readable text format.
    输出博弈树求解结果，以文字形式展示每个节点的选择以及最终的收益值。
    Also return the ultimate nodes and actions.
    """
    ultimate_nodes = []  # Store the nodes in the optimal solution path
    ultimate_actions = []  # Store the actions in the optimal solution path

    def traverse(node_id, path):
        """
        Recursively traverse the game tree, building the path and printing the choices.
        递归遍历博弈树，构建路径并打印选择
        """
        node = game_tree.nodes[node_id]  # Get the current node
        
        # If it's a leaf node, print the path and the payoffs
        if node.is_leaf:
            print(" -> ".join(path) + f" -> Terminal Node {node.id}: A's payoff = {node.payoffs[0]}, B's payoff = {node.payoffs[1]}")
            ultimate_nodes.append(node.id)
        else:
            # If the node has a best action, follow it
            if node.best_action is None:
                print(f"Warning: No best action found at Node {node.id}, skipping...")
                return  # Skip if no best action is found
            
            # Otherwise, follow the best action and continue to the next node
            action = node.best_action
            next_node_id = node.branches[action]  # Get the next node based on the best action
            ultimate_nodes.append(node.id)
            ultimate_actions.append(action)
            print(f"At Node {node.id}, Decision Maker: {node.player}, Action chosen: {action}")
            # 打印当前节点的选择
            
            # Add this action to the path and recurse to the next node
            traverse(next_node_id, path + [f"Action {action} -> Node {next_node_id}"])  # Recursively continue to the next node

    # Start traversal from the given start node and display the entire path
    traverse(start_node_id, [f"Node {start_node_id}"])
    # 从起始节点开始遍历，并显示路径
    
    return ultimate_nodes, ultimate_actions  # Return the nodes and actions in the optimal solution path

# Example code: How to parse, solve, and visualize the game tree
filename = 'game_tree.txt'  # Assuming the file name is game_tree.txt
game_tree = parse_game_tree_from_file(filename)

# Solve the Nash equilibrium and get the optimal nodes and edges
optimal_nodes, optimal_edges = game_tree.solve_nash_equilibrium()

# Output the game tree solution starting from the initial node (e.g., Node 1)
output_game_tree_solution(game_tree, "Node 1")

# Output the game tree solution starting from the initial node (e.g., Node 1)
ultimate_nodes, ultimate_actions = output_game_tree_solution(game_tree, "Node 1")

# Visualize the game tree, highlighting the ultimate path
game_tree.visualize(ultimate_nodes, ultimate_actions)