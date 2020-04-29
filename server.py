from board import Board
from getNextMove import MinimaxPlayer
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Server(BaseHTTPRequestHandler):
    
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        f = open("index.html", "rb")
        self.wfile.write(f.read())
    
    def do_POST(self):
        self._set_headers()
        if self.path == "/get-next-move":
            # 1.capture 2. get the next move 3.capture
            message = json.loads(self.rfile.read(int(self.headers.get('content-length'))))
            stone = 1 if message["last_stone_color"] == "black" else 2
            board_size = len(message["board"])
            last_point = message["last_point"]
            board_str = "".join("".join(map(str, row)) for row in message["board"])
            temp = last_point[0]*board_size+last_point[1]
            previous_board = board_str[:temp] + str(0) + board_str[temp + 1:]
            board = Board(board_str, stone, None, Board(previous_board, 1 if stone == 2 else 2, None, None))
            play = MinimaxPlayer()
            next_move: Optional[Tuple[int, int]] = play.get_best_move(board)
            if next_move is not None:   # Convert the number to a Python int
                next_move = (int(next_move[0]), int(next_move[1]))
            self.wfile.write(bytes(json.dumps(next_move), "utf-8"))
            
        if self.path == "/capture-stones":
            # capture
            message = json.loads(self.rfile.read(int(self.headers.get('content-length'))))
            board_str = "".join("".join(map(str, row)) for row in message["board"])
            stone = 1 if message["stone_color"] == "black" else 2
            opponent_stone = 1 if stone == 2 else 2
            board = Board(board_str, stone, None, None)
            board_str1 = board.capture(opponent_stone)
            new_board = Board(board_str1, stone, None, None)
            board_str2 = new_board.capture(stone)
            list_del_stones = []
            for i in range(len(board_str)):
                if board_str[i] != board_str2[i]:
                    list_del_stones.append((i//board.board_size, i%board.board_size))
            self.wfile.write(bytes(json.dumps(list_del_stones), "utf-8"))
            
        
if __name__ == "__main__":
    httpd = HTTPServer(('localhost', 4830), Server)
    httpd.serve_forever()