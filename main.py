from replay.realtime_video import run_video_tracker

if __name__ == '__main__':
    run_video_tracker("tests/clips/throwin.mp4")
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
