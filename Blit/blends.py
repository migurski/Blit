import numpy

def combine(bottom_rgba, top_rgb, mask_chan, opacity, blendmode):
    """ Blend arrays using a given mask, opacity, and blend mode.
    
        Working blend modes:
        None for plain pass-through, "screen", "multiply", "linear light", and "hard light".
    """
    if opacity == 0 or not mask_chan.any():
        # no-op for zero opacity or empty mask
        return [numpy.copy(chan) for chan in bottom_rgba]
    
    # prepare unitialized output arrays
    output_rgba = [numpy.empty_like(chan) for chan in bottom_rgba]
    
    if not blendmode:
        # plain old paste
        output_rgba[:3] = [numpy.copy(chan) for chan in top_rgb]

    else:
        blend_functions = {'screen': screen_channels,
                           'multiply': multiply_channels,
                           'linear light': linear_light_channels,
                           'hard light': hard_light_channels}

        if blendmode in blend_functions:
            for c in (0, 1, 2):
                blend_function = blend_functions[blendmode]
                output_rgba[c] = blend_function(bottom_rgba[c], top_rgb[c])
        
        else:
            raise KnownUnknown('Unrecognized blend mode: "%s"' % blendmode)
    
    # comined effective mask channel
    if opacity < 1:
        mask_chan = mask_chan * opacity

    # pixels from mask that aren't full-white
    gr = mask_chan < 1
    
    if gr.any():
        # we have some shades of gray to take care of
        for c in (0, 1, 2):
            #
            # Math borrowed from Wikipedia; C0 is the variable alpha_denom:
            # http://en.wikipedia.org/wiki/Alpha_compositing#Analytical_derivation_of_the_over_operator
            #
            
            alpha_denom = 1 - (1 - mask_chan) * (1 - bottom_rgba[3])
            nz = alpha_denom > 0 # non-zero alpha denominator
            
            alpha_ratio = mask_chan[nz] / alpha_denom[nz]
            
            output_rgba[c][nz] = output_rgba[c][nz] * alpha_ratio \
                               + bottom_rgba[c][nz] * (1 - alpha_ratio)
            
            # let the zeros perish
            output_rgba[c][~nz] = 0
    
    # output mask is the screen of the existing and overlaid alphas
    output_rgba[3] = screen_channels(bottom_rgba[3], mask_chan)

    return output_rgba

def screen_channels(bottom_chan, top_chan):
    """ Return combination of bottom and top channels.
    
        Math from http://illusions.hu/effectwiki/doku.php?id=screen_blending
    """
    return 1 - (1 - bottom_chan[:,:]) * (1 - top_chan[:,:])

def multiply_channels(bottom_chan, top_chan):
    """ Return combination of bottom and top channels.
    
        Math from http://illusions.hu/effectwiki/doku.php?id=multiply_blending
    """
    return bottom_chan[:,:] * top_chan[:,:]

def linear_light_channels(bottom_chan, top_chan):
    """ Return combination of bottom and top channels.
    
        Math from http://illusions.hu/effectwiki/doku.php?id=linear_light_blending
    """
    return numpy.clip(bottom_chan[:,:] + 2 * top_chan[:,:] - 1, 0, 1)

def hard_light_channels(bottom_chan, top_chan):
    """ Return combination of bottom and top channels.
    
        Math from http://illusions.hu/effectwiki/doku.php?id=hard_light_blending
    """
    # different pixel subsets for dark and light parts of overlay
    dk, lt = top_chan < .5, top_chan >= .5
    
    output_chan = numpy.empty(bottom_chan.shape, bottom_chan.dtype)
    output_chan[dk] = 2 * bottom_chan[dk] * top_chan[dk]
    output_chan[lt] = 1 - 2 * (1 - bottom_chan[lt]) * (1 - top_chan[lt])
    
    return output_chan
