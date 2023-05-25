''' Simple Photoshop file (PSD) writing support.

Blit blending operations normally return new, flattened bitmap objects.
By starting with a PSD layer class, Blit can maintain a chain of separated
layers and allows saving to PSD files.

>>> from Blit import Color, Bitmap, blends, photoshop
>>> psd = photoshop.PSD(128, 128)
>>> psd = psd.blend('Orange', Color(255, 153, 0), Bitmap('photo.jpg'))
>>> psd = psd.blend('Photo', Bitmap('photo.jpg'), blendfunc=blends.linear_light)
>>> psd.save('photo.psd')

Output PSD files have been tested with Photoshop CS3 on Mac, based on this spec:
    http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm

Photoshop is a registered trademark of Adobe Corporation.
'''
from struct import pack

import numpy
from PIL import Image

from . import Layer
from . import utils
from . import blends
    
def uint8(num):
    return pack('>B', num)

def int16(num):
    return pack('>h', num)

def uint16(num):
    return pack('>H', num)

def uint32(num):
    return pack('>I', num)

def double(num):
    return pack('>d', num)

def pascal_string(chars, pad_to):
    base = uint8(len(chars)) + chars
    base += '\x00' * ((pad_to - len(base) % pad_to) % pad_to)
    
    return base

class Dummy:
    ''' Filler base class for portions of the Photoshop file specification omitted.
    '''
    def tostring(self):
        return uint32(0)

class PhotoshopFile:
    ''' Complete Photoshop file.
    
        http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_pgfId-1036097
        
        The Photoshop file format is divided into five major parts, as shown
        in the Photoshop file structure:
            http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/images/PhotoshopFileFormatsStructure.gif
    '''
    def __init__(self, file_header, color_mode_data, image_resources, layer_mask_info, image_data):
        self.file_header = file_header
        self.color_mode_data = color_mode_data
        self.image_resources = image_resources
        self.layer_mask_info = layer_mask_info
        self.image_data = image_data
    
    def tostring(self):
        return self.file_header.tostring() + self.color_mode_data.tostring() \
             + self.image_resources.tostring() + self.layer_mask_info.tostring() \
             + self.image_data.tostring()

class FileHeader:
    ''' The file header contains the basic properties of the image.
    
        http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_19840
    '''
    def __init__(self, channel_count, height, width, depth, color_mode):
        self.channel_count = channel_count
        self.height = height
        self.width = width
        self.depth = depth
        self.color_mode = color_mode
    
    def tostring(self):
        
        parts = [
            '8BPS',
            uint16(1),
            '\x00' * 6,
            uint16(self.channel_count),
            uint32(self.height),
            uint32(self.width),
            uint16(self.depth),
            uint16(self.color_mode)
        ]
        
        return ''.join(parts)

class ColorModeData (Dummy):
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_71638
    '''
    pass

class ImageResourceSection (Dummy):
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_69883
    '''
    pass

class LayerMaskInformation:
    ''' The fourth section of a Photoshop file with information about layers and masks.
    
        http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_75067
    '''
    def __init__(self, layer_info, global_layer_mask):
        self.layer_info = layer_info
        self.global_layer_mask = global_layer_mask
    
    def tostring(self):
        layer_info = self.layer_info.tostring()
        global_layer_mask = self.global_layer_mask.tostring()
        
        layer_mask_info = layer_info + global_layer_mask
        return uint32(len(layer_mask_info)) + layer_mask_info

class LayerInformation:
    ''' Layer info shows the high-level organization of the layer information.
    
        http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_16000
    '''
    def __init__(self, layer_count, layer_records, channel_image_data):
        self.layer_count = layer_count
        self.layer_records = layer_records
        self.channel_image_data = channel_image_data
    
    def tostring(self):
        layer_count = uint16(self.layer_count)
        layer_records = ''.join([record.tostring() for record in self.layer_records])
        channel_image_data = self.channel_image_data.tostring()
        
        layer_info = layer_count + layer_records + channel_image_data
        return uint32(len(layer_info)) + layer_info

