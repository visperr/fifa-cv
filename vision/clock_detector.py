import cv2
import numpy as np

from config.clock_config import CLOCK_BOUNDS, CLOCK_MASKS, CLOCK_VISIBILITY_THRESHOLD
from models.bound_box import BoundingBox
from util.ocr_engine import ocr_reader
from util.screenlogger import logger
from vision.base_detector import BaseDetector, count_visible_pixels


class ClockDetector(BaseDetector):
    def __init__(self):

        self.bounds = CLOCK_BOUNDS
        self.masks = CLOCK_MASKS
        self.visibility_threshold = CLOCK_VISIBILITY_THRESHOLD

    def get_roi(self, frame):
        return self.bounds.get_roi(frame)

    def is_visible(self, roi, debug=False):
        master_mask = np.zeros(roi.shape[:2], dtype=np.uint8)

        for mask_range in self.masks:
            current_mask = cv2.inRange(roi, mask_range[0], mask_range[1])
            master_mask = cv2.bitwise_or(master_mask, current_mask)

        num_pixels, total_pixels = count_visible_pixels(master_mask)
        is_visible = (num_pixels / total_pixels) > self.visibility_threshold

        logger.push(f"Clock visible: {is_visible} "
                    f"({round(num_pixels / total_pixels, 2) * 100}% > {self.visibility_threshold * 100}%)")

        if debug:
            height, width = master_mask.shape[:2]
            zoomed_clock_mask = cv2.resize(master_mask, (width * 3, height * 3))
            cv2.imshow("Master Mask CLOCK", zoomed_clock_mask)

        return is_visible

    def extract_data(self, roi):
        grey_clock = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        results = ocr_reader.readtext(grey_clock, allowlist='0123456789:', detail=0)

        if len(results) > 0:
            return results[0].strip()
        return -1
