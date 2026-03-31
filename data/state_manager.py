import collections
import statistics
from enum import Enum

from data.frame_data import FrameData, predict_data
from util.minimap_data import *


class GameState(Enum):
    IN_GAME = 1
    MINIMAP_TRANSPARENT = 2
    CUTSCENE = 3
    FOUL = 4

class MatchState(Enum):
    NOT_STARTED = 0
    FIRST_HALF = 1
    SECOND_HALF = 2
    END_GAME = 3

class GameStateManager:
    def __init__(self, memory_size=15):
        self.history = collections.deque(maxlen=memory_size)

        self.ingame_time = "00:00"
        self.last_state = GameState.IN_GAME
        self.last_frame = None
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
        if self.last_state == GameState.MINIMAP_TRANSPARENT:
            self.last_frame = None
        elif self.last_state == GameState.IN_GAME:
            raw_frame = data["frame"]

            frame_data = FrameData(raw_frame)

            predicted_frame = predict_data(frame_data, self.last_frame)

            # Push new last frame
            self.last_frame = predicted_frame


    def get_game_state(self, frame):

        state = statistics.mode(self.history)

        if self.last_state == GameState.CUTSCENE and self.last_state != state:
            state = self.resolve_cutscene(frame, self.data)

        return {
            "time": self.ingame_time,
            "state": state,
            "frame_data": self.last_frame
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
