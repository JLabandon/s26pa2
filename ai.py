from __future__ import absolute_import, division, print_function
import copy, random
from game import Game

MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}
MAX_PLAYER, CHANCE_PLAYER = 0, 1

# Tree node. To be used to construct a game tree.
class Node:
    # Recommended: do not modify this __init__ function
    def __init__(self, state, player_type):
        self.state = (state[0], state[1])

        # to store a list of (direction, node) tuples
        self.children = []

        self.player_type = player_type

    # returns whether this is a terminal state (i.e., no children)
    def is_terminal(self):
        #TODO: complete this
        if not self.children:
            return True
        return False

# AI agent. Determine the next move.
class AI:
    # Recommended: do not modify this __init__ function
    def __init__(self, root_state, search_depth=3):
        self.root = Node(root_state, MAX_PLAYER)
        self.search_depth = search_depth
        self.simulator = Game(*root_state)

    # (Hint) Useful functions:
    # self.simulator.current_state, self.simulator.set_state, self.simulator.move

    # TODO: build a game tree from the current node up to the given depth
    def build_tree(self, node = None, depth = 0):
        if node.player_type == MAX_PLAYER:
            for direction in range(4):
                self.simulator.set_state(*node.state)
                if self.simulator.move(direction):
                    new_state = self.simulator.current_state()
                    child_node = Node(new_state, CHANCE_PLAYER)
                    node.children.append((direction, child_node))
                    if depth > 1:
                        self.build_tree(child_node, depth - 1)
        else:
            tile_value = 2
            for i in range(self.simulator.board_size):
                for j in range(self.simulator.board_size):
                    if node.state[0][i][j]:
                        continue
                    self.simulator.set_state(*node.state)
                    self.simulator.tile_matrix[i][j] = tile_value
                    new_state = self.simulator.current_state()
                    child_node = Node(new_state, MAX_PLAYER)
                    node.children.append((None, child_node))
                    if depth > 1:
                        self.build_tree(child_node, depth - 1)

    # TODO: expectimax calculation.
    # Return a (best direction, expectimax value) tuple if node is a MAX_PLAYER
    # Return a (None, expectimax value) tuple if node is a CHANCE_PLAYER
    def expectimax(self, node = None):
        if not node.children:
            return None, node.state[1]
        if node.player_type == MAX_PLAYER:
            best_direction, best_value = None, float('-inf')
            for direction, child in node.children:
                _, value = self.expectimax(child)
                if value > best_value:
                    best_direction, best_value = direction, value
            return best_direction, best_value
        else:
            total_value = 0
            for _, child in node.children:
                _, value = self.expectimax(child)
                total_value += value
            return None, total_value / len(node.children)

    # Return decision at the root
    def compute_decision(self):
        self.build_tree(self.root, self.search_depth)
        direction, _ = self.expectimax(self.root)
        return direction
    
    NEW_DEPTH = 5
    RATIO = 100

    def penalty_points(self, state):
        penalty = 0
        tile_matrix = state[0]
        l = self.simulator.board_size
        for i in range(l):
            for j in range(l):
                dx = min(i+1, l-i)
                dy = min(j+1, l-j)
                penalty += (dx+dy-1) * tile_matrix[i][j]

        return penalty * self.RATIO

    def expectimax_extension(self, node = None):
        if not node.children:
            return None, node.state[1]
        if node.player_type == MAX_PLAYER:
            best_direction, best_value = None, float('-inf')
            for direction, child in node.children:
                _, value = self.expectimax(child)
                if value > best_value:
                    best_direction, best_value = direction, value
            return best_direction, best_value - self.penalty_points(node.state)
        else:
            total_value = 0
            for _, child in node.children:
                _, value = self.expectimax(child)
                total_value += value
            return None, total_value / len(node.children) - self.penalty_points(node.state)
    
    # TODO (optional): the extension part
    def compute_decision_extension(self):
        self.build_tree(self.root, self.NEW_DEPTH)
        direction, _ = self.expectimax_extension(self.root)
        return direction

