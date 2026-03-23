import cv2
import numpy as np


class ScreenLogger:
    def __init__(self, width=500, height=500):
        self.active_messages = []

        self.width = width
        self.height = height
        self.window_name = "Logger"

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, width, height)

    def push(self, text, frames = 1, colour=(0, 255, 255)):
        self.active_messages.append({
            'text': text,
            'frames_left': frames,
            'colour': colour
        })

    def update(self):
        canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        y_offset = 30
        surviving_messages = []

        for msg in self.active_messages:
            if msg["frames_left"] > 0:
                # 2. Draw the text directly onto our black canvas
                cv2.putText(canvas, msg["text"], (10, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, msg["colour"], 2)

                # Move the next message down by 30 pixels so they stack neatly
                y_offset += 30

                # Tick down the lifespan
                msg["frames_left"] -= 1
                surviving_messages.append(msg)

        # Overwrite our old list with only the surviving messages
        self.active_messages = surviving_messages

        # 3. Show the dedicated window!
        cv2.imshow(self.window_name, canvas)


logger = ScreenLogger()