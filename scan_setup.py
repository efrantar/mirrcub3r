import os
import pickle
import cv2
import numpy as np

IMAGE = 'sample.jpg'
GUI = 'image'
COLOR = (147, 20, 255) # deep pink
FILE = 'scan-setup.pkl'

image = cv2.imread(IMAGE)
image = cv2.resize(image, (image.shape[1] // 2, image.shape[0] // 2))

def scale(points, s):
    for poly in points:
        for i in range(len(poly)):
            x, y = poly[i]
            poly[i] = (int(s * x), int(s * y))

def draw_poly(poly):
    for i in range(len(poly)):
        cv2.line(image, poly[i - 1], poly[i], COLOR, 2)

if os.path.exists(FILE):
    points, order = pickle.load(open(FILE, 'rb'))
    scale(points, .5)
    for poly in points:
        draw_poly(poly)
    for i in range(len(order)):
        if order[i] is not None:
            cv2.putText(image, str(order[i][0]), order[i][1], cv2.FONT_HERSHEY_SIMPLEX, .5, COLOR)
    points.append([])
    order.append(None)
else:
    points = [[]]
    order = [None]

idx = -1
for i in range(len(order)):
    if order[i] is not None:
        idx = max(idx, order[i][0])
idx += 1

def handle_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        for i in range(len(points) - 1):
            if cv2.pointPolygonTest(np.array(points[i]), (x, y), False) > 0:
                order[i] = (idx, (x, y))
                cv2.putText(image, str(idx), (x, y), cv2.FONT_HERSHEY_SIMPLEX, .5, COLOR)
                return

        points[-1].append((x, y))
        cv2.circle(image, (x, y), 4, COLOR, -1)
        if len(points[-1]) > 1:
            cv2.line(image, points[-1][-2], points[-1][-1], COLOR, 2)

cv2.namedWindow(GUI)
cv2.setMouseCallback(GUI, handle_click)

while True:
    cv2.imshow(GUI, image)

    key = cv2.waitKey(1) & 0xff 
    if key == ord('n'):
        cv2.line(image, points[-1][-1], points[-1][0], COLOR, 2)
        points.append([])
        order.append(None)
    elif key == ord('i'):
        idx += 1
    elif key == ord('q'):
        del points[-1]
        del order[-1]
        break

scale(points, 2)
pickle.dump((points, order), open(FILE, 'wb'))

cv2.destroyAllWindows()

