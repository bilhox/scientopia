import pygame
import json
import pathlib
import os

import perlin_noise
import noise
import math

from camera import Camera

class Tilemap():

    def __init__(self):

        # Map size
        self.size = pygame.Vector2() # In pixel
        self.n_size = pygame.Vector2() # in number of tile

        # The tile size
        self.tile_size = pygame.Vector2()

        self.tileset : list[pygame.Surface] = []

        self.layers : dict[str, list[tuple[pygame.Surface, pygame.Vector2]]] = {}
        self.object_layers : dict[str, list] = {}

        self.thresholds = {0:0, 1:None}
    
    def add_threshold(self, threshold, tile_index) -> None:
        """
        Add a new threshold for the noise value, tile_index is the tile value if the value is between this threshold and the next.
        By default, if there is no threshold, it would be the tile index 0. (can be changed)
        """

        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        
        if not (0 <= tile_index <= 9) and isinstance(tile_index, int):
            raise ValueError("tile_index must be between 0 and 9 and an integer")
        
        self.thresholds[threshold] = tile_index
        self.thresholds = {val:self.thresholds[val] for val in sorted(self.thresholds)}

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

    def load(self, path : str) -> None:

        path_obj = pathlib.Path(path)

        if not os.path.exists(path_obj):
            raise FileNotFoundError(f"The Tiled map file  \'{path_obj.as_posix()}\' does not exist.")
        if path_obj.suffix != "":
            ...

        with open(path_obj) as reader:

            json_obj = json.load(reader)

            self.n_size = pygame.Vector2(json_obj["width"], json_obj["height"])            
            self.tile_size = pygame.Vector2(json_obj["tilewidth"], json_obj["tileheight"])
            self.size = self.n_size.elementwise() * self.tile_size

            self.tileset = []

            for tileset in json_obj['tilesets']:
                self.load_tileset(path_obj.parent.joinpath(tileset["source"]))
            
            
            for layer in json_obj["layers"]:
                if layer["type"] == "tilelayer":
                    layer_data = layer["data"]
                    final_layer_data = []
                    for y in range(layer["height"]):
                        for x in range(layer["width"]):
                            tile_value = layer_data[y * layer["width"] + x % layer["width"]] - 1
                            if tile_value != 0:
                                final_layer_data.append((self.tileset[tile_value], pygame.Vector2(x, y).elementwise() * self.tile_size))
                    
                    self.layers[layer["name"]] = final_layer_data
                
                elif layer["type"] == "objectgroup":
                    objects = []
                    for obj in layer["objects"]:
                        rect = pygame.FRect(obj["x"], obj["y"], obj["width"], obj["height"])
                        objects.append(rect)
                    
                    self.object_layers[layer["name"]] = objects


    def draw(self, camera : Camera) -> None:

        for layer in self.layers.values():

            offseted_layer = []

            for surf, pos in layer:
                offseted_layer.append((surf, round(pos - pygame.Vector2(camera.rect.topleft))))
            
            camera.draw(offseted_layer)