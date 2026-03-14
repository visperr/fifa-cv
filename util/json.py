import json

from util.minimap_data import get_minimap_dims


def save_tracking_data(data, output):
    data = {
        "metadata": {
            "minimap_size": {"width": get_minimap_dims()[0], "height": get_minimap_dims()[1]},
        },
        "tracking_data": {
            "ball": data["ball_coords"],
            "opponents": data["opponent_coords"],
            "team": data["team_coords"],
            "controlled": data["controlled_player_coords"],
        }
    }

    with open(output, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Saved tracking data at {output}")