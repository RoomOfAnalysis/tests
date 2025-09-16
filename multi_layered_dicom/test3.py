import sys
from typing import Any

import highdicom as hd
import numpy as np
from highdicom.utils import iter_tiled_full_frame_data
from PIL import Image
from pydicom.datadict import keyword_for_tag, tag_for_keyword


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
def concatenate_frames_by_indices(im):
    """
    Concatenate frames based on dimension indices for TILED_FULL images
    """

    filename = (
        im._file_reader._filename
        if hasattr(im, "_file_reader")
        and hasattr(im._file_reader, "_filename")
        else None
    )

    _is_tiled_full = (
        hasattr(im, "DimensionOrganizationType")
        and im.DimensionOrganizationType == "TILED_FULL"
    )
    assert _is_tiled_full

    _dim_ind_pointers = []
    func_grp_pointers = {}
    if "DimensionIndexSequence" in im:
        _dim_ind_pointers = [
            dim_ind.DimensionIndexPointer
            for dim_ind in im.DimensionIndexSequence
        ]
        for dim_ind in im.DimensionIndexSequence:
            ptr = dim_ind.DimensionIndexPointer
            if ptr in _dim_ind_pointers:
                grp_ptr = getattr(dim_ind, "FunctionalGroupPointer", None)
                func_grp_pointers[ptr] = grp_ptr

    sfgs = None
    if "SharedFunctionalGroupsSequence" in im:
        sfgs = im.SharedFunctionalGroupsSequence[0]

    dim_indices: dict[int, list[int]] = {ptr: [] for ptr in _dim_ind_pointers}
    dim_values: dict[int, list[Any]] = {ptr: [] for ptr in _dim_ind_pointers}

    # Check for dimension index values in the shared functional groups
    if sfgs is not None:
        for ptr in _dim_ind_pointers:
            grp_ptr = func_grp_pointers[ptr]
            dim_val = None
            if grp_ptr is not None:
                try:
                    dim_val = sfgs[grp_ptr][0][ptr].value
                except KeyError:
                    pass
            else:
                try:
                    dim_val = sfgs[ptr].value
                except KeyError:
                    pass
            if dim_val is not None:
                dim_values[ptr] = [dim_val] * im.number_of_frames

    # With TILED_FULL, there is no PerFrameFunctionalGroupsSequence,
    # so we have to deduce the per-frame information

    # (0048,021F) - RowPositionInTotalImagePixelMatrix
    # (0048,021E) - ColumnPositionInTotalImagePixelMatrix
    # 4196138 - XOffsetInSlideCoordinateSystem
    # 4196154 - YOffsetInSlideCoordinateSystem
    # 4196170 - ZOffsetInSlideCoordinateSystem
    # 4718854 - OpticalPathIdentifier

    row_tag = tag_for_keyword("RowPositionInTotalImagePixelMatrix")
    col_tag = tag_for_keyword("ColumnPositionInTotalImagePixelMatrix")
    x_tag = tag_for_keyword("XOffsetInSlideCoordinateSystem")
    y_tag = tag_for_keyword("YOffsetInSlideCoordinateSystem")
    z_tag = tag_for_keyword("ZOffsetInSlideCoordinateSystem")
    tiled_full_dim_indices = {row_tag, col_tag}
    (
        channel_numbers,
        _,
        dim_values[col_tag],
        dim_values[row_tag],
        dim_values[x_tag],
        dim_values[y_tag],
        dim_values[z_tag],
    ) = zip(*iter_tiled_full_frame_data(im))

    if hasattr(im, "SegmentSequence") and im.SegmentationType != "LABELMAP":
        segment_tag = tag_for_keyword("ReferencedSegmentNumber")
        dim_values[segment_tag] = channel_numbers
        if len(im.SegmentSequence) > 1:
            tiled_full_dim_indices |= {segment_tag}
    elif hasattr(im, "OpticalPathSequence"):
        op_tag = tag_for_keyword("OpticalPathIdentifier")
        dim_values[op_tag] = channel_numbers
        if len(im.OpticalPathSequence) > 1:
            tiled_full_dim_indices |= {op_tag}

    # If the image has a dimension index sequence, enforce that it
    # contains the expected indices
    if (
        "DimensionIndexSequence" in im
        and len(tiled_full_dim_indices - set(dim_indices.keys())) > 0
    ):
        expected_str = ", ".join(
            keyword_for_tag(t) for t in tiled_full_dim_indices
        )
        raise RuntimeError(
            "Expected images with "
            '"DimensionOrganizationType" of "TILED_FULL" '
            "to have the following dimension index pointers: "
            f"{expected_str}."
        )

    # Create indices for each of the dimensions
    for ptr, vals in dim_values.items():
        _, indices = np.unique(vals, return_inverse=True)
        dim_indices[ptr] = (indices + 1).tolist()

    # print("Tiled full dimension indices: ", tiled_full_dim_indices)
    # print("Dimension indices:", dim_indices)
    # print("Dimension values:", dim_values)

    row_tag = tag_for_keyword("RowPositionInTotalImagePixelMatrix")
    col_tag = tag_for_keyword("ColumnPositionInTotalImagePixelMatrix")
    z_tag = tag_for_keyword("ZOffsetInSlideCoordinateSystem")
    op_tag = tag_for_keyword("OpticalPathIdentifier")

    # Get unique layers (Z positions or optical paths)
    if z_tag in dim_values and len(set(dim_values[z_tag])) > 1:
        layers = sorted(set(dim_values[z_tag]))
        layer_tag = z_tag
    elif op_tag in dim_values and len(set(dim_values[op_tag])) > 1:
        layers = sorted(set(dim_values[op_tag]))
        layer_tag = op_tag
    else:
        layers = [1]
        layer_tag = None

    frame_height = im.Rows
    frame_width = im.Columns

    # For each layer, create a separate image
    for layer_idx, layer_value in enumerate(layers):
        # Find frames belonging to this layer
        if layer_tag:
            frame_indices = [
                i
                for i, val in enumerate(dim_values[layer_tag])
                if val == layer_value
            ]
        else:
            frame_indices = list(range(im.number_of_frames))

        # Get max row and column indices for this layer
        layer_rows = max(dim_indices[row_tag][i] for i in frame_indices)
        layer_cols = max(dim_indices[col_tag][i] for i in frame_indices)

        print(f"Layer {layer_idx}: {layer_value}, {layer_rows} x {layer_cols}")

        # Create output image for this layer
        output_image = np.zeros(
            (layer_rows * frame_height, layer_cols * frame_width, 3),
            dtype=np.uint8,
        )

        # Place each frame in the correct position
        for frame_idx in frame_indices:
            # Get frame data
            frame = im.get_frame(
                frame_idx + 1, dtype=np.uint8, apply_icc_profile=False
            )

            # Get position indices for this frame (convert to 0-based)
            row_idx = dim_indices[row_tag][frame_idx] - 1
            col_idx = dim_indices[col_tag][frame_idx] - 1

            # Place frame in the correct position
            y_start = row_idx * frame_height
            y_end = y_start + frame_height
            x_start = col_idx * frame_width
            x_end = x_start + frame_width

            output_image[y_start:y_end, x_start:x_end] = frame

        # Display or save this layer
        img = Image.fromarray(
            output_image[
                : im.TotalPixelMatrixRows, : im.TotalPixelMatrixColumns, :
            ]
        )
        title = (
            f"{filename}-Layer_{layer_idx}_{layer_value}"
            if layer_tag
            else "Single_Layer"
        )
        img.save(f"{title}.png")
        # img.show(title=title)
        print(f"Created image for {title} with shape {output_image.shape}")


if __name__ == "__main__":
    # https://highdicom.readthedocs.io/en/latest/image.html#accessing-total-pixel-matrices
    im = hd.imread(sys.argv[1], lazy_frame_retrieval=True)

    print(
        im.TotalPixelMatrixRows,
        im.TotalPixelMatrixColumns,
        im.Rows,
        im.Columns,
        im.number_of_frames,
        im.TotalPixelMatrixFocalPlanes,
    )
    print(f"is_tiled: {im.is_tiled}")
    print(
        f"is_indexable_as_total_pixel_matrix: {im.is_indexable_as_total_pixel_matrix()}"
    )
    print(
        f"are_dimension_indices_unique: {im.are_dimension_indices_unique(im.dimension_index_pointers)}"
    )
    print(im.coordinate_system)

    concatenate_frames_by_indices(im)
