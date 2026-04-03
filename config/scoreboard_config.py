import numpy as np

from models.bound_box import BoundingBox

SCOREBOARD_MASKS = [
    [
        np.array([220, 220, 220]),
        np.array([255, 255, 255]),
    ],
    [
        np.array([0, 0, 0]),
        np.array([30, 30, 30]),
    ],
    [
        np.array([50, 45, 210]),
        np.array([90, 65, 255]),
    ]
]

SCOREBOARD_BOUNDS = {
    "full": BoundingBox(700, 870, 1219, 953),
    "home_score": BoundingBox(84, 0, 167, 83),
    "away_score": BoundingBox(352, 0, 435, 83),
}

SCOREBOARD_VISIBILITY_THRESHOLD = 0.85
