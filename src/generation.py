import pygame
import math
import random
import numpy

from opensimplex import OpenSimplex

SAMPLE_PER_UNIT = 100

NOISE1 = OpenSimplex(2)

def generate_noise1(tilemap, layer, chunk_pos):
    noise_values = NOISE1.noise2array(
            numpy.array([3.5 * (i + chunk_pos[0] * 16) / SAMPLE_PER_UNIT for i in range(16 + 2)]),
            numpy.array([3.5 * (i + chunk_pos[1] * 16) / SAMPLE_PER_UNIT for i in range(16 + 2)]),
        )
    return numpy.absolute(noise_values)