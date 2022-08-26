import pydot
from IPython.display import Image, display
import queue
import numpy as np
from random import randint as randint


# --- CLASS NODO ---#
class Node():
    def __init__(self, state, value, operators, operator=None, parent=None, objective=None):
        self.state = state
        self.value = value
        self.children = []
        self.parent = parent
        self.operator = operator
        self.objective = objective
        self.level = 0
        self.operators = operators
        self.v = 0

    def add_child(self, value, state, operator):
        node = type(self)(value=value, state=state, operator=operator, parent=self, operators=self.operators)
        node.level = node.parent.level + 1
        self.children.append(node)
        return node

    def add_node_child(self, node):
        node.level = node.parent.level + 1
        self.children.append(node)
        return node

    # Devuelve todos los estados según los operadores aplicados
    def getchildrens(self):
        return [
            self.getState(i)
            if not self.repeatStatePath(self.getState(i))
            else None for i, op in enumerate(self.operators)]

    def getState(self, index):
        pass

    def __eq__(self, other):
        return self.state == other.state

    def __lt__(self, other):
        return self.f() < other.f()

    def repeatStatePath(self, state):
        n = self
        while n is not None and n.state != state:
            n = n.parent
        return n is not None

    def pathObjective(self):
        n = self
        result = []
        while n is not None:
            result.append(n)
            n = n.parent
        return result

    def heuristic(self):
        return 0

    def cost(self):
        return 1

    def f(self):
        return self.cost() + self.heuristic()

    ### Crear método para criterio objetivo
    ### Por defecto vamos a poner que sea igual al estado objetivo, para cada caso se puede sobreescribir la función
    def isObjective(self):
        return self.state==self.objective

        # --- CLASS ÁRBOL ---#


