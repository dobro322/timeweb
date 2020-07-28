import shutil


def zip_folder(filename, folder_path):
    return shutil.make_archive("./app/sites/{0}".format(filename), 'zip', folder_path)
