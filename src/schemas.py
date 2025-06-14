from typing import Iterator, List, Optional
import flet as ft
from ollama import ChatResponse
from src.scripts import config
import webbrowser


class Message:
    def __init__(self, user_name: str, text: str, text_stream: Optional[Iterator[ChatResponse]] = None):
        self.user_name = user_name
        self.text = text
        self.text_stream = text_stream


class ChatMessage(ft.Row):
    def __init__(self, page: ft.Page, message: Message):
        super().__init__()

        self.page = page
        self.message = message
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.text = message.text

        self.docs = ft.Column()
        res_text = self.split_text()
        self.thinking = ft.Text(res_text[0], color=ft.Colors.GREY_500)
        self.response = ft.Text(res_text[1], selectable=True)

        msg = []
        if message.user_name == "AI":
            msg = [
                ft.Text(message.user_name, weight="bold"),
                ft.ExpansionTile(
                    title=ft.Text("Thinking..."),
                    affinity=ft.TileAffinity.LEADING,
                    initially_expanded=False,
                    collapsed_text_color=ft.Colors.GREY_400,
                    text_color=ft.Colors.GREY_400,
                    controls=[
                        ft.ListTile(title=self.thinking, dense=True),
                    ],
                ),
                self.docs,
                self.response,
            ]
        else:
            msg = [
                ft.Text(message.user_name, weight="bold"),
                self.response
            ]

        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                msg,
                tight=True,
                spacing=5,
                width=1160,
            ),
        ]

    def set_document(self, external_id: str):
        file = config.db.get_file_by_id(int(external_id))

        if len(self.docs.controls) > 0:
            return

        if file['file_type'] == 'image':
            self.docs.controls.append(
                ft.Image(
                    src=file['file_name'],
                    width=200,
                    height=200,
                    fit=ft.ImageFit.COVER,
                    repeat=ft.ImageRepeat.NO_REPEAT,
                    border_radius=ft.border_radius.all(10),
                )
            )
        else:
            self.docs.controls.append(
                ft.ElevatedButton(
                    text=file['file_name'].split("/")[-1],
                    on_click=lambda _: self.open_file_in_browser(
                        file["file_name"]),
                )
            )

    def open_file_in_browser(self, file_path: str):
        file_url = f"file://{file_path}"
        webbrowser.open(file_url)

    def split_text(self) -> List[str]:
        if "<think>" in self.text:
            txt = self.text.split("<think>")[1].strip()
            if "</think>" in txt:
                txt = txt.split("</think>")

                if "response: " not in txt[1]:
                    return [txt[0].strip(), ""]

                res = txt[1].strip().split("external_id: ")[1]
                res2 = res.split("\nresponse: ")

                external_id = res2[0].strip()

                if external_id != "-1":
                    self.set_document(external_id)

                return [txt[0].strip(), res2[1].strip()]

            return [txt.strip(), ""]
        return ["", self.text.strip()]

    def stream_text(self) -> str:
        if not self.message.text_stream:
            return self.response.value

        for chunk in self.message.text_stream:
            d = chunk['message']['content']
            self.text += d

            res_text = self.split_text()
            self.thinking.value = res_text[0]
            self.response.value = res_text[1]

            self.page.update()

        return self.text

    def get_initials(self, user_name: str) -> str:
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"  # or any default value you prefer

    def get_avatar_color(self, user_name: str) -> str:
        if user_name == "AI":
            return ft.Colors.AMBER
        return ft.Colors.GREEN
