import glob
import os
import fitz


class File():
    def __init__(self):
        pass

    def list_files(self, dir_path: str):
        result = []

        for x in os.walk(dir_path):
            for y in glob.glob(os.path.join(x[0], '*.*')):
                result.append(y)

        return result

    def read_string(self, file_path: str):
        file_extension = file_path.split('.')[-1].lower()

        if file_extension == "pdf":
            return self.read_pdf(file_path)

        with open(file_path, 'r') as file:
            content = file.read()

        return content

    def read_pdf(self, file_path: str):
        with fitz.open(file_path) as doc:
            full_text = ""

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page.clean_contents()
                page.apply_redactions()
                full_text += page.get_text().strip()
            return full_text
        return ""
