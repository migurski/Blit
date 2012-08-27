""" Adjustment factory functions.

An adjustment is a function that takes a list of four identically-sized channel
arrays (red, green, blue, and alpha) and returns a new list of four channels.
The factory functions in this module return functions that perform adjustments.
"""
import sympy
import numpy

def threshold(red_value, green_value=None, blue_value=None):
    """ Return a function that applies a threshold operation.
    """
    if green_value is None or blue_value is None:
        # if there aren't three provided, use the one
        green_value, blue_value = red_value, red_value

    # knowns are given in 0-255 range, need to be converted to floats
    red_value, green_value, blue_value = red_value / 255.0, green_value / 255.0, blue_value / 255.0
    
    def adjustfunc(rgba):
        red, green, blue, alpha = rgba
        
        red[red > red_value] = 1
        red[red <= red_value] = 0
        
        green[green > green_value] = 1
        green[green <= green_value] = 0
        
        blue[blue > blue_value] = 1
        blue[blue <= blue_value] = 0
        
        return red, green, blue, alpha
    
    return adjustfunc

def curves(black, grey, white):
    """ Return a function that applies a curves operation.
        
        Adjustment inspired by Photoshop "Curves" feature.
    
        Arguments are three integers that are intended to be mapped to black,
        grey, and white outputs. Curves2 offers more flexibility, see
        curves2().
        
        Darken a light image by pushing light grey to 50% grey, 0xCC to 0x80
        with black=0, grey=204, white=255.
    """
    # knowns are given in 0-255 range, need to be converted to floats
    black, grey, white = black / 255.0, grey / 255.0, white / 255.0
    
    # coefficients
    a, b, c = [sympy.Symbol(n) for n in 'abc']
    
    # black, gray, white
    eqs = [a * black**2 + b * black + c - 0.0,
           a *  grey**2 + b *  grey + c - 0.5,
           a * white**2 + b * white + c - 1.0]
    
    co = sympy.solve(eqs, a, b, c)
    
    def adjustfunc(rgba):
        red, green, blue, alpha = rgba
    
        # arrays for each coefficient
        do, re, mi = [float(co[n]) * numpy.ones(red.shape, numpy.float32) for n in (a, b, c)]
        
        # arithmetic
        red   = numpy.clip(do * red**2   + re * red   + mi, 0, 1)
        green = numpy.clip(do * green**2 + re * green + mi, 0, 1)
        blue  = numpy.clip(do * blue**2  + re * blue  + mi, 0, 1)
        
        return red, green, blue, alpha
    
    return adjustfunc

def curves2(map_red, map_green=None, map_blue=None):
    """ Return a function that applies a curves operation.
        
        Adjustment inspired by Photoshop "Curves" feature.
    
        Arguments are given in the form of three value mappings, typically
        mapping black, grey and white input and output values. One argument
        indicates an effect applicable to all channels, three arguments apply
        effects to each channel separately.
    
        Simple monochrome inversion:
            map_red=[[0, 255], [128, 128], [255, 0]]
    
        Darken a light image by pushing light grey down by 50%, 0x99 to 0x66:
            map_red=[[0, 255], [153, 102], [255, 0]]
    
        Shaded hills, with Imhof-style purple-blue shadows and warm highlights:
            map_red=[[0, 22], [128, 128], [255, 255]],
            map_green=[[0, 29], [128, 128], [255, 255]],
            map_blue=[[0, 65], [128, 128], [255, 228]]
    """
    if map_green is None or map_blue is None:
        # if there aren't three provided, use the one
        map_green, map_blue = map_red, map_red

    def adjustfunc(rgba):
        red, green, blue, alpha = rgba
        out = []
        
        for (chan, input) in ((red, map_red), (green, map_green), (blue, map_blue)):
            # coefficients
            a, b, c = [sympy.Symbol(n) for n in 'abc']
            
            # parameters given in 0-255 range, need to be converted to floats
            (in_1, out_1), (in_2, out_2), (in_3, out_3) \
                = [(in_ / 255.0, out_ / 255.0) for (in_, out_) in input]
            
            # quadratic function
            eqs = [a * in_1**2 + b * in_1 + c - out_1,
                   a * in_2**2 + b * in_2 + c - out_2,
                   a * in_3**2 + b * in_3 + c - out_3]
            
            co = sympy.solve(eqs, a, b, c)
            
            # arrays for each coefficient
            a, b, c = [float(co[n]) * numpy.ones(chan.shape, numpy.float32) for n in (a, b, c)]
            
            # arithmetic
            out.append(numpy.clip(a * chan**2 + b * chan + c, 0, 1))
        
        return out + [alpha]
    
    return adjustfunc
