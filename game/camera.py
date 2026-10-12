class Camera:
    def __init__(self, screen, camera_pos, camera_dist):
        self.screen = screen
        self.camera_pos = camera_pos
        self.camera_dist = camera_dist

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.perspective = True