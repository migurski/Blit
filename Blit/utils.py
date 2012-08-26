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

def chan2img(chan):
    """ Convert single Numeric array object to one-channel PIL Image.
    """
    return arr2img(numpy.round(chan * 255.0).astype(numpy.ubyte))

def img2chan(img):
    """ Convert one-channel PIL Image to single Numeric array object.
    """
    return img2arr(img).astype(numpy.float32) / 255.0

def rgba2img(rgba):
    """ Convert four Numeric array objects to PIL Image.
    """
    assert type(rgba) in (tuple, list)
    return Image.merge('RGBA', [chan2img(band) for band in rgba])

def img2rgba(im):
    """ Convert PIL Image to four Numeric array objects.
    """
    assert im.mode == 'RGBA'
    return [img2chan(band) for band in im.split()]
