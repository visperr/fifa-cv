import cv2
from state_manager import GameStateManager, GameState
from util.minimap_data import get_minimap_roi, get_ball, get_opponents, get_team, get_controlled_player
from tqdm import tqdm

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)

    all_ball_coords = []
    all_opponent_coords = []
    all_player_coords = []
    all_controlled_coords = []

    state_manager = GameStateManager()

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print("Processing video...")

    with tqdm(total=total_frames, desc="Analysing Frames") as pbar:
        while(True):
            ret, frame = cap.read()
            if not ret:
                break

            roi_frame = get_minimap_roi(frame)
            current_state = state_manager.get_smoothed_state(roi_frame)

            if (current_state == GameState.IN_GAME):
                ball_pos = get_ball(roi_frame)
                if ball_pos is not None:
                    x = int(ball_pos[0])
                    y = int(ball_pos[1])
                    all_ball_coords.append((x, y))

                opponents = get_opponents(roi_frame)
                for opp in opponents:
                    x = int(opp[0])
                    y = int(opp[1])
                    all_opponent_coords.append((x, y))

                players = get_team(roi_frame)
                for player in players:
                    x = int(player[0])
                    y = int(player[1])
                    all_player_coords.append((x, y))

                controlled_player = get_controlled_player(roi_frame)
                if controlled_player is not None:
                    x = int(controlled_player[0])
                    y = int(controlled_player[1])
                    all_controlled_coords.append((x, y))

            pbar.update(1)

    cap.release()
    print("Finished processing video.")

    data = {
        "ball_coords": all_ball_coords,
        "opponent_coords": all_opponent_coords,
        "team_coords": all_player_coords,
        "controlled_player_coords": all_controlled_coords
    }
    return data