import pygame
import math
import random
import numpy

from opensimplex import OpenSimplex

SAMPLE_PER_UNIT = 512

NOISE1 = OpenSimplex(5)
THRESHOLD_LAYER_ONE = {0:5, 0.1:1, 0.2:4,1:None}
THRESHOLD_LAYER_TWO = {0:0, 0.4:152, 0.5:171, 0.6:172, 1:None}

def generate_noise1(tilemap, layer, chunk_pos):
    thresholds = list(THRESHOLD_LAYER_ONE.items())
    m_datas = []
    map_samples = NOISE1.noise2array(
        numpy.array(
            [3.5 * (i + chunk_pos[0] * 16) / SAMPLE_PER_UNIT for i in range(16 + 2)]
        ),
        numpy.array(
            [3.5 * (i + chunk_pos[1] * 16) / SAMPLE_PER_UNIT for i in range(16 + 2)]
        ),
    )
    map_samples = numpy.absolute(map_samples)
    # From height float values to integer values representing the type of tile
    for j in range(tilemap.chunk_size + 2):
        l = []
        for i in range(tilemap.chunk_size + 2):
            index = 0
            for k in range(len(thresholds) - 1):
                if thresholds[k][0] <= map_samples[j, i] <= thresholds[k + 1][0]:
                    index = thresholds[k][1]
                    break

            l.append(index)
        m_datas.append(l)
    return m_datas

def generate2(tilemap, layer, chunk_pos):
    map_samples_layer_one = NOISE1.noise2array(
        numpy.array(
            [3.5 * (i + chunk_pos[0] * 16) / SAMPLE_PER_UNIT for i in range(16 + 2)]
        ),
        numpy.array(
            [3.5 * (i + chunk_pos[1] * 16) / SAMPLE_PER_UNIT for i in range(16 + 2)]
        ),
    )
    map_samples_layer_one = numpy.absolute(map_samples_layer_one)


    thresholds = list(THRESHOLD_LAYER_TWO.items())
    m_datas = []
    map_samples = NOISE1.noise2array(
        numpy.array(
            [3.5 * (i + chunk_pos[0] * 16) for i in range(16 + 2)]
        ),
        numpy.array(
            [3.5 * (i + chunk_pos[1] * 16) for i in range(16 + 2)]
        ),
    )
    map_samples = numpy.absolute(map_samples)
    # From height float values to integer values representing the type of tile
    for j in range(tilemap.chunk_size + 2):
        l = []
        for i in range(tilemap.chunk_size + 2):
            index = 0
            for k in range(len(thresholds) - 1):
                if thresholds[k][0] <= map_samples[j, i] <= thresholds[k + 1][0] and map_samples_layer_one[j, i] > list(THRESHOLD_LAYER_ONE.items())[2][0]:
                    index = thresholds[k][1]
                    break

            l.append(index)
        m_datas.append(l)
    return m_datas
