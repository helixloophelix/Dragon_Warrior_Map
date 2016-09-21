#! /usr/bin/env python

import tmxlib
import cv2
import numpy as np
from PIL import Image

#Open up the tileset
tilefile = open("dragonwarriortiles.png")

dwtileimage = tmxlib.image.open(tilefile.name)
dwtiles = tmxlib.tileset.ImageTileset("dragonwarriortiles", (16, 16), dwtileimage)

# #tmxlib loads the tileset image vertically (in column-major order), whereas Tiled reads it horizontally (in
# #row-major order).
# #So we have to convert between the two when writing the array of matched tiles.

nrows = dwtiles.row_count
ncols = dwtiles.column_count

conversion_table = {}
for index in range(0, len(dwtiles)):
    x, y = divmod(index, nrows)
    cvt_number = y * ncols + x
    conversion_table[cvt_number] = dwtiles[index]

# #tmxlib has effectively no support for actually displaying tiles, so we're going to use OpenCV to cut them out
# #as numpy arrays; it might be cleaner if I used PIL instead.

#Load the actual image using OpenCV
tileset_pixels = cv2.imread(tilefile.name)

#Slice up the image and store the slices in a dictionary relating them to tile numbers

tileset_number_to_tile_pixels = {}
for index in range(0, len(dwtiles)):
    #Use the ImageRegion information to get the coordinates for each slice
    image_region = dwtiles.tile_image(index) 
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
#The use of np.hsplit and np.vsplit relies on the squareness of the map, and consequently the map height and width
#are presently hard-coded. This will need to be fixed if the script is to be generalized; maybe use PIL to do it.

alefgard_array_list = []
horizontal_split = np.hsplit(alefgard_map, 128)
for hsclice in horizontal_split:
    vertical_split = np.vsplit(hsclice, 128)
    alefgard_array_list = alefgard_array_list + vertical_split

#Generate the map in list form and then cast it to an array
#The better way to do this is to use numpy's fromiter() method (np.fromiter() )
#But this is best used with an actual function...

map_list = []
#Make sure that the numbers in our tileset dictionary line up with the ones in dwtiles
tileset_index = sorted(tileset_number_to_tile_pixels.keys())
for map_tile in alefgard_array_list:
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
    #Owing to the earlier problem regarding the way tmxlib reads tileset images vs. the way Tiled reads images,
    #we have to send the map_array values through the conversion table in order to write a tmx file that
    #Tiled can interpret correctly.
    #This means that, technically, the tile written in the tmx file is NOT the matched one, but rather its 
    #column-major to row-major counterpart. However, because Tiled apparently has no idea what the image properties
    #of each tile are, it probably doesn't matter.
    converted_tile = conversion_table[current_tile]
    output_tile_layer[map_array_iterator.multi_index] = converted_tile
    map_array_iterator.iternext()

output_map.save("dragonwarriormap.tmx")