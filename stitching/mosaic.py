import os
import sys
import getopt
import random

vipsbin = os.path.join(os.getcwd(), r'vips-dev-8.16\bin')
# print(vipsbin)
# add_dll_dir = getattr(os, 'add_dll_directory', None)
# if callable(add_dll_dir):
#     add_dll_dir(vipsbin)
# else:
#     os.environ['PATH'] = os.pathsep.join((vipsbin, os.environ['PATH']))
# import cffi
# print(cffi.FFI().dlopen('libvips-42.dll'))

os.environ['PATH'] = os.pathsep.join((vipsbin, os.environ['PATH']))
import pyvips

# | YYYY_XXXX |           |           |     |
# |-----------|-----------|-----------|-----|
# | 0000_0000 | 0000_0001 | 0000_0002 | ... |
# | 0001_0000 | 0001_0001 | 0001_0002 | ... |
# | 0002_0000 | 0002_0001 | 0002_0002 | ... |
# | 0003_0000 | 0003_0001 | 0003_0002 | ... |

argv = sys.argv[1:]

options = "i:o:x:y:d:v"
longoptions = ["help", "in=", "out=", "xsize=", "ysize=", "dpi=", "verbose"]
helptext = [
    "--help or -h: Print this help list.", 
    "--in or -i: Specify file input folder.", 
    "--out or -o: Specify output file location.",
    "--xsize or -x: Specify tile grid size in the X direction.",
    "--ysize or -y: Specify tile grid size in the Y direction.",
    "--dpi or -d: Specify output image DPI (does not affect pixel size)."
    "--verbose or -v: Write debug info to console during operation.",
    "If there are not enough images available to reach the desired grid size,",
    "random tiles will be selected from the set to pad the input image list."
    ]

try:
    opts, args = getopt.getopt(argv, options, longoptions)
    
except:
    print("Couldn't parse arguments; try again.")

# defaults
INPUT_PATH = os.getcwd()+"\\input\\"
OUTPUT_PATH = os.getcwd()+"\\output\\output.png"
GRIDSIZE_X = 0
GRIDSIZE_Y = 0
DPI = 300
DEBUGLOG = False
RANDOMIZE = False
SEED = random.random()
OUTPUT_WIDTH = 2048

if not opts:
    sys.exit("Not enough arguments! Use --help for help.")

for opt, arg in opts:
    if opt in ['--help']:
        for i in helptext:
            print(i)
        sys.exit()
    elif opt in ['-i', '--in']: # input folder
        INPUT_PATH = arg
    elif opt in ['-o', '--out']: # output file
        OUTPUT_PATH = arg
    elif opt in ['-x', '--xsize']:
        GRIDSIZE_X = int(arg)
    elif opt in ['-y', '--ysize']:
        GRIDSIZE_Y = int(arg)
    elif opt in ['-d', '--dpi']:
        DPI = int(arg)
    elif opt in ['-v', '--verbose']:
        DEBUGLOG = True
    else:
        sys.exit("Not enough arguments! Use --help for help.")

if GRIDSIZE_X == 0 or GRIDSIZE_Y == 0:
    try:
        for f in os.listdir(INPUT_PATH):
            if f.endswith(".jpg"):
                GRIDSIZE_Y = max(int(f[:4]), GRIDSIZE_Y)
                GRIDSIZE_X = max(int(f[5:9]), GRIDSIZE_X)
    except:
        GRIDSIZE_Y = 0
        GRIDSIZE_X = 0
    if GRIDSIZE_X == 0 or GRIDSIZE_Y == 0:
        sys.exit("Grid size cannot be 0; use --xsize [int] and --ysize [int] to specify tile grid dimensions.")
# start from 0
GRIDSIZE_X += 1
GRIDSIZE_Y += 1
print(f'GridSize: rows: {GRIDSIZE_Y}, cols: {GRIDSIZE_X}')


input_filenames = []
for y in range(GRIDSIZE_Y):
    for x in range(GRIDSIZE_X):
        input_filenames.append(f'{y:0>4}_{x:0>4}.jpg')


def pad_image_list(input_list, newsize):
    image_count = len(input_list)
    add_count = newsize - image_count
    statistics_list = []

    # initialize statistics list to make sure percentages add up to 100%
    for i in range(0, image_count):
        statistics_list.append(i)

    for i in range(0, add_count):
        pick = i % image_count
        input_list.append(input_list[pick])
        statistics_list.append(pick)

    print(f"Padded list from {image_count} to {len(input_list)} items.")
    for variant in range(0, image_count):
        count = statistics_list.count(variant)
        print(f"Tile {variant} occured {count} times in list ({round((count/newsize)*100, 1)}% of total)")

    return input_list


# simple stitching
def merge_images(filelist, gridsize_x, gridsize_y):
    image_objects = [pyvips.Image.thumbnail(os.path.join(INPUT_PATH, filename), 100) for filename in filelist]

    if (gridsize_x * gridsize_y) > len(image_objects):
        print(f"Expected {gridsize_x * gridsize_y} images while {len(image_objects)} were provided!")
        image_objects = pad_image_list(image_objects, (gridsize_x * gridsize_y))

    image_index = 0
    merged = None
    for _ in range(0, gridsize_y):
        merged_row = None
        for _ in range(0, gridsize_x):
            # up left - 0, 0
            merged_row = image_objects[image_index] if not merged_row else merged_row.join(image_objects[image_index], "horizontal")
            image_index += 1
        merged = merged_row if not merged else merged.join(merged_row, "vertical")
    merged = merged.resize(2048 / merged.width)
    merged.write_to_file(OUTPUT_PATH)


# https://github.com/libvips/libvips/issues/2600#issuecomment-1000805038
# can not use thumnail due to the error `VipsJpeg: out of order read at line 308`
# https://libvips.github.io/pyvips/vimage.html#pyvips.Image.mosaic
def mosaic_images(filelist, gridsize_x, gridsize_y):
    image_objects = [pyvips.Image.new_from_file(os.path.join(INPUT_PATH, filename)).resize(0.3) for filename in filelist]

    if (gridsize_x * gridsize_y) > len(image_objects):
        print(f"Expected {gridsize_x * gridsize_y} images while {len(image_objects)} were provided!")
        image_objects = pad_image_list(image_objects, (gridsize_x * gridsize_y))

    image_width = image_objects[0].width
    image_height = image_objects[0].height

    image_index = 0
    mosaic = None
    overlap = 0.2
    for y in range(0, gridsize_y):
        mosaic_row = None
        for _ in range(0, gridsize_x):
            # up left - 0, 0
            mosaic_row = image_objects[image_index] if not mosaic_row else mosaic_row.mosaic(image_objects[image_index], "horizontal", 0, 0, (1 - overlap) * image_width, 0)
            image_index += 1
        mosaic = mosaic_row if not mosaic else mosaic.mosaic(mosaic_row, "vertical", 0, 0, 0, (1 - overlap) * image_height)
        print(f'row {y}')
        mosaic.write_to_file(os.getcwd()+f'\\output\\row_{y}.png')
    #mosaic = mosaic.globalbalance()
    mosaic = mosaic.resize(2048 / mosaic.width)
    mosaic.write_to_file(OUTPUT_PATH)

#merge_images(input_filenames, GRIDSIZE_X, GRIDSIZE_Y)
mosaic_images(input_filenames, GRIDSIZE_X, GRIDSIZE_Y)
print("done")
