import collections
import statistics
from enum import Enum

from util.minimap_data import *


class GameState(Enum):
    IN_GAME = 1
    MINIMAP_TRANSPARENT = 2
    CUTSCENE = 3

class GameStateManager:
    def __init__(self, memory_size=15):
        self.history = collections.deque(maxlen=memory_size)

    def get_smoothed_state(self, roi_frame):
        raw_state = self._get_raw_state(roi_frame)

        self.history.append(raw_state)

        smoothed_state = statistics.mode(self.history)

        return smoothed_state

    def _get_raw_state(self, roi_frame):
        ball_pos = get_ball(roi_frame)

        if ball_pos is not None:
            return GameState.IN_GAME

        opponent_list = get_opponents(roi_frame)

        # adjust threshold accordingly
        if len(opponent_list) > 5:
            return GameState.MINIMAP_TRANSPARENT
        else:
            return GameState.CUTSCENE