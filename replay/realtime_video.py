from data.roi.scoreboard_data import SCOREBOARD_MASKS, get_scoreboard_roi, is_scoreboard_visible
from data.state_manager import GameState, GameStateManager
from data.roi.clock_data import get_clock_roi, get_ingame_time, is_clock_visible, CLOCK_MASKS
from util.mask_viewer import setup_colour_debugger, apply_colour_debugger, setup_multiple_colour_debugger, \
    apply_multi_colour_debugger
from data.roi.minimap_data import *

def run_video_tracker(video_path):
    cap = cv2.VideoCapture(video_path)

    state_manager = GameStateManager(start_score=(1,0))

    # setup_debuggers()

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
        scoreboard_roi = get_scoreboard_roi(frame)

        if frame_counter % 30 == 0:
            ingame_time = get_ingame_time(clock_roi)

        logger.push(f"Frame: {frame_counter}")
        logger.push(f"Game Time: {ingame_time}")

        clock_visible = is_clock_visible(clock_roi)
        minimap_visible = is_minimap_visible(frame)
        scoreboard_visible = is_scoreboard_visible(frame)

        if not is_paused:
            game_data = {
                "clock_visible": clock_visible,
                "minimap_visible": minimap_visible,
                "scoreboard_visible": scoreboard_visible,
                "ingame_time": ingame_time,
                "frame": frame,
                "frame_counter": frame_counter,
            }

            state_manager.push_data(game_data)

        game_state = state_manager.get_game_state(clean_roi)

        logger.push(f"Game State: {game_state["state"].name}")
        logger.push(f"Home Score: {game_state["home_score"]}, Away Score: {game_state["away_score"]}")

        # 3. CREATE A CANVAS AND DRAW THE DATA
        drawn_canvas = clean_roi.copy()

        if game_state["state"] == GameState.IN_GAME:

            frame_data = game_state["frame_data"]

            if frame_data is not None:

                opponent_list = frame_data.opponents
                ball_pos = frame_data.ball
                team_list = frame_data.team
                player_pos = frame_data.controlled

                logger.push(f"Amount of detected opponents: {len(opponent_list)}")
                logger.push(f"Amount of detected teammates: {len(team_list)}")
                if ball_pos is not None: logger.push(f"Ball position: {ball_pos.coordinate[0]}, {ball_pos.coordinate[1]}")
                if player_pos is not None: logger.push(f"Controlled Player position: {player_pos.coordinate[0]}, {player_pos.coordinate[1]}")

                # Draw Opponents
                for opponent in opponent_list:
                    (x, y, radius) = opponent.coordinate
                    cv2.circle(drawn_canvas, (x, y), 4, (0, 0, 255), 2)

                # Draw Opponents
                for team in team_list:
                    (x, y) = team.coordinate
                    cv2.circle(drawn_canvas, (x, y), 4, (255, 0, 0), 2)

                if player_pos is not None:
                    cv2.circle(drawn_canvas, (player_pos.coordinate[0], player_pos.coordinate[1]), 4, (255, 255, 0), 2)

                # # Draw the Ball
                if ball_pos is not None:
                    x, y, bw, bh = ball_pos.coordinate
                    c_x, c_y = (x + int(bw / 2)), (y + int(bh / 2))

                    cv2.circle(drawn_canvas, (c_x, c_y), 2, (0, 255, 0), 2)

        # show_debuggers(frame)

        final_frame = frame.copy()

        # 4. Stitch and Display
        final_frame[Y_START:Y_END, X_START:X_END] = drawn_canvas

        if not is_paused:  logger.update()

        display_frame = cv2.resize(final_frame, (1280, 720))
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

        if not is_paused: frame_counter += 1

    cap.release()
    cv2.destroyAllWindows()

def setup_debuggers():
    setup_multiple_colour_debugger(
        "UI Border Tuning Multi",
        default_lower=[
            MINIMAP_LINES_MASKS[1][0],
            MINIMAP_LINES_MASKS[1][2]
        ],
        default_upper=[
            MINIMAP_LINES_MASKS[1][1],
            MINIMAP_LINES_MASKS[1][3]
        ]
    )

    setup_colour_debugger(
        "UI Border Tuning",
        default_lower=MINIMAP_LINES_MASKS[0][0],
        default_upper=MINIMAP_LINES_MASKS[0][1]
    )

    setup_colour_debugger(
        "UI Border Tuning 2",
        default_lower=MINIMAP_LINES_MASKS[0][0],
        default_upper=MINIMAP_LINES_MASKS[0][1]
    )

    setup_colour_debugger(
        "BALL TUNER",
        default_lower=BALL_MASK[0],
        default_upper=BALL_MASK[1]
    )

    setup_colour_debugger(
        "TEAM TUNER",
        default_lower=TEAM_MASK[0],
        default_upper=TEAM_MASK[1]
    )

    setup_colour_debugger(
        "CONTROLLED TUNER",
        default_lower=CONTROLLED_MASK[0],
        default_upper=CONTROLLED_MASK[1]
    )
    setup_colour_debugger(
        "OPPONENT TUNER",
        default_lower=OPPONENT_MASK[0],
        default_upper=OPPONENT_MASK[1]
    )
    setup_multiple_colour_debugger(
        "CLOCK TUNER",
        default_lower=[
            CLOCK_MASKS[0][0],
            CLOCK_MASKS[1][0]
        ],
        default_upper=[
            CLOCK_MASKS[0][1],
            CLOCK_MASKS[1][1]
        ]
    )

def show_debuggers(frame):
    minimap_roi = get_minimap_roi(frame).copy()
    clock_roi = get_clock_roi(frame).copy()

    apply_colour_debugger("TEAM TUNER", minimap_roi, zoom_scale=2)
    apply_colour_debugger("OPPONENT TUNER", minimap_roi, zoom_scale=2)
    apply_colour_debugger("BALL TUNER", minimap_roi, zoom_scale=2)
    apply_colour_debugger("CONTROLLED TUNER", minimap_roi, zoom_scale=2)
    apply_multi_colour_debugger("CLOCK TUNER", clock_roi, 2, 2)

    TARGET_X1, START_Y1, END_Y1 = 806, 929, 960
    TARGET_X2, START_Y2, END_Y2 = 1110, 929, 960

    ui_border_roi = frame[START_Y1:END_Y1, TARGET_X1:TARGET_X1 + 1]
    apply_colour_debugger("UI Border Tuning", ui_border_roi, zoom_scale=4)

    ui_border_roi = frame[START_Y2:END_Y2, TARGET_X2:TARGET_X2 + 1]
    apply_colour_debugger("UI Border Tuning 2", ui_border_roi, zoom_scale=4)

    START_X, END_X, TARGET_Y = 816, 1099 , 1031
    ui_bottom_roi = frame[TARGET_Y:TARGET_Y+1, START_X:END_X]
    apply_multi_colour_debugger("UI Border Tuning Multi", ui_bottom_roi, 2, zoom_scale=4)