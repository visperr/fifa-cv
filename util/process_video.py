import cv2
from state_manager import GameStateManager, GameState
from util.clock_data import get_clock_roi, get_ingame_time
from util.minimap_data import get_minimap_roi, get_ball, get_opponents, get_team, get_controlled_player
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
            current_state = state_manager.get_smoothed_state(minimap_frame)

            if current_state == GameState.IN_GAME:

                if frame_counter % 30 == 0:
                    ingame_time = get_ingame_time(clock_frame)

                ball_pos = get_ball(minimap_frame)
                ball_coords = None
                if ball_pos is not None:
                    x = int(ball_pos[0])
                    y = int(ball_pos[1])
                    ball_coords = (x, y)

                opponents = get_opponents(minimap_frame)
                opponents_coords = []
                for opp in opponents:
                    x = int(opp[0])
                    y = int(opp[1])
                    opponents_coords.append((x, y))

                players = get_team(minimap_frame)
                player_coords = []
                for player in players:
                    x = int(player[0])
                    y = int(player[1])
                    player_coords.append((x, y))

                controlled_player = get_controlled_player(minimap_frame)
                controlled_player_coords = None
                if controlled_player is not None:
                    x = int(controlled_player[0])
                    y = int(controlled_player[1])
                    controlled_player_coords = (x, y)

                frame_data = {
                    "frame_counter": frame_counter,
                    "game_state": str(current_state),
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