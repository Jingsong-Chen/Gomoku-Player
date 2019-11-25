from __future__ import absolute_import, division, print_function
from math import sqrt, log
import random
import numpy as np
import copy

MAXRC = 10
GRID_COUNT = 11
GRID_SIZE = 52
BLACK = 0
WHITE = 1
DRAW = 0.5
BUDGET = 1600


# the node class in the simulator tree
class State:
    # node constructor in a game emulation tree
    def __init__(self):
        self.grid = None
        self.player = None  # the color that the current player wants to play next
        self.game_over = False
        self.move = None
        self.children = []
        self.winner = None
        self.encounter = 0
        self.win = 0
        self.options = []
        self.rand = False
        self.parent = None

    # a constructor that create a child by taking a move from a parent
    def constructor_move(self, parent, move):
        self.grid = copy.deepcopy(parent.grid)
        self.player = parent.player
        self.parent = parent
        self.move = move
        self.set_piece(move[0], move[1])
        self.check_win(move[0], move[1])
        self.options = self.get_options()

    # a constructor that initializes the fields with parameters
    def constructor_params(self, grid, player):
        self.grid = copy.deepcopy(grid)
        self.player = player  # the color of the CURRENT player
        self.options = self.get_options()

    # helper function. take a pair of coordinates and set
    def set_piece(self, r, c):
        if self.grid[r][c] == '.':
            self.grid[r][c] = self.player
            # as soon as the piece is set, switch the children's role
            if self.player == 'b':
                self.player = 'w'
            else:
                self.player = 'b'
            self.rand = not self.rand
            return True
        return False

    # heuristics that only checks the neighbors of existing pieces
    # if the whole board is
    def get_options(self):
        # get options for the random player
        # if self.rand:
        # collect all occupied spots
        current_pcs = []
        for r in range(GRID_COUNT):
            for c in range(GRID_COUNT):
                if not self.grid[r][c] == '.':
                    current_pcs.append((r, c))
        # At the beginning of the game, current_pcs is empty
        if not current_pcs:
            return [(MAXRC//2, MAXRC//2)]
        # Reasonable moves should be close to where the current pieces are
        # Think about what these calculations are doing
        # Note: min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-1)
        max_r = min(MAXRC, max(current_pcs, key=lambda x: x[0])[0]+1)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-1)
        max_c = min(MAXRC, max(current_pcs, key=lambda x: x[1])[1]+1)
        # Options of reasonable next step moves
        options = []
        for i in range(min_r, max_r+1):
            for j in range(min_c, max_c+1):
                if self.grid[i][j] == '.':
                    options.append((i, j))
        # get options for my AI
        # else:
        #     # # get all the positions of the pieces of the AI's color
        #     current_pcs = []
        #     # for r in range(GRID_COUNT):
        #     #     for c in range(GRID_COUNT):
        #     #         if self.grid[r][c] == self.player:
        #     #             current_pcs.append((r, c))
        #
        #     for r in range(GRID_COUNT):
        #         for c in range(GRID_COUNT):
        #             if self.grid[r][c] != '.':
        #                 current_pcs.append((r, c))
        #     # At the beginning of the game, current_pcs is empty
        #     if not current_pcs:
        #         return [(MAXRC // 2 - 1, MAXRC // 2 - 1)]
        #     # only explore the positions right next to the pieces of our own color
        #     options = []
        #     temp = set()
        #     for occupied in current_pcs:
        #         temp.add((occupied[0] - 1, occupied[1] - 1))
        #         temp.add((occupied[0], occupied[1] - 1))
        #         temp.add((occupied[0] + 1, occupied[1] - 1))
        #         temp.add((occupied[0] - 1, occupied[1]))
        #         temp.add((occupied[0] + 1, occupied[1]))
        #         temp.add((occupied[0] - 1, occupied[1] + 1))
        #         temp.add((occupied[0], occupied[1] + 1))
        #         temp.add((occupied[0] + 1, occupied[1] + 1))
        #     for potential in list(temp):
        #         if 0 <= potential[0] < GRID_COUNT and 0 <= potential[1] < GRID_COUNT:
        #             if self.grid[potential[0]][potential[1]] == '.':
        #                 options.append(potential)
        # In the unlikely event that no one wins before board is filled
        if len(options) == 0:
            self.game_over = True
            self.winner = 'd'
        return options

    # checks if five pieces have formed
    # if so set the game over flag and record the winner
    def check_win(self, r, c):
        # there are eight direction to check, (row, column)
        # north direction (up)
        n_count = self.get_continuous_count(r, c, -1, 0)
        # south direction (down)
        s_count = self.get_continuous_count(r, c, 1, 0)
        # east direction (right)
        e_count = self.get_continuous_count(r, c, 0, 1)
        # west direction (left)
        w_count = self.get_continuous_count(r, c, 0, -1)
        # south_east diagonal (down right)
        se_count = self.get_continuous_count(r, c, 1, 1)
        # north_west diagonal (up left)
        nw_count = self.get_continuous_count(r, c, -1, -1)
        # north_east diagonal (up right)
        ne_count = self.get_continuous_count(r, c, -1, 1)
        # south_west diagonal (down left)
        sw_count = self.get_continuous_count(r, c, 1, -1)
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
            self.winner = self.grid[r][c]
            self.game_over = True
        return

    # count the number of the pieces of the same color as the current piece in a certain direction
    def get_continuous_count(self, r, c, dr, dc):
        piece = self.grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < GRID_COUNT and 0 <= new_c < GRID_COUNT:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result


class MCTS:
    # constructor of a Monte Carlo Tree Search object
    def __init__(self, grid, player):
        self.initial_board = grid
        self.ai_role = player
        self.cur_role = player

    # high level interface for MCTS. takes a root state and make a decision by calling other functions
    def uct_search(self):
        # create the root node and get all the possible moves
        root_state = State()
        root_state.constructor_params(self.initial_board, self.ai_role)
        for i in range(0, BUDGET):
            # decide which child should we try next
            next_try = self.selection(root_state)
            # simulate a game to the end on the chosen child
            terminal = self.simulation(next_try)
            # update the child with the game result
            self.back_propagation(next_try, terminal)
        # return the child with the formula: argmax(Q / N)
        index = np.argmax([child.win / child.encounter
                              for child in root_state.children])
        decision = root_state.children[index].move
        return [decision[0], decision[1]]

    # responsible for expand the next node to simulate. will only be called on the root
    # by the design of the game the root state must not be terminal. otherwise the MCTS AI won't be called
    def selection(self, state):
        next_state = state
        # need to make sure that get_options and check_win
        while not next_state.game_over:
            # if the current node is not fully expanded
            # meaning the next move option list is not empty, as every time a child is created, an option will be popped
            if len(next_state.options):
                return self.expansion(next_state)
            # if the root is fully expanded
            else:
                next_state = self.best_child(next_state)
        return next_state

    # expand one child at a time of the parameter state
    def expansion(self, parent):
        # get the position to put the next piece
        next_pos = parent.options.pop(0)
        # create a child state
        child = State()
        child.constructor_move(parent, next_pos)
        # the above two steps guarantees that the child's game over indicator is correctly updated
        # append the new child to the root state
        parent.children.append(child)
        return child

    # apply the evaluation function and return the best child
    def best_child(self, parent):
        # argmax (Q / N + c * sqrt(ln(N) / N))
        index = np.argmax([child.win / child.encounter + 2 * sqrt(log(parent.encounter) / child.encounter)
                          for child in parent.children])
        return parent.children[index]

    # keeps randomly playing till a terminal state is met
    def simulation(self, starting_state):
        cur_state = starting_state
        # create a sandbox to simulate on
        next_state = State()
        while not cur_state.game_over:
            # randomly generate a position to put the next piece
            next_pos = cur_state.options.pop(random.randint(0, len(cur_state.options) - 1))
            # apply the move on the sandbox
            next_state.constructor_move(cur_state, next_pos)
            # move on to the next player
            cur_state = next_state
        return cur_state.winner

    def back_propagation(self, to_update, result):
        # keeps going up
        while to_update is not None:
            # update how many times we have seen the current state
            to_update.encounter += 1
            # update the performance. the update is inverted because of the implementation details
            # do nothing if tie
            if result == 'd':
                a = 0
            # penalize if lose
            if result == to_update.player:
                to_update.win -= 1
            # reward if win
            else:
                to_update.win += 1
            # move up the tree
            to_update = to_update.parent