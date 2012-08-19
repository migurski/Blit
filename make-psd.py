''' See: 
'''

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
        pass

class LayerInformation:
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_16000
    '''
    def __init__(self, layer_count, layer_records, channel_image_data):
        pass

class LayerRecord:
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_13084
    '''
    def __init__(self, rectangle, channel_count, channel_info, blend_mode, opacity, clipping, mask_data, blending_ranges, name):
        pass

class LayerMaskAdjustmentData (Dummy):
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_22582
    '''
    pass

class LayerBlendingRangesData (Dummy):
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_21332
    '''
    pass

class ChannelImageData:
    ''' http://www.adobe.com/devnet-apps/photoshop/fileformatashtml/PhotoshopFileFormats.htm#50577409_26431
    '''
    def __init__(self, image):
        pass

if __name__ == '__main__':

    print Dummy()