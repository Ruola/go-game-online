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
        message = json.loads(self.rfile.read(int(self.headers.get('content-length'))))
        stone = 1 if message["last_stone_color"] == "black" else 2
        board_size = len(message["board"])
        last_point = message["last_point"]
        board_str = "".join("".join(map(str, row)) for row in message["board"])
        temp = last_point[0]*board_size+last_point[1]
        previous_board = board_str[:temp] + str(0) + board_str[temp + 1:]
        board = Board(board_str, stone, None, Board(previous_board, 1 if stone == 2 else 2, None, None))
        play = MinimaxPlayer()
        next_move: Tuple[int, int] = play.get_best_move(board)
        self.wfile.write(bytes(json.dumps(next_move), "utf-8"))
    
if __name__ == "__main__":
    httpd = HTTPServer(('localhost', 4838), Server)
    httpd.serve_forever()
    