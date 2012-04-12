import numpy
import Image

def arr2img(ar):
    """ Convert Numeric array to PIL Image.
    """
    return Image.fromstring('L', (ar.shape[1], ar.shape[0]), ar.astype(numpy.ubyte).tostring())

def img2arr(im):
    """ Convert PIL Image to Numeric array.
    """
    assert im.mode == 'L'
    return numpy.reshape(numpy.fromstring(im.tostring(), numpy.ubyte), (im.size[1], im.size[0]))

def rgba2img(rgba):
    """ Convert four Numeric array objects to PIL Image.
    """
    assert type(rgba) in (tuple, list)
    return Image.merge('RGBA', [arr2img(numpy.round(band * 255.0).astype(numpy.ubyte)) for band in rgba])

def img2rgba(im):
    """ Convert PIL Image to four Numeric array objects.
    """
    assert im.mode == 'RGBA'
    return [img2arr(band).astype(numpy.float32) / 255.0 for band in im.split()]
