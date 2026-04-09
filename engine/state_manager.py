import collections
import statistics

from config.minimap_config import MINIMAP_BOUNDS
from models.frame_data import FrameData, predict_data
from engine.event_detector import OutOfBoundsDetector
from models.game_states import GameState
from util.screenlogger import logger
from vision.clock_detector import ClockDetector
from vision.minimap_detector import MinimapDetector
from vision.scoreboard_detector import ScoreboardDetector

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
        self.scoreboard_visible = False
        self.data = {}
        self.oob_detector = OutOfBoundsDetector()
        self.no_ball_counter = 0

    def push_data(self, data):
        step = data.get("step", 1)

        raw_state = self._get_raw_state(data)
        self.data = data

        if len(self.history) > 0:
            self.last_state = statistics.mode(self.history)

        for _ in range(step):
            self.history.append(raw_state)

        frame = data["frame"]
        clock_detector = ClockDetector()

        if data["frame_counter"] % 30 == 0:
            self.ingame_time = clock_detector.process(frame)

        logger.push(f"IG Time: {self.ingame_time}")

        raw_frame = data["frame"]

        # Start processing data
        if self.last_state == GameState.CUTSCENE:
            self.last_frame = None

            scoreboard_detector = ScoreboardDetector()

            self.scoreboard_visible = scoreboard_detector.is_visible(scoreboard_detector.get_roi(raw_frame))
            if self.scoreboard_visible:
                if self.scoreboard_counter == 0:
                    self.last_home_score = self.home_score
                    self.last_away_score = self.away_score

                if self.scoreboard_counter > 90:
                    self._process_scoreboard(data)

                self.scoreboard_counter += step

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

        frame = data["frame"]

        clock_detector = ClockDetector()
        minimap_detector = MinimapDetector()

        if minimap_detector.is_visible(minimap_detector.get_roi(frame)):
            return GameState.IN_GAME
        elif clock_detector.is_visible(clock_detector.get_roi(frame)):
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

            scoreboard_detector = ScoreboardDetector()

            (home_score, away_score) = scoreboard_detector.process(raw_frame)

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
        minimap_bounds = MINIMAP_BOUNDS["full"]
        global_pos = (center[0] + minimap_bounds.x, center[1] + minimap_bounds.y)

        # Debug output
        # logger.push(f"Ball global: {global_pos}", 100, (0, 255, 0))

        event = self.oob_detector.update(global_pos)

        if event:
            logger.push(f"{event['type']} ({event['side']})", 300, (0, 255, 0))