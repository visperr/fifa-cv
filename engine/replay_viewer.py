import cv2
import json
import numpy as np


def start_replay(json_path, pitch_image_path, video_path):
    print("Loading match data...")
    with open(json_path, 'r') as f:
        full_data = json.load(f)
        frames_data = full_data.get("frames", [])

    total_frames = len(frames_data)
    if total_frames == 0:
        print("No frames found in JSON!")
        return

    # 1. LOAD THE PITCH AND THE VIDEO
    # ---------------------------------------------------------
    base_pitch = cv2.imread(pitch_image_path)
    if base_pitch is None:
        print("Could not load pitch image!")
        return

    scale_factor = 4.0
    new_width = int(base_pitch.shape[1] * scale_factor)
    new_height = int(base_pitch.shape[0] * scale_factor)
    zoomed_pitch = cv2.resize(base_pitch, (new_width, new_height))

    # Open the original video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Could not load the original video!")
        return

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

        # Draw Opponents
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

        actual_frame_num = current_frame.get("frame_counter", frame_index)

        # Find out where OpenCV is currently paused in the video
        current_vid_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        # 1. If we scrubbed backwards, or made a massive jump forwards, we HAVE to use the slow cap.set()
        if actual_frame_num < current_vid_frame or (actual_frame_num - current_vid_frame) > 60:
            cap.set(cv2.CAP_PROP_POS_FRAMES, actual_frame_num)
            ret, vid_frame = cap.read()

        # 2. If we are just playing forward normally, or doing a small skip (like your x10 cutscene skip)
        else:
            frames_to_advance = actual_frame_num - current_vid_frame

            # Use cap.grab() to skip unneeded frames super fast without doing the heavy pixel decoding
            if frames_to_advance > 0:
                for _ in range(frames_to_advance - 1):
                    cap.grab()

            # Finally, decode the actual frame we want to see!
            ret, vid_frame = cap.read()

        # Display the video
        if ret:
            vid_frame_resized = cv2.resize(vid_frame, (1280, 720))
            cv2.imshow("Original Video", vid_frame_resized)

    # 3. SET UP THE WINDOW
    # ---------------------------------------------------------
    cv2.namedWindow("EA FC Tactical Replay")
    cv2.createTrackbar("Timeline", "EA FC Tactical Replay", 0, total_frames - 1, on_trackbar)
    on_trackbar(0)

    # 4. THE 30FPS OPTIMISED ANIMATION LOOP
    # ---------------------------------------------------------
    is_playing = False
    print("Replay loaded! Press SPACEBAR to play/pause.")

    while True:
        # Wait 33ms between loops (~30 frames per second)
        key = cv2.waitKey(33) & 0xFF

        if key == ord('q'):
            break
        elif key == ord(' '):
            is_playing = not is_playing

        if is_playing:
            current_pos = cv2.getTrackbarPos("Timeline", "EA FC Tactical Replay")

            # Jump forward by 2 frames at a time to keep it real-time!
            if current_pos < total_frames - 2:
                cv2.setTrackbarPos("Timeline", "EA FC Tactical Replay", current_pos + 2)
            elif current_pos < total_frames - 1:
                # Just in case we are on the very last frame
                cv2.setTrackbarPos("Timeline", "EA FC Tactical Replay", current_pos + 1)
            else:
                is_playing = False

    # Clean up the video capture when we quit
    cap.release()
    cv2.destroyAllWindows()