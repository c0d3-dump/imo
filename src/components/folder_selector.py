import flet as ft

from src.scripts import config

FILE_TYPES = {
    "text": ["txt", "pdf"],
    "image": ["png", "jpg", "jpeg"]
}


class FolderSelector():
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page
        directory_picker = ft.FilePicker(on_result=self.on_dialog_result)
        page.overlay.append(directory_picker)

        base_folder = self.page.client_storage.get("base_folder")
        self.text = ft.Text(base_folder)

        page.add(
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        on_click=self.refresh_files,
                    ),
                    ft.ElevatedButton(
                        "Pick Folder",
                        icon=ft.Icons.UPLOAD,
                        on_click=lambda _: directory_picker.get_directory_path(),
                    ),
                    self.text
                ],
            )
        )

    def on_dialog_result(self, e: ft.FilePickerResultEvent):
        self.page.client_storage.set("base_folder", e.path)
        self.text.value = e.path
        self.page.update()

    def refresh_files(self, e):
        base_folder = self.page.client_storage.get("base_folder")
        files = config.file.list_files(base_folder)
        print(files)

        for file in files:
            file_extension = file.split('.')[-1].lower()

            if file_extension in FILE_TYPES["text"]:
                saved_file = config.db.save_file(file, "text", False)

                data = config.file.read_string(file)

                for txt in data.split("\n"):
                    vector = config.llm_model.embed_text(txt)
                    config.db.save_vector(saved_file['id'], txt, vector)

            elif file_extension in FILE_TYPES["image"]:
                saved_file = config.db.save_file(file, "image", False)

                res = config.llm_model.embed_image(file)
                config.db.save_vector(saved_file['id'], res[0], res[1])

            print(f"embedding done :> {file}")

            config.db.update_file(file, True)
