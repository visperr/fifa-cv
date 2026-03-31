class BoundingBox:
    def __init__(self, x1, y1, x2, y2):
        self.x = x1
        self.y = y1
        self.x2 = x2
        self.y2 = y2
        self.width = x2 - x1
        self.height = y2 - y1

    def get_roi(self, frame):
        roi = frame[self.y:self.y2, self.x:self.x2]
        return roi