#!/usr/bin/env python3
"""
Prepare the profile avatar (noir fedora silhouette with newspaper under streetlights)
for clean, high-contrast ASCII conversion:
  1. Convert to grayscale and stretch tones
  2. Apply Difference-of-Gaussians local edge enhancement so the fedora silhouette,
     newspaper folds/text, and streetlamp posts pop clearly at ASCII resolution
  3. Apply a clean circular vignette mask onto white (255) so the portrait floats
     cleanly without a boxy background border.
"""
import os
import sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")


def prep():
    im = Image.open(INP).convert("L")
    w, h = im.size

    # Smooth fine noise while preserving edges
    smooth_im = im.filter(ImageFilter.MedianFilter(size=3))
    arr = np.array(smooth_im, dtype=np.float32)

    # Local contrast (Difference of Gaussians) to highlight fedora, newspaper text & lamps
    fine = np.array(smooth_im.filter(ImageFilter.GaussianBlur(radius=1.5)), dtype=np.float32)
    coarse = np.array(smooth_im.filter(ImageFilter.GaussianBlur(radius=10.0)), dtype=np.float32)
    dog = np.clip((coarse - fine) / 28.0, -0.5, 1.0)

    # Global tone stretch
    lo, hi = np.percentile(arr, [5, 96])
    tone = np.clip((arr - lo) / max(hi - lo, 1.0), 0.0, 1.0)

    # Brighten mid-tones slightly so misty background clears out while dark silhouette & ridges stay strong
    tone = np.power(tone, 0.72)
    enhanced = np.clip(tone - 0.55 * np.clip(dog, 0, 1), 0.0, 1.0)

    # Circular feathered mask so the portrait floats cleanly on paper background
    yy, xx = np.ogrid[:h, :w]
    cx, cy = w / 2.0, h / 2.0
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (min(w, h) * 0.47)
    mask = np.clip((1.0 - r) / 0.12, 0.0, 1.0)

    # Composite onto white (255)
    final = (enhanced * mask + 1.0 * (1.0 - mask)) * 255.0
    out_im = Image.fromarray(final.astype(np.uint8), mode="L")
    out_im.save(OUT)
    print(f"wrote {OUT} ({w}x{h})")


if __name__ == "__main__":
    prep()
