import cv2
import json
import numpy as np


def start_replay(json_path, pitch_image_path):
    print("Loading match data...")
    with open(json_path, 'r') as f:
        full_data = json.load(f)
        frames_data = full_data.get("frames", [])

    total_frames = len(frames_data)
    if total_frames == 0:
        print("No frames found in JSON!")
        return

    # 1. LOAD AND ZOOM THE PITCH
    # ---------------------------------------------------------
    base_pitch = cv2.imread(pitch_image_path)
    if base_pitch is None:
        print("Could not load pitch image!")
        return

    scale_factor = 4.0  # Change this to 1.5 or 3.0 to adjust the zoom!
    new_width = int(base_pitch.shape[1] * scale_factor)
    new_height = int(base_pitch.shape[0] * scale_factor)
    zoomed_pitch = cv2.resize(base_pitch, (new_width, new_height))

    # 2. THE DRAWING FUNCTION
    # ---------------------------------------------------------
    def on_trackbar(frame_index):
        display_canvas = zoomed_pitch.copy()
        current_frame = frames_data[frame_index]

        # Draw the UI instructions
        cv2.putText(display_canvas, "SPACEBAR: Play/Pause | 'Q': Quit", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

        time_text = f"Time: {current_frame.get('time', '00:00')}"
        cv2.putText(display_canvas, time_text, (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

        # Draw Opponents (Multiply coords by the scale_factor!)
        for opp in current_frame.get('opponents', []):
            x = int(opp[0] * scale_factor)
            y = int(opp[1] * scale_factor)
            cv2.circle(display_canvas, (x, y), 8, (0, 0, 255), -1)

        # Draw Team
        for teammate in current_frame.get('team', []):
            x = int(teammate[0] * scale_factor)
            y = int(teammate[1] * scale_factor)
            cv2.circle(display_canvas, (x, y), 8, (255, 0, 0), -1)

        # Draw Ball
        ball_pos = current_frame.get('ball')
        if ball_pos and len(ball_pos) == 2:
            bx = int(ball_pos[0] * scale_factor)
            by = int(ball_pos[1] * scale_factor)
            cv2.circle(display_canvas, (bx, by), 10, (0, 255, 255), -1)
            cv2.circle(display_canvas, (bx, by), 10, (0, 0, 0), 2)

        cv2.imshow("EA FC Tactical Replay", display_canvas)

    # 3. SET UP THE WINDOW
    # ---------------------------------------------------------
    cv2.namedWindow("EA FC Tactical Replay")
    cv2.createTrackbar("Timeline", "EA FC Tactical Replay", 0, total_frames - 1, on_trackbar)
    on_trackbar(0)  # Draw the very first frame

    # 4. THE 60FPS ANIMATION LOOP
    # ---------------------------------------------------------
    is_playing = False
    print("Replay loaded! Press SPACEBAR to play/pause.")

    while True:
        # Wait 16ms between loops (~60 frames per second)
        key = cv2.waitKey(16) & 0xFF

        if key == ord('q'):
            break
        elif key == ord(' '):  # If you press the Spacebar
            is_playing = not is_playing  # Toggle between True and False

        if is_playing:
            # Find out where the slider currently is
            current_pos = cv2.getTrackbarPos("Timeline", "EA FC Tactical Replay")

            if current_pos < total_frames - 1:
                # Move the slider forward by 1.
                # (This automatically triggers the on_trackbar drawing function!)
                cv2.setTrackbarPos("Timeline", "EA FC Tactical Replay", current_pos + 1)
            else:
                # Pause automatically if we hit the end of the video
                is_playing = False

    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Point these to your specific files!
    start_replay("../throwin.json", "../minimap_clean.png")