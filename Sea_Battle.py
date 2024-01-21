import random
from enum import Enum

SHIPS_LENGTH = [3, 2, 2, 1, 1, 1, 1]  # зададим длины кораблей

NUMBER_OF_ATTEMPTS = 3000  # попытки заполнения доски


class Direction(Enum):
    Horizontal = 1
    Vertical = 2


class BoardOutException(Exception):  # игрок пытается выстрелить в клетку за пределами поля
    pass


class RepeatShotException(Exception):  # игрок повторно выстреливает в одну и ту же клетку
    pass


class CellIsOccupiedException(Exception):  # игрок пытается выстрелить в занятую клетку
    pass


class ContourOccupiedException(Exception):  # игрок попытается разместить судно в занятом контуре
    pass


class Dot:  # точки на поле

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):  # проверяем точки на равенство
        return self.x == other.x and self.y == other.y


EMPTY = '0'
MISS = 'T'
HIT = 'X'
SHIP = '■'


class Ship:  # корабли на игровом поле

    def __init__(self, length, nose, direction):
        self.length = length
        self.nose = nose
        self.direction = direction
        self.health_count = self.length

    def dots(self):  # возвращаем список всех точек корабля
        dots = []
        if self.direction == Direction.Vertical:  # если корабль вертикалбный, двигаемся вверх
            for i in range(0, self.length):
                next_dot = Dot(self.nose.x, self.nose.y + i)
                dots.append(next_dot)
        else:
            for i in range(0, self.length):  # если горизонтальный, двигаемся вправо
                next_dot = Dot(self.nose.x + i, self.nose.y)
                dots.append(next_dot)
        return dots


class Board:  # нарисуем игровую доску

    def __init__(self, size=6, hid=False):
        self.size = size
        self.hid = hid
        self.board = [[EMPTY for _ in range(size)] for _ in range(size)]
        self.ships = []

    def out(self, dot):  # проверим, принадлежит ли точка полю
        return (0 > dot.x > self.size) or (0 > dot.y > self.size)

    def contour(self, dot):  # обведем корабли по контуру
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:  # пропустим точку
                    continue
                new_x = dot.x + i
                new_y = dot.y + j
                if (0 <= new_x < self.size) and (0 <= new_y < self.size):
                    if self.board[new_x][new_y] == SHIP:  # корабль в соседней точке
                        return True
        return False

    def print_board(self):  # выведем доску в консоль
        print('   |1|2|3|4|5|6|')
        for i in range(len(self.board)):
            print(f'{i + 1}', '|', end=' ')
            for j in range(len(self.board[i])):
                if self.hid and self.board[i][j] == SHIP:
                    print(EMPTY, end=' ')
                else:
                    print(self.board[i][j], end=' ')
            print()

    def all_ships_hit(self):  # проверим, все ли корабли потоплены
        for ship in self.ships:
            if ship.health_count > 0:
                return False
        return True

    def _get_ship_by_dot(self, dot):  # вернем корабль, содержащий точку
        for ship in self.ships:
            if dot in ship.dots():
                return ship

    def shot(self, dot):  # делаем выстрел по доске
        if self.board[dot.x][dot.y] == MISS or self.board[dot.x][dot.y] == HIT:
            raise RepeatShotException(f'Точка была поражена ранее! Выберите другую координату для выстрела!')
        if self.out(dot):  # (0 > dot.x > self.size) or (0 > dot.y > self.size)
            raise BoardOutException(f'Координата выстрела за пределами доски! Выберите другую координату для выстрела!')

        # Попадание по коралю уменьшает его счетчик жизни. Если жизни закончились, тогда корабль потоплен.
        if self.board[dot.x][dot.y] == SHIP:
            self.board[dot.x][dot.y] = HIT
            print('Есть попадание! Так держать!')
            ship = self._get_ship_by_dot(dot)
            ship.health_count -= 1

            if ship.health_count == 0:
                print('КОРАБЛЬ ПОТОПЛЕН!')
            return True  # попадание
        if self.board[dot.x][dot.y] == EMPTY:
            self.board[dot.x][dot.y] = MISS
            return False  # промах

    def add_ship(self, ship):  # проверим исключения и добавим корабли на поле
        for dot in ship.dots():
            if self.out(dot):
                raise BoardOutException(f'Точка выходит за пределы доски')
            if self.board[dot.x][dot.y] == SHIP:
                raise CellIsOccupiedException(f'Точка уже занята другим кораблем')
            if self.contour(dot):  # проверим контуры кораблей
                raise ContourOccupiedException(f'Точка является контуром соседнего корабля')

        for dot in ship.dots():  # отдельно ставим точки
            self.board[dot.x][dot.y] = SHIP
        self.ships.append(ship)
        return True  # корабль успешно поставлен, переходим к следующему


