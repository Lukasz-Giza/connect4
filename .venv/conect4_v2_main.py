import numpy as np
import pygame
import sys
import random
import math
import time

# based on https://www.youtube.com/@KeithGalli

row_count = 6
col_count = 7
# test
#tsest

red = (255, 0, 0)
black = (0, 0, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
magenta =(255,0,255)
lime = (0,255,0)

player = 0
ai = 1

ai_time=0
player_time=0
player_time_start = 0

empty = 0
window_length = 4

player_piece = 1
ai_piece = 2

square_size = 100
width = col_count * square_size
heigth = (row_count + 1) * square_size

size = (width, heigth)
radius = int(square_size / 2 - 5)


def create_board():
    board = np.zeros((row_count, col_count))
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[row_count - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(row_count):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    # horizontal
    win_type=0
    for c in range(col_count - 3):
        for r in range(row_count):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][
                c + 3] == piece:
                win_type=1
                return True,win_type,r,c
    # vertical
    for c in range(col_count):
        for r in range(row_count - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][
                c] == piece:
                win_type = 2
                return True,win_type,r,c

    # positively sloped diagonols
    for c in range(col_count - 3):
        for r in range(row_count - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][
                c + 3] == piece:
                win_type = 3
                return True,win_type,r,c

    # negatively sloped diagonols
    for c in range(col_count - 3):
        for r in range(3, row_count):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][
                c + 3] == piece:
                win_type = 4
                return True,win_type,r,c


def evaluate_window(window,piece):
    score = 0
    opp_piece = player_piece
    if piece == player_piece:
        opp_piece = ai_piece

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(empty) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(empty) == 2:
        score += 2
    if window.count(opp_piece) ==3 and window.count(empty) ==1:
        score -= 4
    return score