class LayerRecord:
    ''' Information about each layer.
    
        http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_13084
    '''
    def __init__(self, rectangle, channel_count, channel_info, blend_mode, opacity,
                 clipping, mask_data, blending_ranges, name, additional_infos):
        self.rectangle = rectangle
        self.channel_count = channel_count
        self.channel_info = channel_info
        self.blend_mode = blend_mode
        self.opacity = opacity
        self.clipping = clipping
        self.mask_data = mask_data
        self.blending_ranges = blending_ranges
        self.name = name
        self.additional_infos = additional_infos
    
    def tostring(self):
        pixel_count = (self.rectangle[2] - self.rectangle[0]) * (self.rectangle[3] - self.rectangle[1])
        mask_data = self.mask_data.tostring()
        blending_ranges = self.blending_ranges.tostring()
        name = pascal_string(self.name, 4)
        additional_infos = ''.join([info.tostring() for info in self.additional_infos])
    
        parts = [
            ''.join(map(uint32, self.rectangle)),
            uint16(self.channel_count),
            ''.join([int16(chid) + uint32(2 + pixel_count) for chid in self.channel_info]),
            '8BIM',
            self.blend_mode,
            uint8(self.opacity),
            uint8(self.clipping),
            uint8(0b00000000),
            uint8(0x00),
            uint32(len(mask_data + blending_ranges + name + additional_infos)),
            mask_data,
            blending_ranges,
            name,
            additional_infos
        ]
        
        return ''.join(parts)

class GlobalLayerMask (Dummy):
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_17115
    '''
    pass

class AdditionalLayerInfo:
    ''' Several types of layer information added in Photoshop 4.0 and later.
    
        http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_71546
    '''
    code, data = None, None
    
    def tostring(self):
        return '8BIM' + self.code + uint32(len(self.data)) + self.data

class SolidColorInfo (AdditionalLayerInfo):
    ''' Solid color sheet setting (Photoshop 6.0).
    '''
    def __init__(self, red, green, blue):
        red, green, blue = [double(component) for component in (red, green, blue)]
    
        self.code = 'SoCo'
        self.data = '\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00null\x00\x00\x00\x01\x00\x00\x00\x00Clr Objc\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00RGBC\x00\x00\x00\x03\x00\x00\x00\x00Rd  doub%(red)s\x00\x00\x00\x00Grn doub%(green)s\x00\x00\x00\x00Bl  doub%(blue)s' % locals()

class LayerMaskAdjustmentData (Dummy):
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_22582
    '''
    pass

