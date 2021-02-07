import random
from typing import List

import constants
from constants import LEFT, UP, DOWN, RIGHT


def get_pos(x, y=None) -> (int, int):
    if isinstance(x, tuple):
        x, y = x
    if isinstance(x, dict):
        x, y = x['x'], x['y']
    return x, y


def distance(a, b) -> float:
    xA, yA = get_pos(a)
    xB, yB = get_pos(b)
    return abs(xB - xA) + abs(yB - yA)


def directions(a, b) -> List[str]:
    x1, y1 = get_pos(a)
    x2, y2 = get_pos(b)
    moves = []
    if x1 > x2:
        moves.append(LEFT)
    elif x1 < x2:
        moves.append(RIGHT)
    if y1 > y2:
        moves.append(DOWN)
    elif y1 < y2:
        moves.append(UP)
    return moves


def tail_chase(board, possible_moves, space_per_direction, surroundings_per_direction, available_spaces_per_direction):
    returned_moves = {}
    for name, space in space_per_direction.items():
        my_tail = board.me.tail
        if my_tail in surroundings_per_direction[name] or my_tail in available_spaces_per_direction[name]:
            returned_moves[name] = possible_moves[name]
    if board.me.is_full_length:
        for name, move in get_moves(board.me.head, board=board).items():
            if move == board.me.tail:
                returned_moves[name] = move
    return returned_moves


def predict_moves(board, snake):
    me = board.me
    if snake != me:
        curr_pos = snake.head
        moves = board.safe_moves(curr_pos, safe_content=[board.MY_TAIL, board.ENEMY_TAIL, board.ENEMY_NEXT_MOVE]).values()
        for i in range(constants.PREDICTION_DEPTH):
            for pos in moves:
                if should_yield(snake, me, i + 1, distance(me.head, pos)):
                    board.board[pos] = board.ENEMY_NEXT_MOVE + i
                moves = board.safe_moves(pos, safe_content=[board.MY_TAIL, board.ENEMY_TAIL]).values()


def should_yield(there_snake, me, there_dist, my_dist):
    if there_dist > my_dist:  # I get there first
        return False
    elif there_dist < my_dist:  # They get there first Yield
        return True
    else:
        return len(there_snake) >= len(me)  # Don't yield if we are longer


def is_another_snake_closer(board, my_dist, target):
    return any([should_yield(snake, board.me, distance(snake.head, target), my_dist) for snake in board.enemy_snakes])


def find_food(board, possible_moves):
    my_head = board.me.head
    food_distance_map = [(target, distance(my_head, target)) for target in board.food]
    food_distance_map.sort(key=lambda target: target[1])
    for food, distance_to_food in food_distance_map:
        if not is_another_snake_closer(board, distance_to_food, food):
            moves_to_food = directions(my_head, food)
            for move in moves_to_food:
                if move in possible_moves.keys():
                    return move
    return None


def move_up(x, y):
    return x, y + 1


def move_down(x, y):
    return x, y - 1


def move_left(x, y):
    return x - 1, y


def move_right(x, y):
    return x + 1, y


def pick_move(possible_moves):
    if type(possible_moves) == type(dict()):
        return random.choice(list(possible_moves.keys()))
    else:
        return random.choice(list(possible_moves))


def get_moves(x, board):
    x, y = get_pos(x)
    moves = {}
    if board.on_board(move_up(x, y)):
        moves[UP] = move_up(x, y)
    if board.on_board(move_down(x, y)):
        moves[DOWN] = move_down(x, y)
    if board.on_board(move_left(x, y)):
        moves[LEFT] = move_left(x, y)
    if board.on_board(move_right(x, y)):
        moves[RIGHT] = move_right(x, y)
    return moves
