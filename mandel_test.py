import sys
import pygame
from pygame import gfxdraw
from pygame import Color
import cmath

pygame.init()

maxIter        = 40
width          = 300
height         = 200
nb_sections    = 10

section_width  = int(width / nb_sections)
section_height = int(height / nb_sections)

def draw_mandel(window, sequence_function, re_min = -2, re_max = 1, im_min = -1, im_max = 1):
    screen_array = [[0] * height for _ in range(width)] 
    x_ratio      = (re_max - re_min) / width
    y_ratio      = (im_max - im_min) / height
    for x in range(width):
        for y in range(height):
            c = complex((x * x_ratio) + re_min, (y * y_ratio) + im_min)
            z = c
            for i in range(maxIter):
                z = sequence_function(z, c)
                if (z.real * z.real + z.imag * z.imag) > 4:
                    color_ratio = int((i * 255.) / maxIter)
                    gfxdraw.pixel(window, x, y, Color(color_ratio, color_ratio, color_ratio, 255))
                    screen_array[x][y] = color_ratio
                    break
            else:
                gfxdraw.pixel(window, x, y, Color(0,0,0,255))

    pygame.display.flip()

    return screen_array

def sec_number_to_indices(w_sec, h_sec):
    x_min = w_sec * section_width
    x_max = (w_sec + 1) * section_width
    y_min = h_sec * section_height
    y_max = (h_sec + 1) * section_height
    
    return x_min, x_max, y_min, y_max

def section_intensity(screen_array, weight, w_sec, h_sec):
    x_min, x_max, y_min, y_max = sec_number_to_indices(w_sec, h_sec)
    s    = sum((weight(screen_array[x][y]) for x in range(x_min, x_max) for y in range(y_min, y_max)))
    norm = section_width * section_height

    return s / norm

def sections_to_intensities(screen_array, weight = lambda x: x):
    sec_to_int = {}
    for w_sec in range(nb_sections):
        for h_sec in range(nb_sections):
            sec_to_int[(w_sec, h_sec)] = section_intensity(screen_array, weight, w_sec, h_sec)

    return sec_to_int

def sort_section_intensities(sec_to_int):
    return sorted(sec_to_int.keys(), key = sec_to_int.get, reverse = True)

if __name__ == '__main__':
    window = pygame.display.set_mode((width, height))

    screen_array         = draw_mandel(window, lambda z, c: z**2 + c)

    sec_to_int = sections_to_intensities(screen_array)
    w_sec_max, h_sec_max = sort_section_intensities(sec_to_int)[4]
    print(w_sec_max, h_sec_max)
    x_min, x_max, y_min, y_max = sec_number_to_indices(w_sec_max, h_sec_max)
    print(x_min, x_max, y_min, y_max)

    for x in range(x_min, x_max):
        for y in range(y_min, y_max):
            gfxdraw.pixel(window, x, y, Color(255, 0, 0, 255))            
    pygame.display.flip()
        
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