class Player:

    def __init__(self, own_board, opponent_board):
        self.own_board = own_board
        self.opponent_board = opponent_board

    def ask(self):
        pass

    @property
    def move(self):  # делаем ход в игре
        print(f'{self.name()} ходит')
        dot = self.ask()
        try:
            shot = self.opponent_board.shot(dot)
            self.opponent_board.print_board()
            return shot
        except Exception as ex:
            print(ex)
            return True

    def name(self):
        pass


class User(Player):

    def ask(self):
        while True:
            x = input('Введите координату X: ')
            y = input('Введите координату Y: ')
            try:
                x = int(x)
                y = int(y)
                if 1 <= x <= 6 and 1 <= y <= 6:
                    break
                else:
                    raise BoardOutException
            except ValueError:
                print("Вы ввели некорректную координату выстрела!")
            except BoardOutException:
                print("Координата выстрела за пределами доски! Выберите другую координату для выстрела!")
                continue
        return Dot(y - 1, x - 1)

    def name(self):
        return '-Пользователь-'


class AI(Player):

    def ask(self):
        x = random.randint(0, self.opponent_board.size - 1)
        y = random.randint(0, self.opponent_board.size - 1)
        return Dot(x, y)

    def name(self):
        return '-ИИ-'


class Game:

    def __init__(self):  # загружаем игру
        user_board = self.random_board()
        ai_board = self.random_board(hid=True)
        self.user_board = user_board
        self.ai_board = ai_board
        self.user = User(user_board, ai_board)
        self.ai = AI(ai_board, user_board)

    @staticmethod
    def random_board(hid=False):  # сгенерим случайную доску
        board = Board(hid=hid)

        create_board_retry_count = 0

        added_ships = 0
        while added_ships < len(SHIPS_LENGTH):
            while True:
                if create_board_retry_count == NUMBER_OF_ATTEMPTS:
                    # Если попыток для установки корабля не хватило, генерим новую доску
                    print('Создаем игровое поле заново!')
                    create_board_retry_count = 0
                    board = Board(hid=hid)
                    added_ships = 0
                    break
                x = random.randint(0, board.size - 1)
                y = random.randint(0, board.size - 1)
                direction = random.choice([Direction.Vertical, Direction.Horizontal])
                ship = Ship(SHIPS_LENGTH[added_ships], Dot(x, y), direction)

                try:
                    if board.add_ship(ship):
                        added_ships += 1
                        break
                except Exception:
                    create_board_retry_count += 1
                    continue
        return board

    @staticmethod
    def greet():  # приветственное сообщение
        print("Поиграем в 'Морской бой'!")

    def loop(self):  # игровой цикл
        while True:
            while True:
                if self.ai_board.all_ships_hit():
                    print('Игрок -Пользователь- победил!')
                    return
                if not self.user.move:  # если Пользователь не сходил, тогда переход хода
                    break
            while True:
                if self.user_board.all_ships_hit():
                    print('Игрок -ИИ- победил!')
                    return
                if not self.ai.move:  # если ИИ не сходил, тогда переход хода
                    break

    def start(self):  # запуск игры
        self.greet()
        print('Доска Пользователя!')
        self.user_board.print_board()
        self.loop()
        print('Игра окончена!')


if __name__ == '__main__':
    game = Game()
    game.start()
