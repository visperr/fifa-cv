import json

from util.generate_heatmap import generate_better_heatmap, generate_heatmap_dashboard
from util.json import save_tracking_data
from util.process_video import process_video
from util.realtime_video import run_video_tracker

if __name__ == '__main__':
    run_video_tracker("tests/clips/goal.mp4")
    # save_tracking_data(process_video("testclip.mp4"), "output.json")

    # with open("output.json", "r") as f:
    #     data = json.load(f)
    #
    #     heatmaps = {
    #         "Ball Positioning": data["tracking_data"]["ball"],
    #         "Opponent Positioning": data["tracking_data"]["opponents"],
    #         "Team Positioning": data["tracking_data"]["team"],
    #         "Controlled Player Positioning": data["tracking_data"]["controlled"],
    #     }
    #
    #     generate_heatmap_dashboard(heatmaps)
