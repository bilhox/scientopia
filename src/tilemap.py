import pygame
import json
import pathlib
import opensimplex
import numpy

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

    def generate(self, size : pygame.Vector2) -> None:
        """
        Generates the map, the size must be a vector of 2 integer values
        """


        self.n_size = size.copy()
        self.tile_size = pygame.Vector2(16, 16)
        self.size = pygame.Vector2(self.n_size.x*self.tile_size.x, self.n_size.y*self.tile_size.y)
        a = opensimplex.OpenSimplex(0)
        map_samples = a.noise2array(numpy.array([2*i/size.x for i in range(int(size.x))]), numpy.array([2*i/size.x for i in range(int(size.y))]))
        

        final_map = []
        thresholds = list(self.thresholds.items())

        for j in range(int(size.y)):
            for i in range(int(size.x)):

                index = 0
                for k in range(len(thresholds) - 1):
                    if thresholds[k][0] <= abs(map_samples[i, j]) <= thresholds[k + 1][0]:
                        index = thresholds[k][1]
                        break

                tile = self.tileset[index], pygame.Vector2(i, j).elementwise() * self.tile_size
                final_map.append(tile)

        self.layers["foreground"] = final_map


    def draw(self, camera : Camera) -> None:

        for layer in self.layers.values():

            offseted_layer = []

            for surf, pos in layer:
                offseted_layer.append((surf, round(pos - pygame.Vector2(camera.rect.topleft))))
            
            camera.draw(offseted_layer)