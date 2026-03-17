from replay.realtime_video import run_video_tracker
from replay.replay_viewer import start_replay
from util.json import save_tracking_data
from util.process_video import process_video

if __name__ == '__main__':
    run_video_tracker("testclip.mp4")
    # start_replay("throwin.json", "minimap_clean.png")
    # save_tracking_data(process_video("tests/clips/throwin.mp4"), "throwin.json")
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
