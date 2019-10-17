# Minimal utility for setting up the scan-positions.
# It is rather primitive and not at all user-friendly yet it gets the job done decently enough.

import os
import pickle
import cv2
import numpy as np

IMAGE = 'scan.jpg'
GUI = 'Setup scan positions.'
COLOR = (147, 20, 255) # deep pink
FILE = 'scan-pos.pkl'

image = cv2.imread(IMAGE)
image = cv2.resize(image, (image.shape[1] // 2, image.shape[0] // 2))

def scale(points, s):
    return [[(int(s * x), int(s * y)) for x, y in ps] for ps in points]

def draw_point(point):
    cv2.circle(image, point, 4, COLOR, -1)

if os.path.exists(FILE):
    points = pickle.load(open(FILE, 'rb'))
    points = scale(points, .5)
    for i, ps in enumerate(points):
        for p in ps:
            cv2.putText(image, str(i), p, cv2.FONT_HERSHEY_SIMPLEX, .5, COLOR)
            # draw_point(p)
else:
    points = []
i = len(points)
points.append([])

def handle_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points[-1].append((x, y))
        draw_point((x, y))

cv2.namedWindow(GUI)
cv2.setMouseCallback(GUI, handle_click)

while True:
    cv2.imshow(GUI, image)
    key = cv2.waitKey(1) & 0xff
    if key == ord('i'):
        points.append([])
        i += 1
    elif key == ord('q'):
        break

del points[-1]
points = scale(points, 2)
pickle.dump(points, open(FILE, 'wb'))

cv2.destroyAllWindows()

