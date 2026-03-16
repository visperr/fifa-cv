import cv2

from state_manager import GameState, GameStateManager
from util.minimap_data import *

def run_video_tracker(video_path):
    cap = cv2.VideoCapture(video_path)

    state_manager = GameStateManager()

    while True:
        ret, frame = cap.read()
        if not ret: break

        # 1. Slice out the perfectly clean minimap
        clean_roi = get_minimap_roi(frame)

        game_state = state_manager.get_smoothed_state(clean_roi)

        cv2.putText(frame, f"STATE: {game_state.name}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

        # 3. CREATE A CANVAS AND DRAW THE DATA
        drawn_canvas = clean_roi.copy()

        if game_state == GameState.IN_GAME:
            # 2. DO ALL THE MATHS (Using the clean image every time!)
            opponent_list = get_opponents(clean_roi)
            ball_pos = get_ball(clean_roi)
            team_list = get_team(clean_roi)
            player_pos = get_controlled_player(clean_roi)

            # Draw Opponents
            for (x, y, radius) in opponent_list:
                cv2.circle(drawn_canvas, (x, y), radius, (0, 0, 255), 2)

            # Draw Opponents
            for (x, y) in team_list:
                cv2.circle(drawn_canvas, (x, y), 4, (255, 0, 0), 2)

            if player_pos is not None:
                cv2.circle(drawn_canvas, (player_pos[0], player_pos[1]), 4, (255, 255, 0), 2)

            # # Draw the Ball
            if ball_pos is not None:
                x, y, bw, bh = ball_pos
                c_x, c_y = (x + int(bw / 2)), (y + int(bh / 2))

                cv2.circle(drawn_canvas, (c_x, c_y), 2, (0, 255, 0), 2)

        # 4. Stitch and Display
        frame[Y_START:Y_END, X_START:X_END] = drawn_canvas
        display_frame = cv2.resize(frame, (1280, 720))
        cv2.imshow("EA FC Clean Tracker", display_frame)

        minimap_height, minimap_width = drawn_canvas.shape[:2]
        zoomed_minimap = cv2.resize(drawn_canvas, (minimap_width * 2, minimap_height * 2))

        cv2.imshow("Minimap Analysis (2x Zoom)", zoomed_minimap)

        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()