import flet as ft

from src.chat import Chat
from src.components.welcome_dialog import WelcomeDialog
from src.components.folder_selector import FolderSelector


def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.window.resizable = False
    page.title = "Vector Chat"

    # page.client_storage.clear()
    user_name = page.client_storage.get("user_name")

    if not user_name:
        WelcomeDialog(page)

    FolderSelector(page)

    Chat(page)


ft.app(target=main)