class Tree():
    def __init__(self, root, operators):
        self.root = root
        self.operators = operators

    def printPath(self, n):
        stack = n.pathObjective()
        path = stack.copy()
        while len(stack) != 0:
            node = stack.pop()
            if node.operator is not None:
                print(f'operador:  {self.operators[node.operator]} \t estado: {node.state}')
            else:
                print(f' {node.state}')
        return path

    def reinitRoot(self):
        self.root.operator = None
        self.root.parent = None
        self.root.objective = None
        self.root.children = []
        self.root.level = 0

    ## Primero a lo ancho
    def breadthFirst(self, endState):
        self.reinitRoot()
        pq = queue.Queue()
        pq.put(self.root)
        while not pq.empty():
            node = pq.get()
            children = node.getchildrens()
            for i, child in enumerate(children):
                if child is not None:
                    newChild = node.add_child(value=node.value + '-' + str(i), state=child, operator=i)
                    pq.put(newChild)
                    if endState == child:
                        return newChild

    ## Primero en profundidad
    def dephFirst(self, endState):
        self.reinitRoot()
        pq = []
        pq.append(self.root)
        while len(pq) > 0:
            node = pq.pop()
            if (node.parent is not None):
                node.parent.add_node_child(node)
            children = node.getchildrens()
            temp = []
            for i, child in enumerate(children):
                if child is not None:
                    newChild = type(self.root)(value=node.value + '-' + str(i), state=child, operator=i, parent=node,
                                               operators=node.operators)
                    temp.append(newChild)
                    if endState == child:
                        node.add_node_child(newChild)
                        return newChild
            # Adicionar los hijos en forma inversa para que salga primero el primero que se adicionó
            temp.reverse()
            for e in temp:
                pq.append(e)

    ## Costo uniforme
    def costUniform(self, endState):
        self.reinitRoot()
        pq = queue.PriorityQueue()
        pq.put((self.root.cost(), self.root))
        while not pq.empty():
            node = pq.get()[1]
            children = node.getchildrens()
            for i, child in enumerate(children):
                if child is not None:
                    newChild = node.add_child(value=node.value + '-' + str(i),
                                              state=child, operator=i)
                    pq.put((newChild.cost(), newChild))
                    if endState == child:
                        return newChild

    ## Primero el mejor
    def bestFirst(self, endState):
        self.reinitRoot()
        pq = queue.PriorityQueue()
        pq.put((self.root.heuristic(), self.root))
        while not pq.empty():
            node = pq.get()[1]
            children = node.getchildrens()
            for i, child in enumerate(children):
                if child is not None:
                    newChild = node.add_child(value=node.value + '-' + str(i),
                                              state=child, operator=i)
                    pq.put((newChild.heuristic(), newChild))
                    if endState == child:
                        return newChild

    ## A*
    def Aasterisk(self, endState):
        self.reinitRoot()
        pq = queue.PriorityQueue()
        pq.put((self.root.f(), self.root))
        while not pq.empty():
            node = pq.get()[1]
            children = node.getchildrens()
            for i, child in enumerate(children):
                if child is not None:
                    newChild = node.add_child(value=node.value + '-' + str(i),
                                              state=child, operator=i)
                    pq.put((newChild.f(), newChild))
                    if endState == child:
                        return newChild

        ## Generar los hijos del nodo

    def AlfaBeta(self, depth):
        self.root.v = self.AlfaBetaR(self.root, depth, float('-inf'), float('inf'), True)
        print(self.root.v)
        print("Tercera linea de Alfabeta")
        print()
        ## Comparar los hijos de root
        values = [c.v for c in self.root.children]
        maxvalue = max(values)
        index = values.index(maxvalue)
        return self.root.children[index]

    def AlfaBetaR(self, node, depth, alfa, beta, maxPlayer):
        print("Entro al alphabetaR")

        if depth == 0 or node.isObjective():  # if depth == 0:
            node.v = node.heuristic()
            print(node.v)
            return node.heuristic()

        ## Generar los hijos del nodo
        children = node.getchildrens()
        print(node.getchildrens())

        ## Según el jugador que sea en el árbol
        if maxPlayer:
            value = float('-inf')
            for i, child in enumerate(children):
                if child is not None:
                    newChild = type(self.root)(value=node.value + '-' + str(i), state=child, operator=i, parent=node,
                                               operators=node.operators, player=False)
                    newChild = node.add_node_child(newChild)
                    value = max(value, self.AlfaBetaR(newChild, depth - 1, alfa, beta, False))
                    alfa = max(alfa, value)
                    if alfa >= beta:
                        break
            # return value
            # node.v=value
            # return value
        else:
            value = float('inf')
            for i, child in enumerate(children):
                if child is not None:
                    newChild = type(self.root)(value=node.value + '-' + str(i), state=child, operator=i, parent=node,
                                               operators=node.operators, player=True)
                    newChild = node.add_node_child(newChild)
                    value = min(value, self.AlfaBetaR(newChild, depth - 1, alfa, beta, True))
                    beta = min(beta, value)
                    if alfa >= beta:
                        break
            # return value

        node.v = value
        print(value)
        return value

    ## Método para dibujar el árbol
    def draw(self, path):
        graph = pydot.Dot(graph_type='graph')
        nodeGraph = pydot.Node(str(self.root.state) + "-" + str(0),
                               label=str(self.root.state), shape="circle",
                               style="filled", fillcolor="red")
        graph.add_node(nodeGraph)
        path.pop()
        return self.drawTreeRec(self.root, nodeGraph, graph, 0, path.pop(), path)

    ## Método recursivo para dibujar el árbol
    def drawTreeRec(self, r, rootGraph, graph, i, topPath, path):
        if r is not None:
            children = r.children
            for j, child in enumerate(children):
                i = i + 1
                color = "white"
                if topPath.value == child.value:
                    if len(path) > 0: topPath = path.pop()
                    color = 'red'
                c = pydot.Node(child.value,
                               label=str(child.state) + r"\n" + r"\n" + "f=" + str(child.heuristic()) + r"\n" + str(
                                   child.v),
                               shape="circle", style="filled",
                               fillcolor=color)
                graph.add_node(c)
                graph.add_edge(pydot.Edge(rootGraph, c,
                                          label=str(child.operator) + '(' + str(child.cost()) + ')'))
                graph = self.drawTreeRec(child, c, graph, i, topPath, path)  # recursive call
            return graph
        else:
            return graph

    def best(self, r, rootGraph, graph, i, topPath, path):
        if r is not None:
            children = r.children
            for j, child in enumerate(children):
                i = i + 1
                color = "white"
                if topPath.value == child.value:
                    if len(path) > 0: topPath = path.pop()
                    color = 'red'
                c = pydot.Node(child.value,
                               label=str(child.state) + r"\n" + r"\n" + "f=" + str(child.heuristic()) + r"\n" + str(
                                   child.v),
                               shape="circle", style="filled",
                               fillcolor=color)
                graph.add_node(c)
                graph.add_edge(pydot.Edge(rootGraph, c,
                                          label=str(child.operator) + '(' + str(child.cost()) + ')'))
                graph = self.drawTreeRec(child, c, graph, i, topPath, path)  # recursive call
            return graph
        else:
            return graph

            # --- CLASS JUEGO ---#


