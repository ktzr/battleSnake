"""
Constants used to define directions
"""
LEFT = "left"
RIGHT = "right"
UP = "up"
DOWN = "down"

ALL_MOVES = [UP, DOWN, LEFT, RIGHT]


PREDICTION_DEPTH = 3

# todo Should be an Enum
FREE_SPACE = 0
FOOD = 1

MY_BODY = 2
MY_TAIL = 3

ENEMY_HEAD = 4
ENEMY_BODY = 5
ENEMY_TAIL = 6
ENEMY_NEXT_MOVE = 7
