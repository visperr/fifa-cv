import collections
import statistics
from enum import Enum

from data.frame_data import FrameData, predict_data
from data.roi.minimap_data import *
from data.roi.scoreboard_data import get_scores
from data.roi.minimap_data import OutOfBoundsDetector



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
    def __init__(self, start_score = (0, 0), memory_size=15):
        self.history = collections.deque(maxlen=memory_size)

        self.ingame_time = "00:00"
        self.home_score = start_score[0]
        self.last_home_score = start_score[0]
        self.away_score = start_score[1]
        self.last_away_score = start_score[1]
        self.last_state = GameState.IN_GAME
        self.last_frame = None
        self.scoreboard_counter = 0
        self.data = {}
        self.oob_detector = OutOfBoundsDetector()
        self.no_ball_counter = 0

    def push_data(self, data):

        # Get raw state (Is minimap / clock showing or not?) before being processed
        raw_state = self._get_raw_state(data)

        # Update variables and smooth state
        self.data = data


        if len(self.history) > 0:
            self.last_state = statistics.mode(self.history)

        self.history.append(raw_state)

        self.ingame_time = data["ingame_time"]

        raw_frame = data["frame"]

        # Start processing data
        if self.last_state == GameState.CUTSCENE:
            self.last_frame = None

            scoreboard_visible = data["scoreboard_visible"]
            if scoreboard_visible:
                if self.scoreboard_counter == 0:
                    self.last_home_score = self.home_score
                    self.last_away_score = self.away_score

                if self.scoreboard_counter > 90:
                    self._process_scoreboard(data)

                self.scoreboard_counter += 1

        elif self.last_state == GameState.MINIMAP_TRANSPARENT:
            self.last_frame = None
            self.scoreboard_counter = 0
        elif self.last_state == GameState.IN_GAME:

            self.scoreboard_counter = 0
            self._process_scores()
            self._process_out_of_bounds()

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
            "home_score": self.home_score,
            "away_score": self.away_score,
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


    def _process_scoreboard(self, data):
        if data["frame_counter"] % 15 == 0:
            raw_frame = data["frame"]
            (home_score, away_score) = get_scores(raw_frame)

            logger.push(f"Home score: {home_score}, Away score: {away_score}")

            if home_score is not None and away_score is not None:
                if home_score == self.home_score + 1 and away_score == self.away_score:
                    self.home_score = home_score
                elif home_score == self.home_score and away_score == self.away_score + 1:
                    self.away_score = away_score
                else:
                    # Scores are the same or are incorrect, we skip
                    return

    def _process_scores(self):
        if self.home_score != self.last_home_score:
            # Home scored
            logger.push(f"HOME SCORED!!!", 300, (0, 255, 0))
        elif self.away_score != self.last_away_score:
            # Away scored
            logger.push(f"AWAY SCORED!!!", 300, (0, 255, 0))
        else:
            # New match state (kickoff, halftime, fulltime)
            pass

        self.last_home_score = self.home_score
        self.last_away_score = self.away_score

    def _process_out_of_bounds(self):
        if self.oob_detector is None:
            logger.push("No OOB_DETECTOR", 300, (0, 255, 0))
            return

        ball = getattr(self.last_frame, "ball", None)

        if ball is None:
            self.no_ball_counter += 1
            if self.no_ball_counter > 5:
                logger.push("No BALL", 30, (0, 0, 255))
            return

        self.no_ball_counter = 0
        # Convert (x,y,w,h) → center
        x, y, w, h = ball.coordinate
        center = (x + w // 2, y + h // 2)

        # Convert ROI → GLOBAL coordinates
        global_pos = (center[0] + X_START, center[1] + Y_START)

        # Debug output
        # logger.push(f"Ball global: {global_pos}", 100, (0, 255, 0))

        event = self.oob_detector.update(global_pos)

        if event:
            logger.push(f"{event['type']} ({event['side']})", 300, (0, 255, 0))