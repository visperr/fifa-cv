from config.minimap_config import MINIMAP_REGIONS
from models.bound_box import BoundingBox

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


class OutOfBoundsDetector:
    def __init__(self, threshold_frames=5, movement_tolerance=3):
        self.threshold = threshold_frames
        self.tolerance = movement_tolerance

        self.counter = 0
        self.last_position = None

        self.last_event = None
        self.cooldown = 0

    def update(self, position):
        if position is None:
            self._reset()
            return None

        # Cooldown to prevent spam
        if self.cooldown > 0:
            self.cooldown -= 1
            return None

        # 🔍 Check movement stability
        if self.last_position is not None:
            dx = abs(position[0] - self.last_position[0])
            dy = abs(position[1] - self.last_position[1])

            if dx <= self.tolerance and dy <= self.tolerance:
                self.counter += 1
            else:
                self.counter = 1
        else:
            self.counter = 1

        self.last_position = position

        # 🔍 Check if ball is in any OUT-OF-BOUNDS region
        region = find_region(position, MINIMAP_REGIONS)

        if region is None:
            self._reset()
            return None

        # 🎯 Only trigger if stable for enough frames
        if self.counter >= self.threshold:
            event = self._region_to_event(region)
            return self._trigger_event(event)

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
        self.last_position = None




