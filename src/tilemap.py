import pygame
import json
import pathlib
import opensimplex
import numpy
import random
import math

from camera import Camera

def inv_lerp(a: float, b: float, v: float) -> float:
    return (v - a) / (b - a)

def lerp(a: float, b:float, v:float) -> float:
    return a + (b - a) * v

def remap_array(array, i_min, i_max, o_min, o_max):
    for j in range(0, array.shape[1]):
        for i in range(0, array.shape[0]):
            t = inv_lerp(i_min, i_max, array[j, i])
            array[j, i] = lerp(o_min, o_max, t)


def pixelate(array : numpy.ndarray, pixel_size : int):
    if array.shape[0] % pixel_size != 0 and array.shape[1] % pixel_size != 0:
        raise ValueError(f"Failed to pixelate map samples :\n\tArray shape : {array.shape}")
    
    temp_samples = []
    print(array.shape)

    for j in range(0, array.shape[1], pixel_size):
        line = []
        for i in range(0, array.shape[0], pixel_size):
            xsum = 0
            for k in range(pixel_size):
                for l in range(pixel_size):
                    xsum += array[j + k, i + k]
            line.append(xsum / (pixel_size ** 2))
        temp_samples.append(line)
    
    for j in range(array.shape[1]):
        for i in range(array.shape[0]):
            pos = (i // pixel_size, j // pixel_size)
            array[j, i] = temp_samples[pos[1]][pos[0]]
    
class Layer():

    def __init__(self):
        self.tiles : list[tuple[pygame.Surface, pygame.Vector2]] = []
        self.thresholds = {0:0, 1:None}
        # self.pixelize_value = 1
        self.based_layer : Layer = None
        self.threshold_on_layer = 0.0
        self.value_based_tiles = []
        self.noise_values : numpy.ndarray = None
    
    def add_threshold(self, threshold, tile_index) -> None:
        """
        Add a new threshold for the noise value, tile_index is the tile value if the value is between this threshold and the next.
        By default, if there is no threshold, it would be the tile index 0. (can be changed)
        """

        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        
        if not (0 <= tile_index <= 10) and isinstance(tile_index, int):
            raise ValueError("tile_index must be between 0 and 9 and an integer")
        
        self.thresholds[threshold] = tile_index
        self.thresholds = {val:self.thresholds[val] for val in sorted(self.thresholds)}

    def build_layer(self, tilemap : "Tilemap"):

        m_datas = []
        thresholds = list(self.thresholds.items())

        final_map = []

        for j in range(int(tilemap.n_size.y + 2)):
            l = []
            for i in range(int(tilemap.n_size.x + 2)):

                if self.based_layer and self.based_layer.noise_values[j, i] < self.threshold_on_layer:
                    index = 10
                else:

                    index = 0
                    for k in range(len(thresholds) - 1):

                        if thresholds[k][0] <= self.noise_values[j, i] <= thresholds[k + 1][0]:
                            index = thresholds[k][1]
                            break

                tile = tilemap.tileset[index], pygame.Vector2(i-1, j-1).elementwise() * tilemap.tile_size
                final_map.append(tile)
            m_datas.append(l)
    
        self.tiles = final_map

class Tilemap():

    def __init__(self):

        # Map size
        self.size = pygame.Vector2() # In pixel
        self.n_size = pygame.Vector2() # in number of tile

        # The tile size
        self.tile_size = pygame.Vector2()

        self.tileset : list[pygame.Surface] = []

        self.layers : dict[str, Layer] = {
            "foreground":Layer(),
            "grass":Layer(),
            "flowers":Layer()
        }
        self.object_layers : dict[str, list] = {}

        self.patterns = {}
        self.value_based_tiles = []
        self.abc = 1 # Pas trouvé de nom

    def _find_similar_pattern(self, pattern : tuple[int]) -> tuple[int]:
        for p in self.patterns:
            s = []
            for i, v in enumerate(pattern):
                if (v == p[i] or p[i] == 0):
                    s.append(p[i])
            
            if len(s) == 8:
                return tuple(s)
        
        return None
                    
    
    def get_pattern(self, pattern : tuple[int], original_value : int) -> list[int]:

        index = self.patterns.get(pattern, None)
        
        if index != None:
            return index
        
        p = self._find_similar_pattern(pattern)
            
        if p == None:
            return self.patterns[tuple(original_value for _ in range(8))]
        else:
            return self.patterns[p]

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
            
            if not "wangsets" in json_obj:
                self.tileset.extend(tile_list)
                return
            
            for wangset in json_obj["wangsets"]:
                for pattern in wangset["wangtiles"]:
                    p = tuple(pattern["wangid"])
                    if not p in self.patterns:
                        self.patterns[p] = [pattern["tileid"]]
                    else:
                        self.patterns[p].append(pattern["tileid"])
        
        self.tileset.extend(tile_list)

    def generate(self, size : pygame.Vector2, seed = 0) -> None:
        """
        Generates the map, the size must be a vector of 2 integer values
        """


        self.n_size = size.copy()
        self.tile_size = pygame.Vector2(16, 16)
        self.size = pygame.Vector2(self.n_size.x*self.tile_size.x, self.n_size.y*self.tile_size.y)

        # Mettre les valeurs en absolue
        a = opensimplex.OpenSimplex(seed)
        b = opensimplex.OpenSimplex(seed + 1)
        c = opensimplex.OpenSimplex(seed + 2)
        ms_size = int(size.x + 2), int(size.y + 2)
        a_map_samples = a.noise2array(numpy.array([1.75*i/ms_size[0] for i in range(ms_size[0])]), 
                                    numpy.array([1.75*i/ms_size[1] for i in range(ms_size[1])]))
        a_map_samples = numpy.absolute(a_map_samples)

        b_map_samples = b.noise2array(numpy.array([2.5*i/ms_size[0] for i in range(ms_size[0])]), 
                                    numpy.array([2.5*i/ms_size[1] for i in range(ms_size[1])]))
        remap_array(b_map_samples, -1, 1, 0, 1)
    

        self.layers["foreground"].noise_values = a_map_samples
        self.layers["grass"].noise_values = b_map_samples
        self.layers["grass"].build_layer(self)
        self.layers["flowers"].noise_values = b_map_samples
        self.layers["flowers"].build_layer(self)

        pixelate(a_map_samples, 2)
        self.layers["foreground"].build_layer(self)


    def draw(self, camera : Camera) -> None:

        for layer in self.layers.values():

            offseted_layer = []

            for surf, pos in layer.tiles:
                offseted_layer.append((surf, round(pos - pygame.Vector2(camera.rect.topleft))))
            
            camera.draw(offseted_layer)