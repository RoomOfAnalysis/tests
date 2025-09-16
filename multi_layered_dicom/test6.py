import sys
from pathlib import Path

import dicomslide
import dicomweb_client
import numpy as np
import pydicom
from matplotlib import pyplot as plt

print(Path(sys.argv[1]).absolute().as_uri())

client = dicomweb_client.DICOMfileClient(
    url=f"{Path(sys.argv[1]).absolute().as_uri()}",
    db_dir=f"{Path(__file__).parent.absolute().as_posix()}",
    # readonly=True,
)

# mannually store the dataset and revise the `_file_path` column with local file path to make it work
# dataset = pydicom.dcmread(sys.argv[1])
# client.store_instances(datasets=[dataset])
# print(client.url_prefix)

# ICC profile is None
# https://github.com/ImagingDataCommons/dicomslide/issues/8

# still have error
# ValueError: VOLUME and THUMBNAIL images for channel 0 and focal plane 0 do not represent a valid image pyramid. Images in pyramid must have unique sizes.

# if comment out all code which raised error in `dicomslide`, the following code works.
# but the volume images will be treated as a whole for `focal_plane_index = 0`,
# which means though the slide has 3 focal planes, but only one focal plane has volume images.
# the slide is NOT standard conformant!

found_slides = dicomslide.find_slides(client)
assert len(found_slides) >= 1
slide = found_slides[0]

print(slide.num_channels)
print(slide.num_focal_planes)
print(slide.num_levels)
print(slide.total_pixel_matrix_dimensions)
print(slide.downsampling_factors)
print(slide.label_images)
print(slide.get_volume_images(channel_index=0, focal_plane_index=0))

region: np.ndarray = slide.get_image_region(
    offset=(0, 0),
    level=-1,
    size=(256, 256),
    channel_index=0,
    focal_plane_index=0,
)
plt.imshow(region)
plt.show()
