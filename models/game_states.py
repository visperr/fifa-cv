from enum import Enum

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