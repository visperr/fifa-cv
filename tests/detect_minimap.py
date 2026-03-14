import cv2
import pytest

from util.minimap import minimap_visible


def test_detect_minimap1():
    img = cv2.imread("minimap/minimap_visible_1.png")
    assert minimap_visible(img)

def test_detect_minimap2():
    img = cv2.imread("minimap/minimap_visible_2.png")
    assert minimap_visible(img)

def  test_detect_minimap_trans1():
    img = cv2.imread("minimap/minimap_trans_1.png")
    assert minimap_visible(img)

def test_detect_minimap_trans2():
    img = cv2.imread("minimap/minimap_trans_2.png")
    assert minimap_visible(img)

def test_detect_minimap_hidden():
    img = cv2.imread("minimap/minimap_hide_1.png")
    assert not minimap_visible(img)