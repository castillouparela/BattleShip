import pydot
import queue
import random

import engine
from engine import Game, Player, Ship #Se importan las clases necesarias
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
        return self.state == self.objective

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
        print(values)
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
                                               operators=node.operators, player=False, game=node.game)
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
                                               operators=node.operators, player=True, game=node.game)
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

class Battleship(Node):

    def __init__(self,player,game, **kwargs): #def __init__(self, root, operators):
        # **kwargs evita la necesidad de ingresar nuevamente los atributos del método anterior
        super(Battleship, self).__init__(**kwargs)
        self.player = player
        self.Game = Game
        if player:
            self.v = float('-inf')
        else:
            self.v = float('inf')

    def getState(self, index):  # dado un operador determinado calcula un estado al que se llega

        nextState = self.game.player1.search[index]

        return nextState

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

        # LLAMADO DEL PROGRAMA#


nG = Game("nG")
nG.play_game()
