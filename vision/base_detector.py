from abc import ABC, abstractmethod

import cv2


class BaseDetector(ABC):

    @abstractmethod
    def get_roi(self, frame):
        """Crops the main frame to only show the relevant area."""
        pass

    @abstractmethod
    def is_visible(self, roi, debug=False):
        """Checks if the UI element (like the clock or minimap) is currently on screen."""
        pass

    @abstractmethod
    def extract_data(self, roi):
        pass

    def process(self, frame, debug=False):
        roi = self.get_roi(frame)
        if self.is_visible(roi, debug=debug):
            return self.extract_data(roi)
        return None

def count_visible_pixels(frame, mask=None):

    if mask is None:
        masked = frame.copy()
    else:
        masked = cv2.inRange(frame, mask[0], mask[1])

    total = frame.shape[0] * frame.shape[1]
    matched = cv2.countNonZero(masked)

    return matched, total
