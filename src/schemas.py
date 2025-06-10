from typing import Iterator, Optional
import flet as ft
from ollama import ChatResponse


class Message:
    def __init__(self, user_name: str, text: str, message_type: str, text_stream: Optional[Iterator[ChatResponse]] = None):
        self.user_name = user_name
        self.text = text
        self.text_stream = text_stream
        self.message_type = message_type


class ChatMessage(ft.Row):
    def __init__(self, page: ft.Page, message: Message):
        super().__init__()

        self.page = page
        self.message = message
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.text = ft.Text(message.text, selectable=True)
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight="bold"),
                    self.text
                ],
                tight=True,
                spacing=5,
                width=800,
            ),
        ]

    def stream_text(self):
        if not self.message.text_stream:
            return

        for chunk in self.message.text_stream:
            d = chunk['message']['content']
            self.text.value += d
            self.page.update()

    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"  # or any default value you prefer

    def get_avatar_color(self, user_name: str):
        if user_name == "AI":
            return ft.Colors.AMBER
        return ft.Colors.GREEN
