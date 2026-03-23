import cv2
import easyocr
import numpy as np

from util.minimap_data import count_visible_pixels
from util.screenlogger import logger

# 1. Initialise the reader OUTSIDE your loop.
# We tell it we only want English ('en').
# gpu=False ensures it runs on your CPU, which is universally safe.
print("Loading OCR AI... (This might take a few seconds on the first run)")
reader = easyocr.Reader(['en'], gpu=True)

# CLOCK ROI
Y_START = 104
Y_END = 150
X_START = 85
X_END = 160

CLOCK_MASKS = [
    [
        np.array([220, 220, 220]),
        np.array([255, 255, 255]),
    ],
    [
        np.array([0, 0, 0]),
        np.array([30, 30, 30]),
    ]
]

def get_clock_dims():
    return X_END - X_START, Y_END - Y_START

def get_clock_roi(frame):
    return frame[Y_START:Y_END, X_START:X_END]


def get_ingame_time(clock_roi):
    """
    Reads the digital clock using a pure Python deep-learning model.
    """
    # EasyOCR is incredibly smart and often doesn't need heavy thresholding,
    # but converting to greyscale still helps it run faster!
    grey_clock = cv2.cvtColor(clock_roi, cv2.COLOR_BGR2GRAY)

    # 2. Ask EasyOCR to read the image
    # The 'allowlist' parameter forces it to ONLY look for numbers and colons
    # detail=0 tells it to just give us the text string, not the bounding box coordinates
    results = reader.readtext(grey_clock, allowlist='0123456789:', detail=0)

    # EasyOCR returns a list of found strings.
    # If the list isn't empty, we grab the first item.
    if len(results) > 0:
        return results[0].strip()
    else:
        return -1

def is_clock_visible(roi, debug=False):

    master_mask = np.zeros(roi.shape[:2], dtype=np.uint8)
    for i in range(2):
        current_mask = cv2.inRange(roi, CLOCK_MASKS[i][0], CLOCK_MASKS[i][1])
        master_mask = cv2.bitwise_or(master_mask, current_mask)

    num_pixels, total_pixels = count_visible_pixels(master_mask)

    threshold = 0.85
    is_visible = num_pixels / total_pixels > threshold

    logger.push(f"Clock visible: {is_visible} ({round(num_pixels / total_pixels, 2) * 100}% > {threshold * 100}%)")

    if debug:
        height, width = master_mask.shape[:2]
        zoomed_clock_mask = cv2.resize(master_mask, (width * 3, height * 3))
        cv2.imshow("Master Mask CLOCK", zoomed_clock_mask)

    return is_visible