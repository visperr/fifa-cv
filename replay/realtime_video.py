import cv2
import numpy as np

from state_manager import GameState, GameStateManager
from util.clock_data import get_clock_roi, get_ingame_time
from util.mask_viewer import setup_colour_debugger, apply_colour_debugger, setup_multiple_colour_debugger, \
    apply_multi_colour_debugger
from util.minimap_data import *

def run_video_tracker(video_path):
    cap = cv2.VideoCapture(video_path)

    state_manager = GameStateManager()

    # setup_multiple_colour_debugger(
    #     "UI Border Tuning Multi",
    #     default_lower=[
    #         MINIMAP_LINES_MASKS[1][0],
    #         MINIMAP_LINES_MASKS[1][2]
    #     ],
    #     default_upper=[
    #         MINIMAP_LINES_MASKS[1][1],
    #         MINIMAP_LINES_MASKS[1][3]
    #     ]
    # )
    #
    # setup_colour_debugger(
    #     "UI Border Tuning",
    #     default_lower=MINIMAP_LINES_MASKS[0][0],
    #     default_upper=MINIMAP_LINES_MASKS[0][1]
    # )
    #
    # setup_colour_debugger(
    #     "UI Border Tuning 2",
    #     default_lower=MINIMAP_LINES_MASKS[0][0],
    #     default_upper=MINIMAP_LINES_MASKS[0][1]
    # )

    # setup_colour_debugger(
    #     "BALL TUNER",
    #     default_lower=BALL_MASK[0],
    #     default_upper=BALL_MASK[1]
    # )
    #
    # setup_colour_debugger(
    #     "TEAM TUNER",
    #     default_lower=TEAM_MASK[0],
    #     default_upper=TEAM_MASK[1]
    # )

    # setup_colour_debugger(
    #     "CONTROLLED TUNER",
    #     default_lower=CONTROLLED_MASK[0],
    #     default_upper=CONTROLLED_MASK[1]
    # )
    # setup_colour_debugger(
    #     "OPPONENT TUNER",
    #     default_lower=OPPONENT_MASK[0],
    #     default_upper=OPPONENT_MASK[1]
    # )
    # setup_multiple_colour_debugger(
    #     "CLOCK TUNER",
    #     default_lower=[
    #         CLOCK_MASKS[0][0],
    #         CLOCK_MASKS[1][0]
    #     ],
    #     default_upper=[
    #         CLOCK_MASKS[0][1],
    #         CLOCK_MASKS[1][1]
    #     ]
    # )

    is_paused = False
    frame_counter = 0
    ingame_time = 0
    while True:
        if not is_paused:
            ret, frame = cap.read()
            if not ret: break

        # 1. Slice out the perfectly clean minimap
        clean_roi = get_minimap_roi(frame)

        clock_roi = get_clock_roi(frame)
        if frame_counter % 30 == 0:
            ingame_time = get_ingame_time(clock_roi)
        cv2.putText(frame, f"TIME: {ingame_time}", (500, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

        game_state = state_manager.get_smoothed_state(clean_roi)

        cv2.putText(frame, f"STATE: {game_state.name}", (500, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

        # 3. CREATE A CANVAS AND DRAW THE DATA
        drawn_canvas = clean_roi.copy()

        # apply_colour_debugger("TEAM TUNER", drawn_canvas, zoom_scale=2)
        # apply_colour_debugger("OPPONENT TUNER", drawn_canvas, zoom_scale=2)
        # apply_colour_debugger("BALL TUNER", drawn_canvas, zoom_scale=2)
        # apply_colour_debugger("CONTROLLED TUNER", drawn_canvas, zoom_scale=2)
        # apply_multi_colour_debugger("CLOCK TUNER", clock_roi, 2, 2)

        clock_visible = is_clock_visible(clock_roi)

        minimap_visible = is_minimap_visible(frame)

        cv2.putText(frame, f"CLOCK_VISIBLE: {clock_visible}", (500, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

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


        # TARGET_X1, START_Y1, END_Y1 = 806, 929, 960
        # TARGET_X2, START_Y2, END_Y2 = 1110, 929, 960
        #
        # ui_border_roi = frame[START_Y1:END_Y1, TARGET_X1:TARGET_X1 + 1]
        # apply_colour_debugger("UI Border Tuning", ui_border_roi, zoom_scale=4)
        #
        # ui_border_roi = frame[START_Y2:END_Y2, TARGET_X2:TARGET_X2 + 1]
        # apply_colour_debugger("UI Border Tuning 2", ui_border_roi, zoom_scale=4)
        #
        # START_X, END_X, TARGET_Y = 816, 1099 , 1031
        # ui_bottom_roi = frame[TARGET_Y:TARGET_Y+1, START_X:END_X]
        # apply_multi_colour_debugger("UI Border Tuning Multi", ui_bottom_roi, 2, zoom_scale=4)

        logger.update()

        display_frame = cv2.resize(frame, (1280, 720))
        cv2.imshow("EA FC Clean Tracker", display_frame)

        minimap_height, minimap_width = drawn_canvas.shape[:2]
        zoomed_minimap = cv2.resize(drawn_canvas, (minimap_width * 2, minimap_height * 2))

        cv2.imshow("Minimap Analysis (2x Zoom)", zoomed_minimap)


        time_canvas = clock_roi.copy()
        time_height, time_width = time_canvas.shape[:2]
        zoomed_clock = cv2.resize(time_canvas, (time_width * 2, time_height * 2))

        cv2.imshow("Clock Analysis (2x Zoom)", zoomed_clock)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord(" "):
            is_paused = not is_paused

        frame_counter += 1

    cap.release()
    cv2.destroyAllWindows()