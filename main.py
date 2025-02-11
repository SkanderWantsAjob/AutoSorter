import os
import shutil
import time
import logging
import colorlog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# Directories
source_dir = "C:/Users/benac/Downloads"
dest_dir_sfx = "C:/Users/benac/Downloads/Sound"
dest_dir_music = "C:/Users/benac/Downloads/Sound/music"
dest_dir_video = "C:/Users/benac/Downloads/Downloaded Videos"
dest_dir_image = "C:/Users/benac/Downloads/downloaded Images"

os.makedirs(dest_dir_sfx, exist_ok=True)
os.makedirs(dest_dir_music, exist_ok=True)
os.makedirs(dest_dir_video, exist_ok=True)
os.makedirs(dest_dir_image, exist_ok=True)

# Configure colored logging using colorlog

log_colors={
        'DEBUG': 'bold_green',        # Debug logs in green
        'INFO': 'blue',          # Info logs in blue
        'WARNING': 'yellow',     # Warning logs in yellow
        'ERROR': 'red',          # Error logs in red
        'CRITICAL': 'bold_red',  # Critical logs in bold red
    }


log_format = "%(asctime)s - %(log_color)s%(message)s"
log_handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(log_format, log_colors=log_colors)
log_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

def makeUnique(path):
    """Ensure unique filename if file already exists"""
    filename, extension = os.path.splitext(path)
    counter = 1
    while os.path.exists(path):
        path = f"{filename} ({counter}){extension}"
        counter += 1
    logger.info(f"Created unique path: {path}")
    return path

def is_file_complete(file_path):
    """Check if the file is still downloading by comparing its size over time"""
    initial_size = os.path.getsize(file_path)
    time.sleep(2)  
    final_size = os.path.getsize(file_path)
    if initial_size == final_size:
        logger.debug(f"File completed downloading: {file_path}")
        return True
    else:
        logger.error(f"File still downloading: {file_path}")
        return False

def move(dest, entry, name):
    """Move file to the destination folder"""
    new_path = os.path.join(dest, name)
    if os.path.exists(new_path):
        logger.info(f"already a file name {name}")
        new_path = makeUnique(new_path)

    try:
        shutil.move(entry.path, new_path)
    except shutil.Error as e:
        logger.error(f"Error moving file {entry.name}: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error moving file {entry.name}: {e}")

class MoverHandler(FileSystemEventHandler):
    def on_modified(self, event):
        """Triggered when files are modified"""
        time.sleep(1)  # Delay to prevent moving incomplete files
        logger.warning("Directory modified, checking files...")
        
        with os.scandir(source_dir) as entries:
            for entry in entries:
                if not entry.is_file():
                    continue  # Skip folders
                
                name = entry.name
                dest = None

                if name.endswith(('.wav', '.mp3')):
                    logger.info(f"{name} -> Detected as audio file")
                    dest = dest_dir_sfx if entry.stat().st_size < 25_000_000 or "SFX" in name else dest_dir_music
                elif name.endswith(('.mov', '.mp4')):
                    logger.info(f"{name} -> Detected as video file")
                    dest = dest_dir_video
                elif name.endswith(('.jpg', '.jpeg', '.png')):
                    logger.info(f"{name} -> Detected as image file")
                    dest = dest_dir_image

                if dest:
                    if is_file_complete(entry.path):
                        move(dest, entry, name)
                        logger.debug(f"Moved {name} to {dest}")

if __name__ == "__main__":
    observer = Observer()
    event_handler = MoverHandler()
    observer.schedule(event_handler, source_dir, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
