import random
import os
import time
from pynput.keyboard import Listener, Key
from threading import Thread


def insert_gameboard(coord, value):
    gameboard[coord[0]][coord[1]] = value


def paint(game_board):
    global SCORE
    print('\n' * 3, '                        ', '   LEVEL:', LEVEL, '\n')
    print('                         ', '   SCORE:', SCORE, '\n')
    print('                        ', '    ESC to exit', '\n'*2)
    for row in game_board:
        segment = ''
        for cell in row:
            segment += u"\u2588"*2 if cell else '  '
        print('                        ' + segment)


def check_side(location, side):
    global direction
    global SCORE
    side_variable = {'vert': [location[0] + direction_value[direction[0]], location[1]],
                     'hori': [location[0], location[1] + direction_value[direction[1]]],
                     'both': [location[0] + direction_value[direction[0]], location[1] + direction_value[direction[1]]]}

    if gameboard[side_variable[side][0]][side_variable[side][1]]:
        if side_variable[side] in BLOCKS:
            time.sleep(0.5)
            BLOCKS.remove(side_variable[side])
            insert_gameboard(side_variable[side], False)
            SCORE += 1
            os.system("cls")
            paint(gameboard)

        if side == 'vert':
            direction[0] = reverse[direction[0]]
        elif side == 'hori':
            direction[1] = reverse[direction[1]]
        else:
            direction = [reverse[direction[0]], reverse[direction[1]]]


def check_neighbors(location):   # location = BOMB[0], location[0] -> row
    global direction
    for _ in range(2):  # niezbedne podwojne sprawdzenie warunku dla pewnych szczegolnych przypadkow
        check_side(location, 'vert')    # ruch pionowy, wiec nie sprawdzamy czy rusza sie na boki

        if direction[1]:  # jesli ruch zawiera skłądową poziomą
            check_side(location, 'hori')

        if direction[1]:  # jesli ruch zawiera skłądową poziomą
            check_side(location, 'both')


def new_bomb_placement():
    insert_gameboard(BOMB[0], False)
    BOMB[0] = [BOMB[0][0] + direction_value[direction[0]], BOMB[0][1] + direction_value[direction[1]]]
    insert_gameboard(BOMB[0], True)


def push_bomb():
    if [BOMB[0][0] + 1, BOMB[0][1]] in PLATFORM:
        if platform_direction[current_direc] == reverse[direction[1]]:
            direction[1] = None
            new_bomb_placement()
        elif platform_direction[current_direc] and not direction[1]:
            direction[1] = platform_direction[current_direc]
            new_bomb_placement()
        elif (platform_direction[current_direc] == direction[1]) and direction[1]:
            if gameboard[BOMB[0][0]][BOMB[0][1] + direction_value[direction[1]]*2]:
                insert_gameboard(BOMB[0], False)
                BOMB[0] = [BOMB[0][0] - 1, BOMB[0][1]]
                direction[1] = reverse[direction[1]]
                insert_gameboard(BOMB[0], True)
            else:
                insert_gameboard(BOMB[0], False)
                BOMB[0] = [BOMB[0][0] + direction_value[direction[0]], BOMB[0][1] + direction_value[direction[1]]*2]
                insert_gameboard(BOMB[0], True)

        else:
            new_bomb_placement()

    else:
        new_bomb_placement()


def new_platform_placement():
    global current_direc
    global PLATFORM

    if (current_direc == Key.left and PLATFORM[0][1] == 1) or (current_direc == Key.right and PLATFORM[-1][1] == n-2):
        return

    temp_PLATFORM = []

    if current_direc == Key.left:
        insert_gameboard(PLATFORM[-1], False)
    elif current_direc == Key.right:
        insert_gameboard(PLATFORM[0], False)

    for block in PLATFORM[:]:
        if current_direc == Key.left:
            temp_PLATFORM.append([block[0], block[1]-1])
        elif current_direc == Key.right:
            temp_PLATFORM.append([block[0], block[1] + 1])

    PLATFORM = temp_PLATFORM

    if current_direc == Key.left:
        insert_gameboard(PLATFORM[0], True)
    elif current_direc == Key.right:
        insert_gameboard(PLATFORM[-1], True)


def on_press(key):
    global current_direc
    current_direc = key


m = 26
n = 26

direction_value = {'left': -1, 'right': 1, 'down': 1, 'up': -1, None: 0}
reverse = {'left': 'right', 'right': 'left', 'down': 'up', 'up': 'down', None: 'Nope!'}


x = 8  # ilosc wierszy BLOCKS
PLATFORM = [[m-3, 11], [m-3, 12], [m-3, 13]]    # platforma na pierwszym poziomie
SCORE = 0
LEVEL = 1

while True:
    # nowa plansza przy kazdym poziomie
    gameboard = [[True for i in range(n)]] + [[True] + [False for i in range(n - 2)] + [True] for j in range(m - 2)] + \
                [[True for i in range(n)]]  # m wierszy po n kolumn

    BOMB = [[m - 9, 14]]  # nowa lokalizacja bomby przy nowym poziomie
    direction = ['up', 'right']  # nowy kierunek bomby

    BLOCKS = set()  # przy kazdym poziomie generujemy nowe bloki
    for _ in range(5 * LEVEL):
        BLOCKS.add((random.randint(2, 2 + x - 1), random.randint(2, n - 3)))

    BLOCKS = list(BLOCKS)  # niezbedna sztuczka do zamiany zbioru zlozonego list na liste zlozona z list
    temp_BLOCKS = []
    for element in BLOCKS:
        temp_BLOCKS.append(list(element))
    BLOCKS = temp_BLOCKS

    for block in BLOCKS + PLATFORM + BOMB:  # nanosimy wszystkie bloki do planszy
        insert_gameboard(block, True)

    current_direc = None        # obecny kierunek w ktorym przesuwamy platformę
    possible_directions = [Key.left, Key.right, None]  # kierunki
    platform_direction = {Key.left: 'left', Key.right: 'right', None: None}

    end_game = False

    while True:
        os.system("cls")
        paint(gameboard)
        if BOMB[0][0] == 24:
            time.sleep(1)
            if len(PLATFORM) != 1:
                insert_gameboard(BOMB[0], False)
                BOMB[0] = PLATFORM.pop()
                direction = ['up', None]
                continue
            else:
                insert_gameboard(PLATFORM[0], False)
                insert_gameboard(BOMB[0], False)
                os.system("cls")
                paint(gameboard)
                time.sleep(1)
                os.system("cls")
                end_game = True
                print("GAME OVER!!!")
                break

        check_neighbors(BOMB[0])
        if not len(BLOCKS):
            LEVEL += 1
            break
        # decyzja o ruchu platformy

        with Listener(on_press=on_press) as ls:
            def time_out(period_sec: int):
                time.sleep(period_sec)  # Listen to keyboard for period_sec seconds
                ls.stop()


            Thread(target=time_out, args=((LEVEL ** (-1 / 2))/2,)).start()
            ls.join()

        push_bomb()

        if current_direc:
            if current_direc == Key.esc:
                os.system("cls")
                end_game = True
                break

            new_platform_placement()

        current_direc = None

    if end_game:
        break

print('SCORE:', SCORE)
input("press ENTER to exit")
