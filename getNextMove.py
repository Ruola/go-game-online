from typing import Dict, Deque, List, Tuple, Set, Optional

import numpy as np
import copy
import operator
import collections
import heapq
from board import Board

KOMI = 2.5


class MinimaxPlayer():

    STONE_PRIORITY = [(2, 2), (2, 3), (3, 2), (2, 1), (1, 2), (1, 1), (1, 3),
                      (3, 1), (3, 3), (0, 2), (4, 2), (1, 0), (0, 1), (0, 3),
                      (1, 4), (3, 0), (4, 1), (4, 3), (3, 4), (2, 0), (2, 4),
                      (0, 0), (0, 4), (4, 0), (4, 4)]
    STONE = 0

    def __init__(self):
        self.MAX_LEVEL = 2

    def _get_score(self, board: str, stone: int) -> float:
        return np.count_nonzero(
            np.asarray(list(board)) == str(stone)) - np.count_nonzero(
                np.asarray(list(board)) ==
                ("1" if stone == 2 else "2")) + (KOMI if stone == 2 else -KOMI)

    def _get_next_move(self, curr_board: Board, level: int) -> List[Board]:
        if level == 0:
            self.STONE = 1 if curr_board.stone == 2 else 2
        # build children
        for (i, j) in self.STONE_PRIORITY:
            ii = i * curr_board.board_size + j
            is_valid, temp = curr_board.is_valid_move((i, j))
            if is_valid == False or temp is None:
                continue
            if level + 1 == self.MAX_LEVEL:
                if self._get_score(
                        curr_board.board, curr_board.stone
                ) < 0:  # try to protect my stones and max the liberties
                    if temp.stone == self.STONE:
                        num_my_liberties = np.sum(
                            temp.my_liberty()) / np.count_nonzero(
                                temp.my_liberty())
                    else:
                        num_my_liberties = np.sum(
                            temp.opponent_liberty()) / np.count_nonzero(
                                temp.opponent_liberty())
                    num_liberty = num_my_liberties
                else:  # try to aggresively attack opponents
                    if temp.stone == self.STONE:
                        num_my_liberties = np.sum(
                            temp.my_liberty()) / np.count_nonzero(
                                temp.my_liberty())
                        num_opponent_liberties = np.sum(
                            temp.opponent_liberty()) / np.count_nonzero(
                                temp.opponent_liberty())
                    else:
                        num_opponent_liberties = np.sum(
                            temp.my_liberty()) / np.count_nonzero(
                                temp.my_liberty())
                        num_my_liberties = np.sum(
                            temp.opponent_liberty()) / np.count_nonzero(
                                temp.opponent_liberty())
                    num_liberty = num_my_liberties - num_opponent_liberties
                temp.utility = (self._get_score(temp.board,
                                                self.STONE), num_liberty)
            curr_board.child.append(temp)
        if len(curr_board.child) == 0:
            if self._get_score(curr_board.board, self.STONE) >= 0:
                if curr_board.stone == self.STONE:
                    num_my_liberties = np.sum(
                        curr_board.my_liberty()) / np.count_nonzero(
                            curr_board.my_liberty())
                else:
                    num_my_liberties = np.sum(
                        curr_board.opponent_liberty()) / np.count_nonzero(
                            curr_board.opponent_liberty())
                num_liberty = num_my_liberties
            else:
                if curr_board.stone == self.STONE:
                    num_my_liberties = np.sum(
                        curr_board.my_liberty()) / np.count_nonzero(
                            curr_board.my_liberty())
                    num_opponent_liberties = np.sum(
                        curr_board.opponent_liberty()) / np.count_nonzero(
                            curr_board.opponent_liberty())
                else:
                    num_opponent_liberties = np.sum(
                        curr_board.my_liberty()) / np.count_nonzero(
                            curr_board.my_liberty())
                    num_my_liberties = np.sum(
                        curr_board.opponent_liberty()) / np.count_nonzero(
                            curr_board.opponent_liberty())
                num_liberty = num_my_liberties - num_opponent_liberties
            curr_board.utility = (self._get_score(curr_board.board,
                                                  self.STONE), num_liberty)
        return curr_board.child

    def _get_min(self, state: Board, alpha, beta,
                 level) -> Tuple[float, float]:
        if state.utility is not None:
            return state.utility
        self._get_next_move(state, level)
        if state.utility is not None:  # when state does not have children
            return state.utility
        v = (float("inf"), float("inf"))
        for x in state.child:
            v = min(v, self._get_max(x, alpha, beta, level + 1)[0])
            if v <= alpha:
                return v
            beta = min(beta, v)
        state.utility = v
        return v

    def _get_max(self, state: Board, alpha, beta,
                 level) -> Tuple[Tuple[float, float], Optional[Board]]:
        if state.utility is not None:
            return (state.utility, state)
        self._get_next_move(state, level)
        if state.utility is not None:  # when state does not have children
            return state.utility
        u = (-float("inf"), -float("inf"))
        max_board = None
        for x in state.child:
            temp = self._get_min(x, alpha, beta, level + 1)
            if temp > u:
                u = temp
                max_board = x
            if u >= beta:
                return (u, max_board)
            alpha = max(alpha, u)
        state.utility = u
        return (u, max_board)

    def _make_decision(self, game_tree: Board) -> Optional[Board]:
        _, max_board = self._get_max(game_tree, (-float("inf"), -float("inf")),
                                     (float("inf"), float("inf")), 0)
        return max_board

    def get_best_move(self, opponent_board: Board) -> Optional[Tuple[int, int]]:
        # return the best movement
        self.STONE = 1 if opponent_board.stone == 2 else 2
        # modify stone_priority
        # if opponent has points with liberty 2, then check whether my stone can reduce the liberty with max score
        my_stone_priority = copy.copy(self.STONE_PRIORITY)
        l1, l2 = np.nonzero(np.asarray(opponent_board.my_liberty()) == 2)
        visited: Set[Tuple[int, int]] = set()
        for x in zip(l1, l2):
            for next_move in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                next = next_move[0] + x[0], next_move[1] + x[1]
                if next[0] < 0 or next[0] >= opponent_board.board_size or next[
                        1] < 0 or next[1] >= opponent_board.board_size:
                    continue
                if next in visited:
                    continue
                visited.add(next)
                if opponent_board.board[next[0] * opponent_board.board_size +
                                        next[1]] == "0":
                    # check the score
                    my_stone_priority.pop(my_stone_priority.index(next))
                    my_stone_priority.insert(0, next)
        self.STONE_PRIORITY = my_stone_priority

        num_zeros = np.count_nonzero(
            np.asarray(list(opponent_board.board)) == "0")

        max_point = None
        max_board = None
        if num_zeros == 25:  # first stone
            max_point = (2, 2)
        elif num_zeros >= 21 and self.STONE == 1:
            for point in [(2, 2), (2, 3), (3, 2), (2, 1), (1, 2)]:
                if opponent_board.board[point[0] * opponent_board.board_size +
                                        point[1]] == "0":
                    max_board = opponent_board.add_stone(point[0], point[1])
                    max_point = point
                    break
        else:
            max_board = self._make_decision(opponent_board)
            if max_board is not None:
                max_point = max_board.point
        return max_point


