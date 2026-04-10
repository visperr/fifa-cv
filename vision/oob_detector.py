from config.minimap_config import MINIMAP_REGIONS
from models.bound_box import BoundingBox
from util.screenlogger import logger


class OutOfBoundsDetector:
    def __init__(self, threshold_frames=5, movement_tolerance=3):
        self.threshold = threshold_frames
        self.tolerance = movement_tolerance

        self.counter = 0
        self.last_region = None

        self.last_event = None
        self.cooldown = 0

    def update(self, position):
        if position is None:
            self._reset()
            if self.cooldown > 0:
                self.cooldown -= 1
            return None

        region = find_region(position, MINIMAP_REGIONS)

        if region is None:
            self._reset()
            if self.cooldown > 0:
                self.cooldown -= 1
            return None

        if region == self.last_region:
            self.counter += 1
        else:
            self.counter = 1

        self.last_region = region

        if self.counter >= self.threshold:
            event = self._region_to_event(region)
            if event is None:
                if self.cooldown > 0:
                    self.cooldown -= 1
                return None

            if self.cooldown > 0 and self.last_event is not None:
                if self.last_event["type"] == event["type"]:
                    self.cooldown -= 1
                    return None

            if region.startswith("baselines") or region.startswith("corners") or region.startswith("sidelines"):
                logger.push(region, 120, (255, 0, 0))

            return self._trigger_event(event)

        if self.cooldown > 0: self.cooldown -= 1
        return None

    def _region_to_event(self, region):
        # Corner detection
        if region.startswith("corners"):
            if "left" in region:
                return {"type": "corner", "side": "left"}
            else:
                return {"type": "corner", "side": "right"}

        # Sideline → throw-in
        if region.startswith("sidelines"):
            if "top" in region:
                return {"type": "throw_in", "side": "top"}
            else:
                return {"type": "throw_in", "side": "bottom"}

        if region.startswith("baselines"):
            if "goal_chance" in region:
                if "left" in region:
                    return {"type": "shot", "side": "left"}
                else:
                    return {"type": "shot", "side": "right"}

        return None

    def _trigger_event(self, event):
        if event is None:
            return None

        self.last_event = event
        self.cooldown = 75  # frames

        self._reset()
        return event

    def _reset(self):
        self.counter = 0
        self.last_region = None

def find_region(point, region_dict):
    x, y = point

    for key, value in region_dict.items():
        if isinstance(value, BoundingBox):
            if value.contains(x, y):
                return key
        elif isinstance(value, dict):
            result = find_region(point, value)
            if result:
                return f"{key}.{result}"

    return None

def is_inside_field(point, regions):
    # If it's NOT in any out-of-bounds region → it's inside
    return find_region(point, regions) is None