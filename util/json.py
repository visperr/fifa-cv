import json

from config.minimap_config import MINIMAP_BOUNDS


def save_tracking_data(data, output):

    metadata = {
        "metadata": {
            "minimap_size": {
                "width": MINIMAP_BOUNDS["full"].width,
                "height": MINIMAP_BOUNDS["full"].height,
            },
        },
    }

    with open(output, "w") as f:
        f.write("{")

        meta_str = json.dumps(metadata, indent=4)
        f.write(meta_str[1:-2] + ", \n")

        f.write('    "frames": [\n')
        frame_lines = []
        for frame in data:
            frame_lines.append("        " + json.dumps(frame))

        f.write(",\n".join(frame_lines))

        f.write('\n    ]\n}')

    print(f"Saved tracking data at {output}")