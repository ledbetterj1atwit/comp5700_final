class Piece:
    def __init__(self, color, location):
        self.color = color
        self.location = location
        self.kinged = False

    def __str__(self):
        if self.kinged:
            return "K" + self.color
        else:
            return " " + self.color

    def __repr__(self):
        return f"{self.__str__()}: {self.location}"


class Board:
    def __init__(self, size=4, peice_rows=1):
        self.size = size
        self.pieces = []
        for i in range(size):
            for j in range(peice_rows):
                self.pieces.append(Piece("B", (i, j)))
                self.pieces.append(Piece("W", (i, size - 1 - j)))

    def print_board(self):
        cols = ""
        for j in range(self.size):
            cols += f" {j} "
        print(f"   {cols} ")
        print(f"  {'-' * (self.size * 3)}-")
        for j in range(self.size):
            row = []
            for i in range(self.size):
                blank = True
                for p in self.pieces:
                    if p.location == (i, j):
                        row.append(str(p))
                        blank = False
                        break
                if blank:
                    row.append("  ")
            print(f"{j} |" + "|".join(row) + "|")
        print(f"  {'-' * (self.size * 3)}-")

    def move(self, current, move):
        selected = None
        for p in self.pieces:
            if p.location == current:
                selected = p
                break
        if selected is None:
            return False
        new = None
        captured = None
        if move == "fl":
            if selected.color == "W" or selected.color == "KW":
                new = (selected.location[0] - 1, selected.location[1] - 1)
            elif selected.color == "B" or selected.color == "KB":
                new = (selected.location[0] - 1, selected.location[1] + 1)
        elif move == "fr":
            if selected.color == "W" or selected.color == "KW":
                new = (selected.location[0] + 1, selected.location[1] - 1)
            elif selected.color == "B" or selected.color == "KB":
                new = (selected.location[0] + 1, selected.location[1] + 1)
        elif move == "bl":
            if selected.color == "KW":
                new = (selected.location[0] - 1, selected.location[1] + 1)
            elif selected.color == "KB":
                new = (selected.location[0] - 1, selected.location[1] - 1)
        elif move == "br":
            if selected.color == "KW":
                new = (selected.location[0] + 1, selected.location[1] + 1)
            elif selected.color == "KB":
                new = (selected.location[0] + 1, selected.location[1] - 1)
        elif move == "cfl":
            if selected.color == "W" or selected.color == "KW":
                new = (selected.location[0] - 2, selected.location[1] - 2)
                captured = (selected.location[0] - 1, selected.location[1] - 1)
            elif selected.color == "B" or selected.color == "KB":
                new = (selected.location[0] - 2, selected.location[1] + 2)
                captured = (selected.location[0] - 1, selected.location[1] + 1)
        elif move == "cfr":
            if selected.color == "W" or selected.color == "KW":
                new = (selected.location[0] + 2, selected.location[1] - 2)
                selected = (selected.location[0] + 1, selected.location[1] - 1)
            elif selected.color == "B" or selected.color == "KB":
                new = (selected.location[0] + 2, selected.location[1] + 2)
                captured = (selected.location[0] + 1, selected.location[1] + 1)
        elif move == "cbl":
            if selected.color == "KW":
                new = (selected.location[0] - 2, selected.location[1] + 2)
                captured = (selected.location[0] - 1, selected.location[1] + 1)
            elif selected.color == "KB":
                new = (selected.location[0] - 2, selected.location[1] - 2)
                captured = (selected.location[0] - 1, selected.location[1] - 1)
        elif move == "cbr":
            if selected.color == "KW":
                new = (selected.location[0] + 2, selected.location[1] + 2)
                captured = (selected.location[0] + 1, selected.location[1] + 1)
            elif selected.color == "KB":
                new = (selected.location[0] + 2, selected.location[1] - 2)
                captured = (selected.location[0] + 1, selected.location[1] - 1)

        if new[0] < 0 or new[0] >= self.size or new[1] < 0 or new[1] >= self.size:  # OOB
            return False
        if len([p for p in self.pieces if p.location == new]) > 0:  # Overlapping Piece.
            return False
        if captured is not None:  # Attempting to capture.
            to_capture = None
            for p in self.pieces:
                if p.location == captured:
                    to_capture = p
                    break
            if to_capture is None:  # Nothing to capture.
                return False
            if to_capture.color == selected.color:  # Capturing own piece.
                return False
            self.pieces.remove(to_capture)
        if selected.color == "B" and new[1] == self.size-1:
            selected.kinged = True
        if selected.color == "W" and new[1] == 0:
            selected.kinged = True
        selected.location = new
        return True


if __name__ == "__main__":
    board = Board()
    print(board.pieces)
    board.print_board()
    game_over = False
    print("Move: <piece x> <piece y> <movement>")
    print("Movement: c for capture, f/b for piece forward, l/r for left or right")
    print("          so capturing forward and right is \"cfr\"")
    while not game_over:
        move = input("Move?: ")
        move = move.split(" ")
        result = board.move((int(move[0]), int(move[1])), move[2])
        if not result:
            print("Invalid Move")
        else:
            board.print_board()
        w_count = 0
        b_count = 0
        for p in board.pieces:
            if p.color == "W":
                w_count += 1
            if p.color == "B":
                b_count += 1
        if w_count == 0:
            print("Black wins.")
            game_over = True
        if b_count == 0:
            print("White wins.")
            game_over = True
