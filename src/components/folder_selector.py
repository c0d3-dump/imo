import flet as ft

from src.scripts import config, utils

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
        self.selected_folder = ft.Text(base_folder.split("/")[-1])
        self.file_processing = ft.Text("")

        page.add(
            ft.Row(
                [
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            on_click=self.refresh_files,
                        ),
                        self.file_processing
                    ]),
                    ft.Row([
                        self.selected_folder,
                        ft.ElevatedButton(
                            "Pick Folder",
                            icon=ft.Icons.UPLOAD,
                            on_click=lambda _: directory_picker.get_directory_path(),
                        ),
                    ])
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        )

    def on_dialog_result(self, e: ft.FilePickerResultEvent):
        if not e.path:
            return
        self.page.client_storage.set("base_folder", e.path)
        self.selected_folder.value = e.path
        self.page.update()

    def refresh_files(self, e):
        base_folder = self.page.client_storage.get("base_folder")
        files = config.file.list_files(base_folder)

        for file in files:
            self.file_processing.value = file
            self.page.update()

            try:
                config.db.get_file_by_name(file)
            except:
                self.store_embeddings(file)

            config.db.update_file(file, True)

        self.file_processing.value = ""
        self.page.update()

    def store_embeddings(self, file: str):
        try:
            file_extension = file.split('.')[-1].lower()

            if file_extension in FILE_TYPES["text"]:
                saved_file = config.db.save_file(file, "text", False)
                data = config.file.read_string(file)
                for txt in data.split("\n"):
                    if not txt.strip() or utils.is_number(txt.strip()):
                        continue

                    vector = config.llm_model.embed_text(txt.strip())
                    config.db.save_vector(
                        saved_file['id'], txt.strip(), vector)

            elif file_extension in FILE_TYPES["image"]:
                saved_file = config.db.save_file(file, "image", False)
                res = config.llm_model.embed_image(file)
                config.db.save_vector(saved_file['id'], res[0], res[1])
        except:
            config.db.delete_vector_by_file_name(file)
