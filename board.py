from typing import Dict, Deque, List, Tuple, Set, Optional
import math

class Board:

    def __init__(self, board: str, stone: int, my_previous: Optional["Board"],
                 opponent: Optional["Board"]):
        self.board = board
        self.stone = stone
        self.my_previous_board = my_previous
        self.opponent_board = opponent
        self.point: Optional[Tuple[int, int]] = None  # If None, means PASS
        self.child: List[Board] = []
        self.utility: Optional[Tuple[float, float]] = None
        self.board_size = int(math.sqrt(len(board)))

    def __hash__(self):
        return hash(self.board)

    def __eq__(self, other):
        if self.board == other.board and self.stone == other.stone:
            return True
        return False

    def is_ko(self) -> bool:
        if self.my_previous_board is None:
            raise ValueError("self.my_previous_board is None")
        return self == self.my_previous_board

    def add_stone(self, i: int, j: int) -> "Board":
        # when to expend children (opponent's board),
        # need to add opponent's stone based on current board.
        stone = 1 if self.stone == 2 else 2
        if i < 0 or i >= self.board_size or j < 0 or j >= self.board_size:  # PASS
            temp = Board(self.board, stone, self.opponent_board, self)
            temp.point = None
            return temp
        temp_board_list = self.board[0:i * self.board_size + j] + str(
            stone) + self.board[i * self.board_size + j + 1:]
        temp = Board(temp_board_list, stone, self.opponent_board, self)
        temp.point = (i, j)
        temp.board = temp.capture(1 if stone == 2 else 2)
        temp.board = temp.capture(stone)
        return temp

    def _dfs(self, be_captured_stone: str, point: Tuple[int, int],
             visited) -> int:
        # Used by _compute_liberty
        if point in visited:
            return 0
        count = 0
        visited.add(point)
        temp = self.board[point[0] * self.board_size + point[1]]
        if temp == ("1" if be_captured_stone == "2" else "2"):
            return 0
        if temp == "0":
            return 1
        for next_move in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            next = next_move[0] + point[0], next_move[1] + point[1]
            if next in visited:
                continue
            if next[0] >= 0 and next[0] < self.board_size and next[
                    1] >= 0 and next[1] < self.board_size:
                count += self._dfs(be_captured_stone, next, visited)
        return count

    def _compute_liberty(self, be_captured_stone: str) -> List[List[int]]:
        # curr liberty = sum of liberties of all neighbors
        # total_visited: visited stones in all rounds
        # visited: visited stones in this round
        liberty = [[0] * self.board_size for i in range(self.board_size)]
        total_visited: Set[Tuple[int, int]] = set()
        for ii in range(self.board_size * self.board_size):
            i, j = ii // self.board_size, ii % self.board_size
            if self.board[ii] == be_captured_stone and (
                    i, j) not in total_visited:
                visited: Set[Tuple[int, int]] = set()
                count_liberty = self._dfs(be_captured_stone, (i, j), visited)
                total_visited.update(visited)
                for x in visited:
                    # capture all elements in visited
                    if self.board[
                            x[0] * self.board_size +
                            x[1]] == be_captured_stone and count_liberty != 0:
                        liberty[x[0]][x[1]] = count_liberty
        return liberty

    def my_liberty(self):
        if not hasattr(self, "_my_liberty"):
            self._my_liberty = self._compute_liberty(str(self.stone))
        return self._my_liberty

    def opponent_liberty(self):
        if not hasattr(self, "_opponent_liberty"):
            self._opponent_liberty = self._compute_liberty("1" if self.stone ==
                                                           2 else "2")
        return self._opponent_liberty

    def capture(self, be_captured_stone: int) -> str:
        # remove all died stones
        new_board_list = self.board
        if be_captured_stone == self.stone:
            liberty_list = self.my_liberty()
            delattr(self, "_my_liberty")
        else:
            liberty_list = self.opponent_liberty()
            delattr(self, "_opponent_liberty")
        for ii in range(self.board_size * self.board_size):
            i, j = ii // self.board_size, ii % self.board_size
            if i < 0 or i >= self.board_size or j < 0 or j >= self.board_size:
                continue
            if self.board[ii] != str(be_captured_stone):
                continue
            if liberty_list[i][j] == 0:
                new_board_list = new_board_list[:ii] + "0" + new_board_list[
                    ii + 1:]
        return new_board_list

    def is_valid_move(self, point: Tuple[int, int]
                      ) -> Tuple[bool, Optional["Board"]]:
        i, j = point
        ii = i * self.board_size + j
        if i < 0 or i >= self.board_size or j < 0 or j >= self.board_size:
            return False, None
        if self.board[i * self.board_size + j] != "0":
            return False, None
        temp = self.add_stone(i, j)
        if temp.board[ii] == "0" or temp.is_ko():  # suicide or KO
            return False, None
        return True, temp
