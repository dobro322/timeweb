import shutil


def zip_folder(folder_path):
    return shutil.make_archive(folder_path, 'zip', folder_path)
