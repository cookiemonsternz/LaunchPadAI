import mido
import math
from enum import Enum

# https://fael-downloads-prod.focusrite.com/customer/prod/s3fs-public/downloads/Launchpad%20Mini%20-%20Programmers%20Reference%20Manual.pdf

#### TODO ####
# Make sure parameters fit when sending lighting data 
# E.g RGB should have 3 parameters, Flash should have 2, etc.

# Find a way to have quicker reference to palette colors
# Could do an enum, but names are not very descriptive 
# Color syntax? Vscode please help me

class LightingType(Enum):
    Palette = 0
    Flash = 1
    Pulse = 2
    RGB = 3

class Layout(Enum):
    Session = 0
    User1 = 4
    User2 = 5
    User3 = 6
    DAWFaders = 13
    Programmer = 127

def set_layout_message(layout):
    """
    Set the layout mode
    
    :param layout: 0 - Session, 4 - User 1, 5 - User 2, 6 - User 3, 13 - DAW Faders, 127 - Programmer
    :type layout: int
    :return: Message to set the layout
    :rtype: Message
    """
    return mido.Message('sysex', data=[0, 32, 41, 2, 13, 0, layout])

def set_light_message(LightingType, LEDIndex, LightingData):
    """
    Set the color of a LED
    
    :param LightingType: 0 - Pallate, 1 - Flash, 2 - Pulse, 3 - RGB
    :type LightingType: int
    :param LEDIndex: Index of led
    :type LEDIndex: int
    :param LightingData: Color pallete index
    :type LightingData: int 
    """
    # 0 32 41 2 13 3 <colourspec>
    return mido.Message('sysex', data=[0, 32, 41, 2, 13, 3, LightingType, LEDIndex, LightingData])

def set_light_multiple(data):
    """
    Set the color of multiple leds
    
    :param LightingType: 0 - Pallate, 1 - Flash, 2 - Pulse, 3 - RGB
    :type LightingType: int
    :param data: List of LEDIndex, LightingData pairs
    :type data: List[Tuple[int, [int]]]]
    """

    flattened_data = []
    for pair in data:
        flattened_data.append(pair[0].value) # LightingType
        flattened_data.append(pair[1]) # Index
        for item in pair[2]:
            flattened_data.append(int(item)) # Data
    # 0 32 41 2 13 3 [<colourspec> […]]
    return mido.Message('sysex', data=[0, 32, 41, 2, 13, 3] + flattened_data)

def flatten_rgb_array(data):
    # Takes an array of form:
    # [[r, g, b], [r, g, b], ...]
    # which has 64 elements and flattens it to:
    # [r, g, b, r, g, b, ...]
    flattened_data = []
    for item in data:
        for i in item:
            flattened_data.append(i)

    return flattened_data

def make_rgb_array(data):
    # Makes an array of form:
    # [[r, g, b], [r, g, b], ...]
    # from an array of form:
    # [r, g, b, r, g, b, ...]
    rgb_data = []
    for i in range(0, len(data), 3):
        rgb_data.append([int(data[i]), int(data[i+1]), int(data[i+2])])

    return rgb_data

def rgb_array_to_light_data(array):
    # Takes an array of form:
    # [[r, g, b], [r, g, b], ...]
    # and converts it to an array of form:
    # [[LightingType, Index, [r, g, b]], ...]
    # Index is from bottom left to top right, 11 - 88
    # where row 1 is 11-18, row 2 is 21-28, etc.
    light_data = []
    i = 0
    for pad in array:
        light_data.append([LightingType.RGB, i + 11, pad])
        if str(i)[-1] == '7':
            i += 3
        else:
            i += 1
    return light_data

#print(mido.get_output_names())
#outport = mido.open_output('MIDIOUT2 (LPMiniMK3 MIDI) 2')
#outport.send(set_layout_message(127))


# TESTING FLATTEN AND MAKE FUNCS
# dataA = [[0, 0, 0], [127, 127, 127], [56, 80, 25], [90, 12, 3], [108, 3, 4], [1, 2, 3], [3, 2, 1], [2, 1, 3], [0, 0, 0], [127, 127, 127], [56, 80, 25], [90, 12, 3], [108, 3, 4], [1, 2, 3], [3, 2, 1], [2, 1, 3], [0, 0, 0], [127, 127, 127], [56, 80, 25], [90, 12, 3], [108, 3, 4], [1, 2, 3], [3, 2, 1], [2, 1, 3], [0, 0, 0], [127, 127, 127], [56, 80, 25], [90, 12, 3], [108, 3, 4], [1, 2, 3], [3, 2, 1], [2, 1, 3], [0, 0, 0], [127, 127, 127], [56, 80, 25], [90, 12, 3], [108, 3, 4], [1, 2, 3], [3, 2, 1], [2, 1, 3], [0, 0, 0], [127, 127, 127], [56, 80, 25], [90, 12, 3], [108, 3, 4], [1, 2, 3], [3, 2, 1], [2, 1, 3], [0, 0, 0], [127, 127, 127], [56, 80, 25], [90, 12, 3], [108, 3, 4], [1, 2, 3], [3, 2, 1], [2, 1, 3], [0, 0, 0], [127, 127, 127], [56, 80, 25], [90, 12, 3], [108, 3, 4], [1, 2, 3], [3, 2, 1], [2, 1, 3]]
# print(flatten_rgb_array(dataA))
# print(make_rgb_array(flatten_rgb_array(dataA)))
# print(rgb_array_to_light_data(make_rgb_array(flatten_rgb_array(dataA))))
# outport.send(set_light_multiple(rgb_array_to_light_data(make_rgb_array(flatten_rgb_array(dataA)))))


# Set the color of the first 8 pads
# for i in range(8):
#    outport.send(set_light_message(LightingType.Palette, i + 11, 3))


# With the new function: sets first 4 vertically with different effects
# outport.send(set_light_multiple([[LightingType.Flash, 11, [3, 0]], [LightingType.Pulse, 21, [12]], [LightingType.Palette, 31, [3]], [LightingType.RGB, 41, [0, 127, 56]]]))