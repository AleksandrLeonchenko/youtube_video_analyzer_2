import tarfile

# Указываем путь к вашему архиву
tar_file_path = "../ssd_mobilenet_v2_coco_2018_03_29.tar.gz"

# Указываем путь, куда вы хотите распаковать архив
# extract_path = "../ssd_mobilenet_v2_coco_2018_03_29"
extract_path = ".."

# Открываем архив для чтения
with tarfile.open(tar_file_path, 'r:gz') as tar:
    # Распаковываем содержимое архива
    tar.extractall(extract_path)

print("Архив успешно распакован.")
