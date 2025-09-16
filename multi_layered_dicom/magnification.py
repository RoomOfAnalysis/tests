import sys
import pydicom

# Load DICOM file
ds = pydicom.dcmread(sys.argv[1])

# Method 1: Calculate from pixel spacing
pixel_spacing = ds.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0].PixelSpacing
pixel_spacing_mm = float(pixel_spacing[0])
pixel_spacing_um = pixel_spacing_mm * 1000

# Assuming 0.25 μm/pixel is the reference for 40x magnification
reference_um_per_pixel_at_40x = 0.25
magnification = reference_um_per_pixel_at_40x / pixel_spacing_um * 40

# Method 2: Look for objective information in private tags
# (0009,1026) Private tag data                    SH: 'UPlanXAPO40X'
objective_magnification = ds.get((0x0009, 0x1026)).value

print(f"Magnification: {magnification:.1f}x, Objecttive Magnification: {objective_magnification}")
