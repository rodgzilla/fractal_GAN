import sys
from PIL import Image
import cmath
import random

# The small size will help for future generation.
unit   = 100
width  = 3 * unit
height = 2 * unit

# nb_sections represents the number of slice of each axis we are going
# to consider for the zoom. The number of sections considered will be
# nb_sections * nb_sections
nb_sections    = 10
section_width  = int(width / nb_sections)
section_height = int(height / nb_sections)

# We select the region on which we zoom amongst the top_select most bright
top_select = 20

def convert_pixel_complex(x, y, re_min, re_max, im_min, im_max):
    """
    Converts pixel coordinates to complex plane coordinates. The re and
    im arguments indicates the part of the complex plane represented by the window.
    """
    re = x * (re_max - re_min) / width  + re_min
    im = y * (im_max - im_min) / height + im_min

    return complex(re, im)

def iterate_sequence(seq_fn, max_iter, c):
    z = c
    for i in range(max_iter):
        z = seq_fn(z, c)
        # If we detect that the sequence diverges
        if (z.real * z.real + z.imag * z.imag) > 4:
            # The value of the pixel intensity will be proportional to
            # the number of iterations we ran before detecting the
            # divergence
            color_ratio = int((i * 255.) / max_iter)
            return color_ratio
    # If we did not detect a divergence in max_iter steps, we consider
    # that the sequence does not diverge and return 0 as intensity.
    return 0
            
def draw_mandel(seq_fn, max_iter, re_min, re_max, im_min, im_max):
    """
    Computes the mandelbrot set on a given part of the complex plane.
    """
    screen_array = [[0] * height for _ in range(width)] 
    # For every pixel of the screen
    for x in range(width):
        for y in range(height):
            # Compute the associated complex number
            c = convert_pixel_complex(x, y, re_min, re_max, im_min, im_max)
            # Then, compute max_iter element of sequence function with
            # c as initial value
            screen_array[x][y] = iterate_sequence(seq_fn, max_iter, c)

    return screen_array

def sec_number_to_indices(w_sec, h_sec):
    """
    Converts sections indices into window coordinates.
    """
    x_min = w_sec * section_width
    x_max = (w_sec + 1) * section_width
    y_min = h_sec * section_height
    y_max = (h_sec + 1) * section_height
    
    return x_min, x_max, y_min, y_max

def section_intensity(screen_array, weight, w_sec, h_sec):
    """
    Computes the weighted average of the pixel intensity after
    computing the Mandelbrot set.
    """
    x_min, x_max, y_min, y_max = sec_number_to_indices(w_sec, h_sec)
    s    = sum((weight(screen_array[x][y]) for x in range(x_min, x_max) for y in range(y_min, y_max)))
    norm = section_width * section_height

    return s / norm

def sections_to_intensities(screen_array, weight = lambda x: x):
    """
    Creates a dictionary which associates sections indices to their
    weighted average pixel intensity.
    """
    sec_to_int = {}
    for w_sec in range(nb_sections):
        for h_sec in range(nb_sections):
            sec_to_int[(w_sec, h_sec)] = section_intensity(screen_array, weight, w_sec, h_sec)

    return sec_to_int

def sort_section_intensities(sec_to_int):
    """
    Sorts the sections indices according to their intensities in
    decreasing order.
    """
    return sorted(sec_to_int.keys(), key = sec_to_int.get, reverse = True)

def generate_fractal_sequence(seq_fn = lambda z, c: z**2 + c, seq_len = 8, top_select = 5, return_steps = False):
    """
    Generates the multiple zoom on the Mandelbrot set. seq_len
    pictures will be generated and the zoom will chose amongst the
    top_select most intense sections.
    """
    tl = complex(-2, 1) # top left complex number
    br = complex(1, -1) # bottom right complex number
    result = []
    for i in range(seq_len):
        min_re, max_re             = tl.real, br.real
        min_im, max_im             = br.imag, tl.imag
        # Experimental formula to have greater max_iter when we zoom
        max_iter                   = 50 + i ** 3 * 16
        # Draw the fractal in the window, divide the result in
        # sections and compute their intensities. Chose one of the
        # most intense section and update the top left and bottom
        # right complex numbers to zoom on this section.
        screen_array               = draw_mandel(seq_fn, max_iter, min_re, max_re, min_im, max_im)
        sec_to_int                 = sections_to_intensities(screen_array)
        w_sec_max, h_sec_max       = random.choice(sort_section_intensities(sec_to_int)[:top_select])
        x_min, x_max, y_min, y_max = sec_number_to_indices(w_sec_max, h_sec_max)
        tl                         = convert_pixel_complex(x_min, y_min, min_re, max_re, min_im, max_im) 
        br                         = convert_pixel_complex(x_max, y_max, min_re, max_re, min_im, max_im) 
        result.append(screen_array)

    return result if return_steps else result[-1]
        
def save_screen(screen_array, filename = 'renders/test.bmp'):
    """
    Save the array in a file. The saving is done using PIL.
    """
    data = [(screen_array[x][y],) * 3 for y in range(height) for x in range(width)]
    img  = Image.new('RGB', (width, height))
    img.putdata(data)
    img.save(filename)

if __name__ == '__main__':
    final = generate_fractal_sequence(seq_fn = lambda z, c: z ** 2 + c, seq_len = 4)
    save_screen(final)
