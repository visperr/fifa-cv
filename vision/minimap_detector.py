import cv2
import numpy as np

from config.minimap_config import *
from models.bound_box import BoundingBox
from util.ocr_engine import ocr_reader
from util.screenlogger import logger
from vision.base_detector import BaseDetector, count_visible_pixels


class MinimapDetector(BaseDetector):
    def __init__(self):
        self.bounds = MINIMAP_BOUNDS
        self.masks = MINIMAP_MASKS
        self.visibility_threshold = MINIMAP_VISIBILITY_THRESHOLD

    def get_roi(self, frame):
        return self.bounds["full"].get_roi(frame)

    def is_visible(self, roi, debug=False):
        bottom_roi = self.bounds["line_bottom"].get_roi(roi)
        bottom_mask = np.zeros(bottom_roi.shape[:2], dtype=np.uint8)
        for mask_range in self.masks["line_bottom"]:
            current_mask = cv2.inRange(bottom_roi, mask_range[0], mask_range[1])
            bottom_mask = cv2.bitwise_or(bottom_mask, current_mask)

        if debug:
            height, width = bottom_mask.shape[:2]
            zoomed_minimap_mask = cv2.resize(bottom_mask, (width * 3, height * 3))
            cv2.imshow("Minimap bottom row", zoomed_minimap_mask)

        num_pixels, total_pixels = count_visible_pixels(bottom_mask)

        sidelines = [self.bounds["line_l"].get_roi(roi), self.bounds["line_r"].get_roi(roi)]
        for i, line_roi in enumerate(sidelines):
            side_mask = cv2.inRange(line_roi, self.masks["line_side"][0], self.masks["line_side"][1])

            if debug:
                height, width = line_roi.shape[:2]
                zoomed_minimap_mask = cv2.resize(side_mask, (width * 3, height * 3))
                cv2.imshow(f"Minimap side row {i}", zoomed_minimap_mask)

            side_pixels, side_total_pixels = count_visible_pixels(side_mask)

            num_pixels += side_pixels
            total_pixels += side_total_pixels

        threshold = self.visibility_threshold
        is_visible = num_pixels / total_pixels > threshold

        logger.push(
            f"Minimap visible: {is_visible} ({round(num_pixels / total_pixels, 2) * 100}% > {threshold * 100}%)")

        return is_visible

    def extract_data(self, roi):
        return {
            "ball": self._get_ball(roi),
            "team": self._get_team(roi),
            "controlled": self._get_controlled(roi),
            "opponents": self._get_opponents(roi),
        }

    def _get_ball(self, roi, debug=False):
        mask_range = self.masks["ball"]
        mask = cv2.inRange(roi, mask_range[0], mask_range[1])

        kernel = np.ones((3, 3), np.uint8)
        clean_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        MIN_AREA = 10
        MAX_AREA = 30

        best_candidate = None
        best_aspect_diff = float('inf')

        if debug: canv = cv2.cvtColor(clean_mask, cv2.COLOR_GRAY2BGR)

        for cnt in contours:
            area = cv2.contourArea(cnt)

            # 1. The Size Test
            if MIN_AREA <= area <= MAX_AREA:
                x, y, bw, bh = cv2.boundingRect(cnt)

                if debug:
                    cv2.rectangle(canv, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
                    cv2.putText(canv, f"Area {area}", (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 255, 0), 1)

                # 2. The Aspect Ratio Test (Width divided by Height)
                # A perfect square is 1.0. We allow a little bit of stretch (0.7 to 1.3)
                aspect_ratio = float(bw) / float(bh)

                if 0.7 < aspect_ratio < 1.3:

                    # 3. The Solidity Test (Contour Area divided by Bounding Hull Area)
                    hull = cv2.convexHull(cnt)
                    hull_area = cv2.contourArea(hull)

                    if hull_area > 0:
                        solidity = float(area) / hull_area

                        # A cross has missing corners, so it shouldn't be a solid 1.0 block!
                        if 0.35 < solidity < 0.85:

                            # If multiple blobs pass all tests, we mathematically pick the
                            # one that is closest to a perfect square (aspect ratio of 1.0)
                            diff = abs(1.0 - aspect_ratio)
                            if diff < best_aspect_diff:
                                best_aspect_diff = diff
                                best_candidate = (x, y, bw, bh)

        if debug:
            if best_candidate is not None:
                (x, y, bw, bh) = best_candidate
                cv2.rectangle(canv, (x, y), (x + bw, y + bh), (0, 0, 255), 3)

            height, width = canv.shape[:2]
            zoomed_canv = cv2.resize(canv, (width * 3, height * 3))
            cv2.imshow("BALL detector", zoomed_canv)

        return best_candidate

    def _get_team(self, roi, debug=False):
        mask_range = self.masks["team"]
        mask = cv2.inRange(roi, mask_range[0], mask_range[1])

        kernel = np.ones((3, 3), np.uint8)
        clean_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if debug: canv = cv2.cvtColor(clean_mask, cv2.COLOR_GRAY2BGR)

        team_coords = []
        for cnt in contours:
            contour_area = cv2.contourArea(cnt)

            # 3. Basic size check (tune these to your minimap size)
            if 2 < contour_area < 30:
                x, y, w, h = cv2.boundingRect(cnt)

                if debug: cv2.rectangle(canv, (x, y), (x + w, y + h), (0, 0, 255), 1)

                # 4. The Extent Test
                bounding_box_area = w * h
                extent = float(contour_area) / bounding_box_area

                # A solid circle/triangle usually has an extent above 0.25
                if extent > 0.25:
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        centre_x = int(M["m10"] / M["m00"])
                        centre_y = int(M["m01"] / M["m00"])

                        team_coords.append((centre_x, centre_y))

                        if debug: cv2.rectangle(canv, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if debug:
            height, width = canv.shape[:2]
            zoomed_canv = cv2.resize(canv, (width * 3, height * 3))
            cv2.imshow("Team Tracker Debug", zoomed_canv)

        return team_coords

    def _get_controlled(self, roi, debug=False):
        mask_range = self.masks["controlled"]
        mask = cv2.inRange(roi, mask_range[0], mask_range[1])

        kernel = np.ones((3, 3), np.uint8)
        clean_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if debug: canv = cv2.cvtColor(clean_mask, cv2.COLOR_GRAY2BGR)

        for cnt in contours:
            contour_area = cv2.contourArea(cnt)

            # 3. Basic size check
            if 2 < contour_area < 40:
                x, y, w, h = cv2.boundingRect(cnt)

                if debug: cv2.rectangle(canv, (x, y), (x + w, y + h), (0, 0, 255), 1)

                # 4. The Extent Test (Area of contour / Area of bounding box)
                bounding_box_area = w * h
                extent = float(contour_area) / bounding_box_area

                # If it's a solid shape (extent > 0.25), we have found our player!
                if extent > 0.25:
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        centre_x = int(M["m10"] / M["m00"])
                        centre_y = int(M["m01"] / M["m00"])

                        if debug:
                            cv2.rectangle(canv, (x, y), (x + w, y + h), (0, 255, 0), 2)

                            height, width = canv.shape[:2]
                            zoomed_canv = cv2.resize(canv, (width * 3, height * 3))
                            cv2.imshow("Controlled Player Debug", zoomed_canv)

                        # Return the very first one that passes all the maths
                        return centre_x, centre_y

        if debug:
            height, width = canv.shape[:2]
            zoomed_canv = cv2.resize(canv, (width * 3, height * 3))
            cv2.imshow("Controlled Player Debug", zoomed_canv)

        return None

    def _get_opponents(self, roi, debug=False):
        mask_range = self.masks["opponents"]
        mask = cv2.inRange(roi, mask_range[0], mask_range[1])

        kernel = np.ones((3, 3), np.uint8)
        clean_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if debug:
            canv = cv2.cvtColor(clean_mask, cv2.COLOR_GRAY2BGR)

        opponent_data = []

        for cnt in contours:
            area = cv2.contourArea(cnt)

            if debug:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(canv, (x, y), (x + w, y + h), (0, 255, 255), 1)

            # 3. Size check (tune these to your minimap size)
            if 10 < area < 75:
                x, y, w, h = cv2.boundingRect(cnt)

                if debug: cv2.rectangle(canv, (x, y), (x + w, y + h), (0, 0, 255), 1)

                # 4. The Circularity Test!
                # We measure the perimeter to see how perfectly round the blob is
                perimeter = cv2.arcLength(cnt, True)

                # Prevent the script from crashing if the blob is just a single dot!
                if perimeter == 0:
                    continue

                # The magic maths formula for a perfect circle
                circularity = 4 * np.pi * (area / (perimeter * perimeter))

                # A perfect circle is 1.0. Squares sit around 0.78.
                # We allow a little wiggle room (0.75 to 1.2) for blurry pixels!
                if debug: cv2.putText(canv, f"Circularity {round(circularity, 2)}",
                                      (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 0, 255), 1)

                if 0.75 < circularity <= 1.2:
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        centre_x = int(M["m10"] / M["m00"])
                        centre_y = int(M["m01"] / M["m00"])

                        # We estimate the radius (half the width) so it perfectly
                        # matches the output format of your old HoughCircles code!
                        radius = int(w / 2)
                        opponent_data.append((int(centre_x), int(centre_y), int(radius)))

                        # Draw the accepted, mathematically perfect circles in green!
                        if debug: cv2.circle(canv, (centre_x, centre_y), radius, (0, 255, 0), 2)

        if debug:
            height, width = canv.shape[:2]
            zoomed_canv = cv2.resize(canv, (width * 3, height * 3))
            cv2.imshow("Opponent Tracker Debug", zoomed_canv)

        return opponent_data

