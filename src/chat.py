import flet as ft

from src.schemas import Message, ChatMessage
from src.scripts import config


class Chat():
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page
        self.no_folder_alert = ft.AlertDialog(
            open=False,
            content=ft.Text("Please select folder to continue chat"),
        )
        self.page.overlay.append(self.no_folder_alert)

        self.new_message = self.text_field()

        self.chat = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True,
        )

        self.chat_list()
        self.page.pubsub.subscribe(self.on_message)

        history = config.db.get_history()
        for h in history:
            m = ChatMessage(self.page, Message(h['role'], h['message']))
            self.chat.controls.append(m)

        self.page.update()

    def text_field(self):
        return ft.TextField(
            hint_text="Write a message...",
            autofocus=True,
            shift_enter=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            prefix=self.page.client_storage.get("user_name"),
            on_submit=self.send_message_click,
        )

    def chat_list(self):
        self.page.add(
            ft.Container(
                content=self.chat,
                border=ft.border.all(1, ft.Colors.OUTLINE),
                border_radius=5,
                padding=10,
                expand=True,
            ),
            ft.Row(
                [
                    self.new_message,
                    ft.IconButton(
                        icon=ft.Icons.SEND_ROUNDED,
                        tooltip="Send message",
                        on_click=self.send_message_click,
                    ),
                ]
            ),
        )

    def send_message_click(self, e):
        base_folder = self.page.client_storage.get("base_folder")
        if not base_folder:
            self.page.open(self.no_folder_alert)
            return

        if self.new_message.value != "":
            self.page.pubsub.send_all(
                Message(
                    self.page.client_storage.get("user_name"),
                    self.new_message.value,
                ),
            )
            msg = self.new_message.value
            self.new_message.value = ""
            self.new_message.focus()
            self.page.update()

            embeddings = config.llm_model.embed_text(msg)
            context = config.db.search_vector(embeddings)
            context = "\n".join(
                [f"vector_id: {ctx['id']} \nslug: {ctx['slug']}\n" for ctx in context])
            response = config.llm_model.chat(msg, context)

            self.page.pubsub.send_all(
                Message(
                    "AI",
                    "",
                    response,
                ),
            )

            self.new_message.focus()
            self.page.update()

    def on_message(self, message: Message):
        m = ChatMessage(self.page, message)

        self.chat.controls.append(m)
        text = m.stream_text()

        # parse data to fetch only required info

        config.db.save_history(message.user_name, text)

        self.page.update()
