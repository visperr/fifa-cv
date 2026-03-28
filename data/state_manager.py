import collections
import statistics
from enum import Enum

from data.frame_data import FrameData
from util.minimap_data import *


class GameState(Enum):
    IN_GAME = 1
    MINIMAP_TRANSPARENT = 2
    CUTSCENE = 3
    FOUL = 4

class GameStateManager:
    def __init__(self, memory_size=15):
        self.history = collections.deque(maxlen=memory_size)

        self.ingame_time = "00:00"
        self.last_state = GameState.IN_GAME
        self.last_frame = None
        self.frame_data = None
        self.data = {}

    def push_data(self, data):

        # Get raw state (Is minimap / clock showing or not?) before being processed
        raw_state = self._get_raw_state(data)

        # Update variables and smooth state
        self.data = data

        if len(self.history) > 0:
            self.last_state = statistics.mode(self.history)

        self.history.append(raw_state)

        self.ingame_time = data["ingame_time"]

        # Start processing data
        if self.last_state == GameState.IN_GAME:
            raw_frame = data["frame"]

            frame_data = FrameData(raw_frame)
            last_frame = FrameData(self.last_frame)
            predicted_frame = self.predict_frame_data(frame_data, last_frame)

            self.frame_data = predicted_frame

            # Push new last frame
            self.last_frame = raw_frame


    def get_game_state(self, frame):

        state = statistics.mode(self.history)

        if self.last_state == GameState.CUTSCENE and self.last_state != state:
            state = self.resolve_cutscene(frame, self.data)

        return {
            "time": self.ingame_time,
            "state": state,
        }

    def _get_raw_state(self, data):

        if data["minimap_visible"]:
            return GameState.IN_GAME
        elif data["clock_visible"]:
            return GameState.MINIMAP_TRANSPARENT
        else:
            return GameState.CUTSCENE

    def resolve_cutscene(self, frame, data):
        raw_state = self._get_raw_state(data)

        if raw_state == GameState.IN_GAME:
            logger.push(f"Foul detected", 300, (0, 255, 0))
            return GameState.FOUL

        return GameState.CUTSCENE

    def predict_frame_data(self, frame_data, last_frame):
        if last_frame is None:
            return frame_data

        predicted_frame = frame_data.copy()

        if predicted_frame.ball is None:
            # ball_coord =
