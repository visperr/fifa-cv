from enum import Enum

class GameState(Enum):
    IN_GAME = "In-Game"
    MINIMAP_TRANSPARENT = "In-Game, transparent minimap"
    CUTSCENE = "Cutscene"
    FOUL = "Foul"

class MatchState(Enum):
    NOT_STARTED = 0
    FIRST_HALF = 1
    SECOND_HALF = 2
    END_GAME = 3