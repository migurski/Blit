''' See: 
'''
from struct import pack

def uint8(num):
    return pack('>B', num)

def int16(num):
    return pack('>h', num)

def uint16(num):
    return pack('>H', num)

def uint32(num):
    return pack('>I', num)

def pascal_string(chars, pad_to):
    base = uint8(len(chars)) + chars
    base += '\x00' * ((pad_to - len(base) % pad_to) % pad_to)
    
    return base

class Dummy:
    pass

class PhotoshopFile:
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_pgfId-1036097
    '''
    def __init__(self, file_header, color_mode_data, image_resources, layer_mask_info, image_data):
        pass

class FileHeader:
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_19840
    '''
    def __init__(self, channel_count, height, width, depth, color_mode):
        pass

class ColorModeData (Dummy):
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_71638
    '''
    pass

class ImageResourceSection (Dummy):
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_69883
    '''
    pass

class LayerMaskInformation:
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_75067
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
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_16000
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
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_13084
    '''
    def __init__(self, rectangle, channel_count, channel_info, blend_mode, opacity, clipping, mask_data, blending_ranges, name):
        self.rectangle = rectangle
        self.channel_count = channel_count
        self.channel_info = channel_info
        self.blend_mode = blend_mode
        self.opacity = opacity
        self.clipping = clipping
        self.mask_data = mask_data
        self.blending_ranges = blending_ranges
        self.name = name
    
    def tostring(self):
        pixel_count = (self.rectangle[2] - self.rectangle[0]) * (self.rectangle[3] - self.rectangle[1])
        mask_data = self.mask_data.tostring()
        blending_ranges = self.blending_ranges.tostring()
        name = pascal_string(self.name, 4)
    
        parts = [
            ''.join(map(uint32, self.rectangle)),
            uint16(self.channel_count),
            ''.join([int16(chid) + uint32(2 + pixel_count) for chid in self.channel_info]),
            '8BIM',
            self.blend_mode,
            uint8(self.opacity),
            uint8(self.clipping),
            uint8(0b00000000),
            uint32(len(mask_data + blending_ranges + name)),
            mask_data,
            blending_ranges,
            name
        ]
        
        return ''.join(parts)

class GlobalLayerMask (Dummy):
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_17115
    '''
    def tostring(self):
        return uint32(0)

class LayerMaskAdjustmentData (Dummy):
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_22582
    '''
    def tostring(self):
        return uint32(0)

class LayerBlendingRangesData (Dummy):
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_21332
    '''
    def tostring(self):
        return uint32(0)

class ChannelImageData:
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_26431
    '''
    def __init__(self, channels):
        self.channels = channels
    
    def tostring(self):
        ''' Compression. 0 = Raw Data, 1 = RLE compressed, 2 = ZIP without prediction, 3 = ZIP with prediction.
        '''
        return ''.join(['\x00\x00' + chan.tostring() for chan in self.channels])

if __name__ == '__main__':

    from PIL import Image
    
    img = Image.new('RGBA', (8, 8), (0xff, 0x99, 0x00, 0xff))
    
    rec_args = dict(
        rectangle = (0, 0, 8, 8),
        channel_count = 4,
        channel_info = (0, 1, 2, -1),
        blend_mode = 'pass',
        opacity = 0xff,
        clipping = 0x00,
        mask_data = LayerMaskAdjustmentData(),
        blending_ranges = LayerBlendingRangesData(),
        name = 'Orange'
        )
    
    rec = LayerRecord(**rec_args)
    cim = ChannelImageData(img.split())
    info = LayerInformation(1, [rec], cim)
    
    lmi = LayerMaskInformation(info, GlobalLayerMask())
    
    print repr(lmi.tostring())
