import collections
import statistics

from config.minimap_config import MINIMAP_BOUNDS
from models.event import GameEvent, EventType
from models.frame_data import FrameData, predict_data
from vision.oob_detector import OutOfBoundsDetector
from models.game_states import GameState
from util.screenlogger import logger
from vision.clock_detector import ClockDetector
from vision.minimap_detector import MinimapDetector
from vision.scoreboard_detector import ScoreboardDetector


class GameStateManager:
    def __init__(self, start_score=(0, 0), memory_size=15):
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
        self.events = []
        self.pre_cutscene_oob_event = None

    def push_data(self, data):
        step = data.get("step", 1)
        raw_state = self._get_raw_state(data)
        self.data = data

        previous_state = self.last_state

        for _ in range(step):
            self.history.append(raw_state)

        current_smoothed_state = statistics.mode(self.history) if self.history else raw_state

        if previous_state == GameState.CUTSCENE and current_smoothed_state == GameState.IN_GAME:
            self._evaluate_cutscene(data["frame_counter"])

        self.last_state = current_smoothed_state

        raw_frame = data["frame"]
        clock_detector = ClockDetector()

        if data["frame_counter"] % 30 == 0:
            self.ingame_time = clock_detector.process(raw_frame)
        logger.push(f"IG Time: {self.ingame_time}")

        # Start processing data
        if current_smoothed_state == GameState.CUTSCENE:
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
        else:
            self.scoreboard_visible = False

        if current_smoothed_state == GameState.MINIMAP_TRANSPARENT:
            self.last_frame = None
            self.scoreboard_counter = 0

        elif current_smoothed_state == GameState.IN_GAME:
            self.scoreboard_counter = 0

            self._process_out_of_bounds()

            frame_data = FrameData(raw_frame)
            predicted_frame = predict_data(frame_data, self.last_frame)
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

    def _process_out_of_bounds(self):
        if self.oob_detector is None:
            return

        ball = getattr(self.last_frame, "ball", None)

        if ball is None:
            return

        x, y, w, h = ball.coordinate
        center = (x + w // 2, y + h // 2)

        minimap_bounds = MINIMAP_BOUNDS["full"]
        global_pos = (center[0] + minimap_bounds.x, center[1] + minimap_bounds.y)

        event = self.oob_detector.update(global_pos)

        if event:
            if event["type"] == "shot":
                new_event = GameEvent(EventType.SHOT, self.data["frame_counter"], event)
                self.events.append(new_event)
                logger.push("EVENT: SHOT", 150, (255, 165, 0))
            else:
                self.pre_cutscene_oob_event = event

    def _evaluate_cutscene(self, frame_counter):

        if self.home_score > self.last_home_score:
            new_event = GameEvent(EventType.GOAL, frame_counter, {"scoring_team": "home"})
            self.events.append(new_event)
            logger.push("Event: HOME GOAL!", 300, (0, 255, 0))

        elif self.away_score > self.last_away_score:
            new_event = GameEvent(EventType.GOAL, frame_counter, {"scoring_team": "away"})
            self.events.append(new_event)
            logger.push("Event: AWAY GOAL!", 300, (0, 255, 0))

        elif self.pre_cutscene_oob_event is not None:
            if self.pre_cutscene_oob_event["type"] == "corner":
                event_type = EventType.CORNER
            elif self.pre_cutscene_oob_event["type"] == "throw_in":
                event_type = EventType.THROW_IN
            elif self.pre_cutscene_oob_event["type"] == "shot":
                event_type = EventType.SHOT
            else:
                event_type = EventType.UNKNOWN

            new_event = GameEvent(event_type, frame_counter, self.pre_cutscene_oob_event)
            self.events.append(new_event)
            logger.push(f"Event: {event_type.value}", 300, (255, 255, 0))

        else:
            new_event = GameEvent(EventType.UNKNOWN, frame_counter)
            self.events.append(new_event)
            logger.push(f"Event: {EventType.UNKNOWN.value}", 300, (0, 0, 255))

        self.last_home_score = self.home_score
        self.last_away_score = self.away_score
        self.pre_cutscene_oob_event = None
