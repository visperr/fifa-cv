import cv2
import numpy as np

from config.scoreboard_config import SCOREBOARD_MASKS, SCOREBOARD_BOUNDS, SCOREBOARD_VISIBILITY_THRESHOLD
from models.bound_box import BoundingBox
from util.ocr_engine import ocr_reader
from util.screenlogger import logger
from vision.base_detector import BaseDetector, count_visible_pixels


class ScoreboardDetector(BaseDetector):
    def __init__(self):
        self.masks = SCOREBOARD_MASKS
        self.bounds = SCOREBOARD_BOUNDS
        self.visibility_threshold = SCOREBOARD_VISIBILITY_THRESHOLD

    def get_roi(self, frame):
        return self.bounds["full"].get_roi(frame)

    def is_visible(self, roi, debug=False):

        master_mask = np.zeros(roi.shape[:2], dtype=np.uint8)
        for mask_range in self.masks:
            current_mask = cv2.inRange(roi, mask_range[0], mask_range[1])
            master_mask = cv2.bitwise_or(master_mask, current_mask)

        num_pixels, total_pixels = count_visible_pixels(master_mask)

        is_visible = (num_pixels / total_pixels) > self.visibility_threshold

        logger.push(
            f"Scoreboard visible: {is_visible} "
            f"({round(num_pixels / total_pixels, 2) * 100}% > {self.visibility_threshold * 100}%)")

        if debug:
            height, width = master_mask.shape[:2]
            zoomed_clock_mask = cv2.resize(master_mask, (width * 1, height * 1))
            cv2.imshow("Master Mask SCOREBOARD", zoomed_clock_mask)

        return is_visible

    def extract_data(self, roi):
        home_roi = self.bounds["home_score"].get_roi(roi)
        away_roi = self.bounds["away_score"].get_roi(roi)

        logger.push("TRYING TO READ SCORES")

        rois = [home_roi, away_roi]
        scores = []
        for roi in rois:
            grey_score = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            score = ocr_reader.readtext(grey_score, allowlist='0123456789', detail=0)
            if len(score) == 0:
                scores.append(None)
            else:
                scores.append(int(score[0].strip()))
                logger.push(f"DETECTED: {scores[-1]}", 30)

        return scores