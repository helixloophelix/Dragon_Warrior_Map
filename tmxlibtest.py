#! /usr/bin/env python

import tmxlib
import cv2
import numpy as np
from PIL import Image

#Open up the tileset
tilefile = open("dragonwarriortiles.png")

dwtileimage = tmxlib.image.open(tilefile.name)
dwtiles = tmxlib.tileset.ImageTileset("dragonwarriortiles", (16, 16), dwtileimage, source=tilefile.name)

#tmxlib has effectively no support for actually displaying tiles, so we're going to use OpenCV to cut them out
#as numpy arrays; it might be cleaner if I used PIL instead.

#Load the actual image using OpenCV
tileset_pixels = cv2.imread(tilefile.name)

#Slice up the image and store the slices in a dictionary relating them to tile numbers

tileset_number_to_tile_pixels = {}
for index in range(0, len(dwtiles)):
    #Use the ImageRegion information to get the coordinates for each slice
    image_region = dwtiles.tile_image(index) #Technically an ImageRegion object
    top_left_x, top_left_y = image_region.top_left
    bottom_right_x = top_left_x + image_region.width
    bottom_right_y = top_left_y + image_region.height
    test_pixels = tileset_pixels[top_left_x:bottom_right_x, top_left_y:bottom_right_y]
    #PIL is probably the right way to do this generally; I should be using the Image class more often
    color_test = Image.fromarray(test_pixels)
    colors = color_test.getcolors()
    #Fuschia tiles are only there to keep the tileset loader happy and functional, so we don't need them
    #Also, tmxlib cheerfully loads tiles of transparent pixels as the empty set, so we need to get rid of those
    if test_pixels.size != 0 and (256, (255, 0, 255)) not in colors:
        tileset_number_to_tile_pixels[index] = test_pixels
    
#Now we can load the world of Alefgard and begin classifying tiles

alefgard_map = cv2.imread("alefgard.png")

#Split the map into subarrays, first vertically and then horizontally

alefgard_array_list = []
horizontal_split = np.hsplit(alefgard_map, 128)
for hsclice in horizontal_split:
    vertical_split = np.vsplit(hsclice, 128)
    alefgard_array_list = alefgard_array_list + vertical_split
    
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

map_list = []
for map_tile in alefgard_array_list:
    
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

    for tile_number in tileset_number_to_tile_pixels:
        current_tile = tileset_number_to_tile_pixels[tile_number]
        tile_match_list = []
        if np.array_equal(map_tile, current_tile):
            tile_match_list.append(tile_number)
            break

    if not tile_match_list:
        print("Error: tile not recognized")
        cv2.imshow("Unrecognized Tile", map_tile)
        cv2.waitKey(0)
    elif len(tile_match_list) >= 2:
        print("Error: Multiple tileset tiles match map tile")
    else:
        map_list.append(tile_number)

print(len(map_list))

# oneD_map_array = np.fromiter(map_list, int)
# map_array = np.reshape(oneD_map_array, (128,128))
# # np.reshape(map_array, (128, 128, 3))
# print(len(map_list))
# print(map_array)


