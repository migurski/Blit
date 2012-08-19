from struct import unpack

def next_uint8(file):
    return unpack('>B', file.read(1))[0]

def next_int16(file):
    return unpack('>h', file.read(2))[0]

def next_uint16(file):
    return unpack('>H', file.read(2))[0]

def next_uint32(file):
    return unpack('>I', file.read(4))[0]

def next_string(file):
    pairs = []
    while True:
        pairs.append(file.read(2))
        if pairs[-1][-1] == '\x00':
            break
    return ''.join(pairs).rstrip('\x00')

def next_pascal_string(file, buffer=4):
    length = next_uint8(file)
    string = file.read(length)
    
    # padded to multiples of buffer
    skip_bytes(file, (buffer - (1 + length) % buffer) % buffer)
    
    return string

def skip_bytes(file, count):
    file.seek(count, 1)
    

if __name__ == '__main__':

    file = open('orange.psd')
    
    #
    # http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_19840
    #
    print '---- Header'
    
    # Signature: always equal to '8BPS'
    assert file.read(4) == '8BPS'
    
    # Version: always equal to 1
    assert unpack('>H', file.read(2)) == (1, )
    
    # Reserved: must be zero
    assert file.read(6) == '\x00' * 6
    
    # The number of channels in the image, including any alpha channels
    channel_count = next_uint16(file)
    print 'Channels:', channel_count
    
    # The height and width of the image in pixels
    image_height = next_uint32(file)
    image_width = next_uint32(file)
    print 'Image size:', image_width, 'x', image_height
    
    # Depth: the number of bits per channel
    bit_depth = next_uint16(file)
    print 'Bit depth:', bit_depth
    
    # The color mode of the file
    color_modes = 'Bitmap,Grayscale,Indexed,RGB,CMYK,,,Multichannel,Duotone,Lab'.split(',')
    color_mode = color_modes[next_uint16(file)]
    print 'Color mode:', color_mode
    
    #
    # http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_71638
    #
    print '---- Color Mode Data'
    
    size = next_uint32(file)
    skip_bytes(file, size)
    
    print 'Skipping', size, 'bytes'
    
    #
    # http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_69883
    #
    
    print '---- Image Resources Section'
    
    size = next_uint32(file)
    ends = file.tell() + size
    
    # skip the resources
    file.seek(ends)
    
    while file.tell() < ends:
        #
        # http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_38034
        #
        
        assert file.read(4) == '8BIM'

        # Unique identifier for the resource
        resource_id = next_uint16(file)
        print '  -- Resource ID:', resource_id
        
        # Name: Pascal string, padded to make the size even
        resource_name = next_string(file)
        print '  Resource name:', resource_name
        
        # Actual size of resource data that follows
        resource_size = next_uint32(file)
        print '  Resource size:', resource_size
        
        # The resource data ... padded to make the size even
        skip_bytes(file, resource_size + resource_size%2)
    
    #
    # http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_75067
    #
    
    print '---- Layer and Mask Information Section'
    
    # Length of the layer and mask information section
    size = next_uint32(file)
    
    next_uint32(file)
    
    layer_count = next_uint16(file)
    print 'Layers:', layer_count
    
    for layer_index in range(layer_count):
    
        print '-- Layer', layer_index
    
        # Rectangle containing the contents of the layer
        layer_rectangle = [next_uint32(file) for i in range(4)]
        print 'Layer rectangle:', layer_rectangle
        
        # Number of channels in the layer
        layer_channels = next_uint16(file)
        print 'Layer channels:', layer_channels
        
        # Channel information. Six bytes per channel ...
        channel_info = [(next_int16(file), next_uint32(file)) for i in range(layer_channels)]
        print 'Channel info:', channel_info
        
        # Blend mode signature: '8BIM'
        assert file.read(4) == '8BIM'
        
        # Blend mode key
        blend_mode_key = file.read(4)
        print 'Blend mode key:', blend_mode_key
        
        # Opacity
        opacity = next_uint8(file)
        print 'Opacity:', opacity
        
        # Clipping
        clipping = next_uint8(file)
        print 'Clipping:', clipping
        
        # Flags
        flags = next_uint8(file)
        print 'Flags:', bin(flags)
        
        next_uint8(file)
        
        layer_extra_data_size = next_uint32(file)
        layer_end_byte = file.tell() + layer_extra_data_size
        
        layer_mask_data_size = next_uint32(file)
        skip_bytes(file, layer_mask_data_size)
        
        layer_blending_ranges_size = next_uint32(file)
        skip_bytes(file, layer_blending_ranges_size)
        
        # Layer name: Pascal string, padded to a multiple of 4 bytes
        layer_name = next_pascal_string(file, 4)
        print 'Layer name:', layer_name
        
        while file.tell() < layer_end_byte:
            assert file.read(4) in ('8BIM', '8B64')
            
            layer_info_key = file.read(4)
            layer_info_size = next_uint32(file)
            layer_info_data = file.read(layer_info_size)
            
            if layer_info_key in ('SoCo',):
                print '  --', layer_info_key, '-', repr(layer_info_data)
            

    #
    # http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_89817
    #
    
    print '---- Image Data'
    print 'Starts at', file.tell()

    compression_methods = 'Raw image data,RLE compressed,ZIP without prediction,ZIP with prediction'.split()
    compression_method = compression_methods[next_uint16(file)]
    print 'Compression method:', compression_method
    
    #
    # PackBits follows
    # http://en.wikipedia.org/wiki/PackBits
    # http://web.archive.org/web/20080705155158/http://developer.apple.com/technotes/tn/tn1023.html
    #

    print [next_uint16(file) for i in range(8)]
    print repr(file.read())