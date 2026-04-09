from enum import Enum

class EventType(Enum):
    Unknown = "Unknown"
    GOAL = "Goal"
    CORNER = "Corner"
    THROW_IN = "Throw-in"
    FOUL = "Foul"
    KICK_OFF = "Kick-off"
    MATCH_START = "Match Start"
    HALF_TIME = "Half Time"
    FULL_TIME = "Full Time"

class GameEvent:
    def __init__(self, event_type, frame, details=None):
        self.event_type = event_type
        self.frame = frame
        self.details = details or {}

    def to_dict(self):
        return {
            "event_type": self.event_type.value,
            "frame": self.frame,
            "details": self.details
        }