from pathlib import Path
import cv2
import numpy as np

# MINIMAP REGION
Y_START = 850
Y_END = 1040
X_START = 800
X_END = 1115


MINIMAP_LINES_MASKS = [
    # SIDE LINES
    [
        np.array([120, 175, 150]),
        np.array([175, 255, 190])
    ],
    # BOTTOM LINE
    [
        # WHITE PART
        np.array([110, 175, 120]),
        np.array([180, 255, 255]),
        # BLACK PART
        np.array([0, 0, 0]),
        np.array([20, 75, 35]),
    ]
]

BALL_MASK = [
    np.array([0, 170, 175]),
    np.array([100, 255, 255])
]

TEAM_MASK = [
    np.array([26, 0, 0]),
    np.array([132, 50, 60])
]

CONTROLLED_MASK = [
    np.array([24, 0, 69]),
    np.array([150, 50, 150])
]

OPPONENT_MASK = [
    np.array([200, 200, 200]),
    np.array([255, 255, 255])
]

def get_minimap_dims():
    return X_END - X_START, Y_END - Y_START

def get_minimap_roi(frame):
    return frame[Y_START:Y_END, X_START:X_END]

def count_visible_pixels(frame, mask):

    masked = cv2.inRange(frame, mask[0], mask[1])

    total = frame.shape[0] * frame.shape[1]
    matched = cv2.countNonZero(masked)

    return matched, total


def get_opponents(clean_roi, debug=False):
    """
    Uses your tuned BGR mask and Contour Circularity maths to find the round opponent icons!
    """
    lower_opp = OPPONENT_MASK[0]
    upper_opp = OPPONENT_MASK[1]

    mask = cv2.inRange(clean_roi, lower_opp, upper_opp)

    kernel = np.ones((2, 2), np.uint8)
    clean_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if debug:
        canv = cv2.cvtColor(clean_mask, cv2.COLOR_GRAY2BGR)

    opponent_data = []

    for cnt in contours:
        area = cv2.contourArea(cnt)

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
            if 0.75 < circularity <= 1.2:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    centre_x = int(M["m10"] / M["m00"])
                    centre_y = int(M["m01"] / M["m00"])

                    # We estimate the radius (half the width) so it perfectly
                    # matches the output format of your old HoughCircles code!
                    radius = int(w / 2)
                    opponent_data.append((centre_x, centre_y, radius))

                    # Draw the accepted, mathematically perfect circles in green!
                    if debug: cv2.circle(canv, (centre_x, centre_y), radius, (0, 255, 0), 2)

    if debug:
        height, width = canv.shape[:2]
        zoomed_canv = cv2.resize(canv, (width * 3, height * 3))
        cv2.imshow("Opponent Tracker Debug", zoomed_canv)

    return opponent_data


def get_ball(clean_roi, debug=False):
    lower_orange = BALL_MASK[0]
    upper_orange = BALL_MASK[1]

    mask = cv2.inRange(clean_roi, lower_orange, upper_orange)

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

    # Returns the absolute best match, or None if the ball is covered up by players

    if debug:
        if best_candidate is not None:
            (x, y, bw, bh) = best_candidate
            cv2.rectangle(canv, (x, y), (x + bw, y + bh), (0, 0, 255), 3)

            # Zoom it in a bit so you don't have to squint at the tiny numbers
        height, width = canv.shape[:2]
        zoomed_canv = cv2.resize(canv, (width * 3, height * 3))
        cv2.imshow("BALL thingy", zoomed_canv)

    return best_candidate


def get_team(clean_roi, debug=False):
    """
    Finds your players using your tuned BGR colour and the 'Extent' property,
    completely ignoring blurry noise.
    """
    lower_team = TEAM_MASK[0]
    upper_team = TEAM_MASK[1]

    mask = cv2.inRange(clean_roi, lower_team, upper_team)

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


def get_controlled_player(clean_roi, debug=False):
    """
    Finds your currently controlled player using tuned BGR colours and the 'Extent' property.
    Draws a visual debug canvas so you can see exactly what it is testing.
    """

    lower_controlled = CONTROLLED_MASK[0]
    upper_controlled = CONTROLLED_MASK[1]

    mask = cv2.inRange(clean_roi, lower_controlled, upper_controlled)

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


def minimap_visible(roi):
    pass