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
