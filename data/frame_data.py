from util.minimap_data import get_team, get_minimap_roi, get_opponents, get_controlled_player, get_ball


class CoordinateData:
    def __init__(self, coordinate, predicted_lifespan = -1):
        self.coordinate = coordinate
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
