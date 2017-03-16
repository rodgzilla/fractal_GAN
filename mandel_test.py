import sys
import pygame
from pygame import gfxdraw
from pygame import Color
import cmath
import random

pygame.init()

maxIter     = 40
# width       = 300
# height      = 200
width       = 200
height      = 200
nb_sections = 10
top_select  = 20

section_width  = int(width / nb_sections)
section_height = int(height / nb_sections)

def convert_pixel_complex(x, y, re_min, re_max, im_min, im_max):
    re = x * (re_max - re_min) / width  + re_min
    im = y * (im_max - im_min) / height + im_min

    return complex(re, im)

def draw_mandel(window, sequence_function, max_iter, re_min = -2, re_max = 1, im_min = -1, im_max = 1):
    screen_array = [[0] * height for _ in range(width)] 
    for x in range(width):
        for y in range(height):
            c = convert_pixel_complex(x, y, re_min, re_max, im_min, im_max)
            z = c
            for i in range(max_iter):
                z = sequence_function(z, c)
                if (z.real * z.real + z.imag * z.imag) > 4:
                    color_ratio = int((i * 255.) / max_iter)
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

def generate_fractal_sequence(window, function = lambda z, c: z**2 + c, seq_len = 8, top_select = 5):
    tl = complex(-2, 1) # top left complex number
    br = complex(1, -1) # bottom right complex number
    for i in range(seq_len):
        min_re, max_re             = tl.real, br.real
        min_im, max_im             = br.imag, tl.imag
        max_iter                   = 50 + i ** 3 * 16
        print('iteration', i + 1)
        print('min_re, max_re = ', min_re, ',', max_re)
        print('min_im, max_im = ', min_im, ',', max_im)
        print('max_iter', max_iter)
        screen_array               = draw_mandel(window, lambda z, c: z**2 + c, max_iter, min_re, max_re, min_im, max_im) 
        sec_to_int                 = sections_to_intensities(screen_array)
        w_sec_max, h_sec_max       = random.choice(sort_section_intensities(sec_to_int)[:top_select])
        x_min, x_max, y_min, y_max = sec_number_to_indices(w_sec_max, h_sec_max)
        tl                         = convert_pixel_complex(x_min, y_min, min_re, max_re, min_im, max_im) 
        br                         = convert_pixel_complex(x_max, y_max, min_re, max_re, min_im, max_im) 


if __name__ == '__main__':
    window = pygame.display.set_mode((width, height))

    generate_fractal_sequence(window, seq_len = 6)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
