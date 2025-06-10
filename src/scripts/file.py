import glob
import json
import os


class File():
    def __init__(self):
        pass

    def list_files(self, dir_path: str):
        result = []

        for x in os.walk(dir_path):
            for y in glob.glob(os.path.join(x[0], '*.*')):
                result.append(y)

        return result

    def read_json(self, file_path: str):
        with open(file_path, 'r') as file:
            content = file.read()

        return json.loads(content)

    def read_string(self, file_path: str):
        with open(file_path, 'r') as file:
            content = file.read()

        return content

    def read_csv(self, file_path: str):
        pass

    def read_pdf(self, file_path: str):
        pass
