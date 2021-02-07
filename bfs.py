import util
from util import tail_chase


def search_for_moves(board, curr_pos, safe_content):
    possible_moves = board.safe_moves(curr_pos, safe_content=safe_content)
    space_per_direction, surroundings_per_direction, available_spaces_per_direction = compare_moves(board, possible_moves, safe_content)

    tail_chase_moves = tail_chase(board, possible_moves, space_per_direction, surroundings_per_direction, available_spaces_per_direction)
    if len(tail_chase_moves) > 0:
        possible_moves = tail_chase_moves
    elif len(possible_moves) > 1:
        possible_moves = select_roomiest_moves(possible_moves, space_per_direction)
    return possible_moves


def select_roomiest_moves(possible_moves, space_per_direction):
    most_free_space = max(space_per_direction.values())
    return {name: possible_moves[name] for name, space in space_per_direction.items() if space == most_free_space}


def compare_moves(board, possible_moves, safe_content):
    space_per_direction = {}
    surroundings_per_direction = {}
    available_spaces_per_direction = {}
    for name, move in possible_moves.items():
        free_space, available_spaces, surroundings = bfs(board, move, safe_content)
        space_per_direction[name] = free_space
        surroundings_per_direction[name] = surroundings
        available_spaces_per_direction[name] = available_spaces
    return space_per_direction, surroundings_per_direction, available_spaces_per_direction


def bfs(board, pos, safe_content):
    free_space = 0
    available_spaces = set()
    queue = [pos]
    surroundings = set()
    if not board.is_safe(pos, safe_content):
        return free_space, available_spaces, surroundings
    while len(queue) > 0:
        pos = queue.pop()
        potential_moves = util.get_moves(pos, board=board).values()
        for move in potential_moves:
            if move not in available_spaces and board.is_safe(move, safe_content=safe_content):
                available_spaces.add(move)
                queue.append(move)
                free_space += 1
            elif move not in surroundings:
                surroundings.add(move)
    return free_space, available_spaces, surroundings
