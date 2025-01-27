import mido
#import math
from enum import Enum
import utils
import numpy as np
from PIL import Image
from PIL.ImageOps import colorize
#from tensorflow import keras
import tensorflow as tf
import os

# I'm first trying to train a basic dense network to create a kind of video generator for the launchpad
# It will take in a frame as an array of RGB values and output a frame as an array of RGB values
# Hopefully it will be able to learn to create some cool patterns

# I'll be training it of a series of 64x64 image sequences of patterns I've created
# A good number of different 32 frame patterns is around 1000, so I'll try to get that many
# I can manually create around 100, and the rest I can generate using code by rotating and flipping the patterns as well as adding noise and maybe some other transformations (like scaling)

batch_size = 32
num_epochs = 128


# Create rotated and flipped versions if they don't already exist
# I store these in the root data folder as 
# rot_90_NAME, rot_180_NAME, rot_270_NAME, flip_h_NAME, flip_v_NAME, flip_hv_NAME
# Where NAME is the name of the original folder. 
# I need to do the same to all the images in the folder
# otherwise the sequences could have one image flipped and one not, etc.

class Transform(Enum):
    ROT_90 = 1
    ROT_180 = 2
    ROT_270 = 3
    FLIP_H = 4
    FLIP_V = 5
    FLIP_HV = 6

for folder in os.listdir('data'):
    # make sure it's a folder
    if not os.path.isdir('data/' + folder):
        continue

    if (folder.startswith('.')):
        continue
    # check if the transformed versions exist, and if not, create them
    folders = os.listdir('data')
    for transform in Transform:
        if ("." + transform.name + '_' + folder) not in folders:
            os.mkdir('data/.' + transform.name + '_' + folder)
        else:
            continue

        # create the transformed images
        for i in range(len(os.listdir('data/' + folder))):
            filename = 'pixil-frame-' + str(i) + '.png'
            with Image.open('data/' + folder + '/' + filename) as im:
                if transform == Transform.ROT_90:
                    im = im.rotate(90)
                elif transform == Transform.ROT_180:
                    im = im.rotate(180)
                elif transform == Transform.ROT_270:
                    im = im.rotate(270)
                elif transform == Transform.FLIP_H:
                    im = im.transpose(Image.FLIP_LEFT_RIGHT)
                elif transform == Transform.FLIP_V:
                    im = im.transpose(Image.FLIP_TOP_BOTTOM)
                elif transform == Transform.FLIP_HV:
                    im = im.transpose(Image.TRANSPOSE)
                im.save('data/.' + transform.name + '_' + folder + '/' + filename)


# Create hue shifted versions
# Images are all black and white, so I can just shift the hue by using colorize
# Just make a few different variation with different colors
class Colors(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    CYAN = 5
    MAGENTA = 6

for folder in os.listdir('data'):
    # make sure it is a folder
    if not os.path.isdir('data/' + folder):
        continue

    # Exclude folders that are already colorized, but not ones that have been transformed (flipped, etc)
    is_colorized = False
    for color in Colors:
        if folder.startswith('.' + color.name):
            is_colorized = True
            break
    if is_colorized:
        continue

    # check if the transformed versions exist, and if not, create them
    folders = os.listdir('data')
    for color in Colors:
        
        if ("." + color.name + '_' + folder) not in folders:
            os.mkdir('data/.' + color.name + '_' + folder)
        else:
            continue
        # create the transformed images
        for i in range(len(os.listdir('data/' + folder))):
            filename = 'pixil-frame-' + str(i) + '.png'
            with Image.open('data/' + folder + '/' + filename) as im:
                im = im.convert('L')
                if color == Colors.RED:
                    im = colorize(im, (0, 0, 0), (255, 0, 0))
                elif color == Colors.GREEN:
                    im = colorize(im, (0, 0, 0), (0, 255, 0))
                elif color == Colors.BLUE:
                    im = colorize(im, (0, 0, 0), (0, 0, 255))
                elif color == Colors.YELLOW:
                    im = colorize(im, (0, 0, 0), (255, 255, 0))
                elif color == Colors.CYAN:
                    im = colorize(im, (0, 0, 0), (0, 255, 255))
                elif color == Colors.MAGENTA:
                    im = colorize(im, (0, 0, 0), (255, 0, 255))
                im.save('data/.' + color.name + '_' + folder + '/' + filename)


# Overall, all this processing creates 36 folders for each original folder
# if i want 1000 folders, I need to create 1000/36 = 28ish original folders


# GIF DATA IMPORT AND PROCESSING
image_sequences = []

# Load all the sequences in the data folder
for folder in os.listdir('data'):
    if not os.path.isdir('data/' + folder):
        continue
    frames = []
    # sorted_list = {}
    # for filename in os.listdir('data/' + folder):
    #     filename.removeprefix('pixil-frame-')
    #     filename.removesuffix('.png')
    #     sorted_list[int(filename)] = filename
    for i in range(len(os.listdir('data/' + folder))):
        filename = 'pixil-frame-' + str(i) + '.png'
        if filename.endswith('.png'):
            with Image.open('data/' + folder + '/' + filename) as im:
                frames.append(im.copy().convert('RGB').rotate(180))
    image_sequences.append(frames)




# Convert the frames to numpy arrays
# np arrays are stored as
# [[ROW [R G B], ...], ...]
for i in range(len(image_sequences)):
    for j in range(len(image_sequences[i])):
        image_sequences[i][j] = np.array(image_sequences[i][j])

# Now we have a list of lists of numpy arrays, where each numpy array is a frame of the gif
# We need to convert this into my propietary ChrisIMG™ format
# This is an array where a frame is encoded as [r, g, b, r, g, b, ...] where each is a 7 bit int. Encoded from bottom left to top right, left to right
# Frames should all already be 64x64
def convert_frame(frame):
    new_frame = []
    for i in range(8):
        for j in range(8):
            # Bitshift to get 7 bit int
            # 11111111 -> 01111111
            new_frame.append(frame[i][j][0] >> 1)
            new_frame.append(frame[i][j][1] >> 1)
            new_frame.append(frame[i][j][2] >> 1)
    return new_frame

for i in range(len(image_sequences)):
    for j in range(len(image_sequences[i])):
        image_sequences[i][j] = convert_frame(image_sequences[i][j])


# Now to turn it into a dataset for training (I'm scared)
x_data = []
y_data = []

for sequence in image_sequences:
    for i in range(len(sequence) - 1):
        x_data.append(sequence[i])
        y_data.append(sequence[i + 1])

x_data = np.array(x_data)
y_data = np.array(y_data)

dataset = tf.data.Dataset.from_tensor_slices((x_data, y_data))
dataset = dataset.shuffle(buffer_size=len(x_data))
dataset = dataset.batch(batch_size)
dataset = dataset.prefetch(tf.data.AUTOTUNE)

# model definition
# First attempt is using a sequential model
# 192 -> 256 -> 192
# Each value is an RGB value between 0 and 127
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(192,)),
    tf.keras.layers.Dense(192, activation='leaky_relu'),
    tf.keras.layers.Dense(192, activation='relu')
])

model.compile(optimizer='adam', loss='mean_squared_error')

model.fit(dataset, epochs=num_epochs)

model.evaluate(dataset)

# save
model.save('model/model.keras')

#print(mido.get_output_names())
#outport = mido.open_output('MIDIOUT2 (LPMiniMK3 MIDI) 2')
#outport.send(utils.set_layout_message(127))

#outport.send(utils.set_light_multiple(utils.rgb_array_to_light_data(utils.make_rgb_array(image_sequences[0][0]))))