import pygame
import json
import pathlib
import opensimplex
import numpy
import random
import math

from camera import Camera

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
        self.patterns = {}
        self.value_based_tiles = []
        self.abc = 1 # Pas trouvé de nom
    
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

    def build_layer(self, map_samples : numpy.ndarray):

        m_datas = []
        thresholds = list(self.thresholds.items())

        final_map = []

        for j in range(int(self.n_size.y + 2)):
            l = []
            for i in range(int(self.n_size.x + 2)):

                index = 0
                for k in range(len(thresholds) - 1):
                    if thresholds[k][0] <= abs(map_samples[j, i]) <= thresholds[k + 1][0]:
                        index = thresholds[k][1]
                        break

                # tile = self.tileset[index], pygame.Vector2(i, j).elementwise() * self.tile_size
                l.append(index)
            m_datas.append(l)

        for j in range(1, int(self.n_size.y + 2) - 1):
            for i in range(1, int(self.n_size.x + 2) - 1):
                if m_datas[j][i] in self.value_based_tiles:
                    indexs = self.get_pattern(tuple(m_datas[j][i] for _ in range(8)), m_datas[j][i])
                else:
                    pattern = (
                        m_datas[j - 1][i],
                        m_datas[j - 1][i + 1],
                        m_datas[j][i + 1],
                        m_datas[j + 1][i + 1],
                        m_datas[j + 1][i],
                        m_datas[j + 1][i - 1],
                        m_datas[j][i - 1],
                        m_datas[j - 1][i - 1]
                    )
                    indexs = self.get_pattern(pattern, m_datas[j][i])
                index = random.choice(indexs)
                tile = self.tileset[index], pygame.Vector2(i-1, j-1).elementwise() * self.tile_size
                final_map.append(tile)
    
        return final_map

    def generate(self, size : pygame.Vector2, seed = 0) -> None:
        """
        Generates the map, the size must be a vector of 2 integer values
        """


        self.n_size = size.copy()
        self.tile_size = pygame.Vector2(16, 16)
        self.size = pygame.Vector2(self.n_size.x*self.tile_size.x, self.n_size.y*self.tile_size.y)

        a = opensimplex.OpenSimplex(seed)
        ms_size = int(size.x + 2), int(size.y + 2)
        map_samples = a.noise2array(numpy.array([3.5*i/ms_size[0] for i in range(ms_size[0])]), numpy.array([3.5*i/ms_size[1] for i in range(ms_size[1])]))
        if self.abc > 1:
            pixelate(map_samples, self.abc)
        
        thresholds = list(self.thresholds.items())
        final_map = []

        if self.patterns:
            final_map = self.build_layer(map_samples)
        else:

            for j in range(1, int(size.y + 2) - 1):
                for i in range(1, int(size.x + 2) - 1):

                    index = 0
                    for k in range(len(thresholds) - 1):
                        if thresholds[k][0] <= abs(map_samples[j, i]) <= thresholds[k + 1][0]:
                            index = thresholds[k][1]
                            break

                    tile = self.tileset[index], pygame.Vector2(i-1, j-1).elementwise() * self.tile_size
                    final_map.append(tile)


        self.layers["foreground"] = final_map


    def draw(self, camera : Camera) -> None:

        for layer in self.layers.values():

            offseted_layer = []

            for surf, pos in layer:
                offseted_layer.append((surf, round(pos - pygame.Vector2(camera.rect.topleft))))
            
            camera.draw(offseted_layer)