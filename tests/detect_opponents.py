import cv2

from util.find_opponents import track_opponents_fast, get_minimap_roi


def test_find_opponents():
    img = cv2.imread("minimap/minimap_visible_1.png")
    roi = get_minimap_roi(img)
    opponents = track_opponents_fast(roi)

    assert len(opponents) > 5

def test_find_opponents_2():
    img = cv2.imread("minimap/minimap_visible_2.png")
    roi = get_minimap_roi(img)
    opponents = track_opponents_fast(roi)

    assert len(opponents) > 5

def test_find_opponents_trans():
    img = cv2.imread("minimap/minimap_trans_1.png")
    roi = get_minimap_roi(img)
    opponents = track_opponents_fast(roi)

    assert len(opponents) > 5

def test_find_opponents_trans_2():
    img = cv2.imread("minimap/minimap_trans_2.png")
    roi = get_minimap_roi(img)
    opponents = track_opponents_fast(roi)

    assert len(opponents) > 5

def test_find_opponents_hide():
    img = cv2.imread("minimap/minimap_hide_1.png")
    roi = get_minimap_roi(img)
    opponents = track_opponents_fast(roi)

    assert len(opponents) < 2
