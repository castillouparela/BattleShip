import random


class Ship:
    def __init__(self, size):
        self.row = random.randrange(0, 9)
        self.col = random.randrange(0, 9)
        self.size = size
        self.orientation = random.choice(["h", "v"])
        self.indexes = self.compute_indexes()

    def compute_indexes(self):
        start_index = self.row * 10 + self.col
        if self.orientation == "h":
            return [start_index + i for i in range(self.size)]
        elif self.orientation == "v":
            return [start_index + i * 10 for i in range(self.size)]


class Player:
    def __init__(self):
        self.ships = []
        self.search = ["U" for i in range(100)]  # U for unknown
        self.place_ships(sizes=[5, 4, 3, 3, 2])
        list_of_lists = [ship.indexes for ship in self.ships]
        self.indexes = [index for sublist in list_of_lists for index in sublist]
        self.totalSP = 0  # Conteo de barcos hundidos para el jugador

    def place_ships(self, sizes):
        for size in sizes:
            placed = False
            while not placed:

                # create a new ship
                ship = Ship(size)

                # check if placement is possible
                possible = True
                for i in ship.indexes:

                    # indexes must be less than 100
                    if i >= 100:
                        possible = False
                        break

                    # ships cannot behave like the "snake" in the "snake game"
                    new_row = i // 10
                    new_col = i % 10
                    if new_row != ship.row and new_col != ship.col:
                        possible = False
                        break

                    # ships cannot intersect
                    for other_ship in self.ships:
                        if i in other_ship.indexes:
                            possible = False
                            break

                # place the ship
                if possible:
                    self.ships.append(ship)
                    placed = True

    def show_ships(self):
        indexes = ["-" if i not in self.indexes else "X" for i in range(100)]
        for row in range(10):
            print(" ".join(indexes[(row - 1) * 10:row * 10]))


p = Player()


class Game:
    def __init__(self, human1, human2):
        self.human1 = human1
        self.human2 = human2
        self.player1 = Player()
        self.player2 = self.player1
        self.player1_turn = True
        self.computer_turn = True if not self.human1 else False
        self.over = False
        self.result = None
        self.scoreP1 = 0
        self.scoreP2 = 0

    def make_move(self, i):
        player = self.player1 if self.player1_turn else self.player2
        opponent = self.player2 if self.player1_turn else self.player1
        hit = False

        if player.search[i] == "U":  # Validate if the position was played

            # set miss or hit
            if i in opponent.indexes and player.search[i] == "U":
                player.search[i] = "H"
                hit = True

                # check if ship is sunk
                for ship in opponent.ships:
                    sunk = True
                    for i in ship.indexes:
                        if player.search[i] == "U":
                            sunk = False
                            break
                    if sunk:
                        for i in ship.indexes:
                            player.search[i] = "S"
                    if self.player1_turn:
                        self.scoreP1 = self.scoreP1 + 1
                    else:
                        self.scoreP2 = self.scoreP2 + 1

            else:
                player.search[i] = "M"
            # check if game over
            game_over = True
            for i in opponent.indexes:
                if player.search[i] == "U":
                    game_over = False
            self.over = game_over
            self.result = 1 if self.scoreP1 > self.scoreP2 else 2

            # change the active team
            if not hit:
                self.player1_turn = not self.player1_turn
                # switch between human and computer turns
                if (self.human1 and not self.human2) or (not self.human1 and self.human2):
                    self.computer_turn = not self.computer_turn
