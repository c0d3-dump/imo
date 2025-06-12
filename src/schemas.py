from typing import Iterator, List, Literal, Optional
import flet as ft
from ollama import ChatResponse


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
                self.response
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

    def split_text(self) -> List[str]:
        if "<think>" in self.text:
            txt = self.text.split("<think>")[1].strip()
            if "</think>" in txt:
                txt = txt.split("</think>")
                return [txt[0].strip(), txt[1].strip()]

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

        return self.response.value

    def get_initials(self, user_name: str) -> str:
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"  # or any default value you prefer

    def get_avatar_color(self, user_name: str) -> str:
        if user_name == "AI":
            return ft.Colors.AMBER
        return ft.Colors.GREEN
