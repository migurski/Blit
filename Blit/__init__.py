""" Simple pixel-composition library.

Dependencies: numpy, sympy, PIL.

Blit performs basic, Photoshop-style layer compositions with blend modes
and selected adjustments, using Numpy internally to perform all math.

See Blit.adjustments for information on filters, Blit.blends for blend modes,
and Blit.photoshop for PSD file output support.

>>> from Blit import Bitmap, adjustments
>>> photo = Bitmap('photo.jpg')
>>> sepia = adjustments.curves2([(0, 64), (128, 158), (255, 255)], [(0, 23), (128, 140), (255, 255)], [(0, 0), (128, 98), (255, 194)])
>>> oldphoto = photo.adjust(sepia)

>>> from Blit import Color
>>> purple = Color(50, 0, 100)
>>> orange = Color(255, 220, 180)
>>> duotone = purple.blend(orange, mask=photo)
"""
__version__ = 'N.N.N'

import numpy
from PIL import Image

from . import blends
from . import adjustments
from . import utils

class Layer:
    """ Represents a raster layer that can be combined with other layers.
    """
    def __init__(self, channels):
        """ Channels is a four-element list of numpy arrays: red, green, blue, alpha.
        """
        self._rgba = channels

    def size(self):
        """ Return width and height of the raster layer in pixels.
        """
        return self._rgba[0].shape[1], self._rgba[0].shape[0]
    
    def rgba(self, width, height):
        """ Return a list of numpy arrays, one for each channel.
        
            Width and height are required, and the resulting channels
            will be clipped or extended to match the requested size.
        """
        w, h = self.size()
        
        if w == width and h == height:
            return self._rgba

        #
        # In theory, this should bring back a right-sized image.
        #
        r, g, b, a = [numpy.zeros((height, width), dtype=float) for i in '1234']

        w = min(w, width)
        h = min(h, height)
        
        r[:w,:h] = self._rgba[0][:h,:w]
        g[:w,:h] = self._rgba[1][:h,:w]
        b[:w,:h] = self._rgba[2][:h,:w]
        a[:w,:h] = self._rgba[3][:h,:w]
        
        return r, g, b, a
    
    def image(self):
        """ Generate a new PIL Image representation of the contained channels.
        """
        return utils.rgba2img(self._rgba)
    
    def blend(self, other, mask=None, opacity=1, blendfunc=None):
        """ Return a new Layer, with data from another layer blended on top.
        
            See blends.combine() for details on blend functions.
        """
        no_dim = False
        
        #
        # Choose an output size based on the first input that has one.
        #
        if self.size():
            dim = self.size()
        elif other.size():
            dim = other.size()
        elif mask and mask.size():
            dim = mask.size()
        else:
            no_dim = True
            dim = 1, 1
        
        bottom_rgba = self.rgba(*dim)
        alpha_chan = other.rgba(*dim)[3]
        top_rgb = other.rgba(*dim)[0:3]
        
        if mask is not None:
            # Multiply alpha channel by mask image luminance
            alpha_chan *= utils.rgba2lum(mask.rgba(*dim))
        
        output_rgba = blends.combine(bottom_rgba, top_rgb, alpha_chan, opacity, blendfunc)
        
        if no_dim:
            rgba = [chan[0,0] * 255 for chan in output_rgba]
            return Color(*rgba)
        
        return Layer(output_rgba)
    
    def adjust(self, adjustfunc):
        """
        """
        return Layer(adjustfunc(self._rgba))

class Bitmap (Layer):
    """ Raster layer instantiated with a bitmap image.
    """
    def __init__(self, input):
        """ Input is a PIL Image or file name.
        """
        if type(input) in (str, unicode):
            input = Image.open(input)
        
        self._rgba = utils.img2rgba(input.convert('RGBA'))

class Color (Layer):
    """ Simple single-color layer of indeterminate size.
    """
    def __init__(self, red, green, blue, alpha=0xFF):
        """ Red, green, blue and alpha are 8-bit channel values. Alpha optional.
        """
        self._components = red / 255., green / 255., blue / 255., alpha / 255.
    
    def size(self):
        """ Return nothing so it's clear that a color has no intrinsic size.
        """
        return None
    
    def image(self):
        """ Return a fresh 1x1 image with the correct color.
        """
        color = [int(c * 255) for c in self._components]
        return Image.new('RGBA', (1, 1), tuple(color))
    
    def rgba(self, width, height):
        """ Generate a new list of channel arrays for the given dimensions.
        """
        r = numpy.ones((height, width)) * self._components[0]
        g = numpy.ones((height, width)) * self._components[1]
        b = numpy.ones((height, width)) * self._components[2]
        a = numpy.ones((height, width)) * self._components[3]
        
        return r, g, b, a
    
    def adjust(self, adjustfunc):
        """
        """
        # make a list of 1x1 arrays as though this was a bitmap
        rgba = [numpy.ones((1, 1), dtype=float) * c for c in self._components]

        # apply adjustment to arrays and turn them back into 8-bit components
        rgba = [chan[0,0] * 255 for chan in adjustfunc(rgba)]
        
        return Color(*rgba)
