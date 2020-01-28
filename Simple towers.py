# Определение библиотек
import pygame
import sys
import os

# Определение глобальных переменных
pygame.init()
# Ширина и высота экрана
size = WIDTH, HEIGHT = (600, 450)
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
tower_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
FPS = 60
Life = 100
# Настройки и загрузка уровней находятся в разработке
# Settings, Load_game = [False] * 2
Game = False
# Уровень в переменной
table = []


# Загрузка текстур
def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


# Аварийное завершение программы
def terminate():
    pygame.quit()
    sys.exit()


# Кнопка
class Button(pygame.sprite.Sprite):
    # Определение переменных
    def __init__(self, group, rect, depth=1, color=None, text='', text_color=None):
        self.x, self.y, self.width, self.height = rect
        self.id = len(group)
        self.image = pygame.Surface((self.x, self.y), pygame.SRCALPHA)
        super().__init__(group)
        # Отрисовка текста кнопки
        font = pygame.font.Font(None, 40)
        if isinstance(text_color, str):
            text = font.render(text, 1, pygame.Color(text_color))
        elif isinstance(text_color, tuple):
            text = font.render(text, 1, text_color)
        else:
            text = font.render(text, 1, (0, 0, 0))
        text_x = self.width // 2 - text.get_width() // 2
        text_y = self.height // 2 - text.get_height() // 2
        self.image.blit(text, (text_x, text_y))
        # Отрисовка фона кнопки
        if isinstance(color, str):
            pygame.draw.rect(self.image, pygame.Color(color), (0, 0, self.width, self.height),
                             depth)
        elif isinstance(text_color, tuple):
            pygame.draw.rect(self.image, color, (0, 0, self.width, self.height), depth)
        else:
            pygame.draw.rect(self.image, (0, 0, 0), (0, 0, self.width, self.height), depth)
        self.rect = pygame.Rect(rect)

    # Проверка и отклик на нажатие на кнопку
    def update(self, *args):
        global Game
        # global Settings, Load_game
        if args[0] and args[0].button == 1 and \
                self.rect.collidepoint(args[0].pos[0], args[0].pos[1]):
            if self.id == 0:
                Game = True
            # elif self.id == 1:
            #     Load_game = True
            # elif self.id == 2:
            #     Settings = True
            elif self.id == 3:
                terminate()


