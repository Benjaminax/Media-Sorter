import os
import shutil
import re
import logging
import time

# Dynamically get the user's home directory
home_directory = os.path.expanduser("~")
downloads_folders = [
    os.path.join(home_directory, "Downloads"),
    os.path.join(home_directory, "Downloads", "Telegram Desktop")
]
movies_folder = os.path.join(home_directory, "Videos", "Movies")
series_folder = os.path.join(home_directory, "Videos", "Series")

target_folder = None  # For moving sorted files back

# Define file extensions
media_extensions = ['.mp4', '.mkv', '.avi', '.mov']

# Set up logging
log_file = os.path.join(home_directory, "sort_files.log")
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def replace_underscores_and_dots(file_name):
    return file_name.replace('_', ' ').replace('.', ' ')

def is_series(file_name):
    series_pattern = re.compile(r'.*[Ss](\d{1,2})[Ee](\d{1,2})', re.IGNORECASE)
    return series_pattern.search(file_name)

def get_series_info(file_name):
    match = re.search(r'(.+?)[Ss](\d{1,2})[Ee](\d{1,2})', file_name, re.IGNORECASE)
    if match:
        series_name = match.group(1).strip()
        season = f"Season {int(match.group(2))}"
        return series_name, season
    return None, None

def get_unique_filename(dest_folder, file_name):
    base_name, extension = os.path.splitext(file_name)
    unique_name = file_name
    counter = 1
    while os.path.exists(os.path.join(dest_folder, unique_name)):
        unique_name = f"{base_name}_{counter}{extension}"
        counter += 1
    return unique_name

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")

def move_file(src_path, dest_folder, file_name):
    retries = 3
    for attempt in range(retries):
        try:
            ensure_directory_exists(dest_folder)
            unique_name = get_unique_filename(dest_folder, file_name)
            dest_path = os.path.join(dest_folder, unique_name)
            logging.info(f"Moving file from {src_path} to {dest_path}")
            shutil.move(src_path, dest_path)
            logging.info(f"Moved {file_name} to {dest_folder}")
            break
        except PermissionError as e:
            logging.error(f"Permission error moving {file_name}: {str(e)}")
            time.sleep(5)
        except FileNotFoundError as e:
            logging.error(f"File not found: {file_name}. Error: {str(e)}")
            break
        except Exception as e:
            logging.error(f"Error moving {file_name}: {str(e)}")
            break

def process_downloads_folder(downloads_folder):
    for file_name in os.listdir(downloads_folder):
        file_path = os.path.join(downloads_folder, file_name)
        if os.path.isdir(file_path):
            continue
        try:
            if any(file_name.lower().endswith(ext) for ext in media_extensions):
                file_name_with_spaces = replace_underscores_and_dots(file_name)
                if is_series(file_name_with_spaces):
                    series_name, season = get_series_info(file_name_with_spaces)
                    if series_name:
                        series_folder_path = os.path.join(series_folder, series_name, season)
                        move_file(file_path, series_folder_path, file_name)
                    else:
                        move_file(file_path, movies_folder, file_name)
                else:
                    move_file(file_path, movies_folder, file_name)
        except Exception as e:
            logging.error(f"Failed to process {file_name}: {str(e)}")

def move_sorted_files_back():
    global target_folder
    if not target_folder:
        print("No target folder selected to move files back.")
        return
    for root, _, files in os.walk(series_folder):
        for file_name in files:
            move_file(os.path.join(root, file_name), target_folder, file_name)
    for root, _, files in os.walk(movies_folder):
        for file_name in files:
            move_file(os.path.join(root, file_name), target_folder, file_name)

def main_menu():
    global target_folder
    while True:
        print("\nSelect an option:")
        print("1. Move sorted files back to Telegram Desktop")
        print("2. Move sorted files back to Downloads folder")
        print("3. Sort files into Series and Movies")
        print("4. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            target_folder = os.path.join(home_directory, "Downloads", "Telegram Desktop")
            move_sorted_files_back()
        elif choice == "2":
            target_folder = os.path.join(home_directory, "Downloads")
            move_sorted_files_back()
        elif choice == "3":
            sort_files()
        elif choice == "4":
            confirm = input("Are you sure you want to exit? (yes/no): ")
            if confirm.lower() == "yes":
                break
        else:
            print("Invalid choice. Try again.")

def sort_files():
    for downloads_folder in downloads_folders:
        if os.path.exists(downloads_folder):
            process_downloads_folder(downloads_folder)
        else:
            logging.error(f"Downloads folder not found: {downloads_folder}")

if __name__ == "__main__":
    main_menu()