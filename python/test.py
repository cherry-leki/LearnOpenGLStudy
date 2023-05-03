import os
import glob

path = "./**/**/*.py"

# top_folders = os.listdir("./")
# top_folders = [folder for folder in top_folders if folder.startswith("0")]

# for folder in top_folders:
#     path = "./" + folder + "/"
#     folders = os.listdir(path)
#     folders = [file for file in folders if file.startswith("0")]

path = "./**/**/*.py"
tutorial_file_list = glob.glob(path)
folder_path_list = []
chap_name_list   = []
flie_name_list   = []

for file in tutorial_file_list:
    chapter_name = file.split("/")[1]
    file_name    = file.split("/")[-1]
    
    folder_path_list.append(file)
    chap_name_list.append(chapter_name + "/" + file_name)
    flie_name_list.append(file_name)

print(chap_name_list)
print(flie_name_list)
# files = [file for file in file_list if file.split("/").startswith("") and file.endswith(".py")]