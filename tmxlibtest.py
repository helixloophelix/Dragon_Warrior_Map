#! /usr/bin/env python

import tmxlib
import cv2
import numpy as np
from sklearn.feature_extraction import image

#Open up the tileset
tilefile = open("dragonwarriortiles.png")

dwtileimage = tmxlib.image.open(tilefile.name)
dwtiles = tmxlib.tileset.ImageTileset("dragonwarriortiles", (16, 16), dwtileimage, source=tilefile.name)
# print(type(dwtiles))
print(len(dwtiles))
# print(type(dwtiles.tile_image(0)))

#tmxlib has effectively no support for actually displaying tiles, so we're going to use OpenCV to cut them out
#as numpy arrays

#Load the actual image using OpenCV
tileset_pixels = cv2.imread(tilefile.name)

#Slice up the image and store the slices in a dictionary relating them to tile numbers

#tmxlib.image.open doesn't actually do anything with the color-key transparency, which is the fault of PIL,
#as far as I can tell

tileset_number_to_tile_pixels = {}
for index in range(0, len(dwtiles)):
    #Use the ImageRegion information to get the coordinates for each slice
    image_region = dwtiles.tile_image(index) #Technically an ImageRegion object
    top_left_x, top_left_y = image_region.top_left
    bottom_right_x = top_left_x + image_region.width
    bottom_right_y = top_left_y + image_region.height
    print(top_left_x, top_left_y, bottom_right_x, bottom_right_y)
    test_pixels = tileset_pixels[top_left_x:bottom_right_x, top_left_y:bottom_right_y]
    if test_pixels.size != 0:   #tmxlib cheerfully loads transparent pixels as the empty set
        tileset_number_to_tile_pixels[index] = test_pixels
    
#Now we can load the world of Alefgard and begin classifying tiles

for key in sorted(tileset_number_to_tile_pixels):
    cv2.imshow("Tile", tileset_number_to_tile_pixels[key])
    cv2.waitKey(0)

# alefgard_map = cv2.imread("alefgard.png")
# print(alefgard_map.size)

#Split the map into subarrays, first vertically and then horizontally

#alefgard_array_list = []
# horizontal_split = np.hsplit(alefgard_map, 128)
# for hsclice in horizontal_split:
#     vertical_split = np.vsplit(hsclice, 128)
#     alefgard_array_list = alefgard_array_list + vertical_split

# print(len(alefgard_array_list))

# for key in tileset_number_to_tile_pixels:
#     print(tileset_number_to_tile_pixels[key])
#     cv2.imshow("Tile", tileset_number_to_tile_pixels[key])
#     cv2.waitKey(0)
    
#Split the map into subarrays
#I stole this off Stack Overflow and I'm not 100% sure why it works
#Guess I need more practice with arrays
#http://stackoverflow.com/questions/16856788/slice-2d-array-into-smaller-2d-arrays
#This doesn't work becase I need a list of arrays

# map_height, map_width, color = alefgard_map.shape
# alefgard_subarrays = alefgard_map.reshape(map_height//16, 16, -1, 16).swapaxes(1,2).reshape(-1, 16, 16)
# print(alefgard_map[0,0])
# print(type(alefgard_map))
# alefgard_array_list = alefgard_subarrays.tolist()

#Generate the map in list form and then cast it to an array
#The better way to do this is to use numpy's fromiter() method (np.fromiter() )
#But this is best used with an actual function, so I'll try it when I clean this script up

# map_list = []
# for map_tile in alefgard_array_list:
#     # print(map_tile)
#     # cv2.imshow("Map Tile", map_tile)
#     # cv2.waitKey(0)
#     #let's try replacing this with a list comprehension
#
#     # current_tile = [tile_number for tile_number in tileset_number_to_tile_pixels
#     #     if np.array_equal(map_tile, tileset_number_to_tile_pixels[tile_number])]
#     # cv2.imshow("Map Tile", map_tile)
#     # cv2.waitKey(0)
#     # print(current_tile)
#     # if not current_tile:
#     #     #check whether we failed to find a match while comparing tile pixel arrays
#     #     print("Error: Tile not recognized")
#     # elif len(current_tile) >= 2:
#     #     #check whether we found more than one match when comparing tile pixel arrays
#     #     print("Error: Multiple tileset tiles match map tile")
#     # else:
#     #     print("Tile number is %i") % current_tile
#     #     cv2.imshow("Tileset Tile", tileset_number_to_tile_pixels[tile_number])
#     #     cv2.waitKey(0)
#     #     map_list.append(tile_number)
#
#     for tile_number in tileset_number_to_tile_pixels:
#         current_tile = tileset_number_to_tile_pixels[tile_number]
#         tile_match_list = []
#         if np.array_equal(map_tile, current_tile):
#             tile_match_list.append(tile_number)
#             print(type(tile_number))
#             print("Tile number is %i") % tile_number
#             print(tile_match_list)
#             break
#
#     if not tile_match_list:
#         print("Error: tile not recognized")
#     elif len(tile_match_list) >= 2:
#         print("Error: Multiple tileset tiles match map tile")
#     else:
#         map_list.append(tile_number)
            





            # map_pointer_x += 1
            # if map_pointer_x < 127:
            #     map_tile_value = tile_number    #We have to do this because tile_number isn't really an integer
            #     map_array([map_pointer_x, map_pointer_y]) = map_tile_value
            # else:
            #     #Wrap around when we reach the edge of the array
            #     map_pointer_x = 0
            #     map_pointer_y += 1
            #     map_tile_value = tile_number
            #     map_array([map_pointer_x, map_pointer_y]) = map_tile_value
# oneD_map_array = np.fromiter(map_list, int)
# map_array = np.reshape(oneD_map_array, (128,128))
# # np.reshape(map_array, (128, 128, 3))
# print(len(map_list))
# print(map_array)


