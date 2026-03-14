import cv2

from state_manager import GameStateManager, GameState
from util.generate_heatmap import generate_heatmap
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
                    all_ball_coords.append(ball_pos)

                opponents = get_opponents(roi_frame)
                for opp in opponents:
                    all_opponent_coords.append((opp[0], opp[1]))

                players = get_team(roi_frame)
                for player in players:
                    all_player_coords.append((player[0], player[1]))

                controlled_player = get_controlled_player(roi_frame)
                if controlled_player is not None:
                    all_controlled_coords.append(controlled_player)

            pbar.update(1)

    cap.release()
    print("Finished processing video.")

    width = roi_frame.shape[1]
    height = roi_frame.shape[0]

    generate_heatmap(all_ball_coords, "Ball Heatmap" ,width, height)
    generate_heatmap(all_opponent_coords, "Opponent Heatmap" ,width, height)
    generate_heatmap(all_controlled_coords, "Controlled Heatmap" ,width, height)
    generate_heatmap(all_player_coords, "Team Heatmap" ,width, height)
