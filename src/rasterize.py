from PIL import Image, ImageDraw
import numpy as np


def to_raster(dset, bound):
    bitrange = 16777200.0  # 24 bit RGB image range 2^24
    width = dset.shape[1]
    height = dset.shape[0]
    maxval = np.max(dset)
    minval = np.min(dset)
    arr = np.zeros((height, width - 1, 4), dtype=np.uint8)
    scale = (maxval - minval) / bitrange
    dset = np.flipud(dset)
    for i, row in enumerate(arr):
        for j, val in enumerate(row):
            binr = "{0:024b}".format \
                (int((dset[i, j] - minval) / scale))
            arr[i, j, 0], arr[i, j, 1], arr[i, j, 2], arr[i, j, 3] = int(binr[0:8], 2), \
                                                                     int(binr[8:16], 2), \
                                                                     int(binr[16:24], 2), \
                                                                     255
            if dset[i, j] <= 0:
                arr[i, j, 3] = 0
    img = Image.fromarray(arr, 'RGBA')
    # RASTER|minval|maxval|TOP|BOTTOM|LEFT|RIGHT
    info = "RASTER|{}|{}|{}|{}|{}|{}xxxx".format(minval, maxval, bound["top"], bound["bottom"], bound["left"],
                                                 bound["right"])
    return add_info(img, info)


def add_info(img, info):
    draw = ImageDraw.Draw(img)
    # draw.rectangle([0, 0, width - 1, 1], fill=(0, 0, 0, 0))
    seq = 0
    for i, ch in enumerate(info):
        if (i + 1) % 3 == 0:
            blue = ord(info[i])
            green = ord(info[i - 1])
            red = ord(info[i - 2])
            x = seq
            x1 = seq + 1
            seq += 1
            alpha = 255
            draw.rectangle([x, 0, x1, 1], fill=(red, green, blue, alpha))
    return img