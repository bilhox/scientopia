import pygame
import json
import pathlib
import opensimplex
import numpy
import random
import math

from camera import Camera


class Tilemap:
    def __init__(self):
        # Map size
        self.size = (0, 0)  # In pixel
        self.n_size = (0, 0)  # in number of tile

        # The tile size
        self.tile_size = (0, 0)

        self.tileset: list[pygame.Surface] = []

        self.layers: dict[str, list[tuple[pygame.Surface, pygame.Vector2]]] = {}
        self.object_layers: dict[str, list] = {}

        self.thresholds = {0: 0, 1: None}
        self.patterns = {}
        self.value_based_tiles = []

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
        self.thresholds = {val: self.thresholds[val] for val in sorted(self.thresholds)}

    def _find_similar_pattern(self, pattern: tuple[int]) -> tuple[int]:
        for p in self.patterns:
            s = []
            for i, v in enumerate(pattern):
                if v == p[i] or p[i] == 0:
                    s.append(p[i])

            if len(s) == 8:
                return tuple(s)

        return None

    def get_pattern(self, pattern: tuple[int], original_value: int) -> list[int]:
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

            image = pygame.image.load(
                path_obj.parent.joinpath(json_obj["image"])
            ).convert_alpha()

            for y in range(json_obj["imageheight"] // tile_height):
                for x in range(json_obj["columns"]):
                    tile_list.append(
                        image.subsurface(
                            pygame.Rect(
                                [x * tile_width, y * tile_height],
                                [tile_width, tile_height],
                            )
                        )
                    )

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

    def build_layer(self, map_samples: numpy.ndarray):
        """
        This method builds the map, based on `map_samples` given, which is the height map generated with opensimplex algorithm.
        """

        m_datas = []
        thresholds = list(self.thresholds.items())

        final_map = []

        # From height float values to integer values representing the type of tile
        for j in range(self.n_size[1] + 2):
            l = []
            for i in range(self.n_size[0] + 2):
                index = 0
                for k in range(len(thresholds) - 1):
                    if thresholds[k][0] <= map_samples[j, i] <= thresholds[k + 1][0]:
                        index = thresholds[k][1]
                        break

                l.append(index)
            m_datas.append(l)

        # Selecting which tile should be used
        for j in range(1, self.n_size[1] + 1):
            for i in range(1, self.n_size[0] + 1):
                if m_datas[j][i] in self.value_based_tiles:
                    indices = self.get_pattern(
                        tuple(m_datas[j][i] for _ in range(8)), m_datas[j][i]
                    )
                else:
                    pattern = (
                        m_datas[j - 1][i],
                        m_datas[j - 1][i + 1],
                        m_datas[j][i + 1],
                        m_datas[j + 1][i + 1],
                        m_datas[j + 1][i],
                        m_datas[j + 1][i - 1],
                        m_datas[j][i - 1],
                        m_datas[j - 1][i - 1],
                    )
                    indices = self.get_pattern(pattern, m_datas[j][i])
                index = random.choice(indices)
                tile = (
                    self.tileset[index],
                    pygame.Vector2(i - 1, j - 1).elementwise() * self.tile_size,
                )
                final_map.append(tile)

        return final_map

    def generate(self, size: tuple[int, int], seed=0) -> None:
        """
        Generates the map, the size must be a tuple of 2 integer values
        """

        self.n_size = size
        self.tile_size = (16, 16)
        self.size = (
            self.n_size[0] * self.tile_size[0],
            self.n_size[1] * self.tile_size[1],
        )

        a = opensimplex.OpenSimplex(seed)
        map_samples = a.noise2array(
            numpy.array([3.5 * i / (size[0] + 2) for i in range(size[0] + 2)]),
            numpy.array([3.5 * i / (size[1] + 2) for i in range(size[1] + 2)]),
        )
        map_samples = numpy.absolute(map_samples)

        thresholds = list(self.thresholds.items())
        final_map = []

        if self.patterns:
            final_map = self.build_layer(map_samples)
        else:
            for j in range(1, self.n_size[1] + 2):
                for i in range(1, self.n_size[0] + 2):
                    index = 0
                    for k in range(len(thresholds) - 1):
                        if (
                            thresholds[k][0]
                            <= map_samples[j, i]
                            <= thresholds[k + 1][0]
                        ):
                            index = thresholds[k][1]
                            break

                    tile = (
                        self.tileset[index],
                        pygame.Vector2(i, j).elementwise() * self.tile_size,
                    )
                    final_map.append(tile)

        self.layers["foreground"] = final_map

    def draw(self, camera: Camera) -> None:
        """
        This method draws the tilemap
        """

        for layer in self.layers.values():
            offseted_layer = []

            for surf, pos in layer:
                offseted_layer.append(
                    (surf, round(pos - pygame.Vector2(camera.rect.topleft)))
                )

            camera.draw(offseted_layer)
