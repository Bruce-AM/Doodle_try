import pygame
from random import randint
from collections import deque

pygame.init()

WIDTH, HEIGHT = 500, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('Doodle copy')

class Player:
    def __init__(self):
        self.radius = 20
        self.pos = pygame.Vector2(WIDTH // 2, 600 - self.radius)
        self.old_pos = pygame.Vector2(WIDTH // 2, 600 - self.radius)
        self.acc = pygame.Vector2(0, 0)
        self.gravity = 1
        self.damping = 0.9
        self.speed = 1
        self.jump_height = -35
        self.jump = True
        self.movement = {pygame.K_a: (-self.speed, 0), 
                         pygame.K_d: (self.speed, 0), 
                         pygame.K_SPACE: (0, self.jump_height)}

    def update(self):
        velocity = (self.pos - self.old_pos) * self.damping
        self.old_pos = self.pos.copy()
        self.pos += velocity + self.acc  # Apply acceleration
        self.acc = pygame.Vector2(0, 0)  # Reset acceleration
        if self.pos.x > WIDTH: # wrap around x
            self.pos.x -= WIDTH
            self.old_pos.x -= WIDTH
        elif self.pos.x < 0:
            self.pos.x += WIDTH
            self.old_pos.x += WIDTH

    def apply_force(self, force):
        self.acc = force

player = Player()

class Obstacle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 100, 10)
        self.speed = 1
        self.collidable = False

    def update(self):
        self.rect.y += self.speed

    def check_collidability(self):
        return self.rect.left < player.pos.x < self.rect.left + self.rect.width and player.pos.y + player.radius < self.rect.top
    
    def keep_player_on_top(self):
        if self.rect.left < player.pos.x < self.rect.left + self.rect.width:
            if player.pos.y + player.radius > self.rect.top:
                player.pos.y = self.rect.top - player.radius
                player.jump = True
        else:
            self.collidable = False
    

random_x_pos = lambda : randint(0, WIDTH-100)
random_y_pos = lambda y: randint(y - 200, y - player.radius)

# pre spawn obstacle
obstacles = deque([])
obstacles.append(Obstacle(WIDTH // 2 - 50, 650)) # initial position

score = 0
best_score = 0
time, time_step = 0, 100
running = True
while running:
    color = 30 + (170 * min(1, score/17000))
    screen.fill((color, color, color))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # CONTROLLS check
    keys = pygame.key.get_pressed() 
    for key in player.movement:
        if keys[key]:
            if key == pygame.K_SPACE:
                if player.jump:
                    player.apply_force(player.movement[key])
                    player.update()    
            else:
                player.apply_force(player.movement[key])
                player.update()
    
    player.apply_force((0, player.gravity))
    player.update()
    player.jump = False

    # bound with floor check
    score += 1
    if player.pos.y + player.radius > HEIGHT:
        player.pos.y = HEIGHT - player.radius
        player.jump = True
        # update score
        best_score = max(score, best_score)
        score = 0

    # staying on the obstacle check
    for obstacle in obstacles:
        if obstacle.check_collidability():
            obstacle.collidable = True
        if obstacle.collidable:
            obstacle.keep_player_on_top()
        
    # obstacles spawn / dispawn
    y = obstacles[-1].rect.top
    if y > 0:
        obstacles.append(Obstacle(random_x_pos(), random_y_pos(y)))
    y = obstacles[0].rect.top
    if y > HEIGHT:
        obstacles.popleft()

    # DRAW PLAYER
    pygame.draw.circle(screen, (100, 100, 255), (player.pos.x, player.pos.y), player.radius, 3)

    # draw and move obstacles
    for obstacle in obstacles:
        obstacle.update()
        pygame.draw.rect(screen, (200, 100, 100), obstacle.rect)
    
    #screen.blit(pygame.font.Font(None, 20).render(f"FPS: {int(clock.get_fps())} x: {int(player.pos.x)} y: {int(player.pos.y)}", True, (255, 255, 255)), (10, 30))
    #screen.blit(pygame.font.Font(None, 20).render(f"Obstacles: {len(obstacles)}", True, (255, 255, 255)), (10, 50))
    screen.blit(pygame.font.Font(None, 20).render(f"Best: {best_score}, Score: {score}", True, (255, 255, 255)), (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()