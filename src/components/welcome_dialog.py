import flet as ft

from src.schemas import Message


class WelcomeDialog():
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page
        self.join_user_name = self.text_field()
        self.welcome_dlg = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Welcome!"),
            content=ft.Column([self.join_user_name],
                              width=300, height=70, tight=True),
            actions=[ft.ElevatedButton(
                text="Join chat", on_click=self.join_chat_click)],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(self.welcome_dlg)

    def text_field(self):
        return ft.TextField(
            label="Enter your name to join the chat",
            autofocus=True,
            on_submit=self.join_chat_click,
        )

    def join_chat_click(self, e):
        if not self.join_user_name.value:
            self.join_user_name.error_text = "Name cannot be blank!"
            self.join_user_name.update()
        else:
            self.page.client_storage.set(
                "user_name", self.join_user_name.value)
            self.welcome_dlg.open = False
            self.page.update()
