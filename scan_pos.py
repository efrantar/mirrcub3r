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
    return [(int(s * x), int(s * y)) for x, y in points]

def draw_point(point):
    cv2.circle(image, point, 4, COLOR, -1)

if os.path.exists(FILE):
    points = pickle.load(open(FILE, 'rb'))
    points = scale(points, .5)
    for i, p in enumerate(points):
        cv2.putText(image, str(i), p, cv2.FONT_HERSHEY_SIMPLEX, .5, COLOR)
        # draw_point(p)
else:
    points = []

def handle_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        draw_point((x, y))

cv2.namedWindow(GUI)
cv2.setMouseCallback(GUI, handle_click)

while True:
    cv2.imshow(GUI, image)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
points = scale(points, 2)
pickle.dump(points, open(FILE, 'wb'))

cv2.destroyAllWindows()

