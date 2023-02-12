import copy
from math import log, sqrt, inf
from random import choice

import numpy as np
from rich.console import Console
from rich.progress import track
from rich.table import Table
import random as rd

class Node(object):
    def __init__(self, logic, board, move=(None, None), wins=0, visits=0, children=None):
        # Save the #wins:#visited ratio
        self.state = board
        self.move = move
        self.wins = wins
        self.visits = visits
        self.children = children or []
        self.parent = None
        self.untried_moves = logic.get_possible_moves(board)

    def add_child(self, child):
        child.parent = self
        self.children.append(child)


class STRAT:
    def __init__(self, logic, ui, board_state, starting_player):
        self.logic = logic
        self.ui = ui
        self.root_state = copy.copy(board_state)
        self.state = copy.copy(board_state)
        self.starting_player = starting_player
        self.players = [1, 2]
        self.players.remove(self.starting_player)
        self.other_player = self.players[0]
        self.turn = {True: self.starting_player, False: self.other_player}
        self.turn_state = True

    def start(self) -> tuple:
        root_node = Node(self.logic, self.root_state)

        if self.starting_player is self.ui.BLACK_PLAYER:
            #x, y = rd.choice(self.logic.get_possible_moves(self.logic.logger))
            x, y = self.get_best_move(root_node, self.logic.ui.board_size,  True)
            #x, y = self.get_best_move_ab(root_node, self.logic.ui.board_size, float('-inf'), float('inf'), True)
        elif self.starting_player is self.ui.WHITE_PLAYER:
            #x, y = rd.choice(self.logic.get_possible_moves(self.logic.logger))
            x, y = self.get_best_move(root_node, self.logic.ui.board_size,  False)
            #x, y = self.get_best_move(root_node, self.logic.ui.board_size, float('-inf'), float('inf'), False)

        return (x, y)

    def minimax(self, cur_node: Node, max_depth: int,  maxmizingPlayer: bool) -> float:
        if max_depth == 0 or self.logic.get_possible_moves(self.logic.logger) == []:
            return self.getHeuristicScore(cur_node)
        if maxmizingPlayer:
            bestScore = -inf
            for child in cur_node.children:
                value = self.minimax(child, max_depth - 1, False)
                print(self.minimax(child, max_depth - 1,  False))
                bestScore = max(bestScore, value)
            return bestScore
        else:
            bestScore = inf
            for child in cur_node.children:
                value = self.minimax(child, max_depth - 1, True)
                print(self.minimax(child, max_depth - 1, True))
                bestScore = min(bestScore, value)
            return bestScore

    def minimax_ab(self, cur_node: Node, max_depth: int, alpha: float, beta: float, maxmizingPlayer: bool) -> float:
        alpha = alpha
        beta = beta
        if max_depth == 0 or self.logic.get_possible_moves(self.logic.logger) == []:
            return self.getHeuristicScore(cur_node)
        if maxmizingPlayer:
            value = -inf
            for child in cur_node.children:
                value = max(value,self.minimax_ab(child, max_depth - 1,alpha, beta, False))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = inf
            for child in cur_node.children:
                value = min(value,self.minimax_ab(child, max_depth - 1,alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    def getHeuristicScore(self, cur_node: Node) -> float:
        return self.getShortestPathScore(cur_node.parent.move)


    def compare_players(self, players, num_games):
        player1_wins = 0
        player2_wins = 0
        for i in range(num_games):
            board = []
            for i in range(11):
                row = [0] * 11
                board.append(row)
            current_player = 1
            while not self.get_winner():
                if current_player == 1:
                    board = players[0](board, current_player)
                    current_player = 2
                else:
                    board = players[1](board, current_player)
                    current_player = 1
            if self.get_winner:
                player1_wins += 1
            else:
                player2_wins += 1
        if player1_wins > player2_wins:
            return 1
        elif player1_wins < player2_wins:
            return 2
        else:
            return 0



    def get_best_move(self, cur_node: Node, max_depth: int, maxmizingPlayer: bool) -> tuple:
        val = self.minimax(cur_node, max_depth,  maxmizingPlayer)
        # print(val)
        return rd.choice(cur_node.untried_moves)

    def get_best_move_ab(self, cur_node: Node, max_depth: int, alpha: float, beta: float, maxmizingPlayer: bool) -> tuple:
        val = self.minimax_ab(cur_node, max_depth, alpha, beta, maxmizingPlayer)
        # print(val)
        return rd.choice(cur_node.untried_moves)

    def getShortestPathScore(self, coordinates: tuple) -> float:
        (x, y) = coordinates
        neighbours = self.logic.get_neighbours(coordinates)
        if not neighbours:
            return 0
        for neighbour in neighbours:
            (x1, y1) = neighbour
            if x1 == x and x1 == self.ui.board_size - 1:
                return 0
            if self.logic.logger[x1][y1] == 2:
                return 1 + self.getShortestPathScore(neighbour)
            else:
                return 2 + self.getShortestPathScore(neighbour)