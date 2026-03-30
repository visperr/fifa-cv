import cv2
from data.state_manager import GameStateManager, GameState
from util.clock_data import get_clock_roi, get_ingame_time, is_clock_visible
from util.minimap_data import get_minimap_roi, get_ball, get_opponents, get_team, get_controlled_player, \
    is_minimap_visible
from tqdm import tqdm

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)

    state_manager = GameStateManager()


    print("Processing video...")

    frame_counter = 0
    ingame_time = 0
    match_data = []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    with tqdm(total=total_frames, desc="Analysing Frames") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break



            minimap_frame = get_minimap_roi(frame)
            clock_frame = get_clock_roi(frame)

            if frame_counter % 30 == 0:
                ingame_time = get_ingame_time(clock_frame)

            clock_visible = is_clock_visible(clock_frame)
            minimap_visible = is_minimap_visible(frame)

            game_data = {
                "clock_visible": clock_visible,
                "minimap_visible": minimap_visible,
                "ingame_time": ingame_time,
                "frame": frame,
                "frame_counter": frame_counter,
            }

            state_manager.push_data(game_data)
            game_state = state_manager.get_game_state(minimap_frame)

            if game_state["state"] == GameState.IN_GAME:

                frame_data = game_state["frame_data"]

                if frame_data is not None:
                    opponent_list = frame_data.opponents
                    ball_pos = frame_data.ball
                    team_list = frame_data.team
                    player_pos = frame_data.controlled

                    ball_coords = None
                    if ball_pos is not None:
                        x = int(ball_pos.coordinate[0])
                        y = int(ball_pos.coordinate[1])
                        ball_coords = (x, y)

                    opponents_coords = []
                    for opp in opponent_list:
                        x = int(opp.coordinate[0])
                        y = int(opp.coordinate[1])
                        opponents_coords.append((x, y))

                    player_coords = []
                    for player in team_list:
                        x = int(player.coordinate[0])
                        y = int(player.coordinate[1])
                        player_coords.append((x, y))

                    controlled_player_coords = None
                    if player_pos is not None:
                        x = int(player_pos.coordinate[0])
                        y = int(player_pos.coordinate[1])
                        controlled_player_coords = (x, y)

                    frame_data = {
                        "frame_counter": frame_counter,
                        "game_state": str(game_state["state"].name),
                        "time": ingame_time,
                        "ball": ball_coords,
                        "opponents": opponents_coords,
                        "team": player_coords,
                        "controlled_player": controlled_player_coords,
                    }

                    match_data.append(frame_data)

            frame_counter += 1
            pbar.update(1)

    cap.release()
    print("Finished processing video.")

    return match_data