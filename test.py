import mido
import utils
import keras
import PIL
import numpy as np
import time
import sys

keras.config.disable_interactive_logging()


print(mido.get_input_names())
outport = mido.open_output('MIDIOUT2 (LPMiniMK3 MIDI) 2')
inport = mido.open_input("MIDIIN2 (LPMiniMK3 MIDI) 1")


start_file = 'data/Wave/pixil-frame-2.png'

model = keras.models.load_model('model/model.keras')

outport.send(utils.set_layout_message(127))

max_frames = 10000
sys.setrecursionlimit(max_frames + 100)

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

def get_start_image(path):
    image = PIL.Image.open(path)
    image = image.convert('RGB')
    image = np.array(image)
    image = convert_frame(image)
    return image

def get_next_image(image):
    # Image is a 1D array, 192 elements
    # tiny bit of noise
    #image = np.array(image) + np.random.normal(0, 5, 192)

    next_image = model.predict(np.array([image]))[0]
    # clamp values to 0-127
    for i in range(len(next_image)):
        next_image[i] = min(127, max(0, next_image[i]))
    return next_image

def send_image(image):
    light_data = utils.rgb_array_to_light_data(utils.make_rgb_array(image))
    outport.send(utils.set_light_multiple(light_data))


held_notes = []

def loop_step(image, frame):
    #print(held_notes)
    if frame >= max_frames:
        return
    
    for msg in inport.iter_pending():
        #print(msg)
        if not msg.type == 'note_on':
            continue
        if (msg.velocity == 127):
            held_notes.append(msg.note)
        else:
            if msg.note in held_notes:
                held_notes.remove(msg.note)
    for note in held_notes:
        # set the rgb of the button to white
        index = 8 * (int(str(note)[0]) - 1) + int(str(note)[1]) - 1
        image[index * 3] = 127
        image[index * 3 + 1] = 127
        image[index * 3 + 2] = 127
    next_image = get_next_image(image)
    for note in held_notes:
        # set the rgb of the button to white
        index = 8 * (int(str(note)[0]) - 1) + int(str(note)[1]) - 1
        next_image[index * 3] = 127
        next_image[index * 3 + 1] = 127
        next_image[index * 3 + 2] = 127
    send_image(next_image)
    #time.sleep(1/60)
    loop_step(next_image, frame + 1)

send_image(get_start_image(start_file))

start_image = get_start_image(start_file)

loop_step(start_image, 0)