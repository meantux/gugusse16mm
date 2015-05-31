import numpy as np
import cv2
import os
import pdb
import wave

from array import array
from bisect import bisect

PICTURE_PATH = '.'
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
THRESHOLD = 100
DATA_FILE = 'data.dat'
OUTPUT_FILE = 'out.wav'

images = []
sound_data = []

for f in os.listdir(PICTURE_PATH):
full_path = os.path.join(PICTURE_PATH, f)
if os.path.isfile(full_path) and os.path.splitext(full_path)[-1] in IMAGE_EXTENSIONS:
    images.append(os.path.join(PICTURE_PATH, f))

for image in images:

img = cv2.imread(image, 0)

for line in img:
    line_list = list(line)
    float(bisect(line_list, THRESHOLD)) / len(line_list)
    sound_data.append(float(bisect(line_list, THRESHOLD)) / len(line_list))

output_file = open(DATA_FILE, 'wb')

float_array = np.array(sound_data, dtype=np.float32)
float_array.tofile(output_file)
output_file.close()

input_file = open(DATA_FILE, 'r')
 
wave_obj = wave.openfp(OUTPUT_FILE, 'wb')

wave_obj.setnchannels(1)
wave_obj.setframerate(24000)
wave_obj.setsampwidth(4)

wave_obj.writeframes(input_file.read())
