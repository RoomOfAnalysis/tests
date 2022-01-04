import argparse
import os
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='combine two image vertically')
    parser.add_argument('-i', '--input', dest='input_two_images', required=True, nargs=2, 
                        help='input two images paths')
    parser.add_argument('-o', '--output', dest='output_image', required=True, nargs=1, 
                        help='output image path')
    args = parser.parse_args()

    img1_path = os.path.abspath(args.input_two_images[0])
    img2_path = os.path.abspath(args.input_two_images[1])
    out_img_path = os.path.abspath(args.output_image[0])

    images = [Image.open(x) for x in [img1_path, img2_path]]
    widths, heights = zip(*(i.size for i in images))

    total_height = sum(heights)
    max_width = max(widths)

    new_img = Image.new('RGB', (max_width, total_height))

    offset = 0
    for im in images:
        new_img.paste(im, (0, offset))
        offset += im.size[1]

    new_img.save(out_img_path)