# Загрузка стартового экрана
def start_screen():
    text = ['Новая игра', 'Выход']
    # Отрисовка заднего фона
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    # Отрисовка названия игры
    font = pygame.font.Font(None, 30)
    logo = font.render('Simple towers.', 1, pygame.Color('blue'))
    screen.blit(logo, (WIDTH // 2 - logo.get_width() // 2, HEIGHT // 5 - logo.get_height() // 2))
    # Отступ в пикселях между кнопками
    step = 50
    # Отрисовка каждой кнопки
    for i in range(len(text)):
        Button(button_group, (WIDTH // 2 - 100, HEIGHT // 4 + step * i, 200, 40), 1, (0, 0, 0),
               text[i], 'red')
    # Основной цикл начального экрана
    while True:
        button_group.draw(screen)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                button_group.update(ev)
                return
        pygame.display.flip()
        clock.tick(FPS)

# Выбор уровня. В разработке
# def choose_level():
# fon = pygame.transform.scale(load_image('fon.jpg')
# for ev in pygame.event.get():
# if ev.type == pygame.QUIT:
# terminate()
# elif ev.type == pygame.KEYDOWN:
# if ev.key == pygame.K_ESCAPE:
# return


# Загрузка уровня из папки
def load_level(filename):
    filename = "data/levels/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda z: z.ljust(max_width, '#'), level_map))


# Генерация уровня на экране
def generate_level(level):
    global table
    table, row = [], []
    for rows in range(len(level)):
        for cols in range(len(level[rows])):
            if level[rows][cols] == '.':
                Tile('road', cols, rows)
                row.append(0)
            elif level[rows][cols] == '#':
                Tile('wall', cols, rows)
                row.append(1)
            elif level[rows][cols] == '@':
                Tile('wall', cols, rows)
                Tower(cols, rows)
                row.append(2)
        table.append(row)
        row = []


# Определение основных текстур в переменной
tile_images = {'wall': load_image('grass.png'), 'road': load_image('road.png')}
tile_width = tile_height = 50


# Плитка, по которой двигаются враги или, на которой стоят башни
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


# Башня. Стреляет во врагов
class Tower(pygame.sprite.Sprite):
    # Определение переменных
    def __init__(self, pos_x, pos_y):
        super().__init__(tower_group, all_sprites)
        self.x = pos_x
        self.y = pos_y
        self.rad = 25
        self.pos = []
        self.duration = 50
        self.image = pygame.Surface((2 * self.rad, 2 * self.rad), pygame.SRCALPHA)
        self.radius = self.image.get_width() * 2
        self.rect = self.image.get_rect().move(tile_width * self.x, tile_height * self.y)
        pygame.draw.circle(self.image, (255, 0, 0), (self.rad, self.rad), self.rad)

    # Взаимодействие с врагами и стрельба по ним пулями
    def update(self, *args):
        if not isinstance(args[0], str):
            if self.rect.collidepoint(args[0].pos):
                self.kill()
        elif args[0] == 'shoot':
            if self.duration == 0:
                self.duration = 25
                for i in enemy_group:
                    self.pos = i.get_pos()
                    if pygame.sprite.collide_circle(self, i):
                        Bullet(self.radius, tile_width * self.x, tile_height * self.y,
                               self.pos[0] - self.x * tile_width,
                               self.pos[1] - self.y * tile_height)
            else:
                self.duration -= 1


# Враг, равномерно движущийся по дороге.
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, v_x, v_y):
        # Определение переменных
        super().__init__(enemy_group, all_sprites)
        self.v_x = v_x
        self.v_y = v_y
        self.image = load_image('enemy.png')
        self.radius = self.image.get_width() // 2
        self.rect = self.image.get_rect().move(tile_width * pos_x + 12, tile_height * pos_y + 12)
        self.x = self.rect.x + self.rect.width // 2
        self.y = self.rect.y + self.rect.height // 2

    # Передача своей позиции на экране для расчёта движения пули
    def get_pos(self):
        return [self.rect.x + self.radius, self.rect.y + self.radius]

    # Движение с изменением направления, чтобы враги двигались иключительно по проложенной дороге
    def update(self, *args):
        global Life
        # Условие, исправляющие баг с вылетом игры
        if (self.x + tile_width // 2) // tile_width <= len(table[0]) - 1 and (
                self.y + tile_height // 2) // tile_height <= len(table) - 1:
            # Изменение движения на вертикальное
            if self.v_x != 0 and table[self.y // tile_height]\
            [(self.x + tile_width // 2 * self.v_x) // tile_width] >= 1:
                if table[(self.y + tile_height + 1 // 2) // tile_height][self.x // tile_width] >= 1:
                    self.v_y = -abs(self.v_x)
                else:
                    self.v_y = abs(self.v_x)
                self.v_x = 0
            # Изменение движения на горизонтальное
            elif self.v_y != 0 and table[(self.y + tile_height // 2 * self.v_y) // tile_height]\
            [self.x // tile_width] >= 1:
                if table[self.y // tile_height][(self.x + tile_width + 1 // 2) // tile_width] >= 1:
                    self.v_x = -abs(self.v_y)
                else:
                    self.v_x = abs(self.v_y)
                self.v_y = 0
        # Самоуничтожение при выходе за границы поля
        if self.rect.y > len(table) * tile_height or self.rect.x > len(table[0]) * tile_width or \
                self.rect.y + self.rect.height < 0 or self.rect.x + self.rect.width < 0:
            self.kill()
            Life -= 1
        self.x += self.v_x
        self.y += self.v_y
        self.rect.left += self.v_x
        self.rect.top += self.v_y

    # Самоуничтожение
    def selfdestruct(self):
        self.kill()


# Пуля. Летит по направлению к врагу и убивает его по возможности
class Bullet(pygame.sprite.Sprite):
    def __init__(self, radius, pos_x, pos_y, range_x, range_y):
        # Определение переменных
        super().__init__(bullet_group, all_sprites)
        self.r = radius
        self.range_x = range_x
        self.range_y = range_y
        if range_x < 0:
            self.v_x = range_x // 80
        else:
            self.v_x = range_x // 80 + 1
        if range_y < 0:
            self.v_y = range_y // 80
        else:
            self.v_y = range_y // 80 + 1
        self.count = 0
        self.image = load_image('bullet.png', -1)
        self.rect = self.image.get_rect().move(pos_x + 25 - self.image.get_width() // 2,
                                               pos_y + 25 - self.image.get_height() // 2)

    # Реализация движения
    def update(self, *args):
        global Money
        self.rect.left += self.v_x
        self.rect.top += self.v_y
        for i in enemy_group:
            if pygame.sprite.collide_rect(self, i):
                i.selfdestruct()
                self.kill()
                Money += 1
        if self.count == 80:
            self.kill()
        self.count += 1


# Главный цикл игры
while True:
    start_screen()
    if Game:
        towers = 0
        Life = 100
        Money = 20
        generate_level(load_level('level1.txt'))
        count = 50
        while Game:
            if Life:
                all_sprites.draw(screen)
                font = pygame.font.Font(None, 20)
                money_text = font.render(f'Деньги: {Money}', 1, pygame.Color('yellow'))
                screen.blit(money_text, (100, 25))
                life_text = font.render(f'Жизни: {Life}', 1, pygame.Color('red'))
                screen.blit(life_text, (400, 25))
                if count == 0:
                    Enemy(1, 0, 0, 1)
                    count = 50
                else:
                    count -= 1
                enemy_group.update()
                tower_group.update('shoot')
                bullet_group.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        terminate()
                    if event.type == pygame.MOUSEBUTTONDOWN and Money >= 20 + towers * 10:
                        x, y = event.pos
                        if table[y // 50][x // 50] == 1:
                            Tower(x // 50, y // 50)
                            table[y // 50][x // 50] = 2
                            towers += 1
                            Money -= 20 + (towers - 1) * 10
                        elif table[y // 50][x // 50] == 2:
                            tower_group.update(event)
                            table[y // 50][x // 50] = 1
                            towers -= 1
            else:
                fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
                screen.blit(fon, (0, 0))
                font = pygame.font.Font(None, 30)
                game_over = font.render(f'Вы проиграли', 1, pygame.Color('red'))
                screen.blit(game_over, (WIDTH // 2 - game_over.get_width() // 2,
                                        HEIGHT // 2 - game_over.get_height() // 2))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        terminate()
                    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                        Game = False
            pygame.display.flip()
            clock.tick(FPS)
