from typing import Dict

import numpy as np

import util
from constants import PREDICTION_DEPTH, ENEMY_TAIL, MY_TAIL, ENEMY_NEXT_MOVE, FOOD, MY_BODY, ENEMY_BODY, ENEMY_HEAD, FREE_SPACE
from util import get_pos, distance


class Game:
    def __init__(self, data):
        self.data = data
        self.width = data['board']['width']
        self.height = data['board']['height']
        self.food = [get_pos(food) for food in data['board']['food']]
        self.board = np.zeros((self.width, self.height), dtype=np.int16)
        self.me = Snake(data['you'], self, is_you=True)
        self.enemy_snakes = [Snake(snake, self) for snake in data['board']['snakes'] if snake['id'] != self.me.snake_id]
        self.process_board()

    def __getitem__(self, index):
        return self.board[index]

    def process_board(self):
        self.add_food_to_board()
        self.add_my_snake_to_board()
        self.add_enemy_snakes_to_board()

    def add_food_to_board(self):
        for food in self.food:
            self.board[food] = FOOD

    def add_my_snake_to_board(self):
        for pos in self.me.body:
            self.board[pos] = MY_BODY
        print("if not {snake.is_full_length} and {self.board[snake.tail]} == FREE_SPACE : to set tail")  # todo im not sure on this
        if not self.me.is_full_length and self.board[self.me.tail] == FREE_SPACE:
            self.board[self.me.tail] = MY_TAIL

    def add_enemy_snakes_to_board(self):
        for snake in self.enemy_snakes:
            for pos in snake.body:
                self.board[pos] = ENEMY_BODY
            self.board[snake.tail] = ENEMY_TAIL
            self.board[snake.head] = ENEMY_HEAD
            if snake.length >= self.me.length or distance(self.me.head, snake.head) > PREDICTION_DEPTH:
                # only predict snakes that can kill us
                other_snake_moves = self.safe_moves(snake.head, safe_content=[]).values()
                for move in other_snake_moves:
                    self.board[move] = ENEMY_NEXT_MOVE
                util.predict_moves(self, snake)

    def safe_moves(self, pos, safe_content):
        x, y = get_pos(pos)
        possible_moves = util.get_moves((x, y), board=self)
        return {name: move for name, move in possible_moves.items() if self.is_safe(move, safe_content)}

    def on_board(self, pos):
        x, y = get_pos(pos)
        return x in range(self.width) and y in range(self.height)

    def is_safe(self, pos, safe_content):
        if not self.on_board(pos):
            return False
        contents = self[pos]
        if contents in [FOOD, FREE_SPACE] or contents in safe_content:
            return True
        snake_at_pos = self.get_snake_at(pos)
        #  is it a tail i can chase?
        return snake_at_pos is not None \
               and snake_at_pos.is_full_length \
               and (self[pos] == ENEMY_TAIL or self[pos] == MY_TAIL) \
               and not util.is_another_snake_closer(self, distance(self.me.head, pos), pos)

    def get_snake_at(self, pos):
        for snake in self.enemy_snakes + [self.me]:
            if pos in snake:
                return snake

    def get_enemy_snakes(self):
        return [snake for snake in self.enemy_snakes if not snake.is_me]


class Snake:
    def __init__(self, data, board, is_you=False):
        self.snake_id = data['id']
        self.name = data['name']
        self.health = data['health']
        self.head = get_pos(data['head'])
        self.body = [get_pos(pos) for pos in data['body']]
        self.tail = get_pos(data['body'][-1])
        self.length = data['length']
        self.is_me = is_you
        self.possible_moves = util.get_moves(self.head, board=board)
        self.is_full_length = len(set(self.body)) == len(self.body)

    def __str__(self):
        return self.name

    def __len__(self):
        return len(self.body)

    def __eq__(self, other):
        return self.snake_id == other.snake_id

    def __contains__(self, pos):
        return pos in self.body


