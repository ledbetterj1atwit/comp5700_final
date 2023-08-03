import PDDL


class Piece:
    last_discriminator = 0

    def __init__(self, color, location):
        self.color = color
        self.location = location
        Piece.last_discriminator += 1
        self.discriminator = Piece.last_discriminator
        self.pddl_name = f"{self.color}{self.discriminator}"
        self.kinged = False
        self.captured = False

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
                    if p.location == (i, j) and not p.captured:
                        row.append(str(p))
                        blank = False
                        break
                if blank:
                    row.append("  ")
            print(f"{j} |" + "|".join(row) + "|")
        print(f"  {'-' * (self.size * 3)}-")

    def move(self, current, direction):
        selected = None
        for p in self.pieces:
            if p.location == current:
                selected = p
                break
        if selected is None:
            return False
        if direction == "kill":
            self.pieces.remove(selected)
            return True
        new = None
        captured = None
        if direction == "fl":
            if selected.color == "W":
                new = (selected.location[0] - 1, selected.location[1] - 1)
            elif selected.color == "B":
                new = (selected.location[0] - 1, selected.location[1] + 1)
        elif direction == "fr":
            if selected.color == "W":
                new = (selected.location[0] + 1, selected.location[1] - 1)
            elif selected.color == "B":
                new = (selected.location[0] + 1, selected.location[1] + 1)
        elif direction == "bl":
            if selected.color == "W" and selected.kinged:
                new = (selected.location[0] - 1, selected.location[1] + 1)
            elif selected.color == "B" and selected.kinged:
                new = (selected.location[0] - 1, selected.location[1] - 1)
        elif direction == "br":
            if selected.color == "W" and selected.kinged:
                new = (selected.location[0] + 1, selected.location[1] + 1)
            elif selected.color == "B" and selected.kinged:
                new = (selected.location[0] + 1, selected.location[1] - 1)
        elif direction == "cfl":
            if selected.color == "W":
                new = (selected.location[0] - 2, selected.location[1] - 2)
                captured = (selected.location[0] - 1, selected.location[1] - 1)
            elif selected.color == "B":
                new = (selected.location[0] - 2, selected.location[1] + 2)
                captured = (selected.location[0] - 1, selected.location[1] + 1)
        elif direction == "cfr":
            if selected.color == "W":
                new = (selected.location[0] + 2, selected.location[1] - 2)
                selected = (selected.location[0] + 1, selected.location[1] - 1)
            elif selected.color == "B":
                new = (selected.location[0] + 2, selected.location[1] + 2)
                captured = (selected.location[0] + 1, selected.location[1] + 1)
        elif direction == "cbl":
            if selected.color == "W" and selected.kinged:
                new = (selected.location[0] - 2, selected.location[1] + 2)
                captured = (selected.location[0] - 1, selected.location[1] + 1)
            elif selected.color == "B" and selected.kinged:
                new = (selected.location[0] - 2, selected.location[1] - 2)
                captured = (selected.location[0] - 1, selected.location[1] - 1)
        elif direction == "cbr":
            if selected.color == "W" and selected.kinged:
                new = (selected.location[0] + 2, selected.location[1] + 2)
                captured = (selected.location[0] + 1, selected.location[1] + 1)
            elif selected.color == "B" and selected.kinged:
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
        if selected.color == "B" and new[1] == self.size - 1:
            selected.kinged = True
        if selected.color == "W" and new[1] == 0:
            selected.kinged = True
        selected.location = new
        return True

    def position_to_frees(self, x, y, text="piece", color="B"):
        frees = []
        for i in range(x):
            frees.append(f"LFree({text})")
        for i in range(self.size - x - 1):
            frees.append(f"RFree({text})")
        if color == "B":
            for i in range(y):
                frees.append(f"BFree({text})")
            for i in range(self.size - y - 1):
                frees.append(f"FFree({text})")
        else:
            for i in range(y + 1):
                frees.append(f"FFree({text})")
            for i in range(self.size - y - 1):
                frees.append(f"BFree({text})")
        return frees

    def generate_capture_pddl(self, piece):
        attack_positions = [
            (piece.location[0] - 1, piece.location[1] - 1, "FR"),  # Back Left of p
            (piece.location[0] + 1, piece.location[1] - 1, "FL"),  # Back Right of p
            (piece.location[0] - 1, piece.location[1] + 1, "BR"),  # Front Left of p
            (piece.location[0] + 1, piece.location[1] + 1, "BL"),  # Front Right of p
        ]
        actions = []
        for pos in attack_positions:
            if pos[0] < 0 or pos[0] >= self.size:
                continue  # Remove if OOB.
            elif pos[1] < 0 or pos[1] >= self.size:
                continue  # Remove if OOB.
            elif len([x for x in self.pieces if x.location == pos and x.color == piece.color]) > 0:
                continue  # Remove if attack position blocked.

            landing_x = piece.location[0] - (pos[0] - piece.location[0])
            landing_y = piece.location[1] - (pos[1] - piece.location[1])
            # if landing_x < 0 or landing_x >= self.size:
            #     continue  # Remove if landing position is OOB.
            # elif landing_y < 0 or landing_y >= self.size:  # Skipping to prevent deadlock
            #     continue  # Remove if landing position is OOB.
            if len([x for x in self.pieces if x.location == (landing_x, landing_y)]) > 0:
                continue  # Remove if landing position is unreachable.

            act = (f"Capture{piece.pddl_name}_{pos[2]} piece\n"
                   f"pre: {' '.join(self.position_to_frees(pos[0], pos[1]))} Own(piece)\n"
                   f"preneg: Captured({piece.pddl_name})\n"
                   f"del: {' '.join(self.position_to_frees(pos[0], pos[1]))}\n"
                   f"add: {' '.join(self.position_to_frees(landing_x, landing_y))} Captured({piece.pddl_name})\n")
            actions.append(act)
        return actions

    def generate_init_own_piece(self, piece):
        preds = self.position_to_frees(piece.location[0], piece.location[1], text=piece.pddl_name)
        preds.append(f"Own({piece.pddl_name})")
        if piece.kinged:
            preds.append(f"Kinged({piece.pddl_name}")
        return preds

    def generate_pddl(self, color="B"):
        predicates = "predicates: FFree(x) BFree(x) LFree(x) RFree(x) Captured(x) Kinged(x) Own(x)"
        constants = f"constants: {' '.join([p.pddl_name for p in self.pieces])}"
        actions = []
        init = []
        goal = []
        for piece in self.pieces:
            if piece.color == color:
                init.extend(self.generate_init_own_piece(piece))
            else:
                actions.extend(self.generate_capture_pddl(piece))
                goal.append(f"Captured({piece.pddl_name})")
        with open("checkers_template.pddl", "r") as f:
            base_actions = f.read()
            aditional_actions = "\n".join(actions)
            out = (f"# Checkers({self.size}x{self.size})\n\n"
                   f"{predicates}\n"
                   f"{constants}\n"
                   f"{5 + len(actions)} actions\n\n"
                   f"{base_actions}\n\n"
                   f"{aditional_actions}\n"
                   f"initial: {' '.join(init)}\n"
                   f"goal: {' '.join(goal)}")
            return out


if __name__ == "__main__":
    board = Board()
    board.print_board()
    print(board.generate_pddl())
    comp_wrl = PDDL.World(*PDDL.World.parse(board.generate_pddl())[1:])
    game_over = False
    print("Move: <piece x> <piece y> <movement>")
    print("Movement: c for capture, f/b for piece forward or backward, l/r for left or right")
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
