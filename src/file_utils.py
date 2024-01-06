import os


class FileUtils:
    @staticmethod
    def create_dir_if_not_exists(*args):
        output_path = os.path.join(*args)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        return output_path
