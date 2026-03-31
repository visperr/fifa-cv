from data.roi.minimap_data import get_team, get_minimap_roi, get_opponents, get_controlled_player, get_ball
import math

from util.screenlogger import logger


class CoordinateData:
    def __init__(self, coordinate, predicted_lifespan = None):
        self.coordinate = coordinate

        self.is_predicted = predicted_lifespan is not None
        self.predicted_lifespan = predicted_lifespan

class FrameData:
    def __init__(self, frame):
        self.frame = frame
        self.opponents = []
        self.team = []
        self.controlled = None
        self.ball = None

        self._process()

    def _process(self):
        minimap_roi = get_minimap_roi(self.frame)


        self.opponents = [CoordinateData(coord) for coord in get_opponents(minimap_roi)]
        self.team = [CoordinateData(coord) for coord in get_team(minimap_roi)]

        controlled_coord = get_controlled_player(minimap_roi)
        self.controlled = CoordinateData(controlled_coord) if controlled_coord else None
        ball_coord = get_ball(minimap_roi)
        self.ball = CoordinateData(ball_coord) if ball_coord else None


def predict_data(frame, last_frame):

    LIFESPAN = 20
    MAX_DIST = 10

    if last_frame is None:
        return frame

    predicted_frame = frame

    # BALL PREDICTION
    if predicted_frame.ball is None:
        last_ball = last_frame.ball

        if last_ball is not None:
            if last_ball.is_predicted:
                if last_ball.predicted_lifespan > 0:
                    new_ball = CoordinateData(last_ball.coordinate, last_ball.predicted_lifespan - 1)
                else:
                    new_ball = None
            else:
                new_ball = CoordinateData(last_ball.coordinate, LIFESPAN)
        else:
            new_ball = None

        predicted_frame.ball = new_ball

    # CONTROLLED PLAYER PREDICTION
    if predicted_frame.controlled is None:
        last_controlled = last_frame.controlled

        if last_controlled is not None:
            if last_controlled.is_predicted:
                if last_controlled.predicted_lifespan > 0:
                    new_controlled = CoordinateData(last_controlled.coordinate, last_controlled.predicted_lifespan - 1)
                else:
                    new_controlled = None
            else:
                new_controlled = CoordinateData(last_controlled.coordinate, LIFESPAN)
        else:
            new_controlled = None

        predicted_frame.controlled = new_controlled


    # TEAMMATES PREDICTION
    matched_current_indices = set()
    predicted_teammates = []

    for old_tm in last_frame.team:
        closest_dist = math.inf
        closest_index = -1

        for i, current_tm in enumerate(predicted_frame.team):
            if i in matched_current_indices:
                continue

            dx = current_tm.coordinate[0] - old_tm.coordinate[0]
            dy = current_tm.coordinate[1] - old_tm.coordinate[1]
            dist = math.hypot(dx, dy)

            if dist < closest_dist:
                closest_dist = dist
                closest_index = i

        if closest_dist <= MAX_DIST:
            matched_current_indices.add(closest_index)
        else:
            if old_tm.is_predicted:
                if old_tm.predicted_lifespan > 0:
                    new_tm = CoordinateData(old_tm.coordinate, old_tm.predicted_lifespan - 1)
                    predicted_teammates.append(new_tm)
            else:
                new_tm = CoordinateData(old_tm.coordinate, LIFESPAN)
                predicted_teammates.append(new_tm)

    logger.push(f"Amount of predicted teammates: {len(predicted_teammates)} out of 11")

    for p_tm in predicted_teammates:
        if len(predicted_frame.team) < 11:
            predicted_frame.team.append(p_tm)
        else:
            break

    # OPPONENT PREDICTION
    matched_current_indices = set()
    predicted_opponents = []

    for old_op in last_frame.opponents:
        closest_dist = math.inf
        closest_index = -1

        for i, current_op in enumerate(predicted_frame.opponents):
            if i in matched_current_indices:
                continue

            dx = current_op.coordinate[0] - old_op.coordinate[0]
            dy = current_op.coordinate[1] - old_op.coordinate[1]
            dist = math.hypot(dx, dy)

            if dist < closest_dist:
                closest_dist = dist
                closest_index = i

        if closest_dist <= MAX_DIST:
            matched_current_indices.add(closest_index)
        else:
            if old_op.is_predicted:
                if old_op.predicted_lifespan > 0:
                    new_op = CoordinateData(old_op.coordinate, old_op.predicted_lifespan - 1)
                    predicted_opponents.append(new_op)
            else:
                new_op = CoordinateData(old_op.coordinate, LIFESPAN)
                predicted_opponents.append(new_op)

    logger.push(f"Amount of predicted opponents: {len(predicted_opponents)} out of 11")

    for p_op in predicted_opponents:
        if len(predicted_frame.opponents) < 11:
            predicted_frame.opponents.append(p_op)
        else:
            break

    return predicted_frame