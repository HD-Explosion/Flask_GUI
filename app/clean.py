import os, shutil

def remove_userfolder(folderpath):
    for filename in os.listdir(folderpath):
        folder_path = os.path.join(folderpath, filename)
        print(folder_path)
        try:
            if os.path.isfile(folder_path) or os.path.islink(folder_path):
                os.unlink(folder_path)
            elif os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                print("folders have been removed")
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (folder_path, e))