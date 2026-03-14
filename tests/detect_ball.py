import cv2

from util.find_opponents import get_minimap_roi, interactive_extent_debugger


def test_detect_ball():
    img = cv2.imread("minimap/minimap_visible_1.png")
    roi = get_minimap_roi(img)

    # test_detect_ball(roi)

def test_detect_team():
    img = cv2.imread("minimap/minimap_visible_3.png")
    roi = get_minimap_roi(img)

    interactive_extent_debugger(roi)

