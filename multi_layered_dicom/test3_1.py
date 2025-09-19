import sys
from typing import Any

import highdicom as hd
import numpy as np
from highdicom.utils import iter_tiled_full_frame_data
from PIL import Image
from pydicom.datadict import keyword_for_tag, tag_for_keyword


# this works for layer 0-2 images where its frames are interleaved
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
        layer_rows = im.TotalPixelMatrixRows // im.Rows
        layer_cols = im.TotalPixelMatrixColumns // im.Columns

        print(f"Layer {layer_idx}: {layer_value}, {layer_rows} x {layer_cols}")

        # Calculate frame indices for this specific layer
        # Frames are interleaved in groups across layers
        frame_indices = [group_start + i for group_start in range(layer_idx * layer_cols, im.number_of_frames, layer_cols * len(layers)) for i in range(layer_cols)]

        # print(frame_indices)

        # Create output image for this layer
        output_image = np.zeros(
            (layer_rows * frame_height, layer_cols * frame_width, 3),
            dtype=np.uint8,
        )

        # Place each frame in the correct position
        for idx_in_layer, frame_idx in enumerate(frame_indices):
            # Get frame data
            frame = im.get_frame(
                (frame_idx + 1), dtype=np.uint8, apply_icc_profile=False
            )

            # Calculate position in the grid (row and column in the layer matrix)
            row_idx = idx_in_layer // layer_cols
            col_idx = idx_in_layer % layer_cols
            # print(frame_idx, row_idx, col_idx)

            # Place frame in the correct position
            y_start = row_idx * frame_height
            y_end = y_start + frame_height
            x_start = col_idx * frame_width
            x_end = x_start + frame_width
            # print(y_start, y_end, x_start, x_end)
            
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
        img.save(f"{title}_corrected.png")
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
