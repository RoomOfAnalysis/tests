import os
import sys
import getopt
import random
from PIL import Image
import math

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
Image.MAX_IMAGE_PIXELS = 933120000
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
        input_filenames.append(f'{y:0>4}_{x:0>4}')

dx, dy = 0., 0.
with open(os.path.join(INPUT_PATH, f'{0:0>4}_{0:0>4}.txt')) as f:
    sz = [float(l) for l in f.readlines()]
    img = Image.open(os.path.join(INPUT_PATH, f'{0:0>4}_{0:0>4}.jpg'))
    w, h = img.size
    dx = w / (sz[2] - sz[0])
    dy = h / (sz[3] - sz[1])
print(dx, dy)  # pixel / um

def parse_img_and_txt(fn):
    txt_f = os.path.join(INPUT_PATH, f'{fn}.txt')
    img_f = os.path.join(INPUT_PATH, f'{fn}.jpg')
    if not os.path.exists(txt_f) or not os.path.exists(img_f):
        return None
    sx, sy = 0., 0.
    with open(txt_f) as f:
        sz = [float(l) for l in f.readlines()]
        sx = sz[0]
        sy = sz[1]
    return ((sx, sy), Image.open(img_f))


def overlap_images(filelist, gridsize_x, gridsize_y):
    image_objects = [i for i in (parse_img_and_txt(filename) for filename in filelist) if i is not None]

    if (gridsize_x * gridsize_y) > len(image_objects):
        print(f"Expected {gridsize_x * gridsize_y} images while {len(image_objects)} were provided!")
        return None

    # assuming all images have the same size
    (sx, sy), img = image_objects[0]
    (image_width, image_height) = img.size
    (sx1, sy1), _ = image_objects[-1]

    resulting_width = math.ceil((sx1 - sx) * dx + image_width)
    resulting_height = math.ceil((sy1 - sy) * dy + image_height)

    image_combined = Image.new('RGBA', (resulting_width, resulting_height))

    image_index = 0
    for y_index in range(gridsize_y):
        for x_index in range(gridsize_x):
            (sx1, sy1), img = image_objects[image_index]
            # up left - 0, 0
            xx = math.floor((sx1 - sx) * dx)
            yy = math.floor((sy1 - sy) * dy)
            img0 = image_combined.crop((xx, yy, xx + image_width, yy + image_height)).convert('RGB')
            img1 = Image.blend(img0, img, 0.5) # blending to show overlapping part
            image_combined.paste(im=img1, box=(xx, yy))
            if DEBUGLOG == True:
                print(f"X: {x_index} Y: {y_index}, index: {image_index}, image: {image_objects[image_index]}")
            image_index += 1

    return image_combined.resize((OUTPUT_WIDTH, int(resulting_height / resulting_width * OUTPUT_WIDTH)))

overlapped = overlap_images(input_filenames, GRIDSIZE_X, GRIDSIZE_Y) 
print(f"Exporting tiled image...")

overlapped.save(OUTPUT_PATH, compress_level=5, dpi=(DPI, DPI))
if os.path.exists(OUTPUT_PATH):
    print(f"Exported image with dimensions {overlapped.width}x{overlapped.height} ({round(os.stat(OUTPUT_PATH).st_size/1E6,2)}MB, {DPI}dpi) to {OUTPUT_PATH}.")
