import json

from replay.realtime_video import run_video_tracker
from replay.replay_viewer import start_replay
from util.generate_heatmap import generate_heatmap_dashboard, extract_coords_for_heatmap, generate_heatmap_from_json
from util.json import save_tracking_data
from util.process_video import process_video

if __name__ == '__main__':
    run_video_tracker("testclip.mp4")
    # run_video_tracker("tests/clips/foul.mp4")
    # run_video_tracker("tests/clips/goal_2_kickoff.mp4")
    # run_video_tracker("tests/clips/goal.mp4")
    # run_video_tracker("tests/clips/kickoff.mp4")
    # run_video_tracker("tests/clips/throwin.mp4")
    # run_video_tracker("tests/clips/onlycorner.mp4")

    # save_tracking_data(process_video("testclip.mp4"), "smoothed_data.json")

    # generate_heatmap_from_json("smoothed_data.json")
    # start_replay("smoothed_data.json", "minimap_clean.png")
