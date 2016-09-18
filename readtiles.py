#! /usr/bin/env python

import numpy as np
import cv2

tileset = cv2.imread("dragonwarriortiles.png")
(b, g, r) = tileset[111, 111]
print "Pixel value at (111, 111): Red: %d, Green: %d, Blue: %d" % (r, g, b)

# c = np.arange(24).reshape((4,6))
# print(c)
#
# h, w = c.shape
# d = c.reshape(h//4, 4, -1, 3)
# print(d)
# print(d.shape)

tiles = []
first_split = np.vsplit(tileset, 7)
for image in first_split:
    second_split = np.hsplit(image, 7)
    tiles = tiles + second_split

final_tiles = []
for index in tiles:
    # if np.all(index) not in final_tiles:
    if not np.all(index == [255, 0, 255]): 
        final_tiles.append(index)

for image in final_tiles:
    cv2.imshow("Image", image)
    cv2.waitKey(0)

# tile_list = []
# tile_topleft = 0
# tile_bottomleft = 0
# tile_topright = 0
# tile_bottomright = 0
# #sample the top left color until we hit fuschia
# tile_topleftcolor = ()
# while tile_topleftcolor != (255, 0, 255):
    