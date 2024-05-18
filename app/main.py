import os
import shutil

import flet as ft
import base64
from insightface.app import FaceAnalysis
import cv2
from funcs import look_straight
from flet import Page
from pymongo import MongoClient
from funcs import calculate_rectangle_area
from threading import Thread, Lock

capture = cv2.VideoCapture(0)
THRESHOLD_ADD_DB = 60
THRESHOLD_AREA = 3000
IMAGES_PATH = 'app/upload_images'


# mongo_url = "mongodb+srv://test:y9Ye1cxR7U6JPdSf@cluster0.am0iol8.mongodb.net/"
# client = MongoClient(mongo_url)
# db = client.test
# coll = db['annoy_test']


class CameraStream(object):
    def __init__(self):
        self.stream = cv2.VideoCapture(0)

        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = Lock()

    def start(self):
        if self.started:
            print("already started!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            (grabbed, frame) = self.stream.read()
            self.read_lock.acquire()
            self.grabbed, self.frame = grabbed, frame
            self.read_lock.release()

    def read(self):
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.release()


class Image(ft.UserControl):

    def __init__(self):
        super().__init__()
        self.cap = CameraStream().start()
        self.app = FaceAnalysis()
        self.app.prepare(ctx_id=0)
        self.img = ft.Image(
            border_radius=ft.border_radius.all(10)
        )

    def did_mount(self):
        self.update_timer()

    def update_timer(self):
        while True:
            frame = self.cap.read()
            faces = self.app.get(frame)
            if faces:
                for face in faces:
                    bbox = face['bbox']
                    pose = face['pose']
                    x_min, y_min, x_max, y_max = bbox
                    # Нарисовать прямоугольник bbox
                    area = calculate_rectangle_area(bbox)
                    if area > THRESHOLD_AREA:
                        cv2.rectangle(frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
                        front = look_straight(pose)
                        # print(front)
                        if len(front) != 0:
                            cv2.putText(frame, f"{front}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))
                            # self.name=
                            self.page.update()
                        else:
                            self.page.update()
            else:
                cv2.putText(frame, 'not face', (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))

            _, im_arr = cv2.imencode('.png', frame)
            im_b64 = base64.b64encode(im_arr)
            self.img.src_base64 = im_b64.decode("utf-8")
            self.update()

    def build(self):
        self.img = ft.Image(
            border_radius=ft.border_radius.all(10)
        )
        return ft.Column(
            [ft.Row([self.img], alignment=ft.MainAxisAlignment.CENTER)],
            alignment=ft.MainAxisAlignment.CENTER
        )


class EnterName(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.t = ft.Text()
        self.name = ft.TextField(label="Name")
        self.surname = ft.TextField(label="Surname")
        self.b = ft.ElevatedButton(text="Submit", height=50, on_click=lambda _: self.button_clicked())

    def button_clicked(self):
        self.t.value = f"Input Values are:  '{self.name}', {self.surname}"
        self.update()

    def build(self):
        return ft.Column(
            [
                self.t,
                self.name,
                self.surname,
                self.b,
            ]
        )


def main(page: Page):
    # Pick files dialog
    def pick_files_result(e: ft.FilePickerResultEvent):
        if not os.path.exists(IMAGES_PATH):
            os.makedirs(IMAGES_PATH, exist_ok=True)

        if e.files:
            selected_file_name = e.files[0].name
            new_path = os.path.join(IMAGES_PATH, selected_file_name)
            file_path = e.files[0].path

            shutil.copyfile(file_path, new_path)
            selected_file.value = new_path
            selected_file.update()

            # Обновление изображения
            image_widget.src = new_path
            image_widget.update()
        else:
            selected_file.value = "Cancelled!"
            selected_file.update()

        page.update()

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    selected_file = ft.Text()
    image_widget = ft.Image(width=400, height=400, fit=ft.ImageFit.COVER, repeat=ft.ImageRepeat.NO_REPEAT,
                            border_radius=ft.border_radius.all(20))

    filepicker = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            height=50,
                            text="Upload image",
                            icon=ft.icons.UPLOAD_FILE,
                            expand=True,
                            disabled=page.web,
                            on_click=lambda _: pick_files_dialog.pick_files(
                                allow_multiple=False
                            ),
                        ),

                    ]
                ),
                ft.Row(
                    controls=[
                        ft.Row(controls=[ft.Column(controls=[
                            ft.Row(
                                controls=[EnterName()]),
                            ft.Row(
                                controls=[
                                    selected_file,
                                    image_widget
                                ],

                                alignment=ft.MainAxisAlignment.CENTER,
                            )])]),
                    ]
                )

            ]
        ),
        padding=ft.padding.only(top=20),

    )

    # hide all dialogs in overlay
    page.overlay.extend([pick_files_dialog])

    def custom_app_bar():
        return ft.AppBar(
            title=ft.Text("Facial Recognition"),
            leading=ft.Icon(ft.icons.FACE),
        )

    page.title = "Web camera"
    page.adaptive = True
    page.padding = 20
    page.add(
        ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Recognize face",
                    icon=ft.icons.FIND_IN_PAGE,
                    content=ft.Container(content=Image()),
                ),
                ft.Tab(
                    text="Add face",
                    icon=ft.icons.ATTACH_FILE,
                    content=filepicker
                    # content=()
                ),

                ft.Tab(
                    text="Build model",
                    icon=ft.icons.INSERT_CHART,
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton(
                                            height=50,
                                            text="Start build",
                                            expand=True,
                                        ),
                                    ]
                                )
                            ]
                        ),
                        padding=ft.padding.only(top=20)
                    )
                )
            ],
            expand=True,

        ),
    )
    page.appbar = custom_app_bar()
    # page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme=ft.ColorScheme(primary=ft.colors.BLUE_ACCENT))
    page.update()


if __name__ == '__main__':
    ft.app(target=main)
    cv2.destroyAllWindows()
