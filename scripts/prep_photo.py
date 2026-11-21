#!/usr/bin/env python3
"""
Prepare the current GitHub profile avatar (AHMED BG Crown Emblem)
for clean, high-contrast monochrome ASCII conversion:
  1. Load source-photo.png (dark background with bright crown & AHMED BG emblem)
  2. Invert luminance so the dark background becomes pure white (blank space in ASCII)
     and the bright crown + AHMED BG lettering become dark ink (dense ASCII chars)
  3. Apply local contrast & morphological sharpening so both the crown geometry and
     the "AHMED BG" typography read clearly at ASCII resolution.
"""
import os
import sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")


def prep():
    im_rgb = Image.open(INP).convert("RGB")
    w, h = im_rgb.size
    rgb = np.array(im_rgb, dtype=np.float32) / 255.0
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]

    # Perceived brightness of the emblem on dark background
    lum = 0.299 * r + 0.587 * g + 0.114 * b

    # Circular mask to remove outer background diagonal stripes
    yy, xx = np.ogrid[:h, :w]
    cx, cy = w / 2.0, h / 2.0
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (min(w, h) * 0.46)
    circle_mask = np.clip((1.0 - dist) / 0.06, 0.0, 1.0)

    # Clear out dark background (< 0.17) to 0, keep bright crown & text
    fg = np.where(lum < 0.17, 0.0, lum) * circle_mask

    # Stretch foreground brightness to [0, 1]
    fg = np.clip((fg - 0.12) / 0.78, 0.0, 1.0)

    # Invert so foreground emblem is dark ink (0.0) on white paper (1.0)
    paper = 1.0 - fg

    # Enhance edges slightly for crisp ASCII characters
    out_im = Image.fromarray((paper * 255.0).astype(np.uint8), mode="L")
    out_im = out_im.filter(ImageFilter.SHARPEN)
    out_im.save(OUT)
    print(f"wrote {OUT} ({w}x{h})")


if __name__ == "__main__":
    prep()
