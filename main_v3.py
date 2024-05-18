import base64
import threading
import flet as ft
import cv2


# ... other imports
class CameraManager:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)  # Open default webcam
        self.frame = None
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        t = threading.Thread(target=self.update_frame)
        t.start()

    def stop(self):
        self.running = False
        self.cap.release()

    def update_frame(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame

    def get_latest_frame(self):
        with self.lock:
            return self.frame

    def process_frame(self, frame):
        # Implement your image processing logic here (optional)
        # ...
        return frame

    def get_frame_and_process(self):
        frame = self.get_latest_frame()
        if frame is not None:
            frame = self.process_frame(frame)
        return frame


class Camera(ft.UserControl):

    def __init__(self):
        super().__init__()
        self.img = ft.Image(border_radius=ft.border_radius.all(20))

    def did_mount(self):
        self.update_timer()

    def update_timer(self):
        while True:
            frame = manager.get_frame_and_process()
            if frame is None:
                break

            # Encode frame to base64 for Flet
            _, im_arr = cv2.imencode('.png', frame)
            im_b64 = base64.b64encode(im_arr).decode("utf-8")

            # Update image source in Flet
            self.img.src_base64 = im_b64
            self.update()

    def build(self):
        self.img = ft.Image(
            self.img.src_base64,
            border_radius=ft.border_radius.all(20)
        )
        return self.img


manager = CameraManager()


def main(page: ft.Page):
    page.title = "Webcam"

    # Start camera capture thread
    manager.start()
    page.add(Camera())

    # ... other Flet app logic


if __name__ == '__main__':
    ft.app(target=main)
    # Release resources after app termination

    manager.stop()
    cv2.destroyAllWindows()
