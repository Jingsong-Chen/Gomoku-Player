from __future__ import absolute_import, division, print_function
from math import sqrt, log
from randplay import *
import random
import copy

#Feel free to add extra classes and functions

# Initialize the board state and player type
class State:
    def __init__(self, grid, player, parent=None):
        self.grid = grid
        self.player = player
        self.maxrc = len(grid)-1
        self.n = 0
        self.q = 0
        self.terminal = None
        self.parent = parent
        self.children = []
        self.action = None
        self.options = self.get_options(self.grid)

    def set_piece(self, r, c):
        if self.grid[r][c] == '.':
            self.grid[r][c] = self.player
            self.terminal = self.check_terminal(r,c)
            self.action = [r,c]
            return True
        return False

    # Check if the board is in a draw state
    def check_draw(self):
        for r in range(11):
            for c in range(11):
                if self.grid[r][c] == ".":
                    return False
        return True

    #there are eight direction to check, (row, column)
    def check_win(self, r, c):
        #north direction (up)
        n_count = self.get_continuous_count(r, c, -1, 0)
        #south direction (down)
        s_count = self.get_continuous_count(r, c, 1, 0)
        #east direction (right)
        e_count = self.get_continuous_count(r, c, 0, 1)
        #west direction (left)
        w_count = self.get_continuous_count(r, c, 0, -1)
        #south_east diagonal (down right)
        se_count = self.get_continuous_count(r, c, 1, 1)
        #north_west diagonal (up left)
        nw_count = self.get_continuous_count(r, c, -1, -1)
        #north_east diagonal (up right)
        ne_count = self.get_continuous_count(r, c, -1, 1)
        #south_west diagonal (down left)
        sw_count = self.get_continuous_count(r, c, 1, -1)
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
            winner = self.grid[r][c]
            return winner
        return None

    def check_terminal(self, r, c):
        if self.check_draw:
            return 'draw'
        return self.check_win(r, c)

    def get_continuous_count(self, r, c, dr, dc):
        piece = self.grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < 11 and 0 <= new_c < 11:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result

    def check_expanded(self):
        return (len(self.options) == 0)


    def get_options(self, grid):
        #collect all occupied spots
        current_pcs = []
        for r in range(len(grid)):
            for c in range(len(grid)):
                if not grid[r][c] == '.':
                    current_pcs.append((r, c))
        #At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [(self.maxrc//2, self.maxrc//2)]
        #Reasonable moves should be close to where the current pieces are
        #Think about what these calculations are doing
        #Note: min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-1)
        max_r = min(self.maxrc, max(current_pcs, key=lambda x: x[0])[0]+1)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-1)
        max_c = min(self.maxrc, max(current_pcs, key=lambda x: x[1])[1]+1)
        #Options of reasonable next step moves
        options = []
        for i in range(min_r, max_r+1):
            for j in range(min_c, max_c+1):
                if not (i, j) in current_pcs:
                    options.append((i, j))
        if len(options) == 0:
            #In the unlikely event that no one wins before board is filled
            #Make white win since black moved first
            self.game_over = True
            self.winner = 'd'  # changed to d
        return options


class MCTS:
    # grid, player, Filled slots on board
    def __init__(self, grid, player):
        self.grid = grid
        self.maxrc = len(grid)-1
        self.player = player
        self.root = State(copy.deepcopy(grid), player)

    def uct_search(self):
        for i in range(2000):
            s = self.selection(self.root)
            winner = self.simulation(s)
            self.backpropagation(s, winner)
        return self.action()

    """
    Return an action from mcts.py to board.py. Return the (row, column)
    """
    def action(self):
        maxx = (0, (0,0)) # (score, move)
        for children in self.root.children:
            score = children.q / children.n
            if score > maxx[0]:
                maxx = (score, children.action)
        return maxx[1]

    """
    Tree policy function, for terminal condition check if current player(black/white)
    won, opponent won, or if no one won. Use heuristics to check if state is fully
    expanded
    @param s - state
    """
    def selection(self, s):
        while not s.terminal:
            if not s.check_expanded():
                return self.expansion(s)
            else:
                index = self.best_child(s)
                s = s.children[index]
        return s
    
    """
    Expand using self.optins
    """
    def expansion(self, state):
        move = state.options.pop()
        nxtPlayer = None
        if state.player == 'b':
            nxtPlayer = 'w'
        else:
            nxtPlayer = 'b'
        child = State(copy.deepcopy(state.grid),nxtPlayer)
        child.set_piece(move[0], move[1])
        child.parent = state
        state.children.append(child)
        return child
    
    """
    get the child of expanded state and update tree, then return the child node
    """
    def best_child(self, state):
        index = 0
        for i in range(len(state.children)):
            nxt = state.children[i]
            cur = state.children[index]

            nxtVal = (nxt.q / nxt.n) + 2 * sqrt( log(state.n)/nxt.n )
            curVal = (cur.q / cur.n) + 2 * sqrt( log(state.n)/cur.n )
            if (nxtVal > curVal):
                index = i
        return index

    """
    while state is not terminal, simulate state until terminal state reached then return
    the result of the state: win, lose, or tie. use the class randplay.py to make moves
    """
    def simulation(self, state):
        s = copy.deepcopy(state.grid)
        sim = Randplay(s, state.player)
        sim.rollout()

        return sim.winner

    """
    Return the child node that maximizes  (Q(s')/N(s') + c*sqrt(ln N(s)/ N(s')))
    """
    def backpropagation(self, s, result):
        while s:
            s.n += 1
            if (result == 'd'):
                s.q += 0.5
            elif result == s.player:
                s.q += 1
            s = s.parent
