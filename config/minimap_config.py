import numpy as np

from models.bound_box import BoundingBox

MINIMAP_BOUNDS = {
    "full": BoundingBox(800, 850, 1115, 1040),
    "line_l": BoundingBox(6, 79, 7, 110),
    "line_r": BoundingBox(310, 79, 311, 110),
    "line_bottom": BoundingBox(16, 181, 299, 182)
}

MINIMAP_VISIBILITY_THRESHOLD = 0.85

MINIMAP_REGIONS = {
    "corners": {
        "left_top": BoundingBox(808, 862, 816, 868),
        "left_bottom": BoundingBox(808, 1021, 816, 1025),
        "right_bottom": BoundingBox(1100, 1021, 1108, 1025),
        "right_top": BoundingBox(1100, 862, 1108, 868),
    },

    "sidelines": {
        "top": BoundingBox(817, 860, 1099, 868),
        "bottom": BoundingBox(817, 1021, 1099, 1029),
    },

    "baselines": {
        "left": {
            "goal_chance": BoundingBox(820, 910, 835, 978),
            "top": BoundingBox(820, 864, 835, 909),
            "bottom": BoundingBox(820, 979, 835, 1025),
        },
        "right": {
            "goal_chance": BoundingBox(1082, 910, 1111, 978),
            "top": BoundingBox(1082, 864, 1111, 909),
            "bottom": BoundingBox(1082, 979, 1111, 1025),
        }
    },

    "attacking_zones": {
        "left": {
            "top": BoundingBox(812, 868, 900, 899),
            "middle": BoundingBox(812, 900, 900, 988),
            "bottom": BoundingBox(812, 989, 900, 1020),
        },
        "left_mid": {
            "top": BoundingBox(901, 868, 958, 899),
            "middle": BoundingBox(901, 900, 958, 988),
            "bottom": BoundingBox(901, 989, 958, 1020),
        },
        "right_mid": {
            "top": BoundingBox(959, 868, 1016, 899),
            "middle": BoundingBox(959, 900, 1016, 988),
            "bottom": BoundingBox(959, 989, 1016, 1020),
        },
        "right": {
            "top": BoundingBox(1017, 868, 1105, 899),
            "middle": BoundingBox(1017, 900, 1105, 988),
            "bottom": BoundingBox(1017, 989, 1105, 1020),
        }
    }
}

MINIMAP_MASKS = {
    "line_side": [
        np.array([120, 175, 150]),
        np.array([175, 255, 190])
    ],
    "line_bottom": [
        [
            np.array([110, 175, 120]),
            np.array([232, 255, 255]),
        ],
        [
            np.array([0, 0, 0]),
            np.array([85, 90, 75]),
        ]
    ],
    "ball": [
        np.array([0, 170, 175]),
        np.array([100, 255, 255])
    ], "team": [
        np.array([26, 0, 0]),
        np.array([132, 50, 60])
    ], "controlled": [
        np.array([24, 0, 69]),
        np.array([150, 50, 150])
    ], "opponents": [
        np.array([200, 200, 200]),
        np.array([255, 255, 255])
    ]
}
