import sys

import highdicom as hd
import numpy as np
from highdicom.utils import iter_tiled_full_frame_data
from PIL import Image
from pydicom import dcmread

if __name__ == "__main__":
    ds = dcmread(sys.argv[1])
    print(ds)

    # https://highdicom.readthedocs.io/en/latest/image.html#accessing-total-pixel-matrices
    im = hd.imread(sys.argv[1], lazy_frame_retrieval=True)
    # https://highdicom.readthedocs.io/en/latest/package.html#highdicom.Image
    # print(im.file_meta)
    print(
        im.TotalPixelMatrixRows,
        im.TotalPixelMatrixColumns,
        im.Rows,
        im.Columns,
        im.number_of_frames,
        im.TotalPixelMatrixFocalPlanes,
    )

    LAYERS = im.TotalPixelMatrixFocalPlanes or 3

    print(f"is_tiled: {im.is_tiled}")
    print(
        f"is_indexable_as_total_pixel_matrix: {im.is_indexable_as_total_pixel_matrix()}"
    )
    print(
        f"are_dimension_indices_unique: {im.are_dimension_indices_unique(im.dimension_index_pointers)}"
    )
    print(im.dimension_index_pointers)
    print(im.DimensionOrganizationType)
    print(im.DimensionIndexSequence)
    # https://dicom.innolitics.com/ciods/parametric-map/multi-frame-dimension/00209222/00209167
    print(
        im.DimensionIndexSequence[0][0x0020, 0x9421],
        im.DimensionIndexSequence[1][0x0020, 0x9421],
    )
    dim_ind_positions = {
        dim_ind.DimensionIndexPointer: i
        for i, dim_ind in enumerate(im.DimensionIndexSequence)
    }
    print(dim_ind_positions)

    print(f"Total frames: {im.number_of_frames}")
    print(f"Frame size: {im.Rows} x {im.Columns}")
    print(
        f"Total matrix size: {im.TotalPixelMatrixRows} x {im.TotalPixelMatrixColumns}"
    )
    # im._build_luts()
    # print(im._dim_ind_col_names)

    # https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.17.3.html
    # C.7.6.17.3 Spatial Location and Optical Path of Tiled Images
    #     If Dimension Organization Type (0020,9311) is present with a Value of TILED_FULL, then the Per-Frame Functional Group Macros that would otherwise describe the spatial location of each tile explicitly (e.g., the X, Y and Z offsets from the origin in the Slide Coordinate System Plane Position (Slide)), and the optical path or segment, may be omitted.
    #     A Value of TILED_FULL indicates that the Frames across all Instances of a Concatenation, or a single Instance in the absence of a Concatenation, comprise a non-sparse non-overlapping representation of an entire rectangular region, and are sequentially encoded as successive Frames in Pixel Data (7FE0,0010) in an implicit order varying:
    #         - first along the row direction from left to right, where the row direction is defined in the Slide Coordinate System by the first three Values of Image Orientation (Slide) (0048,0102),
    #         - then along the column direction from top to bottom, where the column direction is defined in the Slide Coordinate System by the second three Values of Image Orientation (Slide) (0048,0102),
    #         - then along the depth direction from the glass slide towards the coverslip, where the depth direction is defined in the Slide Coordinate System from zero to positive,
    #         - then along optical paths, if applicable, where the direction is defined by successive Items of the Optical Path Sequence (0048,0105) in the order in which they are listed in that Sequence,
    #         - then along the segments, if applicable, where the direction is defined by ascending numeric Values of Segment Number (0062,0004) as defined in the Segment Sequence (0062,0002).
    #     If Dimension Organization Type (0020,9311) is absent or has a Value of TILED_SPARSE, then the location of each tile is explicitly encoded using information in the Per-Frame Functional Groups Sequence, and the recipient shall not make any assumption about the spatial position or optical path or segment or order of the encoded Frames, and whether or not any tiles overlap, but shall rely on the values of the relevant Per-Frame Functional Group Macro.
    #     Note
    #         Images with an Image Type (0008,0008) Value 3 of THUMBNAIL, LABEL or OVERVIEW are single Frame and may have a spatial extent that is not the same as the Total Pixel Matrix, so Dimension Organization Type (0020,9311) is not applicable.
    #         The same previously applied to images with an Image Type (0008,0008) Value 3 of LOCALIZER, which has been retired. See PS3.3-2021c.

    assert im.DimensionOrganizationType == "TILED_FULL" and im.is_tiled

    # # RuntimeError: The chosen dimensions do not uniquely identify frames of the image. You may need to provide further dimensions or a filter to disambiguate.
    # pm = im.get_total_pixel_matrix()

    for frame_data in iter_tiled_full_frame_data(im):
        # channel: Union[int, None]
        #     1-based integer index of the "channel". The meaning of "channel"
        #     depends on the image type. For segmentation images, the channel is the
        #     segment number. For other images, it is the optical path number. For
        #     Segmentations of SegmentationType "LABELMAP", the returned value will
        #     be None for all frames.
        # focal_plane_index: int
        #     1-based integer index of the focal plane.
        # column_position: int
        #     1-based column position of the tile (measured left from the left side
        #     of the total pixel matrix).
        # row_position: int
        #     1-based row position of the tile (measured down from the top of the
        #     total pixel matrix).
        # x: float
        #     X coordinate in the frame-of-reference coordinate system in millimeter
        #     units.
        # y: float
        #     Y coordinate in the frame-of-reference coordinate system in millimeter
        #     units.
        # z: float
        #     Z coordinate in the frame-of-reference coordinate system in millimeter
        #     units.
        print(frame_data)

    # # Get each frame and place it in the correct position
    # frames_per_layer = im.number_of_frames // LAYERS

    # # work for 3, 4, 5, 6
    # frames_per_col = int(
    #     np.ceil(
    #         max(im.TotalPixelMatrixRows, im.TotalPixelMatrixColumns)
    #         / min(im.Rows, im.Columns)
    #     )
    # )
    # frames_per_row = frames_per_col * LAYERS

    # print(
    #     f"Frames per layer: {frames_per_layer} ({frames_per_row} x {frames_per_col})"
    # )
    # for i in range(1):
    #     merged_image = np.zeros(
    #         (im.Rows * frames_per_row, im.Columns * frames_per_col, 3),
    #         dtype=np.uint8,
    #     )
    #     print(f"Merged image shape: {merged_image.shape}")
    #     for j in range(frames_per_layer):
    #         frame = im.get_frame(
    #             i * frames_per_layer + j + 1,
    #             dtype=np.uint8,
    #             apply_icc_profile=False,
    #         )
    #         r = j // frames_per_col
    #         c = j % frames_per_col
    #         # print(f"Frame {i * frames_per_layer + j + 1} at ({r}, {c})")
    #         merged_image[
    #             r * im.Rows : (r + 1) * im.Rows,
    #             c * im.Columns : (c + 1) * im.Columns :,
    #         ] = frame
    #     merged_image = merged_image[
    #         : im.TotalPixelMatrixRows, : im.TotalPixelMatrixColumns, :
    #     ]
    #     img = Image.fromarray(merged_image)
    #     img.show()