def score_position(board, piece):

    score = 0
    # score center
    center_array = [int(i) for i in list(board[:,col_count//2])]
    center_count = center_array.count(piece)
    score += center_count * 3



    # horizontal score
    for r in range(row_count):
        row_array = [int(i) for i in list(board[r, :])]

        for c in range(col_count - 3):
            window = row_array[c:c + window_length]
            score += evaluate_window(window, piece)

    # vert score

    for c in range(col_count):
        col_array = [int(i) for i in list(board[:, c])]

        for r in range(row_count - 3):
            window = col_array[r:r + window_length]
            score += evaluate_window(window, piece)

        #posiitve sloped diagonal
    for r in range(row_count-3):
        for c in range(col_count-3):
            window = [board[r+i][c+i] for i in range(window_length)]
            score += evaluate_window(window, piece)

    for r in range(row_count-3):
        for c in range(col_count-3):
            window = [board[r+3-i][c+i] for i in range(window_length)]
            score += evaluate_window(window, piece)

    return score

def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, ai_piece) :
                return (None, 100000000000000)
            elif winning_move(board, player_piece):
                return (None, - 100000000000000)
            else: #no more valid moves
                return (None, 0)
        else: #depth is zeor
            return (None, score_position(board, ai_piece))

    if maximizing_player:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy ()
            drop_piece(b_copy, row, col, ai_piece)
            new_score = minimax (b_copy, depth -1, alpha, beta, False )[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max (alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: #minimazing_player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board,col)
            b_copy = board.copy()
            drop_piece(b_copy,row,col, player_piece)
            new_score = minimax (b_copy, depth -1, alpha, beta,True) [1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta,value)
            if alpha >= beta:
                break
        return column, value



def is_terminal_node(board):
    return winning_move(board,player_piece) or winning_move(board,ai_piece) or len(get_valid_locations(board)) == 0
def get_valid_locations(board):
    valid_locations = []
    for col in range(col_count):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)

    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        #print(score)
        if score > best_score:
            best_score = score

            best_col = col

    return best_col


def draw_board(board):
    for c in range(col_count):
        for r in range(row_count):
            pygame.draw.rect(screen, blue, (c * square_size, r * square_size + square_size, square_size, square_size))
            pygame.draw.circle(screen, black, (
            int(c * square_size + square_size / 2), int(r * square_size + square_size + square_size / 2)), radius)

    for c in range(col_count):
        for r in range(row_count):

            if board[r][c] == player_piece:
                pygame.draw.circle(screen, red, (
                    int(c * square_size + square_size / 2), heigth - int(r * square_size + square_size / 2)), radius)
            elif board[r][c] == ai_piece:
                pygame.draw.circle(screen, yellow, (
                    int(c * square_size + square_size / 2), heigth - int(r * square_size + square_size / 2)),
                                   radius)
    pygame.display.update()

def draw_win_line(win_type, r ,c):
    if win_type == 1:  # horizontal
        pygame.draw.line(screen, lime, (c*square_size+square_size/2,heigth- r*square_size-square_size/2),(c*square_size+square_size/2+square_size*3,heigth-r*square_size-square_size/2),20)
    elif win_type == 2:
        pygame.draw.line(screen, lime, (c*square_size+square_size/2,heigth- r*square_size-square_size/2), (c*square_size+square_size/2,heigth-r*square_size-square_size/2-square_size*3),20)

        print(r)
    pygame.display.update()


board = create_board()
game_over = False

pygame.init()

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(player, ai)

while not game_over:
    for event in pygame.event.get():
        if player_time_start ==0:
            player_time_start = time.time()
        #print(player_time_start)

        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, black, (0, 0, width, square_size))
            posx = event.pos[0]
            if turn == player:
                pygame.draw.circle(screen, red, (posx, int(square_size / 2)), radius)

        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, black, (0, 0, width, square_size))
            # print(event.pos)
            #  player 1 input
            if turn == player:


                posx = event.pos[0]
                col = int(posx // square_size)

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, player_piece)

                    if winning_move(board, player_piece):

                        # print("player 1 wins")
                        label = myfont.render("Gracz 1 wygrał", 1, red)
                        screen.blit(label, (40, 10))
                        game_over = True

                    turn += 1
                    turn = turn % 2

                    player_time_end = time.time()
                    player_time_step = player_time_end - player_time_start
                    player_time = player_time + player_time_step
                    player_time_start=0
                    #print(player_time)

                    # print_board(board)
                    draw_board(board)

                # print(selection)
                # print(type(selection))

            #
            # #player 2 input

    if turn == ai and not game_over:
        ai_time_start = time.time()
        # col = random.randint(0,col_count-1)
        #col = pick_best_move(board, ai_piece)
        col, minimax_score = minimax (board, 1, -math.inf, math.inf, True)

        if is_valid_location(board, col):

            pygame.time.wait(1)

            row = get_next_open_row(board, col)
            drop_piece(board, row, col, ai_piece)
            if winning_move(board, ai_piece):
                win_type= winning_move(board, ai_piece)[1]
                print(win_type)
                # print("player 2 wins")
                label = myfont.render("Gracz 2 wygrał", 1, yellow)
                screen.blit(label, (40, 10))
                game_over = True

            # print_board(board)
            draw_board(board)
            turn += 1
            turn = turn % 2
            ai_time_end=time.time()
            ai_time_step=ai_time_end-ai_time_start
            ai_time=ai_time+ai_time_step
            #print (ai_time)

    if game_over:
        print("czas ruchu SI wynosi", int(ai_time), "sekund")
        print("czas ruchu Gracza wynosi", int(player_time) ,"sekund")

        if turn == ai:
            draw_win_line(winning_move(board, player_piece)[1], winning_move(board, player_piece)[2],winning_move(board, player_piece)[3])

        else:
            draw_win_line(winning_move(board, ai_piece)[1], winning_move(board, ai_piece)[2],winning_move(board, ai_piece)[3])

        # print(win_type)
        pygame.time.wait(2000)
        #while event.type == pygame.MOUSEBUTTONDOWN:
        # win_type = winning_move(board, player_piece)[1]
        #while True:
           # print("c")
           # if event.type == pygame.MOUSEBUTTONDOWN:
               # print("d")
              #  sys.exit()

        pygame.time.wait(2000)