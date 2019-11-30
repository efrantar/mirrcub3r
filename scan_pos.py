# Minimal utility for setting up the scan-positions.
# It is rather primitive and not at all user-friendly yet it gets the job done decently enough.


import os
import pickle
import sys
import time

import cv2
import numpy as np

from scan import *


IMAGE = sys.argv[1]
GUI = 'Scan Setup'
COLOR = (0, 0, 0)
FILE = 'scan-pos.pkl'
SIZE = 5


def scale(points, s):
    return [[(int(s * x), int(s * y)) for x, y in ps] for ps in points]


image_og = cv2.imread(IMAGE)
image = cv2.resize(image_og, (image_og.shape[1] // 2, image_og.shape[0] // 2))
image1 = image.copy()

if os.path.exists(FILE):
    points = pickle.load(open(FILE, 'rb'))
    points = scale(points, .5)
else:
    points = []
i = len(points)
points.append([])


def show_squares():
    global image1
    image1 = image.copy()
    for ps in points:
        for x, y in ps:
            image1[(y - SIZE):(y + SIZE), (x - SIZE):(x + SIZE), :] = COLOR

def show_nums():
    global image1
    image1 = image.copy()
    for i, ps in enumerate(points):
        for p in ps:
            cv2.putText(
                image1, str(i), (p[0] - 5, p[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, .5, COLOR
            )

def show_extracted():
    extractor = ColorExtractor(np.array(scale(points[:-1], 2)), SIZE * 4)
    tick = time.time()
    colors = extractor.extract_bgrs(image_og)
    print(time.time() - tick)    

    global image1
    image1 = image.copy()
    for i, ps in enumerate(points):
        for x, y in ps:
            image1[(y - SIZE):(y + SIZE), (x - SIZE):(x + SIZE), :] = colors[i, :]

def show_matched():
    if len(points) != 55:
        return

    extractor = ColorExtractor(np.array(scale(points[:-1], 2)), SIZE * 4)
    tick = time.time()    
    colors = extractor.extract_bgrs(image_og)
    matcher = ColorMatcher()
    facecube = matcher.match(colors)
    print(time.time() - tick)

    if facecube == '':
        facecube = 'E' * 54

    global image1
    image1 = image.copy()

    bgr = {
        'U': (255, 0, 0), # blue
        'R': (0, 255, 255), # yellow
        'F': (0, 0, 139), # red
        'D': (0, 128, 0), # green
        'L': (255, 255, 255), # white
        'B': (0, 140, 255), # orange
        'E': (128, 128, 128) # ERROR
    }
    for i, ps in enumerate(points):
        for x, y in ps:
            image1[(y - SIZE):(y + SIZE), (x - SIZE):(x + SIZE), :] = bgr[facecube[i]]


show = show_squares
i_edit = -1

def handle_click(event, x, y, flags, param):
    global i_edit

    if event == cv2.EVENT_LBUTTONDOWN:
        if i_edit == -1:
            for i, ps in enumerate(points):
                for p in ps:
                    if p[0] - SIZE <= x <= p[0] + SIZE and p[1] - SIZE <= y <= p[1] + SIZE:
                        i_edit = i
                        points[i].remove(p)
                        show()
                        return
            
            points[-1].append((x, y))
        else:
            points[i_edit].append((x, y))
            i_edit = -1

        show()

cv2.namedWindow(GUI)
cv2.setMouseCallback(GUI, handle_click)
show()

while True:
    cv2.imshow(GUI, image1)
    key = cv2.waitKey(1) & 0xff
    if key == ord('i'):
        points.append([])
        i += 1
    elif key == ord('s'):
        show = show_squares
        show()
    elif key == ord('n'):
        show = show_nums
        show()
    elif key == ord('e'):
        show = show_extracted
        show()
    elif key == ord('m'):
        show_matched()
    elif key == ord('q'):
        break

cv2.destroyAllWindows()


del points[-1]
points = scale(points, 2)
pickle.dump(points, open(FILE, 'wb'))