if __name__ == "main":
    with open("input.txt", "r") as f:
        lines = f.readlines()
    STONE = int(lines[0])
    my_previous_board_list = ""
    board_size = 5
    for i in range(1, board_size + 1):
        my_previous_board_list += lines[i][:-1]
    my_previous_board = Board(my_previous_board_list, STONE, None, None)
    opponent_board_list = ""
    for i in range(board_size + 1, board_size * 2 + 1):
        if lines[i][-1] == "\n":
            opponent_board_list += lines[i][:-1]
        else:
            opponent_board_list += lines[i]
    opponent_board = Board(opponent_board_list, 1 if STONE == 2 else 2, None,
                           my_previous_board)

    temp = np.nonzero(
        np.asarray(list(opponent_board_list)) != np.asarray(
            list(my_previous_board_list)))
    if temp[0] is not None and len(temp[0]) > 0:
        for ii in temp[0]:
            if opponent_board_list[ii] == str(opponent_board.stone):
                opponent_board.point = (ii // board_size,
                                        ii % board_size)
                break

    player = MinimaxPlayer()
    max_point = player.get_best_move(opponent_board, STONE)
    with open("output.txt", "w") as f:
        if max_point is None:
            f.write("PASS")
        else:
            f.write("{},{}".format(max_point[0], max_point[1]))
