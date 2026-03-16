import json

from util.minimap_data import get_minimap_dims


def save_tracking_data(data, output):

    metadata = {
        "metadata": {
            "minimap_size": {
                "width": get_minimap_dims()[0],
                "height": get_minimap_dims()[1]
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