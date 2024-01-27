import pygame
import math
import pathlib
import gif_pygame

from camera import Camera


SIDES = {(1, 0):"east",
         (1, -1):"northeast",
         (0, -1):"north",
         (-1, -1):"northwest",
         (-1, 0):"west",
         (-1, 1):"southwest",
         (0, 1):"south",
         (1, 1):"southeast",
         (0, 0):"None"
         }

def load_player_assets(path : str):

    xpath = pathlib.Path(path)
    
    ressources = {}

    for p in xpath.iterdir():
        if p.name == "animations":
            anims = {}
            for anim in p.iterdir():
                animation = {}
                for side in anim.iterdir():
                    gif = gif_pygame.load(side.as_posix())
                    animation[side.stem] = gif
                anims[anim.name] = animation
            ressources["animations"] = anims
        elif p.name == "textures":
            texs = {}
            for tex in p.iterdir():
                texture = {}
                for side in tex.iterdir():
                    texture[side.stem] = pygame.image.load(side.as_posix()).convert_alpha()
                texs[tex.name] = texture
            ressources["textures"] = texs

    return ressources


class Player:
    def __init__(self):
        self.hitbox = pygame.FRect(0, 0, 12, 8)
        self.z_height = 24

        self.velocity = pygame.Vector2()

        self.speed = 100
        self.easing_timer = 0

        self.keys = {"left": False, "right": False, "up": False, "down": False}
        self.collision_side = {
            "left": False,
            "right": False,
            "top": False,
            "bottom": False,
        }

        self.jumping = False

        self.ressources = load_player_assets("assets/player/")
        self.image = self.ressources["textures"]["idle"]["south"]
        self.animation = None
        self.direction = "south"

    def update(self, dt: float):
        direction = pygame.Vector2()

        if self.keys["left"]:
            direction.x -= 1
        if self.keys["right"]:
            direction.x += 1
        if self.keys["up"]:
            direction.y -= 1
        if self.keys["down"]:
            direction.y += 1

        side = SIDES[tuple(direction)]

        if side == "None":
            self.animation = None
            self.image = self.ressources["textures"]["idle"][self.direction]
        else:
            self.direction = side
            self.animation = self.ressources["animations"]["walking"][self.direction]

        if direction:
            direction.normalize_ip()

        if not direction:
            self.easing_timer = max(self.easing_timer - dt, 0)
        else:
            self.easing_timer = min(self.easing_timer + dt, 0.5)

        self.velocity = (
            direction
            * self.speed
            * dt
            * (math.sin((self.easing_timer / 0.5 * math.pi) / 2))
        )

    def is_able_to_jump(self):
        return not self.jumping and (self.y_timer <= 0)

    def collided(self, colliders: list[pygame.FRect]) -> list[pygame.FRect]:
        collided = []

        for collider in colliders:
            if self.hitbox.colliderect(collider):
                collided.append(collider)

        return collided

    def collisions(self, colliders: list[pygame.FRect]):
        collision_side = {"left": False, "right": False, "top": False, "bottom": False}

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

    def draw(self, camera: Camera):
        pos = pygame.Vector2(
            self.hitbox.centerx - self.image.get_width() / 2,
            self.hitbox.bottom - self.z_height,
        ) - pygame.Vector2(camera.rect.topleft)

        image = self.image if not self.animation else self.animation.blit_ready()

        camera.draw([(image, round(pos))])