class Game:
    # Construtor de la clase Game esta clase contiene la logica detras del juego Battelship o Batalla Naval contiene ademas la iterfaz en consola y los metodos necesarios para jugar
    def __init__(self, name, game_opt="", b1=[], b2=[], p1_name="", p2_name="", p1_ships=[], p2_ships=[],
                 ships=[5, 4, 3, 3, 2], p1_guess_board=[], p2_guess_board=[], p1_guess_list=[],
                 p2_guess_list=[]):
        self.name = name
        self.game_opt = game_opt
        self.b1 = b1  # Esta atributo corresponde al tablero del jugador 1. En caso de ser PvAI este sera el tablero de la maquina. O correspinde a Oceano. S a Barco y H si undo de los barcos ha sido encontrado
        self.b2 = b2  # Este atriburo corresponde al tablero del jugador 2. En caso de ser PvAi este sera el tablero del usuario. O correspinde a Oceano. S a Barco y H si undo de los barcos ha sido encontrado
        self.p1_name = p1_name  # Nombre del jugadore 1. AI si es en el modo PvAI
        self.p2_name = p2_name  # Nombre del jugador 2
        self.p1_ships = p1_ships  # Lista que corresponde a las cordenadas x,y donde se encuentran los barcos del jugador 1
        self.p2_ships = p2_ships  # Lista que corresponde a las coordenadas x,y donde se encuentran los barcos del jugador 2
        self.ships = ships  # Lista que contiene el tamaño de los 5 barcos del juego.
        self.p1_guess_board = p1_guess_board  # Este es el tablero de las posiciones que ha adiviando el jugador 1. O = Oceano, H = Impacto M = Disparo Fallido
        self.p2_guess_board = p2_guess_board  # Este es el tablero de las posiciones que ha adiviando el jugador 2. O = Oceano, H = Impacto M = Disparo Fallido
        self.p1_guess_list = p1_guess_list  # Lista que contiene las posiciones que adivina el p1
        self.p2_guess_list = p2_guess_list  # Lista que contiene las posiciones que adivina el p2

        # Metodo para jugar Batalla Naval. Tiene 2 modos de juego, jugar contra la maquina, jugar contra otro jugador metodo mas que todo para pruebas

    def play_game(self):
        print("BATTLESHIP")
        print("(1) PvAI")
        print("(2) PvP (TestMode)")
        game_opt = input("Selecione Una Opcion ")
        if game_opt == "1":
            print("PvAI")
            self.playPvAI()
        elif game_opt == "2":
            print("PvP")
            self.game_opt = "2"
            self.playPvP()
        else:
            print("Opcion No Valida")

    def playPvAI(self):
        self.b1 = self.gen_board()
        self.b2 = self.gen_board()
        self.p2_name = input("Enter Player Name ")

        # Si se desea se puede elegir la posicion de los barcos de manera aleatoria para fines de pruebas
        rdn_ships_p2 = input("Enter Ships Manualy y/n")
        if rdn_ships_p2 == "y":
            for ship in self.ships:

                valid = False
                while not valid:

                    ship_row = int(input("Enter Ship: " + str(ship) + " Row Location"))
                    print(ship_row)
                    ship_col = int(input("Enter Ship: " + str(ship) + " Col Location"))
                    print(ship_col)
                    ship_or = input("Enter Ship: " + str(ship) + " Orientation (h) or (v) ")
                    print(ship_or)
                    valid = self.validate_ship_place(self.b2, ship, ship_col, ship_row, ship_or)
                    if not valid:
                        print("Enter a Valid Location")
                self.b2, self.p2_ships = self.place_ship(self.b2, self.p2_ships, ship, ship_or, ship_col,
                                                         ship_row)
                self.print_board(self.b2, self.p2_name)
        else:
            for ship in self.ships:
                valid = False
                while not valid:

                    ship_row = randint(0, 9)
                    print(ship_row)
                    ship_col = randint(0, 9)
                    print(ship_col)
                    rdn_or = randint(0, 1)
                    if rdn_or == 1:
                        ship_or = "v"
                    else:
                        ship_or = "h"
                    print(ship_or)
                    valid = self.validate_ship_place(self.b2, ship, ship_col, ship_row, ship_or)
                    if not valid:
                        print("Enter a Valid Location")
                self.b2, self.p2_ships = self.place_ship(self.b2, self.p2_ships, ship, ship_or, ship_col,
                                                         ship_row)
                self.print_board(self.b2, self.p2_name)

        print("Player 2 Ships: " + str(self.p2_ships))  # Sin embargo se usa p1 para la AI

        self.p1_name = "Player AI"

        # Se eligen las posiciones de manera aleatoria para la AI

        for ship in self.ships:
            valid = False
            while not valid:
                ship_row = randint(0, 9)
                print(ship_row)
                ship_col = randint(0, 9)
                print(ship_col)
                rdn_or = randint(0, 1)
                if rdn_or == 1:
                    ship_or = "v"
                else:
                    ship_or = "h"
                print(ship_or)
                valid = self.validate_ship_place(self.b1, ship, ship_col, ship_row, ship_or)
                if not valid:
                    print("Enter a Valid Location")
            self.b1, self.p1_ships = self.place_ship(self.b1, self.p1_ships, ship, ship_or, ship_col,
                                                     ship_row)
            self.print_board(self.b1, self.p1_name)

        print("Player 1 Ships: " + str(self.p1_ships))

        self.p1_guess_board = self.gen_board()
        self.p2_guess_board = self.gen_board()

        # El Juego va a seguir hasta que la lista que contiene las posiciones de los barcos de alguno de los jugadores este vacia. El jugador al que correspona la lista vacia sera el perdedor

        while len(self.p1_ships) > 0 and len(self.p2_ships) > 0:
            guess_col = 0
            guess_row = 0
            is_a_hit = False
            print("Turno de AI:")

            # Inicio del juego para la AI--------------------------------------

            if not self.p1_guess_list:  # Si la lista de adivinanzas no está vacía
                # -----Genera un aletorio para hacer la primera jugada-----
                col = randint(0, 9)
                row = randint(0, 9)
                is_a_hit, self.b2, self.p2_ships, self.p1_guess_board = self.validate_if_hit(
                    self.b2, self.p2_ships, self.p1_guess_board, row, col)
                self.p1_guess_list.append([row, col, is_a_hit])
                print(self.p1_guess_list)
                ai_guess_x = self.p1_guess_list[0][0]
                ai_guess_y = self.p1_guess_list[0][1]
                # Validación de las posiciones cuando la selección de los operadores se encuentra en los extremos (bordes del
                # tablero)

                operators = [(i, j) for i, f in enumerate(self.p1_guess_board) for j, c in enumerate(f)]
                nodeInit = Battleship(self, True, value="inicio", state=self.p1_guess_board, operators=operators)


                treeAlfaBeta = Tree(nodeInit, operators)

                objective = treeAlfaBeta.breadthFirst(self.b1)# retorna el tablero


                # FIN DE LA AI-----------------------------------------------------

            print("Player 2:")

            guess_row = int(input("Enter Guess Row Location "))
            print(guess_row)
            guess_col = int(input("Enter Guess Col Location "))
            print(guess_col)
            is_a_hit, self.b1, self.p1_ships, self.p2_guess_board = self.validate_if_hit(self.b1,
                                                                                         self.p1_ships,
                                                                                         self.p2_guess_board,
                                                                                         guess_row,
                                                                                         guess_col)
            if is_a_hit:
                print("SHIP HIT!!!!!!!")
            else:
                print("MIS")
            self.print_board(self.p2_guess_board)
            self.p2_guess_list.append([guess_row, guess_col, is_a_hit])
            print(self.p2_guess_list)

            # ----------Metodo de Pruebas o PvP----------------

    def playPvP(self):
        self.b1 = self.gen_board()
        self.b2 = self.gen_board()

        self.p1_name = input("Enter Player One Name ")

        # Si se desea se puede elegir la posicion de los barcos de manera aleatoria para fines de pruebas
        rdn_ships_p1 = input("Enter Ships Manualy y/n")
        if rdn_ships_p1 == "y":
            for ship in self.ships:

                valid = False
                while not valid:

                    ship_row = int(input("Enter Ship: " + str(ship) + " Row Location"))
                    print(ship_row)
                    ship_col = randint(0, 9)
                    print(ship_col)
                    ship_or = input("Enter Ship: " + str(ship) + " Orientation (h) or (v) ")
                    print(ship_or)
                    valid = self.validate_ship_place(self.b1, ship, ship_col, ship_row, ship_or)
                    if valid == False:
                        print("Enter a Valid Location")
                self.b1, self.p1_ships = self.place_ship(self.b1, self.p1_ships, ship, ship_or, ship_col,
                                                         ship_row)
                self.print_board(self.b1, self.p1_name)

        else:
            for ship in self.ships:

                valid = False
                while not valid:

                    ship_row = randint(0, 9)
                    print(ship_row)
                    ship_col = randint(0, 9)
                    print(ship_col)
                    rdn_or = randint(0, 1)
                    if rdn_or == 1:
                        ship_or = "v"
                    else:
                        ship_or = "h"
                    print(ship_or)
                    valid = self.validate_ship_place(self.b1, ship, ship_col, ship_row, ship_or)
                    if valid == False:
                        print("Enter a Valid Location")
                self.b1, self.p1_ships = self.place_ship(self.b1, self.p1_ships, ship, ship_or, ship_col,
                                                         ship_row)
                self.print_board(self.b1, self.p1_name)

        print("Player 1 Ships: " + str(self.p1_ships))

        self.p2_name = input("Enter Player Two Name ")

        # Si se desea se puede elegir la posicion de los barcos de manera aleatoria para fines de pruebas
        rdn_ships_p2 = input("Enter Ships Manualy y/n")
        if rdn_ships_p2 == "y":
            for ship in self.ships:

                valid = False
                while not valid:

                    ship_row = int(input("Enter Ship: " + str(ship) + " Row Location"))
                    print(ship_row)
                    ship_col = int(input("Enter Ship: " + str(ship) + " Col Location"))
                    print(ship_col)
                    ship_or = input("Enter Ship: " + str(ship) + " Orientation (h) or (v) ")
                    print(ship_or)
                    valid = self.validate_ship_place(self.b2, ship, ship_col, ship_row, ship_or)
                    if valid == False:
                        print("Enter a Valid Location")
                self.b2, self.p2_ships = self.place_ship(self.b2, self.p2_ships, ship, ship_or, ship_col,
                                                         ship_row)
                self.print_board(self.b2, self.p2_name)
        else:
            for ship in self.ships:

                valid = False
                while not valid:

                    ship_row = randint(0, 9)
                    print(ship_row)
                    ship_col = randint(0, 9)
                    print(ship_col)
                    rdn_or = randint(0, 1)
                    if rdn_or == 1:
                        ship_or = "v"
                    else:
                        ship_or = "h"
                    print(ship_or)
                    valid = self.validate_ship_place(self.b2, ship, ship_col, ship_row, ship_or)
                    if valid == False:
                        print("Enter a Valid Location")
                self.b2, self.p2_ships = self.place_ship(self.b2, self.p2_ships, ship, ship_or, ship_col,
                                                         ship_row)
                self.print_board(self.b2, self.p2_name)

        print("Player 2 Ships: " + str(self.p2_ships))

        self.p1_guess_board = self.gen_board()
        self.p2_guess_board = self.gen_board()

        # El Juego va a seguir hasta que la lista que contiene las posiciones de los barcos de alguno de los jugadores este vacia. El jugador al que correspona la lista vacia sera el perdedor

        while len(self.p1_ships) > 0 and len(self.p2_ships) > 0:
            guess_col = 0
            guess_row = 0
            is_a_hit = False
            print("Player One Guess:")

            guess_row = int(input("Enter Guess Row Location "))
            print(guess_row)
            guess_col = int(input("Enter Guess Col Location "))
            print(guess_col)
            is_a_hit, self.b2, self.p2_ships, self.p1_guess_board = self.validate_if_hit(self.b2,
                                                                                         self.p2_ships,
                                                                                         self.p1_guess_board,
                                                                                         guess_row,
                                                                                         guess_col)
            if is_a_hit:
                print("SHIP HIT!!!!!!!")
            else:
                print("MIS")
            self.print_board(self.p1_guess_board)
            self.p1_guess_list.append([guess_row, guess_col, is_a_hit])
            print(self.p1_guess_list)

            guess_col = 0
            guess_row = 0
            is_a_hit = False
            print("Player Two Guess:")

            guess_row = int(input("Enter Guess Row Location "))
            print(guess_row)
            guess_col = int(input("Enter Guess Col Location "))
            print(guess_col)
            is_a_hit, self.b1, self.p1_ships, self.p2_guess_board = self.validate_if_hit(self.b1,
                                                                                         self.p1_ships,
                                                                                         self.p2_guess_board,
                                                                                         guess_row,
                                                                                         guess_col)
            if is_a_hit:
                print("SHIP HIT!!!!!!!")
            else:
                print("MIS")
            self.print_board(self.p2_guess_board)
            self.p2_guess_list.append([guess_row, guess_col, is_a_hit])
            print(self.p2_guess_list)

            # Metodo Utilizado para validar si la posicion que adivino un jugador es un impacto o un disparo fallido

    def validate_if_hit(self, target_player_board, target_player_ships, player_guess_board, row, col):
        guess = [row, col]
        print(guess)
        is_a_hit = False

        if guess in target_player_ships:
            target_player_ships.pop(target_player_ships.index(guess))
            player_guess_board[row][col] = "H"
            target_player_board[row][col] = "H"
            is_a_hit = True
        else:
            player_guess_board[row][col] = "M"

        return is_a_hit, target_player_board, target_player_ships, player_guess_board

        # Metodo Utilizado para validar si la posicion que adivino un jugador es un impacto o un disparo fallido -Max-

    def validate_if_hit2(self, target_player_board, target_player_ships, player_guess_board, row, col):
        # Recibe el tablero del jugador 1
        # Se usa para el caso de jugar en contra de la AI

        guess = [row, col]
        print(guess)
        is_a_hit = False

        if guess in target_player_ships:
            target_player_ships.pop(target_player_ships.index(guess))
            player_guess_board[row][col] = "H"
            target_player_board[row][col] = "H"
            is_a_hit = True
        else:
            player_guess_board[row][col] = "M"

        return is_a_hit

        # Metodo utilizado para validar si la posicion en la cual se quiere agregar un barco es valida. Verifica que el barco no se salga del tablero ademas de que no se intersecte con otro barco.

    def validate_ship_place(self, board, ship, ship_col, ship_row, ship_or):

        if ship_or != "v" and ship_or != "h":
            return False
        else:
            if ship_or == "v" and ship_row + ship > 10:
                return False
            elif ship_or == "h" and ship_col + ship > 10:
                return False
            else:
                if ship_or == "v":
                    for i in range(0, ship):
                        if board[ship_row + i][ship_col] != "O":
                            return False
                elif ship_or == "h":
                    for i in range(0, ship):
                        if board[ship_row][ship_col + i] != "O":
                            return False
        return True

    # Metodo utilizado para colocar el barco en el tablero. Siempre se tiene que correr luego de haber validado que el barco se pueda colocar usando el metodo validate_ship_place. Este metodo tambien agreaga las coordenads x,y a la lista de los barcos del jugador que esta agregando barcos
    def place_ship(self, board, player_ships, ship, ship_or, ship_col,
                   ship_row):  # Los barcos se denotan con S en el tablero
        if ship_or == "v":
            for i in range(0, ship):
                board[ship_row + i][ship_col] = "S"
                player_ships.append([ship_row + i, ship_col])
        elif ship_or == "h":
            for i in range(ship):
                board[ship_row][ship_col + i] = "S"
                player_ships.append([ship_row, ship_col + i])
        return board, player_ships

    # Metodo para crear un tablero vacio
    def gen_board(self):
        board = []
        for i in range(10):
            board.append(["O"] * 10)
        return board

    # Metodo para imprimir un tablero
    def print_board(self, board, name=""):
        if len(board) > 0:
            iter = 0
            if name != "":
                print(name + "'s Board")
            print("    [0] [1] [2] [3] [4] [5] [6] [7] [8] [9]")
            for row in board:
                print("[" + str(iter) + "]" + "  " + "   ".join(row))
                iter += 1
            print("--------------------------------------------")
        else:
            print("The board is empty.")
        return board

        # --- CLASS BATALLA NAVAL ---#


