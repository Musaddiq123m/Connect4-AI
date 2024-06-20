import pygame
import sys
import random
import math

pygame.init()
pygame.mixer.init()

screen_width = 700
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Connect 4")
clock = pygame.time.Clock()

class Game:
    def __init__(self):
        self.state = -1
        self.first_move = False
        self.starting_player = None
        self.memo = {}
        self.starting_values()

    def check_list(self, line):
        if len(line) < 4:
            return None
        for i in range(len(line) - 3):
            if line[i] == line[i + 1] == line[i + 2] == line[i + 3] != '':
                return line[i]
        return None

    def winning(self, board):
        for row in board:
            winner = self.check_list(row)
            if winner:
                return winner

        for col in range(self.cols):
            column = [board[row][col] for row in range(self.rows)]
            winner = self.check_list(column)
            if winner:
                return winner

        for row in range(self.rows - 3):
            for col in range(self.cols - 3):
                diagonal = [board[row + i][col + i] for i in range(4)]
                winner = self.check_list(diagonal)
                if winner:
                    return winner

        for row in range(3, self.rows):
            for col in range(self.cols - 3):
                diagonal = [board[row - i][col + i] for i in range(4)]
                winner = self.check_list(diagonal)
                if winner:
                    return winner

        if all(board[row][col] != '' for row in range(self.rows) for col in range(self.cols)):
            return 'Draw'

        return None

    def make_move(self, matrix, current_player, col):
        for i in range(self.rows-1, -1, -1):
            if matrix[i][col] == '':
                matrix[i][col] = current_player
                return i, col
        return None, None

    def undo_move(self, matrix, i, col):
        matrix[i][col] = ''

    def AiMove(self):
        move = self.MiniMax(self.matrix, True, depth=4, alpha=float('-inf'), beta=float('inf'))[0]
        #print(f"AI chooses column: {move}")
        if move is not None and self.is_valid_move(self.matrix, move):
            self.make_move(self.matrix, self.current_player, move)
            self.current_player = 'Yellow' if self.current_player == 'Red' else 'Red'

    def making_first_move_for_Ai(self):
        if self.first_move == False and self.starting_player == 'Yellow':
            self.AiMove()
            self.first_move = True

    def starting_values(self):
        self.rows = 6
        self.cols = 7
        self.matrix = [['' for _ in range(self.cols)] for _ in range(self.rows)]
        self.blocks = []
        self.current_player = self.starting_player
        self.first_move = False
        self.make_blank_board()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and self.state == 0:
                for i in range(self.rows):
                    for j in range(self.cols):
                        index = i * self.cols + j
                        if self.blocks[index][1].collidepoint(event.pos):
                            row, col = self.make_move(self.matrix, self.current_player, j)
                            if row is not None and col is not None:
                                self.current_player = 'Yellow' if self.current_player == 'Red' else 'Red'
                                self.draw_the_board()
                                if self.current_player == 'Yellow':
                                    self.AiMove()
                                break
            elif event.type == pygame.MOUSEBUTTONDOWN and (self.state == 1 or self.state == -1):
                self.state = 0
                if event.pos[0] < screen_width/2:
                    self.starting_player = 'Red'
                else:
                    self.starting_player = 'Yellow'
                self.starting_values()
                self.making_first_move_for_Ai()

    def make_blank_board(self):
        for i in range(self.rows):
            for j in range(self.cols):
                block = pygame.Surface((100, 100))
                block.fill('White')
                block_rect = block.get_rect(topleft=(j * 100, i * 100))
                self.blocks.append((block, block_rect))

    def draw_the_board(self):
        if self.blocks:
            for i, (block, block_rect) in enumerate(self.blocks):
                screen.blit(block, block_rect)
                row = i // self.cols
                col = i % self.cols
                pygame.draw.rect(screen, 'Black', block_rect, 1)
                if self.matrix[row][col] == 'Red':
                    pygame.draw.circle(screen, 'Red', block_rect.center, 40)
                elif self.matrix[row][col] == 'Yellow':
                    pygame.draw.circle(screen, 'Yellow', block_rect.center, 40)
                else:
                    pygame.draw.circle(screen, 'Grey', block_rect.center, 40)

    def Playstate(self):
        self.event_handler()
        self.draw_the_board()
        winner = self.winning(self.matrix)
        if winner:
            print(winner)
            self.state = 1
        pygame.display.flip()

    def DisplayText(self, str):
        font = pygame.font.Font('Connect4/font/font.otf', 50)
        gameover_surface = font.render("Play first                    Play Second", False, 'Black')
        gameover_rect = gameover_surface.get_rect(midbottom=(screen_width // 2, screen_height // 2 - 35))
        screen.blit(gameover_surface, gameover_rect)
        
        font_click = pygame.font.Font('Connect4/font/font.otf', 35)
        gameover_surface_click = font_click.render(str, False, 'Black')
        gameover_rect_click = gameover_surface_click.get_rect(midtop=(screen_width // 2, screen_height // 2 + 35))
        screen.blit(gameover_surface_click, gameover_rect_click)

    def TextState(self):
        self.event_handler()
        self.draw_the_board()
        if self.state == 1:
            self.DisplayText("Game Over!")
        elif self.state == -1:
            self.DisplayText("Clicking on Any Column Places your disc")
        pygame.display.flip()

    def state_manager(self):
        if self.state == 0:
            self.making_first_move_for_Ai()
            self.Playstate()
        elif self.state == 1 or self.state == -1:
            self.TextState()

    def is_valid_move(self, board, col):
        return board[0][col] == ''

    def MiniMax(self, board, maximizing_player, depth, alpha, beta):
        player = 'Yellow' if maximizing_player else 'Red'
        position, mask = self.get_position_mask_bitmap(board, player)
        state_key = (position, mask, maximizing_player, depth)
        if state_key in self.memo:
            return self.memo[state_key]

        winner = self.winning(board)
        if winner == 'Yellow':
            return (None, 1000000000 + depth)
        elif winner == 'Red':
            return (None, -1000000000 - depth)
        elif winner == 'Draw':
            return (None, 0)

        if depth == 0:
            return (None, self.score_position(board, player, depth))  # Pass depth to score_position

        if maximizing_player:
            move = None
            max_eval = float('-inf')
            for j in range(self.cols):
                if self.is_valid_move(board, j):
                    b_copy = [row[:] for row in board]
                    i, col = self.make_move(b_copy, 'Yellow', j)
                    if i is not None and col is not None:
                        eval = self.MiniMax(b_copy, False, depth - 1, alpha, beta)[1]
                        self.undo_move(b_copy, i, col)
                        if eval > max_eval:
                            max_eval = eval
                            move = col
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
            result = (move, max_eval)
        else:
            move = None
            min_eval = float('inf')
            for j in range(self.cols):
                if self.is_valid_move(board, j):
                    b_copy = [row[:] for row in board]
                    i, col = self.make_move(b_copy, 'Red', j)
                    if i is not None and col is not None:
                        eval = self.MiniMax(b_copy, True, depth - 1, alpha, beta)[1]
                        self.undo_move(b_copy, i, col)
                        if eval < min_eval:
                            min_eval = eval
                            move = col
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
            result = (move, min_eval)

        self.memo[state_key] = result
        return result

    def evaluate_window(self, window, piece, depth):
        opponent_piece = 'Red' if piece == 'Yellow' else 'Yellow'
        score = 0

        if window.count(piece) == 4:
            score += 1000000000 / (depth + 1)  # Adjust scoring based on depth
        elif window.count(piece) == 3 and window.count('') == 1:
            score += 50 / (depth + 1)
        elif window.count(piece) == 2 and window.count('') == 2:
            score += 10 / (depth + 1)

        if window.count(opponent_piece) == 3 and window.count('') == 1:
            score -= 80 / (depth + 1)
        elif window.count(opponent_piece) == 2 and window.count('') == 2:
            score -= 20 / (depth + 1)

        return score

    def score_position(self, board, piece, depth):
        score = 0

        center_array = [board[r][self.cols // 2] for r in range(self.rows)]
        center_count = center_array.count(piece)
        score += center_count * 200 / (depth + 1) 

        for r in range(self.rows):
            row_array = [board[r][c] for c in range(self.cols)]
            for c in range(self.cols - 3):
                window = row_array[c:c + 4]
                score += (r + 1) * self.evaluate_window(window, piece, depth)

        for c in range(self.cols):
            col_array = [board[r][c] for r in range(self.rows)]
            for r in range(self.rows - 3):
                window = col_array[r:r + 4]
                score += (r + 1) * self.evaluate_window(window, piece, depth)

        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                window = [board[r + i][c + i] for i in range(4)]
                score += (r + 1) * self.evaluate_window(window, piece, depth)

        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                window = [board[r + 3 - i][c + i] for i in range(4)]
                score += (r + 1) * self.evaluate_window(window, piece, depth)

        return score

    def get_position_mask_bitmap(self, board, player):
        position = 0
        mask = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if board[r][c] == player:
                    position |= 1 << (r * self.cols + c)
                if board[r][c] != '':
                    mask |= 1 << (r * self.cols + c)
        return position, mask


game = Game()
while True:
    game.state_manager()
    clock.tick(60)
