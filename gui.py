import engine
import main
from main import *
import pygame

pygame.init()
depth = 0
run = True


class DropDown:

    def __init__(self, color_menu, color_option, x, y, w, h, font, principal, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.principal = principal
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1
        self.myfont = pygame.font.SysFont("fresansttf", 80)

    def draw(self, surf):
        pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.principal, 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=rect.center))

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        return -1


pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((640, 480))

COLOR_INACTIVE = (100, 80, 255)
COLOR_ACTIVE = (100, 200, 255)
COLOR_LIST_INACTIVE = (255, 100, 100)
COLOR_LIST_ACTIVE = (255, 150, 150)

list1 = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    50, 50, 200, 50,
    pygame.font.SysFont(None, 30),
    "Select Mode", ["Medio", "Dificil"])

while run:
    clock.tick(30)
    screen.fill((255, 255, 255))
    list1.draw(screen)
    pygame.display.flip()

    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            run = False

    selected_option = list1.update(event_list)
    if selected_option >= 0:
        list1.principal = list1.options[selected_option]
        if list1.principal == "Medio":
            depth = 1
            run = False
        if list1.principal == "Dificil":
            depth = 2
            run = False

pygame.quit()

pygame.init()
pygame.font.init()
pygame.display.set_caption("Battleship")
myfont = pygame.font.SysFont("fresansttf", 100)
myfont2 = pygame.font.SysFont("fresansttf", 80)
# global variables
SQ_SIZE = 38
H_MARGIN = SQ_SIZE * 4
V_MARGIN = SQ_SIZE
WIDTH = SQ_SIZE * 10 * 1.5 + H_MARGIN
HEIGHT = SQ_SIZE * 10 * 1.5 + V_MARGIN
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
INDENT = 10
HUMAN1 = True  # True es el jugador
HUMAN2 = False  # False coincide con la AI

# colors
GREY = (40, 50, 60)
WHITE = (255, 250, 250)
GREEN = (50, 200, 150)
RED = (150, 50, 100)
RED2 = (250, 0, 0)
BLUE = (50, 150, 200)
ORANGE = (250, 140, 20)
COLORS = {"U": GREY, "M": BLUE, "H": ORANGE, "S": RED}


# function to draw a grid
def draw_grid(player, search=False, left=0, top=0):
    for i in range(100):
        x = left + i % 10 * SQ_SIZE
        y = top + i // 10 * SQ_SIZE
        square = pygame.Rect(x, y, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(SCREEN, WHITE, square, width=3)
        if search:
            x += SQ_SIZE // 2
            y += SQ_SIZE // 2
            pygame.draw.circle(SCREEN, COLORS[player.search[i]], (x, y), radius=SQ_SIZE // 4)


# functions to draw ships onto the position grids
def draw_ships(player, left=0, top=0):
    for ship in player.ships:
        x = left + ship.col * SQ_SIZE + INDENT
        y = top + ship.row * SQ_SIZE + INDENT
        if ship.orientation == "h":
            width = ship.size * SQ_SIZE - 2 * INDENT
            height = SQ_SIZE - 2 * INDENT
        else:
            width = SQ_SIZE - 2 * INDENT
            height = ship.size * SQ_SIZE - 2 * INDENT
        rectangle = pygame.Rect(x, y, width, height)
        pygame.draw.rect(SCREEN, GREEN, rectangle, border_radius=15)


player1 = Player()
player2 = Player()

game = engine.Game(HUMAN1, HUMAN2)
nodeInit = main.Battleship(player=game.player1_turn, value="inicio", state=game.player1.search, game=game,
                           operators=[i for i in range(100)])
treeAlfaBeta = main.Tree(nodeInit, [i for i in range(100)])

# pygame loop
animating = True
pausing = False

while animating:

    # track user interaction
    for event in pygame.event.get():

        # user closes the pygame window
        if event.type == pygame.QUIT:
            animating = False

        # user clicks on mouse
        if event.type == pygame.MOUSEBUTTONDOWN and not game.over:
            x, y = pygame.mouse.get_pos()
            if game.player1_turn and x < 10 * SQ_SIZE and y < 10 * SQ_SIZE:
                row = y // SQ_SIZE
                col = x // SQ_SIZE
                index = row * 10 + col
                game.make_move(index)
            elif not game.player1_turn and x > WIDTH - 10 * SQ_SIZE and y > 10 * SQ_SIZE + V_MARGIN:
                row = (y - SQ_SIZE * 10 - V_MARGIN) // SQ_SIZE
                col = (x - SQ_SIZE * 10 - H_MARGIN) // SQ_SIZE
                index = row * 10 + col
                game.make_move(index)

        # user presses key on keyboard
        if event.type == pygame.KEYDOWN:

            # escape key to close the animation
            if event.key == pygame.K_ESCAPE:
                animating = False

            # space bar to pause and unpause the animation
            if event.key == pygame.K_SPACE:
                pausing = not pausing

            # return key to restart
            if event.key == pygame.K_RETURN:  # Reinit to game
                game = engine.Game(HUMAN1, HUMAN2)
                nodeInit = main.Battleship(player=game.player1_turn, value="inicio", state=game.player1.search,
                                           game=game,
                                           operators=[i for i in range(100)])
                treeAlfaBeta = main.Tree(nodeInit, [i for i in range(100)])

    # EXECUTION
    if not pausing:
        # draw background
        SCREEN.fill(GREY)

        # draw grids
        draw_grid(game.player1, search=True)

        # computer moves
        if not game.over and game.computer_turn:
            objective = treeAlfaBeta.AlfaBeta(depth)

        # game over message
        if game.over:
            if game.result == 1:

                textbox2 = myfont2.render("CONGRATULATIONS!", False, GREEN, WHITE)
                SCREEN.blit(textbox2, (70, 120))
                text = "HUMAN wins!"
            else:

                textbox2 = myfont.render("GAME OVER", False, RED2, WHITE)
                SCREEN.blit(textbox2, (160, 120))
                text = "Player AI wins!"
            textbox = myfont.render(text, False, GREY, WHITE)
            SCREEN.blit(textbox, (WIDTH // 2 - 240, HEIGHT // 2 - 50))

        # update screen
        pygame.time.wait(120)
        pygame.display.flip()
