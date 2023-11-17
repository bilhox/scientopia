import pygame
import json
import perlin_noise
import pathlib
import math

from camera import Camera

class Tilemap():

    def __init__(self):

        # Map size
        self.size = pygame.Vector2() # In pixel
        self.n_size = pygame.Vector2() # in number of tile

        # The tile size
        self.tile_size = pygame.Vector2()

        self.tileset = []

        self.tileset_path = []
        self.tilemap_path = ""

        self.layers : dict[str, list[tuple[pygame.Surface, pygame.Vector2]]] = {}
        self.object_layers : dict[str, list] = {}
    

    def load_tileset(self, path) -> None:
        
        tile_list = []

        path_obj = pathlib.Path(path)

        with open(path_obj) as reader:
            json_obj = json.load(reader)

            tile_width, tile_height = json_obj["tilewidth"], json_obj["tileheight"]

            image = pygame.image.load(path_obj.parent.joinpath(json_obj["image"])).convert_alpha()

            for y in range(json_obj["imageheight"]//tile_height):
                for x in range(json_obj["columns"]):
                    
                    tile_list.append(image.subsurface(pygame.Rect([x*tile_width, y*tile_height], [tile_width, tile_height])))
        
        self.tileset.extend(tile_list)

    def generate(self, size : pygame.Vector2) -> None:


        self.n_size = size.copy()      
        self.tile_size = pygame.Vector2(16, 16)
        self.size = pygame .Vector2(self.n_size.x*self.tile_size.x, self.n_size.y*self.tile_size.y)

        a = perlin_noise.PerlinNoise(octaves=8)

        map_sample = [[round(a([i/size.x, j/size.y]), 1) for i in range(int(size.x))] for j in range(int(size.y))]

        patterns = {(0, 0, 0, 0):158, (0, 0, 1, 1):141, (0, 1, 1, 0):142, (1, 1, 0, 0):130, (1, 0, 0, 1):129, (0, 0, 0, 1):120, (0, 0, 1, 0):138, (0, 1, 0, 0):121, (1, 0, 0, 0):126}
        # (1, 1, 1, 0):121, (1, 1, 0, 1):126, (1, 0, 1, 1):120, (0, 1, 1, 1):138,
        temp_map = []

        for j in range(int(size.y)):
            l = []
            for i in range(int(size.x)):
                if map_sample[j][i] <= 0:
                    l.append(0)
                else:
                    l.append(1)
            temp_map.append(l)

        final_map = []

        for j in range(int(size.y)):
            for i in range(int(size.x)):

                if temp_map[j][i] == 1:
                    final_map.append((self.tileset[125], pygame.Vector2(i, j).elementwise() * self.tile_size))
                    continue
                
                pattern = []

                for k in range(4):
                    b = int(j-math.cos(math.pi/2*k))
                    c = int(i+math.sin(math.pi/2*k))

                    if b < 0 or b > size.x-1 or c < 0 or c > size.y-1:
                        pattern.append(temp_map[j][i])
                    else:
                        pattern.append(temp_map[b][c])
                            
                pattern = tuple(pattern)
                val = patterns.get(pattern, 158)
                final_map.append((self.tileset[val], pygame.Vector2(i, j).elementwise() * self.tile_size))

        self.layers["foreground"] = final_map
        
        # for layer in json_obj["layers"]:
        #     if layer["type"] == "tilelayer":
        #         layer_data = layer["data"]
        #         final_layer_data = {}
        #         for y in range(layer["height"]):
        #             for x in range(layer["width"]):
        #                 tile_value = layer_data[y*layer["width"] + x%layer["width"]]
        #                 if tile_value != 0:
        #                     final_layer_data[(x, y)] = tile_value
                
        #         self.layers[layer["name"]] = final_layer_data
            
        #     elif layer["type"] == "objectgroup":
        #         objects = []
        #         for obj in layer["objects"]:
        #             rect = pygame.FRect(obj["x"], obj["y"], obj["width"], obj["height"])
        #             objects.append(rect)
                
        #         self.object_layers[layer["name"]] = objects
                    

    def draw(self, camera : Camera) -> None:

        for layer in self.layers.values():

            offseted_layer = []

            for surf, pos in layer:
                offseted_layer.append((surf, pos - pygame.Vector2(camera.rect.topleft)))
            
            camera.draw(offseted_layer)