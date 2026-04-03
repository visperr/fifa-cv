from models.bound_box import BoundingBox


MINIMAP_BOUNDS = {
    "full": BoundingBox(800, 850, 1115, 1040)
}

MINIMAP_VISIBILITY_THRESHOLD = 85

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