class Battleship(Node):

    def __init__(self, Game, player=True, **kwargs):
        # **kwargs evita la necesidad de ingresar nuevamente los atributos del método anterior
        super(Battleship, self).__init__(**kwargs)
        self.player = player
        self.Game = Game
        if player:
            self.v = float('-inf')
        else:
            self.v = float('inf')

    def getState(self, index):  # dado un operador determinado calcula un estado al que se llega
        state = self.state
        print("STATE")
        print(state)
        nextState = None
        is_a_hit = False
        (x, y) = self.operators[index]
        print(self.Game.p1_guess_list)
         # si la posición en la matriz no ha sido jugada es posible operarlo
        is_a_hit, self.Game.b2, self.Game.p2_ships, self.Game.p1_guess_board = self.Game.validate_if_hit(self.Game.b2, self.Game.p2_ships, self.Game.p1_guess_board, x, y)
        self.Game.p1_guess_list.append([x, y, is_a_hit])
        nextState = self.Game.p1_guess_board
        if is_a_hit:  ## Si fue un impacto
            print("Hit de  AI")
        else:  ## Si no fue un impacto
            print("Miss de AI")

        return nextState if state != nextState else None

    # Costo acumulativo(valor 1 en cada nivel)
    def cost(self):
        return self.level

    # def isObjective(self):
    # El estado objetivo se alcanza cuando las posiciones que ha adivinado el jugador 1 (AI) coincide con las posiciones
    # en las que se encuentran los barcos del jugador 2 (Usuario)

    # for element in self.Game.p2_ships: #Itera las posiciones de las naves del jugador 2 (Usuario)
    # if element in self.Game.p1_guess_board: #Itera los recuadros que ha adivinado la el jugador 1 (AI)
    # print(f"el elemento {element} está repetido!")
    # return True
    # else:
    # return False

    def heuristic(self):
        print("ENTRA A HEURISTIC")
        print(len(self.Game.p1_guess_list))
        costo = 0
        is_a_hit = False
        guess_actual = self.Game.p1_guess_list[len(self.Game.p1_guess_list) - 1]
        tablr_actual = self.Game.p1_guess_board

        x = [[guess_actual[0] + 1, guess_actual[1]], [guess_actual[0] - 1, guess_actual[1]],
             [guess_actual[0], guess_actual[1] + 1], [guess_actual[0], guess_actual[1] - 1]]

        if guess_actual[0] == 9:
            x[0][0]-=1

        if guess_actual[0] == 0:
            x[1][0]+= 1

        if guess_actual[1] == 9:
            x[2][1] -= 1

        if guess_actual[1] == 0:
            x[3][1] += 1

        for obj in x:
            if tablr_actual[obj[0]][obj[1]] == "H":
                costo += 1
            elif tablr_actual[obj[0]][obj[1]] == "M":
                costo -= 1
            else:
                costo = costo

        return costo

        # LLAMADO DEL PROGRAMA#


nG = Game("nG")
nG.play_game()
