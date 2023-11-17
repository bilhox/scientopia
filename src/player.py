import pygame
from camera import Camera

class Player:

    def __init__(self):

        self.hitbox = pygame.FRect(0, 0, 16, 8)
        self.z_height = 24

        self.image = pygame.Surface([16, self.z_height])
        self.image.fill([237, 25, 158])

        self.velocity = pygame.Vector2()
    
        self.speed = 100
        self.friction = 0.3

        self.keys = {"left":False, "right":False, "up":False, "down":False}
        self.collision_side = {"left":False, "right":False, "top":False, "bottom":False}

        self.jumping = False

    def update(self, dt : float):

        direction = pygame.Vector2()

        if self.keys["left"]:
            direction.x -= 1
        if self.keys["right"]:
            direction.x += 1
        if self.keys["up"]:
            direction.y -= 1
        if self.keys["down"]:
            direction.y += 1
        
        if direction:
            direction.normalize_ip()
        
        if not direction:
            self.velocity *= self.friction
        
        self.velocity = direction * self.speed * dt
    
    def is_able_to_jump(self):
        return not self.jumping and (self.y_timer <= 0)


    def collided(self, colliders : list[pygame.FRect]) -> list[pygame.FRect]:

        collided = []

        for collider in colliders:
            if self.hitbox.colliderect(collider):
                collided.append(collider)

        return collided
    
    def collisions(self, colliders : list[pygame.FRect]):
        
        collision_side = {"left":False, "right":False, "top":False, "bottom":False}

        self.hitbox.x += self.velocity.x
        collided = self.collided(colliders)

        for collider in collided:
            if self.velocity.x < 0:
                self.hitbox.left = collider.right
                collision_side["left"] = True
            else:
                self.hitbox.right = collider.left
                collision_side["right"] = True
        
        self.hitbox.y += self.velocity.y
        collided = self.collided(colliders)

        for collider in collided:
            if self.velocity.y < 0:
                self.hitbox.top = collider.bottom
                collision_side["top"] = True
            else:
                self.hitbox.bottom = collider.top
                collision_side["bottom"] = True
        
        self.collision_side = collision_side
    
    def post_update(self):

        if self.collision_side["bottom"]:
            self.velocity.y = 0
            self.y_timer = 0
            self.jumping = False
        elif self.collision_side["top"]:
            self.velocity.y = 0
            self.y_timer = 0

    def draw(self, camera : Camera):

        pos = pygame.Vector2(self.hitbox.x, self.hitbox.bottom - self.z_height) - pygame.Vector2(camera.rect.topleft)
        camera.draw([(self.image, pos)])