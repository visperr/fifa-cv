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

def get_minimap_dims():
    return X_END - X_START, Y_END - Y_START

def get_minimap_roi(frame):
    return frame[Y_START:Y_END, X_START:X_END]

def count_visible_pixels(frame, mask):

    masked = cv2.inRange(frame, mask[0], mask[1])

    total = frame.shape[0] * frame.shape[1]
    matched = cv2.countNonZero(masked)

    return matched, total


def get_opponents(roi_frame):
    """
    Uses the Hough Gradient method to find translucent circles incredibly quickly.
    Returns the frame with circles drawn, and a list of coordinates.
    """

    # 1. Convert to grayscale (HoughCircles only works on greyscale)
    gray_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

    # 2. Add a slight blur!
    # This is CRUCIAL. It smooths out the messy grass textures bleeding through,
    # but keeps the strong geometric edges of the UI dots.
    blurred_roi = cv2.medianBlur(gray_roi, 3)

    # 3. The Mathematics: Hough Circle Transform
    circles = cv2.HoughCircles(
        blurred_roi,
        cv2.HOUGH_GRADIENT,
        dp=1.2,           # Resolution of the accumulator (1.2 is a safe standard)
        minDist=10,       # The minimum distance between two circles (stops double-counting)
        param1=50,        # Sensitivity of the internal edge detector (Canny)
        param2=20,        # The "Perfect Circle" test. Lower = finds more, Higher = stricter
        minRadius=4,      # MINIMUM size of an opponent dot in pixels
        maxRadius=8      # MAXIMUM size of an opponent dot in pixels
    )

    opponent_data = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            # Save the x, y, and radius so we can draw it later
            opponent_data.append((circle[0], circle[1], circle[2]))

    return opponent_data


def get_ball(clean_roi):
    hsv_roi = cv2.cvtColor(clean_roi, cv2.COLOR_BGR2HSV)

    lower_orange = BALL_MASK[0]
    upper_orange = BALL_MASK[1]

    mask = cv2.inRange(hsv_roi, lower_orange, upper_orange)

    kernel = np.ones((3, 3), np.uint8)

    clean_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Define your minimum and maximum pixel areas
    MIN_AREA = 25
    MAX_AREA = 75

    for cnt in contours:
        area = cv2.contourArea(cnt)

        # Check if the blob passes our size test
        if MIN_AREA <= area <= MAX_AREA:
            x, y, bw, bh = cv2.boundingRect(cnt)
            return x, y, bw, bh

    return None


def get_team(clean_roi):
    """
    Finds your players using colour and the 'Extent' property,
    completely ignoring blurry corners.
    """
    hsv_roi = cv2.cvtColor(clean_roi, cv2.COLOR_BGR2HSV)

    # 1. Your tuned colour filter for your team
    lower_team = np.array([55, 20, 20])
    upper_team = np.array([150, 200, 200])

    mask = cv2.inRange(hsv_roi, lower_team, upper_team)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    team_coords = []
    for cnt in contours:
        contour_area = cv2.contourArea(cnt)

        # 2. Basic size check (tune these to your UI)
        if 10 < contour_area < 75:

            # 3. Get the Bounding Box dimensions
            x, y, w, h = cv2.boundingRect(cnt)

            # Calculate the centre using moments
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                centre_x = int(M["m10"] / M["m00"])
                centre_y = int(M["m01"] / M["m00"])

                team_coords.append((centre_x, centre_y))

    return team_coords

def get_controlled_player(clean_roi):
    """
    Finds your players using colour and the 'Extent' property,
    completely ignoring blurry corners.
    """
    hsv_roi = cv2.cvtColor(clean_roi, cv2.COLOR_BGR2HSV)

    # 1. Your tuned colour filter for your team
    lower_team = np.array([120, 20, 20])
    upper_team = np.array([179, 200, 200])

    mask = cv2.inRange(hsv_roi, lower_team, upper_team)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        contour_area = cv2.contourArea(cnt)

        # 2. Basic size check (tune these to your UI)
        if 10 < contour_area < 75:

            # 3. Get the Bounding Box dimensions
            x, y, w, h = cv2.boundingRect(cnt)

            # Calculate the centre using moments
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                centre_x = int(M["m10"] / M["m00"])
                centre_y = int(M["m01"] / M["m00"])

                return centre_x, centre_y

    return None


def minimap_visible(roi):
    pass