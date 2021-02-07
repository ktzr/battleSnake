import os
import cherrypy

import bfs
import constants
import util
from gameboard import GameBoard, ENEMY_NEXT_MOVE


class Battlesnake(object):

    def __init__(self):
        self.won = 0
        self.lost = 0

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {
            "apiversion": "1",
            "author": "ktzr",
            "color": "#22abba",
            "head": "safe",
            "tail": "round-bum",
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json

        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        data = cherrypy.request.json
        move = find_next_move(data)

        print(f"MOVE: {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json
        if data["you"] in data["board"]["snakes"]:
            print("won")
            self.won += 1
        else:
            print("lost")
            self.lost += 1
        print("END")
        return "ok"


def find_next_move(data):
    board = GameBoard(data)
    should_try_to_get_food = True
    safe_content = []

    possible_moves = bfs.search_for_moves(board, board.me.head, safe_content=safe_content)

    for enemy_move in range(ENEMY_NEXT_MOVE + constants.PREDICTION_DEPTH, ENEMY_NEXT_MOVE - 1, -1):
        if len(possible_moves) == 0:  # no moves - risk hitting enemy prefer hitting them in 4 moves rather then 3 and so on
            safe_content.append(enemy_move)
            possible_moves = bfs.search_for_moves(board, board.me.head, safe_content=safe_content)
            should_try_to_get_food = False

    move = None
    if len(possible_moves) == 1:
        print(f"Only one possible picking that: {possible_moves}")
        move = possible_moves.keys()[0]
    if move is None and should_try_to_get_food and len(possible_moves) > 0:
        print(f"Looking for food: {possible_moves}")
        move = util.find_food(board, possible_moves)
    if move is None and len(possible_moves) > 0:
        # multiple possible moves picking one at random todo add weights to pick the least bad, ok move
        print(f"No multiple moves, picking random one: {possible_moves}")
        move = util.pick_move(possible_moves)
    if move is None:
        # no good moves picking a random move todo add weights to pick the least bad, bad move
        print("No safe move possible, picking random move")
        move = util.pick_move(constants.ALL_MOVES)
    print(f"Move: {move}")
    return move


if __name__ == "__main__":
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update({"server.socket_port": int(os.environ.get("PORT", "8080"))})
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(Battlesnake())
