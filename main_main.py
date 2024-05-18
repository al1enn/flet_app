import flet as ft
import base64
from insightface.app import FaceAnalysis
import cv2
from funcs import look_straight
from flet import Page
from pymongo import MongoClient
from funcs import calculate_rectangle_area

THRESHOLD_ADD_DB = 60
THRESHOLD_AREA = 1700
mongo_url = "mongodb+srv://test:y9Ye1cxR7U6JPdSf@cluster0.am0iol8.mongodb.net/"
client = MongoClient(mongo_url)
db = client.test
coll = db['annoy_test']


class Camera(ft.UserControl):

    def __init__(self):
        super().__init__()
        self.app = FaceAnalysis()
        self.app.prepare(ctx_id=0)
        self.age = ft.Text("", size=20, weight='bold', color='white')
        self.gender = ft.Text("", size=20, weight='bold', color='white')
        self.name = ft.Text("", size=20, weight='bold', color='white')
        self.score = ft.Text("", size=20, weight='bold', color='white')
        self.img = ft.Image(
            border_radius=ft.border_radius.all(10)
        )
        self.cap = cv2.VideoCapture(0)

    def did_mount(self):
        self.update_timer()

    # def restart(self):
    #     if self.cap.isOpened():
    #         self.stop_camera()
    #
    #     self.cap = cv2.VideoCapture(0)
    #
    #     if self.cap.isOpened():
    #         self.update_timer()
    #         self.update()
    #         print("Camera restarted successfully")
    #     else:
    #         print("Failed to restart camera")

    def stop_camera(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def update_timer(self):
        while True:
            # ret, frame = self.cap.read()  # Читаем кадр из видеопотока
            ret, frame = self.cap.read()  #
            if not ret:
                break
            # Обнаружение лиц на кадре
            faces = self.app.get(frame)
            if faces:
                for face in faces:
                    # emb = face['embedding']
                    age = face['age']
                    gender = face['gender']
                    gender = "male" if gender == 1 else "female"
                    bbox = face['bbox']
                    pose = face['pose']
                    x_min, y_min, x_max, y_max = bbox
                    # Нарисовать прямоугольник bbox
                    area = calculate_rectangle_area(bbox)
                    if area > THRESHOLD_AREA:
                        cv2.rectangle(frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
                        # cv2.putText(frame, f"Age: {age}", (int(x_min), int(y_min) - 10), cv2.FONT_HERSHEY_COMPLEX, 1,
                        #             (255, 255, 255), 2)
                        # cv2.putText(frame, f"Gender: {gender}", (int(x_min), int(y_min) + int(y_max) + 10),
                        #             cv2.FONT_HERSHEY_COMPLEX, 1,
                        #             (255, 255, 255), 2)
                    front = look_straight(pose)
                    # print(front)
                    if len(front) != 0:
                        cv2.putText(frame, f"{front}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))
                        self.age.value = f"Age: "
                        self.gender.value = f"Gender: "
                        self.page.update()
                    else:
                        # self.score, self.name = self.who_is(emb)
                        self.age.value = f"Age: {age}"
                        self.gender.value = f"Gender: {gender}"
                        self.page.update()
            else:
                cv2.putText(frame, 'not face', (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))
            # img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # self.img = ft.Image(src=img.tobytes())
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
        # return self.img
        # return ft.Column([
        #     self.img,
        #     ft.Row([
        #         self.gender
        #         # ft.Text(f"Gender: {self.gender}", size=20, weight='bold', color='white')
        #     ]),
        #     ft.Row([
        #         self.age
        #         # ft.Text(f"Age: {self.age}", size=20, weight='bold', color='white')
        #     ]),
        #     ft.Row([
        #         self.name
        #         # ft.Text(f"Age: {self.age}", size=20, weight='bold', color='white')
        #     ]), ft.Row([
        #         self.score
        #         # ft.Text(f"Age: {self.age}", size=20, weight='bold', color='white')
        #     ])
        # ])


class Camera2(ft.UserControl):

    def __init__(self):
        super().__init__()
        self.app = FaceAnalysis()
        self.app.prepare(ctx_id=0)
        self.age = ft.Text("", size=20, weight='bold', color='white')
        self.gender = ft.Text("", size=20, weight='bold', color='white')
        self.name = ft.Text("", size=20, weight='bold', color='white')
        self.score = ft.Text("", size=20, weight='bold', color='white')
        self.img = ft.Image(
            border_radius=ft.border_radius.all(10)
        )
        self.cap = cv2.VideoCapture(0)

    def did_mount(self):
        self.update_timer()

    # def restart(self):
    #     if self.cap.isOpened():
    #         self.stop_camera()
    #
    #     self.cap = cv2.VideoCapture(0)
    #
    #     if self.cap.isOpened():
    #         self.update_timer()
    #         self.update()
    #         print("Camera restarted successfully")
    #     else:
    #         print("Failed to restart camera")

    def stop_camera(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def update_timer(self):
        if self.cap.isOpened():
            self.cap.release()
        else:
            self.cap = cv2.VideoCapture(0)
            while True:
                ret, frame = self.cap.read()  # Читаем кадр из видеопотока
                if not ret:
                    break
                # Обнаружение лиц на кадре
                faces = self.app.get(frame)
                if faces:
                    for face in faces:
                        # emb = face['embedding']
                        age = face['age']
                        gender = face['gender']
                        gender = "male" if gender == 1 else "female"
                        bbox = face['bbox']
                        pose = face['pose']
                        x_min, y_min, x_max, y_max = bbox
                        # Нарисовать прямоугольник bbox
                        area = calculate_rectangle_area(bbox)
                        if area > THRESHOLD_AREA:
                            cv2.rectangle(frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
                            # cv2.putText(frame, f"Age: {age}", (int(x_min), int(y_min) - 10), cv2.FONT_HERSHEY_COMPLEX, 1,
                            #             (255, 255, 255), 2)
                            # cv2.putText(frame, f"Gender: {gender}", (int(x_min), int(y_min) + int(y_max) + 10),
                            #             cv2.FONT_HERSHEY_COMPLEX, 1,
                            #             (255, 255, 255), 2)
                        front = look_straight(pose)
                        # print(front)
                        if len(front) != 0:
                            cv2.putText(frame, f"{front}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))
                            self.age.value = f"Age: "
                            self.gender.value = f"Gender: "
                            self.page.update()
                        else:
                            # self.score, self.name = self.who_is(emb)
                            self.age.value = f"Age: {age}"
                            self.gender.value = f"Gender: {gender}"
                            self.page.update()
                else:
                    cv2.putText(frame, 'not face', (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))
                # img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # self.img = ft.Image(src=img.tobytes())
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
        # return self.img
        # return ft.Column([
        #     self.img,
        #     ft.Row([
        #         self.gender
        #         # ft.Text(f"Gender: {self.gender}", size=20, weight='bold', color='white')
        #     ]),
        #     ft.Row([
        #         self.age
        #         # ft.Text(f"Age: {self.age}", size=20, weight='bold', color='white')
        #     ]),
        #     ft.Row([
        #         self.name
        #         # ft.Text(f"Age: {self.age}", size=20, weight='bold', color='white')
        #     ]), ft.Row([
        #         self.score
        #         # ft.Text(f"Age: {self.age}", size=20, weight='bold', color='white')
        #     ])
        # ])


section = ft.Container(
    margin=ft.margin.only(bottom=20),
    content=ft.Row([
        ft.Card(
            width=600,
            height=500,
            elevation=30,
            content=ft.Container(
                bgcolor='blue',
                padding=5,
                border_radius=ft.border_radius.all(10),
                content=ft.Column([
                    Camera2(),
                ]
                ),
            )
        )
    ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
)


# class FaceRecognitionApp(ft.UserControl):
#
#     def build(self) -> ft.Control:
#         return ft.Tabs(
#             selected_index=0,
#             tabs=[
#                 ft.Tab(
#                     text="Generate data",
#                     icon=ft.icons.INSERT_CHART,
#                     content=Camera(),
#                 ),
#                 ft.Tab(
#                     text="Train model",
#                     icon=ft.icons.ATTACH_FILE,
#                     content=Camera(),
#                 ),
#                 ft.Tab(
#                     text="Recognize faces",
#                     icon=ft.icons.FIND_IN_PAGE,
#                     # content=ft.Text("Recognize faces"),
#                     content=Camera(),
#                 )
#             ],
#             expand=True,
#         )


# class FaceRecognitionApp(ft.UserControl):
#     def __init__(self):
#         super().__init__()
#         self._camera_instances = {}
#
#     def build(self) -> ft.Control:
#         return ft.Tabs(
#             selected_index=0,
#             animation_duration=300,
#             tabs=[
#                 ft.Tab(
#                     text="Generate data",
#                     icon=ft.icons.INSERT_CHART,
#                     content=self._get_tab_content("Generate data"),
#                 ),
#                 ft.Tab(
#                     text="Train model",
#                     icon=ft.icons.ATTACH_FILE,
#                     content=self._get_tab_content("Train model"),
#                 ),
#                 ft.Tab(
#                     text="Recognize faces",
#                     icon=ft.icons.FIND_IN_PAGE,
#                     content=self._get_tab_content("Recognize faces"),
#                 ),
#             ],
#             expand=True,
#         )
#
#     def _get_tab_content(self, tab_name):
#         if tab_name not in self._camera_instances:
#             if tab_name == "Recognize faces":
#                 camera_instance = Camera()
#             else:
#                 camera_instance = ft.Text(f"Content for {tab_name} tab")  # Placeholder content for other tabs
#             self._camera_instances[tab_name] = camera_instance
#         return self._camera_instances[tab_name]


def main(page: Page):
    def custom_app_bar():
        return ft.AppBar(
            title=ft.Text("Facial Recognition"),
            leading=ft.Icon(ft.icons.FACE),
        )

    page.title = "Web camera"
    page.adaptive = True
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.add(
        ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Generate data",
                    icon=ft.icons.INSERT_CHART,
                    content=Camera()
                ),
                ft.Tab(
                    text="Train model",
                    icon=ft.icons.ATTACH_FILE,
                    content=section,

                ),
                ft.Tab(
                    text="Recognize faces",
                    icon=ft.icons.FIND_IN_PAGE,
                    content=section
                )
            ],
            expand=True,
        ),

    )

    page.appbar = custom_app_bar()
    page.theme = ft.Theme(color_scheme=ft.ColorScheme(primary=ft.colors.YELLOW_300))
    page.update()


if __name__ == '__main__':
    ft.app(target=main)
    cv2.destroyAllWindows()
