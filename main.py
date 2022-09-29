from this import d
import pygame
from random import randint, choice

class Brick(pygame.sprite.Sprite):

    def __init__(self, tile_index:tuple[int, int], _type:int, group:pygame.sprite.Group):
        super().__init__(group)
        self.image = pygame.image.load(F"data/graphics/bricks/{_type}.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 40))
        pos = tile_index[0]*GRID_SIZE[0], tile_index[1]*GRID_SIZE[1]
        self.rect = self.image.get_rect(topleft=pos)

class Game:
    def __init__(self):

        self.paddle = Paddle()
        self.ball = Ball(self.paddle.rect)
        self.paddle.ball = self.ball
        self.bricks = pygame.sprite.Group()
        self.make_level()

    def make_level(self):

        for y in range(GRID[1]//2):
            for x in range(GRID[0]):
                if not choice((1, 1, 1, 1, 0)):continue

                Brick((x, y), randint(0,2), [self.bricks])

    def reset(self):
        self.paddle.rect.center = self.paddle.start_pos
        self.ball.attached = True
        self.ball.velocity = pygame.Vector2(choice((1,-1)),-1).normalize()*self.ball.speed
        self.bricks.empty()
        self.make_level()
    
    def draw(self):
        
        screen.fill("skyblue")
        self.bricks.draw(screen)
        self.paddle.draw()
        self.ball.draw()
    
    def run(self):
        self.bricks.update()
        self.paddle.run()
        self.ball.run(self.paddle, self.bricks)

class Paddle:

    def __init__(self):
        self.start_pos = W//2, H-50
        self.image = pygame.image.load("data/graphics/paddle/paddle.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 2)
        self.rect = self.image.get_rect(center=self.start_pos)

        self.ball:Ball = None

        self.moving = False
        self.direction = 1
        self.max_speed = 15
        self.acceleration = 1
        self.deceleration = 5
        self.velocity = 0

    def draw(self):
        screen.blit(self.image, self.rect)

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.moving = True
            self.direction = -1
        if keys[pygame.K_RIGHT]:
            self.moving = True
            self.direction = 1
        if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]: self.moving = False

        if self.ball.attached and keys[pygame.K_SPACE]:
            self.ball.attached = False

    def move(self):

        if self.moving:
            self.velocity += self.acceleration*self.direction
        elif self.velocity > 5 or self.velocity < -5: self.velocity -= self.deceleration*self.direction
        else: self.velocity = 0

        if self.direction == 1 and self.velocity < 0:
            self.velocity = 0
        if self.direction == -1 and self.velocity > 0:
            self.velocity = 0

        self.velocity = max(-self.max_speed, min(self.velocity, self.max_speed))

        self.rect.x += self.velocity

        if self.rect.right > W:
            self.rect.right = W
            self.velocity = 0
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity = 0

    def run(self):
        self.get_input()
        self.move()

class Ball:

    def __init__(self, paddle_rect:pygame.Rect):
        self.image = pygame.image.load("data/graphics/ball/ball.png").convert_alpha()
        # self.image = pygame.transform.rotozoom(self.image, 0, 1)
        self.rect = self.image.get_rect(midbottom=paddle_rect.midtop)
        self.attached = True

        self.speed = 12
        self.velocity = pygame.Vector2(choice((1,-1)),-1).normalize()*self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

    def detect_collsion(self, direction:str, paddle:Paddle, bricks:pygame.sprite.Group):
        collision_objs = list(bricks.sprites())
        collision_objs.append(paddle)

        if direction == "horizontal":
            for obj in collision_objs:

                is_brick = isinstance(obj, Brick)
                if is_brick: moving_vel = 0
                else: moving_vel = paddle.velocity

                if self.rect.colliderect(obj.rect):

                    if self.velocity.x-moving_vel > 0:
                        self.rect.right = obj.rect.left
                    elif self.velocity.x-moving_vel < 0:
                        self.rect.left = obj.rect.right
                    self.velocity.x *= -1

                    if is_brick:
                        obj.kill()
                    else:
                        self.velocity = (self.velocity + pygame.Vector2(paddle.velocity,0)).normalize() *self.speed

                    return
        
        elif direction == "vertical":
            
            for obj in collision_objs:

                if self.rect.colliderect(obj.rect):

                    if self.velocity.y > 0:
                        self.rect.bottom = obj.rect.top
                    elif self.velocity.y < 0:
                        self.rect.top = obj.rect.bottom
                    self.velocity.y *= -1

                    if isinstance(obj, Brick):
                        obj.kill()
                    else:
                        self.velocity = (self.velocity + pygame.Vector2(paddle.velocity,0)).normalize() *self.speed

                    return

    def move(self, paddle, bricks):
        self.rect.x += self.velocity.x
        self.detect_collsion("horizontal", paddle, bricks)
        self.rect.y += self.velocity.y
        self.detect_collsion("vertical", paddle, bricks)

        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity.y *= -1
        elif self.rect.bottom > H:
            self.rect.bottom = H
            self.velocity.y *= -1
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity.x *= -1
        if self.rect.right > W:
            self.rect.right = W
            self.velocity.x *= -1

    def run(self, paddle:Paddle, bricks:pygame.sprite.Group):
        if self.attached:
            self.rect.midbottom = paddle.rect.midtop
            return

        self.move(paddle, bricks)


pygame.init()

W, H = 1280, 720
GRID = (W//32, H//36)
GRID_SIZE = (80,40)

screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN|pygame.SCALED)
clock = pygame.time.Clock()
pygame.display.set_caption("Brick Breaker")
game = Game()

while True:

    pygame.display.update()
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            if event.key == pygame.K_RETURN:
                game.reset()

    game.run()
    game.draw()
