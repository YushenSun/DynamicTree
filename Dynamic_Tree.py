import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
import re
from matplotlib import font_manager

# Manually load the font for English
matplotlib.rcParams['font.family'] = 'Arial'  # Using Arial font
matplotlib.rcParams['axes.unicode_minus'] = False  # To display negative signs

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
        Use backward induction to solve the Nash equilibrium in the game tree.
        """
        for node_id in sorted(self.nodes.keys(), reverse=True):  # Assume node IDs are numeric, process in reverse order
            node = self.nodes[node_id]
            if node.payoffs:
                continue  # Skip if it's a leaf node
            if node.player == 'A':
                best_action = max(node.branches, key=lambda action: self.nodes[node.branches[action]].payoffs[0])
                node.best_action = best_action
            elif node.player == 'B':
                best_action = max(node.branches, key=lambda action: self.nodes[node.branches[action]].payoffs[1])
                node.best_action = best_action

    def visualize(self):
        """
        Visualize the game tree
        """
        G = nx.DiGraph()
        
        for node_id, node in self.nodes.items():
            G.add_node(node.id, label=node.id)
            if node.payoffs:
                G.nodes[node.id]['payoffs'] = node.payoffs

            for action, next_node_id in node.branches.items():
                G.add_edge(node.id, next_node_id, label=action)

        pos = nx.spring_layout(G)  # Using spring_layout for layout
        labels = nx.get_edge_attributes(G, 'label')
        
        # Draw the game tree
        nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", font_size=10, font_weight='bold', arrows=True)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

        # Add payoff information at node positions
        for node_id, node in self.nodes.items():
            if node.payoffs:
                x, y = pos[node_id]
                plt.text(x, y, f"A: {node.payoffs[0]}, B: {node.payoffs[1]}", fontsize=9, ha='center')

        plt.title("Game Tree Visualization")
        plt.show()

# Parse function assuming you have the correct parsing logic
def parse_game_tree_from_file(filename):
    game_tree = GameTree()
    node_map = {}  # Store nodes for easy reference
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0  # Index for line traversal
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("Node"):
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
            if "Subsequent" in branches_line:
                j = i + 4
                while j < len(lines) and not lines[j].startswith("Terminal Node") and lines[j].strip() != "":
                    branch_line = lines[j].strip()
                    if "->" in branch_line:
                        action, next_node = branch_line.split("->")
                        branches[action.strip()] = next_node.strip()
                    j += 1
                i = j - 1

            node = Node(node_id, player, actions, branches, payoffs)
            game_tree.add_node(node)
            node_map[node_id] = node
        
        if line.startswith("Terminal Node"):
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
    Print the structured content of the game tree for debugging purposes.
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

# Example code: How to parse, solve, and visualize the game tree
filename = 'game_tree.txt'  # Assuming the file name is game_tree.txt
game_tree = parse_game_tree_from_file(filename)

# Print the game tree content
print_game_tree(game_tree)

# Visualize the game tree
game_tree.visualize()

# Solve the Nash equilibrium of the game tree
#game_tree.solve_nash_equilibrium()
