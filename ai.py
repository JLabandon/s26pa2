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

    def penalty_points(self, state):
        penalty = 0
        cnt = 0
        tile_matrix = state[0]
        l = len(tile_matrix)
        """
        for i in range(l):
            for j in range(l):
                dx = min(i+1, l-i)
                dy = min(j+1, l-j)
                penalty += (dx+dy-1) * tile_matrix[i][j]
        """
        tile_stack = []
        for i in range(l):
            for j in range(l):
                tile_stack.append(tile_matrix[i][j])
                if tile_matrix[i][j] == 0:
                    cnt += 1
        penalty += 1 / (cnt+1) * tile_stack[0]
        tile_stack.sort(reverse=True)
        for i in range(l*l):
            dx = i // l
            dy = i - dx * l if dx % 2 == 0 else l - 1 - (i - dx * l)
            if tile_matrix[dx][dy] < tile_stack[i]:
                penalty += tile_stack[i] - tile_matrix[dx][dy]

        return penalty

    def _board_to_key(self, board):
        return tuple(tuple(row) for row in board)

    def _count_empty(self, board):
        cnt = 0
        for row in board:
            for value in row:
                if value == 0:
                    cnt += 1
        return cnt

    def _rotate_clockwise(self, board):
        size = len(board)
        rotated = [list(row) for row in board]
        for i in range(int(size / 2)):
            for k in range(i, size - i - 1):
                temp1 = rotated[i][k]
                temp2 = rotated[size - 1 - k][i]
                temp3 = rotated[size - 1 - i][size - 1 - k]
                temp4 = rotated[k][size - 1 - i]
                rotated[size - 1 - k][i] = temp1
                rotated[size - 1 - i][size - 1 - k] = temp2
                rotated[k][size - 1 - i] = temp3
                rotated[i][k] = temp4
        return rotated

    def _compress_row_left(self, row):
        values = [value for value in row if value != 0]
        merged = []
        score_gain = 0
        idx = 0

        while idx < len(values):
            value = values[idx]
            if idx + 1 < len(values) and values[idx + 1] == value:
                value *= 2
                score_gain += value
                idx += 2
            else:
                idx += 1
            merged.append(value)

        merged.extend([0] * (len(row) - len(merged)))
        return merged, score_gain

    def _move_board(self, board, direction):
        working = [list(row) for row in board]
        for _ in range(direction):
            working = self._rotate_clockwise(working)

        moved = False
        score_gain = 0
        next_board = []
        for row in working:
            new_row, row_gain = self._compress_row_left(row)
            if new_row != row:
                moved = True
            score_gain += row_gain
            next_board.append(new_row)

        for _ in range((4 - direction) % 4):
            next_board = self._rotate_clockwise(next_board)

        if not moved:
            return None, 0
        return self._board_to_key(next_board), score_gain

    def _ordered_empty_tiles(self, board):
        empties = []
        size = len(board)
        for i in range(size):
            for j in range(size):
                if board[i][j] == 0:
                    empties.append((i, j))
        return empties

    def _sample_chance_positions(self, board):
        empties = self._ordered_empty_tiles(board)
        empty_cnt = len(empties)
        if empty_cnt <= 4:
            return empties
        if empty_cnt >= 8:
            limit = 4
        else:
            limit = 6

        scored_positions = []
        for i, j in empties:
            next_board = [list(row) for row in board]
            next_board[i][j] = 2
            penalty = self.penalty_points((next_board, 0))
            scored_positions.append((penalty, i, j))

        scored_positions.sort(reverse=True)
        return [(i, j) for _, i, j in scored_positions[:limit]]

    def _extension_depth(self, board):
        empty_cnt = self._count_empty(board)
        if empty_cnt >= 8:
            return 3
        if empty_cnt >= 4:
            return 5
        return 7

    def _evaluate_extension_state(self, board, score):
        return score - self.penalty_points((board, score))

    def _expectimax_extension(self, board, score, depth, player_type):
        if depth == 0:
            return None, self._evaluate_extension_state(board, score)

        if player_type == MAX_PLAYER:
            best_direction = None
            best_value = float("-inf")
            for direction in range(4):
                next_board, score_gain = self._move_board(board, direction)
                if next_board is None:
                    continue
                _, value = self._expectimax_extension(
                    next_board, score + score_gain, depth - 1, CHANCE_PLAYER
                )
                if value > best_value:
                    best_direction = direction
                    best_value = value

            if best_direction is None:
                return None, self._evaluate_extension_state(board, score)
            return best_direction, best_value

        positions = self._sample_chance_positions(board)
        if not positions:
            return None, self._evaluate_extension_state(board, score)

        total_value = 0.0
        for i, j in positions:
            next_board = [list(row) for row in board]
            next_board[i][j] = 2
            _, value = self._expectimax_extension(
                self._board_to_key(next_board), score, depth - 1, MAX_PLAYER
            )
            total_value += value

        return None, total_value / len(positions)

    # TODO (optional): the extension part
    def compute_decision_extension(self):
        board = self._board_to_key(self.root.state[0])
        score = self.root.state[1]
        depth = self._extension_depth(board)
        direction, _ = self._expectimax_extension(board, score, depth, MAX_PLAYER)
        return direction
