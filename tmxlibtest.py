#! /usr/bin/env python

import tmxlib
import cv2
import numpy as np
from PIL import Image

#Open up the tileset
tilefile = open("dragonwarriortiles.png")

dwtileimage = tmxlib.image.open(tilefile.name)
dwtiles = tmxlib.tileset.ImageTileset("dragonwarriortiles", (16, 16), dwtileimage)

# print("Before conversion...")
# print(vars(dwtiles))
#
# nrows = dwtiles.row_count
# ncols = dwtiles.column_count
#
# for index in range(0, len(dwtiles)):
#     current_tile = dwtiles[index]
#     print("Before", current_tile)
#     x, y = divmod(current_tile.number, nrows)
#     cvt_number = y * ncols + x
#     current_tile.number = cvt_number
#     print("After", current_tile)
#
# print("After conversion...")
# print(vars(dwtiles))
    

# #tmxlib has effectively no support for actually displaying tiles, so we're going to use OpenCV to cut them out
# #as numpy arrays; it might be cleaner if I used PIL instead.

#Load the actual image using OpenCV
tileset_pixels = cv2.imread(tilefile.name)

#Slice up the image and store the slices in a dictionary relating them to tile numbers

tileset_number_to_tile_pixels = {}
for index in range(0, len(dwtiles)):
    # print(vars(dwtiles[index]))
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
    
# #tmxlib loads the tileset image vertically (in column-major order), whereas Tiled reads it horizontally (in
# #row-major order)
# #So we have to convert between the two
#
# tmx_tile_numbers = sorted(tmx_tileset_number_to_tile_pixels.keys())
# tileset_number_to_tile_pixels = {}
# nrows = dwtiles.row_count
# ncols = dwtiles.column_count
# print(tmx_tile_numbers)
# #Again, probably better done with a list comprehension, but...
# for second_index in range(0, len(tmx_tile_numbers)):
#     print("Index is", second_index)
#     print("List value is", tmx_tile_numbers[second_index])
#     x, y = divmod(tmx_tile_numbers[second_index], nrows)
#     cvt_tile_number = y * ncols + x
#     current_tile_number = tmx_tile_numbers[second_index]
#     tileset_number_to_tile_pixels[cvt_tile_number] = tmx_tileset_number_to_tile_pixels[current_tile_number]

# #Now we can load the world of Alefgard and begin classifying tiles

# for tile_key in sorted(tileset_number_to_tile_pixels):
#     print(tile_key)

alefgard_map = cv2.imread("alefgard.png")

# #Split the map into subarrays, first vertically and then horizontally

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

# #Generate the map in list form and then cast it to an array
# #The better way to do this is to use numpy's fromiter() method (np.fromiter() )
# #But this is best used with an actual function, so I'll try it when I clean this script up

map_list = []
#Make sure that the numbers in our tileset dictionary line up with the ones in dwtiles
tileset_index = sorted(tileset_number_to_tile_pixels.keys())
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

    for tileset_index in tileset_number_to_tile_pixels:
        current_tile = tileset_number_to_tile_pixels[tileset_index]
        tile_match_list = []
        if np.array_equal(map_tile, current_tile):
            tile_match_list.append(tileset_index)
            break

    if not tile_match_list:
        print("Error: tile not recognized")
        cv2.imshow("Unrecognized Tile", map_tile)
        cv2.waitKey(0)
    elif len(tile_match_list) >= 2:
        print("Error: Multiple tileset tiles match map tile")
    else:
        map_list.append(tileset_index)

oneD_map_array = np.fromiter(map_list, int)
map_array = np.reshape(oneD_map_array, (128, 128))

print(map_array)
#To create the final .tmx map, we first create a Map object
output_map = tmxlib.map.Map((128, 128), (16, 16))

#Then we add a tile layer to it. This tile layer is empty.
output_map.add_tile_layer("Generated Tile Layer")

#Next, we request the layers from the Map object. This gives us a LayerList object.
layers = output_map.layers

#The first element in the LayerList should be our TileLayer object.
output_tile_layer = layers[0]

#Now, we iterate over the map array, stuffing its value into the TileLayer object.
map_array_iterator = np.nditer(map_array, flags=["multi_index"])
while not map_array_iterator.finished:
    current_tile = map_array[map_array_iterator.multi_index]
    current_tile_image = tileset_number_to_tile_pixels[current_tile]
    # print(current_tile)
    # cv2.imshow("Writing tile...", current_tile_image)
    # cv2.waitKey(0)
    output_tile_layer[map_array_iterator.multi_index] = dwtiles[current_tile]
    map_array_iterator.iternext()

output_map.save("dragonwarriormap.tmx")