import sys

from wsidicom import WsiDicom

slide = WsiDicom.open(sys.argv[1])
print(slide.metadata)
print(slide.size)
print(slide.tile_size)
print(slide.uids)
print(slide.levels)

# though the slide has 3 focal planes, only one pyramid is created for the focal plane 0
# which means the slide is NOT standard conformant!
print("Number of pyramids:", len(slide._pyramids))
print(
    "Level dimensions according to wsidicom:",
    tuple((lvl.size.width, lvl.size.height) for lvl in slide.levels),
)

# slide.read_label().show()
# slide.read_overview().show()
# slide.read_thumbnail().show()

w, h = slide.size.width, slide.size.height

region = slide.read_region((w // 2, h // 2), 0, (w // 4, h // 4))
region.show()
