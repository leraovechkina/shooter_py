from pygame import *
from random import randint
from time import time as timer

font.init()

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__()
        self.image = transform.scale(image.load(player_image),(size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    def reset(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_w - 75:
            self.rect.x += self.speed
    def fire(self):
        bullet = Bullet('bullet.png', self.rect.centerx - 5, self.rect.top, 10, 20, 5)
        bullets.add(bullet)

class Enemy(GameSprite):
    def update(self):
        global lost
        if self.rect.y < win_h:
            self.rect.y += self.speed
        else:
            lost += 1
            self.rect.y = 0
            self.rect.x = randint(5, win_w-75)

class Bullet(GameSprite):
    def update(self):
        if self.rect.y > 0:
            self.rect.y -= self.speed
        else:
            self.kill()

class Button():
    def __init__(self, x, y, width, height, text, font, hover_image_path = False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.image = Surface((width, height))
        self.image.fill((106, 90, 205))
        self.hover_image = self.image

        if hover_image_path:
            self.hover_image = Surface((width, height))
            self.hover_image.fill((72, 61, 139))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hovered = False
    def draw(self, screen):
        if self.hovered:
            current_image = self.hover_image
        else:
            current_image = self.image
        screen.blit(current_image, self.rect.topleft)

        if not self.text == '':
            font1 = font.SysFont('Arial', self.font)
            self.text_surface = font1.render(self.text, 1, (75, 0, 130))
            win.blit(self.text_surface, (self.rect.centerx - self.font - 5, self.rect.centery - 20))
    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1: 
            return self.rect.collidepoint(event.pos)
        return False

def mine():
    global win, lost, score, num_fire, rel_time
    num_fire = 0
    rel_time = False
    lost = 0
    score = 0

    for bullet in bullets:
        bullet.kill()
    for monster in enemy:
        monster.kill()
        
    game_button = Button(win_w/2-(250/2), 200, 250, 100, 'Играть', 70, True)
    exit_button = Button(win_w/2-(250/2), 400, 250, 100, 'Выйти', 70, True)

    clock = time.Clock()
    FPS = 60

    game = True
    while game:
        win.blit(fon_game, (0, 0))

        mouse_pos = mouse.get_pos()

        for e in event.get():
            if e.type == QUIT:
                game = False

            if exit_button.handle_event(e):
                game = False

            if game_button.handle_event(e):
                game = False
                game_start()

        win.blit(fon_game, (0, 0))

        game_button.draw(win)
        exit_button.draw(win)
        
        game_button.check_hover(mouse_pos)
        exit_button.check_hover(mouse_pos)

        
        display.update()
        clock.tick(FPS)

def game_start():
    global lost, score, win, num_fire, rel_time, max_score

    clock = time.Clock()
    FPS = 60

    player_rocket = Player('rocket.png', (win_w // 2) - 60, win_h - 145, 70, 70, 7)
    
    for i in range(5):
        monster = Enemy('ufo.png', randint(5, win_w-75), -50, 80, 50, randint(1,4))
        enemy.add(monster)

    font_game = font.SysFont('Arial', 36)
    font_pause = font.SysFont('Arial', 100)
    font_finish = font.SysFont('Arial', 100)
    text_fire = font_game.render('Идёт перезарядка...', 1, (139, 0, 0))

    exit_button = Button(50, 640, 320, 50, 'В миню', 45, True)
    pause_button = Button(510, 640, 320, 50, 'Пауза', 45, True)
    
    game = True
    finish = False
    pause = False
    while game:
        win.blit(fon_game, (0, 0))

        mouse_pos = mouse.get_pos()
        
        for e in event.get():
            if e.type == QUIT:
                game = False

            elif exit_button.handle_event(e):
                game = False
                mine()

            elif e.type == KEYDOWN:
                if e.key == K_SPACE:
                    if num_fire < 7 and rel_time == False:
                        num_fire += 1
                        player_rocket.fire()
                    
                    if num_fire >= 7 and rel_time == False:
                        start_time = timer()
                        rel_time = True

            elif pause_button.handle_event(e):
                pause = not pause
            
        exit_button.check_hover(mouse_pos)
        pause_button.check_hover(mouse_pos)     

        if not pause and not finish:
           
            collides = sprite.groupcollide(enemy, bullets, True, True)

            for collide in collides:
                score += 1
                monster = Enemy('ufo.png', randint(5, win_w - 75), -50, 80, 50, randint(1, 4))
                enemy.add(monster)

            player_rocket.reset(win)
            enemy.draw(win)
            bullets.draw(win)
            exit_button.draw(win)
            pause_button.draw(win)

            player_rocket.update()
            enemy.update()
            bullets.update()

            text_lost = font_game.render('Пропущено: ' + str(lost), 1, (255, 255, 255))
            win.blit(text_lost, (10, 45))

            monster_down_text = font_game.render('Сбито: ' + str(score), 1, (255, 255, 255))
            win.blit(monster_down_text, (10, 15))

            if rel_time == True:
                end_time = timer()
                if end_time - start_time >= 2:
                    num_fire = 0
                    rel_time = False
                win.blit(text_fire, (win_w/2 - 120, win_h - 100))

            if lost >= 5 or sprite.spritecollide(player_rocket, enemy, False):
                finish = True

        elif pause:
            
            text_pause = font_pause.render('ПАУЗА', 1, (255, 255, 0))
            win.blit(text_pause, (win_w/2 - 130, win_h/2 - 20 ))

            exit_button.draw(win)
            pause_button.draw(win)

        elif finish:

            if max_score < score:
                max_score = score

            text_finish = font_finish.render('Игра окончина', 1, (255, 255, 255))
            win.blit(text_finish, (win_w/2 - 220, 100))

            text_max_score = font_game.render('Лучший результат: ' + str(max_score), 1, (255, 255, 255))
            win.blit(text_max_score, (win_w/2 - 200, 250))

            text_lost = font_game.render('Всего пропущено: ' + str(lost), 1, (255, 255, 255))
            win.blit(text_lost, (win_w/2 - 200, 350))

            text_score = font_game.render('Сбито: ' + str(score), 1, (255, 255, 255))
            win.blit(text_score, (win_w/2 - 200, 450))

            exit_button = Button(win_w/2 - 150, 640, 320, 50, 'В миню', 45, True)
            exit_button.check_hover(mouse_pos)
            exit_button.draw(win)
            
        display.update()
        clock.tick(FPS)

    for bullet in bullets:
        bullet.kill()
    for monster in enemy:
        monster.kill()

win_w = 900
win_h = 700

win = display.set_mode((win_w, win_h))
display.set_caption('Шутер')

font.init()

num_fire = 0
rel_time = False
finish = False
lost = 0
score = 0
max_score = 0

fon_game = transform.scale(image.load('galaxy.jpg'), (win_w, win_h))

player_rocket = Player('rocket.png', (win_w//2)-60, win_h-75, 70, 70, 7)
enemy = sprite.Group()
bullets = sprite.Group()

font_game = font.SysFont('Arial', 36)
 
mine()