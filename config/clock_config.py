import numpy as np

from models.bound_box import BoundingBox

CLOCK_BOUNDS = BoundingBox(85, 104, 160, 150)

CLOCK_MASKS = [
    [
        np.array([220, 220, 220]),
        np.array([255, 255, 255]),
    ],
    [
        np.array([0, 0, 0]),
        np.array([30, 30, 30]),
    ]
]

CLOCK_VISIBILITY_THRESHOLD = 0.85