class LayerBlendingRangesData (Dummy):
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_21332
    '''
    pass

class ChannelImageData:
    ''' Bitmap content of color channels.
    
        http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_26431
    '''
    def __init__(self, channels):
        self.channels = channels
    
    def tostring(self):
        '''
        '''
        # Compression. 0 = Raw Data, 1 = RLE compressed, 2/3 = ZIP.
        return ''.join(['\x00\x00' + chan.tostring() for chan in self.channels])

class ImageData:
    ''' Bitmap content of flattened whole-file preview.
    
        http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_89817
    '''
    def __init__(self, channels):
        self.channels = channels
    
    def tostring(self):
        '''
        '''
        # Compression. 0 = Raw Data, 1 = RLE compressed, 2/3 = ZIP.
        return '\x00\x00' + ''.join([chan.tostring() for chan in self.channels])

class PSD (Layer):
    ''' Represents a Photoshop document that can be combined with other layers.
    
        Behaves identically to Blit.Layer with addition of a save() method.
    '''
    def __init__(self, width, height):
        ''' Create a new, plain-black PSD instance with specified width and height.
        '''
        channels = [numpy.zeros((height, width), dtype=float)] * 4
        Layer.__init__(self, channels)
        
        self.head = FileHeader(3, height, width, 8, 3)
        self.info = 'Background', self, None, 0xff, 'norm', False
    
    def blend(self, name, other, mask=None, opacity=1, blendfunc=None, clipped=False):
        ''' Return a new PSD instance, with data from another layer included.
        '''
        return _PSDMore(self, name, other, mask, opacity, blendfunc, clipped)
    
    def adjust(self, adjustfunc):
        ''' Adjustment layers are currently not implemented in PSD.
        '''
        raise NotImplementedError("Sorry, no adjustments on PSD")

    def save(self, outfile):
        ''' Save Photoshop-compatible file to a named file or file-like object.
        '''
        #
        # Follow the chain of PSD instances to build up a list of layers.
        #
        info = []
        psd = self
        
        while psd.info:
            info.insert(0, psd.info)
            
            if psd.head:
                file_header = psd.head
                break

            psd = psd.base
        
        #
        # Iterate over layers, make new LayerRecord objects and add channels.
        #
        records = []
        channels = []
        
        for (index, (name, layer, mask, opacity, mode, clipped)) in enumerate(info):
        
            record = dict(
                name = name,
                channel_count = 4,
                channel_info = (0, 1, 2, -1),
                blend_mode = mode,
                opacity = opacity,
                clipping = int(bool(clipped)),
                mask_data = LayerMaskAdjustmentData(),
                blending_ranges = LayerBlendingRangesData(),
                rectangle = (0, 0) + (self.size()[1], self.size()[0]),
                additional_infos = []
                )
            
            channels += utils.rgba2img(layer.rgba(*self.size())).split()

            if index == 0:
                #
                # Background layer has its alpha channel removed.
                #
                record['channel_count'] = 3
                record['channel_info'] = (0, 1, 2)
                channels.pop()
            
            elif layer.size() is None:
                #
                # Layers without sizes are treated as solid colors.
                #
                red, green, blue = [chan[0,0] * 255 for chan in layer.rgba(1, 1)[0:3]]
                record['additional_infos'].append(SolidColorInfo(red, green, blue))
            
            if mask:
                #
                # Add a layer mask channel.
                #
                record['channel_count'] = 5
                record['channel_info'] = (0, 1, 2, -1, -2)
                luminance = utils.rgba2lum(mask.rgba(*self.size()))
                channels.append(utils.chan2img(luminance))
            
            records.append(LayerRecord(**record))
        
        info = LayerInformation(len(records), records, ChannelImageData(channels))
        layer_mask_info = LayerMaskInformation(info, GlobalLayerMask())
        image_data = ImageData(self.image().split()[0:3])
        
        file = PhotoshopFile(file_header, ColorModeData(), ImageResourceSection(), layer_mask_info, image_data)
        
        if not hasattr(outfile, 'write'):
            outfile = open(outfile, 'w')
        
        outfile.write(file.tostring())
        outfile.close()

_modes = {
    blends.screen: 'scrn',
    blends.add: 'lddg',
    blends.multiply: 'mul ',
    blends.linear_light: 'lLit',
    blends.hard_light: 'hLit'
    }

class _PSDMore (PSD):
    ''' Represents a Photoshop document that can be combined with other layers.
    
        Behaves identically to Blit.Layer with addition of a save() method.
    '''
    head = None

    def __init__(self, base, name, other, mask=None, opacity=1, blendfunc=None, clipped=False):
        ''' Create a new PSD instance with the given additional Layer blended.
        
            Arguments
              base: existing PSD instance.
              name: string with name of new layer for Photoshop output.
              other, mask, etc.: identical arguments as Layer.blend().
              clipped: boolean to clip this layer or no.
        '''
        more = Layer.blend(base, other, mask, opacity, blendfunc)
        Layer.__init__(self, more.rgba(*more.size()))
        
        self.base = base
        self.info = name, other, mask, int(opacity * 0xff), \
                    _modes.get(blendfunc, 'norm'), bool(clipped)
