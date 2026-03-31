import cv2
import easyocr
import numpy as np

from data.roi.minimap_data import count_visible_pixels
from util.bound_box import BoundingBox
from util.screenlogger import logger

# 1. Initialise the reader OUTSIDE your loop.
# We tell it we only want English ('en').
# gpu=False ensures it runs on your CPU, which is universally safe.
print("Loading OCR AI... (This might take a few seconds on the first run)")
reader = easyocr.Reader(['en'], gpu=True)


# SCOREBOARD ROI

regions = {
    "full": BoundingBox(700, 870, 1219, 953),
    "home_score": BoundingBox(784, 870, 867, 953),
    "away_score": BoundingBox(1052, 870, 1135, 953),
}

SCOREBOARD_MASKS = [
    [
        np.array([220, 220, 220]),
        np.array([255, 255, 255]),
    ],
    [
        np.array([0, 0, 0]),
        np.array([30, 30, 30]),
    ],
    [
        np.array([50, 45, 210]),
        np.array([90, 65, 255]),
    ]
]

def get_scoreboard_dims():
    bounds = regions["full"]
    return bounds.width, bounds.height

def get_scoreboard_roi(frame):
    bounds = regions["full"]
    return bounds.get_roi(frame)


def get_scores(frame):
    home_roi = regions["home_score"].get_roi(frame)
    away_roi = regions["away_score"].get_roi(frame)

    logger.push("TRYING TO READ SCORES")

    rois = [home_roi, away_roi]
    scores = []
    for roi in rois:
        grey_score = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        score = reader.readtext(grey_score, allowlist='0123456789', detail=0)
        if len(score) == 0:
            scores.append(None)
        else:
            scores.append(int(score[0].strip()))
            logger.push(f"DETECTED: {scores[-1]}", 30)

    return scores


def is_scoreboard_visible(frame, debug=False):

    roi = regions["full"].get_roi(frame)
    master_mask = np.zeros(roi.shape[:2], dtype=np.uint8)
    for i in range(3):
        current_mask = cv2.inRange(roi, SCOREBOARD_MASKS[i][0], SCOREBOARD_MASKS[i][1])
        master_mask = cv2.bitwise_or(master_mask, current_mask)

    num_pixels, total_pixels = count_visible_pixels(master_mask)

    threshold = 0.90
    is_visible = num_pixels / total_pixels > threshold

    logger.push(f"Scoreboard visible: {is_visible} ({round(num_pixels / total_pixels, 2) * 100}% > {threshold * 100}%)")

    if debug:
        height, width = master_mask.shape[:2]
        zoomed_clock_mask = cv2.resize(master_mask, (width * 1, height * 1))
        cv2.imshow("Master Mask SCOREBOARD", zoomed_clock_mask)

    return is_visible