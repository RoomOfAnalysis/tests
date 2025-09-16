import sys
from typing import Any

import highdicom as hd
import numpy as np
from highdicom.utils import (
    are_plane_positions_tiled_full,
    iter_tiled_full_frame_data,
)
from PIL import Image
from pydicom import dcmread
from pydicom.datadict import get_entry, keyword_for_tag, tag_for_keyword


def concatenate_frames_by_indices(im, dim_indices, dim_values):
    """
    Concatenate frames based on dimension indices for TILED_FULL images
    """
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

        # output_image = output_image[
        #     : im.TotalPixelMatrixRows, : im.TotalPixelMatrixColumns, :
        # ]

        # Display or save this layer
        img = Image.fromarray(output_image)
        title = (
            f"Layer_{layer_idx}_{layer_value}" if layer_tag else "Single_Layer"
        )
        img.show(title=title)
        print(f"Created image for {title} with shape {output_image.shape}")


if __name__ == "__main__":
    # ds = dcmread(sys.argv[1])
    # print(ds)

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

    referenced_uids = im._get_ref_instance_uids()
    all_referenced_sops = {uids[2] for uids in referenced_uids}

    _is_tiled_full = (
        hasattr(im, "DimensionOrganizationType")
        and im.DimensionOrganizationType == "TILED_FULL"
    )

    _dim_ind_pointers = []
    func_grp_pointers = {}
    dim_ind_positions = {}
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
        dim_ind_positions = {
            dim_ind.DimensionIndexPointer: i
            for i, dim_ind in enumerate(im.DimensionIndexSequence)
        }

    sfgs = None
    first_pffgs = None
    if "SharedFunctionalGroupsSequence" in im:
        sfgs = im.SharedFunctionalGroupsSequence[0]
    if "PerFrameFunctionalGroupsSequence" in im:
        first_pffgs = im.PerFrameFunctionalGroupsSequence[0]

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

    # print("Dimension index pointers:", _dim_ind_pointers)
    # print("Functional group pointers:", func_grp_pointers)
    # print("Dimension index positions:", dim_ind_positions)
    print("Dimension indices:", dim_indices)
    print("Dimension values:", dim_values)

    # # Additional information that is not one of the indices
    # extra_collection_pointers = []
    # extra_collection_func_pointers = {}
    # extra_collection_values: dict[int, list[Any]] = {}
    # frame_references = []

    # for grp_ptr, ptr in [
    #     # # PlanePositionSequence/ImagePositionPatient
    #     # (0x0020_9113, 0x0020_0032),
    #     # # PlaneOrientationSequence/ImageOrientationPatient
    #     # (0x0020_9116, 0x0020_0037),
    #     # # PixelMeasuresSequence/PixelSpacing
    #     # (0x0028_9110, 0x0028_0030),
    #     # # PixelMeasuresSequence/SpacingBetweenSlices
    #     # (0x0028_9110, 0x0018_0088),
    #     # FrameContentSequence/StackID
    #     (0x0020_9111, 0x0020_9056),
    #     # FrameContentSequence/InStackPositionNumber
    #     (0x0020_9111, 0x0020_9057),
    # ]:
    #     if ptr in _dim_ind_pointers:
    #         # Skip if this attribute is already indexed due to being a
    #         # dimension index pointer
    #         continue

    #     found = False
    #     dim_val = None

    #     # Check whether the attribute is in the shared functional groups
    #     if sfgs is not None and grp_ptr in sfgs:
    #         grp_seq = None

    #         if grp_ptr is not None:
    #             if grp_ptr in sfgs:
    #                 grp_seq = sfgs[grp_ptr].value[0]
    #         else:
    #             grp_seq = sfgs

    #         if grp_seq is not None and ptr in grp_seq:
    #             found = True

    #             # Get the shared value
    #             dim_val = grp_seq[ptr].value

    #     # Check whether the attribute is in the first per-frame functional
    #     # group. If so, assume that it is there for all per-frame functional
    #     # groups
    #     if first_pffgs is not None and grp_ptr in first_pffgs:
    #         grp_seq = None

    #         if grp_ptr is not None:
    #             grp_seq = first_pffgs[grp_ptr].value[0]
    #         else:
    #             grp_seq = first_pffgs

    #         if grp_seq is not None and ptr in grp_seq:
    #             found = True

    #     if found:
    #         extra_collection_pointers.append(ptr)
    #         extra_collection_func_pointers[ptr] = grp_ptr
    #         if dim_val is not None:
    #             # Use the shared value for all frames
    #             extra_collection_values[ptr] = [dim_val] * im.number_of_frames
    #         else:
    #             # Values will be collected later in loop through per-frame
    #             # functional groups
    #             extra_collection_values[ptr] = []

    # print("Extra collection pointers:", extra_collection_pointers)
    # print("Extra collection func pointers:", extra_collection_func_pointers)
    # print("Extra collection values:", extra_collection_values)
    # print("Frame references:", frame_references)

    # # Get the shared orientation
    # shared_image_orientation: list[float] | None = None
    # if hasattr(im, "ImageOrientationSlide"):
    #     shared_image_orientation = im.ImageOrientationSlide

    if _is_tiled_full:
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

        if (
            hasattr(im, "SegmentSequence")
            and im.SegmentationType != "LABELMAP"
        ):
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
    print("Dimension indices:", dim_indices)
    print("Dimension values:", dim_values)

    # concatenate_frames_by_indices(im, dim_indices, dim_values)
