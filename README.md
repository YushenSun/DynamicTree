# Dynamic Game Tree Parser and Visualizer | 动态博弈树解析与可视化工具

## Project Overview | 项目概述

This project provides a Python-based solution for parsing and visualizing game trees from a text-based format. The tool reads game trees from a structured text file, where each node represents a decision point, and parses the payoffs and branching decisions to build a structured game tree. It also supports solving for Nash equilibrium using backward induction and visualizing the tree.

该项目提供了一个基于 Python 的解决方案，用于从文本格式中解析和可视化博弈树。该工具从结构化文本文件中读取博弈树，每个节点表示一个决策点，并解析收益和分支决策以构建一个结构化的博弈树。它还支持使用逆向归纳法求解纳什均衡，并可视化博弈树。

## Features | 特性

- **Game Tree Parsing** | 博弈树解析：Parses game trees from a structured text file, extracting decision nodes and their respective actions and payoffs.  
- **Backward Induction** | 逆向归纳：Solves for Nash equilibrium by using backward induction on the game tree.  
- **Game Tree Visualization** | 博弈树可视化：Visualizes the game tree structure using `networkx` and `matplotlib`, including payoffs at terminal nodes.  
- **Bilingual Support** | 双语支持：The tool supports both English and Chinese interfaces for broader usability.

## Installation | 安装

1. Clone the repository:  
   克隆仓库：
https://github.com/YushenSun/DynamicTree/
2. Install the required dependencies:  
安装所需依赖：
pip install -r requirements.txt

## Usage | 使用方法

1. **Prepare your input file**:  
准备你的输入文件（如 `game_tree.txt`），文件应该遵循以下格式：

节点 1: 决策者: A 行动: [L, R] 后续: L -> 节点 2 R -> 节点 3

节点 2: 决策者: B 行动: [U, D] 后续: U -> 终点节点 1 D -> 终点节点 2

终点节点 1: 收益: (3, 2)

终点节点 2: 收益: (1, 4)

2. **Run the script** to parse and visualize the game tree:  
运行脚本来解析并可视化博弈树：

```bash
python dynamic_tree.py game_tree.txt
Outputs:
The script will print a structured output of the game tree.
It will visualize the game tree using networkx and matplotlib.
It will solve for the Nash equilibrium if solve_nash_equilibrium() is called.
