import cv2

from engine.state_manager import GameStateManager, GameState
from tqdm import tqdm

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)

    state_manager = GameStateManager()


    print("Processing video...")

    frame_counter = 0
    match_data = []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    with tqdm(total=total_frames, desc="Analysing Frames") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            is_cutscene = state_manager.last_state == GameState.CUTSCENE

            frame_step = 1
            if is_cutscene:
                frame_step = 2 if state_manager.scoreboard_visible else 10

            if frame_step > 1:
                for _ in range(frame_step - 1):
                    ret = cap.grab()
                    if not ret: break
                    frame_counter += 1

            game_data = {
                "frame": frame,
                "frame_counter": frame_counter,
                "step": frame_step,
            }

            state_manager.push_data(game_data)
            game_state = state_manager.get_game_state(frame)

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
                        "time": game_state["time"],
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