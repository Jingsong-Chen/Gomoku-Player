from __future__ import print_function
import pygame
from randplay import *
from mcts import *


class Board:
    # board object constructor
    def __init__(self):
        self.grid_size = 46
        self.start_x, self.start_y = 38, 55  # the starting pixels of the board
        self.edge_size = self.grid_size // 2
        self.grid_count = 11
        self.piece = 'b'  # the color of the current player
        self.winner = None
        self.game_over = False
        self.grid = []  # a 2D array
        self.winning_pos = []   # used to show the winning line
        for i in range(self.grid_count):
            self.grid.append(list("." * self.grid_count))

    # handles the player's clicking
    def handle_key_event(self, e):
        # left-up corner coordinate
        origin_x = self.start_x - self.edge_size
        origin_y = self.start_y - self.edge_size
        size = (self.grid_count - 1) * self.grid_size + self.edge_size * 2
        pos = e.pos
        # Check the coordinates are in valid range
        if origin_x <= pos[0] <= origin_x + size and origin_y <= pos[1] <= origin_y + size:
            if not self.game_over:
                x = pos[0] - origin_x
                y = pos[1] - origin_y
                r = int(y // self.grid_size)
                c = int(x // self.grid_size)
                # set a chess at the place clicked by the user
                if self.set_piece(r, c):
                    self.check_win(r, c)
                    return True
        return False

    # '.' means an empty spot that is available to set the piece
    def set_piece(self, r, c):
        # if the grid is empty, fill it with the color of the current player
        if self.grid[r][c] == '.':
            self.grid[r][c] = self.piece
            # switch the current player
            if self.piece == 'b':
                self.piece = 'w'
            else:
                self.piece = 'b'
            return True
        return False

    # the ai counterpart of handel key event
    # two automatic players against each other
    def autoplay(self):
        # the player 1 is a random player
        if not self.game_over:
            # create a random player
            player1 = Randplay(self.grid, self.piece)
            # generate the coordinates to put the piece
            r, c = player1.make_move()
            print("Auto", self.piece, "move: (", r, ",", c, ")")
            # actually put the piece on the board
            self.set_piece(r, c)
            self.check_win(r, c)
        # the player 2 is a MCTS player
        if not self.game_over:
            # TODO: Modify player2 to use MCTS instead of Randplay
            # create a MCTS player
            player2 = MCTS(copy.deepcopy(self.grid), self.piece)
            # generate the coordinates to put the piece
            r, c = player2.uct_search()
            # player2 = Randplay(self.grid, self.piece)
            # # generate the coordinates to put the piece
            # r, c = player1.make_move()
            print("Auto", self.piece, "move: (", r, ",", c, ")")
            # actually put the piece on the board
            self.set_piece(r, c)
            self.check_win(r, c)

    # Human vs computer
    def semi_autoplay(self):
        if not self.game_over:
            # Create a computer player as the human;s opponent
            # Optional: Change this to MCTS AI and see whether you can win
            player1 = Randplay(self.grid, self.piece)
            # computer generate a move
            r, c = player1.make_move()
            print("Semi-Auto", self.piece, "move: (", r, ",", c, ")")
            # computer executes the move
            self.set_piece(r, c)
            self.check_win(r, c)

    # checks if five pieces have formed
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
        # store the winning line of five pieces
        if self.game_over:
            if n_count + s_count + 1 >= 5:
                # append start piece
                self.winning_pos.append((r - n_count, c))
                # append end piece
                self.winning_pos.append((r + s_count, c))
            elif e_count + w_count + 1 >= 5:
                # append start piece
                self.winning_pos.append((r, c - w_count))
                # append end piece
                self.winning_pos.append((r, c + e_count))
            elif se_count + nw_count + 1 >= 5:
                # append start piece
                self.winning_pos.append((r - nw_count, c - nw_count))
                # append end piece
                self.winning_pos.append((r + se_count, c + se_count))
            elif ne_count + sw_count + 1 >= 5:
                # append start piece
                self.winning_pos.append((r + sw_count, c - sw_count))
                # append end piece
                self.winning_pos.append((r - ne_count, c + ne_count))

    # count the number of the pieces of the same color as the current piece in a certain direction
    def get_continuous_count(self, r, c, dr, dc):
        piece = self.grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result

    # reset the game
    def restart(self):
        for r in range(self.grid_count):
            for c in range(self.grid_count):
                self.grid[r][c] = '.'
        self.piece = 'b'
        self.winner = None
        self.game_over = False
        self.winning_pos = []

    # draw the graphics
    def draw(self, screen):
        pygame.draw.rect(screen, (185, 122, 87),
                         [self.start_x - self.edge_size, self.start_y - self.edge_size,
                          (self.grid_count - 1) * self.grid_size + self.edge_size * 2, (self.grid_count - 1) * self.grid_size + self.edge_size * 2], 0)
        # draw horizontal line
        for r in range(self.grid_count):
            y = self.start_y + r * self.grid_size 
            pygame.draw.line(screen, (0, 0, 0), [self.start_x, y], [self.start_x + self.grid_size * (self.grid_count - 1), y], 2)
        # draw vertical line
        for c in range(self.grid_count):
            x = self.start_x + c * self.grid_size 
            pygame.draw.line(screen, (0, 0, 0), [x, self.start_y], [x, self.start_y + self.grid_size * (self.grid_count - 1)], 2)
        # draw pieces
        for r in range(self.grid_count):
            for c in range(self.grid_count):
                piece = self.grid[r][c]
                if piece != '.':
                    if piece == 'b':
                        color = (0, 0, 0)
                    else:
                        color = (255, 255, 255)
                    x = self.start_x + c * self.grid_size
                    y = self.start_y + r * self.grid_size
                    pygame.draw.circle(screen, color, [x, y], self.grid_size // 2)
        # draw the winning line of five pieces
        if self.game_over:
            start_pos = [self.start_x + self.winning_pos[0][1]*self.grid_size, self.start_y + self.winning_pos[0][0]*self.grid_size]
            end_pos = [self.start_x + self.winning_pos[1][1]*self.grid_size, self.start_y + self.winning_pos[1][0]*self.grid_size]
            pygame.draw.line(screen, (140, 40, 0), start_pos, end_pos, 6)
